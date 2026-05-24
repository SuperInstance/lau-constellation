/*
 * cm7_lattice.c — Bare-metal Lattice Oscillator for STM32H7 (Cortex-M7)
 *
 * No OS, no stdlib — just registers, interrupts, DMA, and math.
 * Target: STM32H743, 480MHz, double-precision FPU
 * Codec: CS42L52 via I2S (or compatible)
 *
 * Features:
 *   - Timer interrupt at 44100 Hz generates audio samples
 *   - DMA double-buffered output to I2S codec
 *   - 8 partials per voice, 4 polyphonic voices
 *   - CMSIS-DSP sin() approximation
 *   - Fits in 64KB RAM
 *
 * Memory budget:
 *   - 4 voices × 8 partials × 16 bytes (state) = 512 bytes
 *   - DMA buffer: 2 × 256 samples × 4 bytes = 2048 bytes
 *   - Stack + misc: ~2KB
 *   - Total: ~5KB (well within 64KB)
 *
 * Build: arm-none-eabi-gcc -mcpu=cortex-m7 -mthumb -mfpu=fpv5-d16 \
 *        -O2 -nostdlib -T stm32h7.ld cm7_lattice.c -o cm7_lattice.elf
 */

#include <stdint.h>

/* ========================================================================= */
/* Register base addresses                                                     */
/* ========================================================================= */
#define PERIPH_BASE         0x40000000UL
#define APB1PERIPH_BASE     PERIPH_BASE
#define APB2PERIPH_BASE     (PERIPH_BASE + 0x00010000UL)
#define AHB1PERIPH_BASE     (PERIPH_BASE + 0x00020000UL)
#define AHB4PERIPH_BASE     (0x58020000UL)

/* RCC */
#define RCC_BASE            (0x58024400UL)
#define RCC_AHB4ENR         (*((volatile uint32_t *)(RCC_BASE + 0x0E0)))
#define RCC_APB1LENR        (*((volatile uint32_t *)(RCC_BASE + 0x0E8)))
#define RCC_APB2ENR         (*((volatile uint32_t *)(RCC_BASE + 0x0F0)))
#define RCC_D2CCIP2R        (*((volatile uint32_t *)(RCC_BASE + 0x054)))

/* GPIO */
#define GPIOA_BASE          (AHB4PERIPH_BASE + 0x0000)
#define GPIOB_BASE          (AHB4PERIPH_BASE + 0x0400)
#define GPIOC_BASE          (AHB4PERIPH_BASE + 0x0800)
#define GPIO_MODER(g)       (*((volatile uint32_t *)((g) + 0x00)))
#define GPIO_OTYPER(g)      (*((volatile uint32_t *)((g) + 0x04)))
#define GPIO_OSPEEDR(g)     (*((volatile uint32_t *)((g) + 0x08)))
#define GPIO_AFRL(g)        (*((volatile uint32_t *)((g) + 0x20)))
#define GPIO_AFRH(g)        (*((volatile uint32_t *)((g) + 0x24)))

/* TIM6 (basic timer for audio sample rate) */
#define TIM6_BASE           (APB1PERIPH_BASE + 0x0400)
#define TIM6_CR1            (*((volatile uint32_t *)(TIM6_BASE + 0x00)))
#define TIM6_DIER           (*((volatile uint32_t *)(TIM6_BASE + 0x0C)))
#define TIM6_SR             (*((volatile uint32_t *)(TIM6_BASE + 0x10)))
#define TIM6_PSC            (*((volatile uint32_t *)(TIM6_BASE + 0x28)))
#define TIM6_ARR            (*((volatile uint32_t *)(TIM6_BASE + 0x2C)))
#define TIM6_CNT            (*((volatile uint32_t *)(TIM6_BASE + 0x24)))

/* DMA1 (for I2S audio streaming) */
#define DMA1_BASE           (AHB1PERIPH_BASE + 0x0000)
#define DMA1_STREAM0_CR     (*((volatile uint32_t *)(DMA1_BASE + 0x010)))
#define DMA1_STREAM0NDTR    (*((volatile uint32_t *)(DMA1_BASE + 0x014)))
#define DMA1_STREAM0PAR     (*((volatile uint32_t *)(DMA1_BASE + 0x018)))
#define DMA1_STREAM0M0AR    (*((volatile uint32_t *)(DMA1_BASE + 0x01C)))
#define DMA1_STREAM0M1AR    (*((volatile uint32_t *)(DMA1_BASE + 0x020)))
#define DMA1_STREAM0FCR     (*((volatile uint32_t *)(DMA1_BASE + 0x024)))

/* SPI2/I2S2 (audio interface to codec) */
#define SPI2_BASE           (APB1PERIPH_BASE + 0x3800)
#define SPI2_CR1            (*((volatile uint32_t *)(SPI2_BASE + 0x00)))
#define SPI2_CFG1           (*((volatile uint32_t *)(SPI2_BASE + 0x04)))
#define SPI2_I2SCFGR        (*((volatile uint32_t *)(SPI2_BASE + 0x1C)))
#define SPI2_I2SPR          (*((volatile uint32_t *)(SPI2_BASE + 0x20)))
#define SPI2_TXDR           (*((volatile uint32_t *)(SPI2_BASE + 0x0C)))

/* NVIC */
#define NVIC_BASE           (0xE000E100UL)
#define NVIC_ISER0          (*((volatile uint32_t *)(NVIC_BASE + 0x00)))
#define NVIC_ICER0          (*((volatile uint32_t *)(NVIC_BASE + 0x080)))

/* SysTick for delay */
#define SYSTICK_BASE        (0xE000E010UL)
#define SYSTICK_CSR         (*((volatile uint32_t *)(SYSTICK_BASE + 0x00)))
#define SYSTICK_RVR         (*((volatile uint32_t *)(SYSTICK_BASE + 0x04)))
#define SYSTICK_CVR         (*((volatile uint32_t *)(SYSTICK_BASE + 0x08)))

/* SCB */
#define SCB_BASE            (0xE000ED00UL)
#define SCB_VTOR            (*((volatile uint32_t *)(SCB_BASE + 0x08)))

/* ========================================================================= */
/* Constants                                                                    */
/* ========================================================================= */
#define SAMPLE_RATE         44100
#define SYSCLK_FREQ         480000000
#define APB1_FREQ           120000000
#define BUFFER_SIZE         256         /* samples per DMA half-buffer */
#define NUM_VOICES          4
#define NUM_PARTIALS        8
#define NUM_CHANNELS        2           /* stereo output */

/* ========================================================================= */
/* Types                                                                        */
/* ========================================================================= */

/* Single partial oscillator state */
typedef struct {
    float phase;           /* current phase accumulator */
    float phase_inc;       /* phase increment per sample */
    float amplitude;       /* partial amplitude */
    float ratio;           /* frequency ratio to fundamental */
} PartialOsc;

/* One polyphonic voice */
typedef struct {
    float frequency;       /* fundamental frequency (Hz), 0 = inactive */
    PartialOsc partials[NUM_PARTIALS];
    float consonance;      /* current consonance score */
} Voice;

/* ========================================================================= */
/* Lattice partial ratios (from constraint theory)                             */
/*   These are the Just Intonation intervals from the (i,j,k) lattice        */
/* ========================================================================= */
static const float LATTICE_RATIOS[NUM_PARTIALS] = {
    1.0f,       /* fundamental */
    1.5f,       /* 3/2 — perfect fifth */
    1.25f,      /* 5/4 — major third */
    1.875f,     /* 15/8 — major seventh */
    2.0f,       /* octave */
    2.25f,      /* 9/4 — major ninth */
    2.5f,       /* 5/2 — major tenth */
    3.125f      /* 25/8 — augmented thirteenth */
};

static const float LATTICE_AMPS[NUM_PARTIALS] = {
    1.0f, 0.6f, 0.45f, 0.3f, 0.25f, 0.15f, 0.1f, 0.05f
};

/* ========================================================================= */
/* Globals (in DTCM RAM for zero-wait-state access)                            */
/* ========================================================================= */

/* Audio DMA buffers (double-buffered) — aligned for DMA */
__attribute__((section(".dtcmram")))
__attribute__((aligned(4)))
static int16_t audio_buf0[BUFFER_SIZE * NUM_CHANNELS];

__attribute__((section(".dtcmram")))
__attribute__((aligned(4)))
static int16_t audio_buf1[BUFFER_SIZE * NUM_CHANNELS];

/* Voice state */
__attribute__((section(".dtcmram")))
static Voice voices[NUM_VOICES];

/* Current write position in active buffer */
__attribute__((section(".dtcmram")))
static volatile int buf_pos = 0;

/* Which DMA buffer is active (0 or 1) */
__attribute__((section(".dtcmram")))
static volatile int active_buf = 0;

/* Sample counter for timing */
__attribute__((section(".dtcmram")))
static volatile uint32_t sample_count = 0;

/* ========================================================================= */
/* CMSIS-DSP inline sin() — polynomial approximation (Horn's method)           */
/* This is the fast path; we don't link the full CMSIS library.               */
/* Range: x in [-π, π]. Accuracy: ~2e-7                                      */
/* ========================================================================= */
static inline float fast_sin(float x)
{
    /* Range reduction to [-π, π] */
    const float INV_TWO_PI = 0.159154943091895f;  /* 1 / (2π) */
    const float TWO_PI = 6.283185307179586f;

    float k = x * INV_TWO_PI;
    k = (float)((int)(k + (k >= 0 ? 0.5f : -0.5f)));  /* round */
    x = x - k * TWO_PI;

    /* Further reduce to [-π/2, π/2] using identities:
     *   sin(π - x) = sin(x)
     *   sin(-x) = -sin(x)
     */
    int sign = 1;
    if (x < 0) { x = -x; sign = -1; }
    if (x > 3.14159265f) { x -= 3.14159265f; sign = -sign; }
    if (x > 1.57079633f) { x = 3.14159265f - x; }

    /* 5th-order polynomial approximation (Horn's method)
     * Coefficients from CMSIS-DSP arm_sin_f32 */
    const float c1 = -1.666666716337e-01f;
    const float c2 =  8.333331965578e-03f;
    const float c3 = -1.984059863258e-04f;
    const float c4 =  2.716628193520e-06f;
    const float c5 = -2.053551234504e-08f;

    float x2 = x * x;
    float result = x + x * x2 * (c1 + x2 * (c2 + x2 * (c3 + x2 * (c4 + x2 * c5))));

    return result * (float)sign;
}

/* ========================================================================= */
/* Voice management                                                            */
/* ========================================================================= */

/* Initialize a voice with a frequency. freq=0 means inactive. */
static void voice_init(Voice *v, float freq)
{
    v->frequency = freq;
    if (freq == 0.0f) return;

    float base_phase_inc = freq / SAMPLE_RATE;

    for (int i = 0; i < NUM_PARTIALS; i++) {
        v->partials[i].phase = 0.0f;
        v->partials[i].ratio = LATTICE_RATIOS[i];
        v->partials[i].phase_inc = base_phase_inc * LATTICE_RATIOS[i];
        v->partials[i].amplitude = LATTICE_AMPS[i];
    }

    /* Compute consonance from lattice structure:
     * Higher consonance = lower indices = simpler ratios
     * This is a simplified heuristic */
    v->consonance = 1.0f;  /* Will be updated by constraint engine */
}

/* Note on: find a free voice and start it */
void note_on(float freq)
{
    /* Find inactive voice */
    for (int i = 0; i < NUM_VOICES; i++) {
        if (voices[i].frequency == 0.0f) {
            voice_init(&voices[i], freq);
            return;
        }
    }
    /* All voices active — steal the oldest (voice 0) */
    voice_init(&voices[0], freq);
}

/* Note off: silence a voice */
void note_off(float freq)
{
    for (int i = 0; i < NUM_VOICES; i++) {
        if (voices[i].frequency == freq) {
            voices[i].frequency = 0.0f;
            return;
        }
    }
}

/* ========================================================================= */
/* Audio sample generation                                                     */
/* ========================================================================= */

/* Compute one sample: sum all active voices and their partials */
static inline float compute_sample(void)
{
    float sample = 0.0f;

    for (int v = 0; v < NUM_VOICES; v++) {
        if (voices[v].frequency == 0.0f) continue;

        float voice_out = 0.0f;
        for (int p = 0; p < NUM_PARTIALS; p++) {
            PartialOsc *osc = &voices[v].partials[p];

            /* Compute sin using phase accumulator */
            float angle = osc->phase * 6.283185307179586f;  /* × 2π */
            voice_out += osc->amplitude * fast_sin(angle);

            /* Advance phase (wrapping at 1.0) */
            osc->phase += osc->phase_inc;
            if (osc->phase >= 1.0f) osc->phase -= 1.0f;
            if (osc->phase < 0.0f)  osc->phase += 1.0f;
        }

        sample += voice_out;
    }

    /* Normalize: divide by (voices × partials) to prevent clipping */
    sample /= (float)(NUM_VOICES * NUM_PARTIALS);

    return sample;
}

/* ========================================================================= */
/* Timer6 ISR — fires at SAMPLE_RATE Hz, computes one audio sample            */
/* ========================================================================= */
void TIM6_DAC_IRQHandler(void)
{
    /* Clear interrupt flag */
    TIM6_SR = 0;

    /* Compute sample */
    float s = compute_sample();

    /* Convert float to int16 */
    if (s > 1.0f) s = 1.0f;
    if (s < -1.0f) s = -1.0f;
    int16_t sample16 = (int16_t)(s * 32767.0f);

    /* Write to current DMA buffer (stereo: duplicate L→R) */
    int16_t *buf = (active_buf == 0) ? audio_buf0 : audio_buf1;
    buf[buf_pos * 2]     = sample16;   /* Left channel */
    buf[buf_pos * 2 + 1] = sample16;   /* Right channel */

    buf_pos++;
    sample_count++;

    /* Buffer full? Signal main loop */
    if (buf_pos >= BUFFER_SIZE) {
        buf_pos = 0;
        active_buf = 1 - active_buf;    /* Swap buffers */
        /* In a real implementation, we'd trigger DMA here or
         * the DMA half-complete interrupt handles the swap */
    }
}

/* ========================================================================= */
/* Hardware initialization                                                     */
/* ========================================================================= */

static void clock_init(void)
{
    /* Assume system clock is already configured by SystemInit
     * (HSI 64MHz or HSE → PLL → 480MHz).
     * For bare-metal, you'd configure PLL here. */
}

static void gpio_init(void)
{
    /* Enable GPIO clocks */
    RCC_AHB4ENR |= (1 << 0) | (1 << 1) | (1 << 2);  /* GPIOA, B, C */

    /* I2S2 pins: PB12 (I2S2_WS), PB13 (I2S2_SCK), PB15 (I2S2_SD) */
    /* AF6 for SPI2/I2S2 */
    GPIO_MODER(GPIOB_BASE) &= ~(3 << (12*2)) | (3 << (13*2)) | (3 << (15*2));
    GPIO_MODER(GPIOB_BASE) |=  (2 << (12*2)) | (2 << (13*2)) | (2 << (15*2));  /* AF mode */
    GPIO_AFRL(GPIOB_BASE) = (GPIO_AFRL(GPIOB_BASE) & ~(0xF << (12*4))) | (6 << (12*4));
    GPIO_AFRH(GPIOB_BASE) = (GPIO_AFRH(GPIOB_BASE) & ~(0xF << ((13-8)*4))) | (6 << ((13-8)*4));
    GPIO_AFRH(GPIOB_BASE) = (GPIO_AFRH(GPIOB_BASE) & ~(0xF << ((15-8)*4))) | (6 << ((15-8)*4));
    GPIO_OSPEEDR(GPIOB_BASE) |= (3 << (12*2)) | (3 << (13*2)) | (3 << (15*2));  /* High speed */
}

static void timer6_init(void)
{
    /* Enable TIM6 clock */
    RCC_APB1LENR |= (1 << 4);   /* TIM6EN */

    /* TIM6 is on APB1 (120MHz with system clock at 480MHz) */
    /* We want 44100 Hz interrupt rate:
     *   prescaler = 0 (divide by 1), ARR = APB1_FREQ / SAMPLE_RATE
     *   But TIM6 runs at APB1×2 = 240MHz when system is 480MHz
     *   ARR = 240000000 / 44100 = 5442 */
    TIM6_PSC = 0;                          /* No prescaler */
    TIM6_ARR = (APB1_FREQ * 2) / SAMPLE_RATE;  /* Auto-reload */

    /* Enable update interrupt */
    TIM6_DIER |= (1 << 0);    /* UIE: Update interrupt enable */

    /* Enable TIM6 in NVIC */
    NVIC_ISER0 |= (1 << 54);  /* TIM6_DAC_IRQn = 54 */

    /* Start timer */
    TIM6_CR1 |= (1 << 0);     /* CEN: Counter enable */
}

static void dma_init(void)
{
    /* Enable DMA1 clock */
    RCC_AHB1ENR |= (1 << 0);   /* DMA1EN */

    /* Configure DMA1 Stream0 for SPI2_TX (I2S output) */
    DMA1_STREAM0_CR = 0;        /* Disable stream first */

    /* Wait for stream to be disabled */
    while (DMA1_STREAM0_CR & 1) ;

    /* Configure:
     *   CHSEL[2:0] = 001 (SPI2_TX on channel 1)
     *   MBURST = 00 (single)
     *   PBURST = 00 (single)
     *   DIR[1:0] = 01 (memory → peripheral)
     *   CIRC = 1 (circular / double-buffer mode)
     *   MINC = 1 (memory increment)
     *   MSIZE = 01 (16-bit)
     *   PSIZE = 01 (16-bit)
     *   TCIE = 1 (transfer complete interrupt)
     *   HTIE = 1 (half-transfer interrupt) */
    DMA1_STREAM0_CR = (1 << 25) |   /* CHSEL = 1 (SPI2_TX) */
                      (1 << 10) |   /* MSIZE = 16-bit */
                      (1 << 8)  |   /* PSIZE = 16-bit */
                      (1 << 7)  |   /* MINC */
                      (1 << 6)  |   /* CIRC */
                      (1 << 5)  |   /* DIR = mem→periph */
                      (1 << 4)  |   /* TCIE */
                      (1 << 3);    /* HTIE */

    DMA1_STREAM0NDTR = BUFFER_SIZE * NUM_CHANNELS;
    DMA1_STREAM0PAR  = (uint32_t)&SPI2_TXDR;
    DMA1_STREAM0M0AR = (uint32_t)audio_buf0;
    DMA1_STREAM0M1AR = (uint32_t)audio_buf1;

    /* FIFO mode disabled (direct mode) */
    DMA1_STREAM0FCR = 0;

    /* Enable stream */
    DMA1_STREAM0_CR |= (1 << 0);  /* EN */
}

static void i2s_init(void)
{
    /* Configure I2S2 as master transmitter, 16-bit, 44100 Hz */
    RCC_APB1LENR |= (1 << 14);    /* SPI2EN */

    /* Disable SPI first */
    SPI2_CR1 &= ~(1 << 0);

    /* I2S mode configuration:
     *   I2SMOD = 1 (I2S mode)
     *   I2SCFG[1:0] = 10 (master transmit)
     *   I2SSTD[1:0] = 00 (I2S Philips)
     *   CKPOL = 0 (clock idle low)
     *   DATLEN = 00 (16-bit data)
     *   CHLEN = 0 (16-bit channel) */
    SPI2_I2SCFGR = (1 << 11) |    /* I2SMOD */
                   (2 << 9)  |    /* I2SCFG = master TX */
                   (0 << 4);     /* 16-bit data */

    /* I2S clock: MCKEN=0, ODD=0, I2SDIV
     * For 44100 Hz from 240MHz:
     *   I2SDIV = (240M / (44100 × 32 × 2)) - 1  (for 16-bit stereo)
     *   = 240000000 / 2822400 - 1 ≈ 84 */
    SPI2_I2SPR = 84;

    /* Enable I2S */
    SPI2_I2SCFGR |= (1 << 10);    /* I2SE */
}

/* ========================================================================= */
/* Main                                                                         */
/* ========================================================================= */

/* Simple delay using SysTick */
static void delay_ms(uint32_t ms)
{
    SYSTICK_RVR = 480000 - 1;     /* 1ms at 480MHz */
    SYSTICK_CSR = 5;              /* processor clock, enable */

    for (uint32_t i = 0; i < ms; i++) {
        while (!(SYSTICK_CSR & (1 << 16))) ;  /* Wait for COUNTFLAG */
    }
    SYSTICK_CSR = 0;              /* Disable */
}

int main(void)
{
    /* Disable interrupts during init */
    __asm volatile ("cpsid i");

    /* Initialize hardware */
    clock_init();
    gpio_init();
    i2s_init();
    dma_init();
    timer6_init();

    /* Initialize all voices as inactive */
    for (int i = 0; i < NUM_VOICES; i++) {
        voices[i].frequency = 0.0f;
    }

    /* Play a demo chord: A minor (A3, C4, E4, A4) */
    note_on(220.0f);     /* A3 */
    note_on(261.63f);    /* C4 */
    note_on(329.63f);    /* E4 */
    note_on(440.0f);     /* A4 */

    /* Enable interrupts — audio starts! */
    __asm volatile ("cpsie i");

    /* Main loop: sleep between timer interrupts */
    while (1) {
        /* WFI (Wait For Interrupt) — lowest power */
        __asm volatile ("wfi");

        /* Optional: check for MIDI input, dial changes, etc.
         * The constraint engine could update voice parameters here. */
    }

    /* Never reached */
    return 0;
}

/* ========================================================================= */
/* Reset handler (entry point for bare-metal)                                  */
/* ========================================================================= */
void Reset_Handler(void)
{
    /* Copy .data from flash to RAM (if needed) */
    /* Zero .bss */
    extern uint32_t _sbss, _ebss;
    for (uint32_t *p = &_sbss; p < &_ebss; p++) *p = 0;

    /* Call main */
    main();
}

/* ========================================================================= */
/* Vector table — must be at 0x08000000 (flash base)                          */
/* ========================================================================= */
__attribute__((section(".isr_vector")))
void (*const vector_table[])(void) = {
    (void *)0x20020000,          /* Initial stack pointer (end of DTCM) */
    Reset_Handler,               /* Reset */
    0, 0, 0, 0, 0, 0, 0, 0,     /* Reserved */
    0, 0, 0, 0, 0, 0,           /* Reserved */
    0,                           /* PendSV */
    0,                           /* SysTick */
    /* External interrupts (0-80+) ... we only define TIM6 */
    [54 + 16] = TIM6_DAC_IRQHandler,  /* TIM6 IRQ at position 54 */
};
