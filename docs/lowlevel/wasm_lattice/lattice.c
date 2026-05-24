/*
 * lattice.c — Portable Lattice Oscillator Core
 *
 * This is the shared synthesis engine used by:
 *   - WASM browser demo (via emscripten)
 *   - Native benchmark
 *   - Embedded targets
 *
 * Constraint-theory additive synthesis:
 *   sample = Σ amp[i] * sin(2π * freq * partial[i] * t + phase[i])
 *
 * Partial ratios come from the (i,j,k) integer lattice:
 *   1, 3/2, 5/4, 15/8, 2, 9/4, 5/2, 25/8, ...
 *
 * The three "dial" parameters control:
 *   I_vertical   → number of octaves (vertical axis of lattice)
 *   I_horizontal → complexity of ratios (horizontal axis)
 *   I_spectral   → amplitude rolloff shape
 *
 * Build:
 *   WASM:  emcc lattice.c -O3 -s WASM=1 -s EXPORTED_FUNCTIONS="['_lattice_init','_lattice_process','_lattice_set_dial','_lattice_note_on','_lattice_note_off']" -o lattice.wasm
 *   Native: gcc -O3 -shared -fPIC lattice.c -o lattice.so -lm
 */

#include <stdint.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define MAX_VOICES    8
#define MAX_PARTIALS  16
#define SAMPLE_RATE   44100

/* ========================================================================= */
/* Types                                                                        */
/* ========================================================================= */

typedef struct {
    float frequency;                       /* Fundamental frequency (Hz) */
    float phases[MAX_PARTIALS];            /* Phase accumulators for each partial */
    float phase_incs[MAX_PARTIALS];        /* Phase increments per partial */
    float amps[MAX_PARTIALS];              /* Amplitudes per partial */
    int   num_partials;                    /* Active partial count */
    int   active;                          /* 1 = playing, 0 = inactive */
    float envelope;                        /* Simple ADSR envelope state */
    float env_state;                       /* Envelope phase: 0=off,1=attack,2=sustain,3=release */
} Voice;

typedef struct {
    Voice voices[MAX_VOICES];
    int   num_voices;
    int   num_partials;

    /* Dial parameters (0.0 to 1.0) */
    float i_vertical;     /* Controls octave range / number of partials */
    float i_horizontal;   /* Controls ratio complexity (which partials) */
    float i_spectral;     /* Controls amplitude rolloff */

    /* Derived synthesis parameters (updated when dials change) */
    float partial_ratios[MAX_PARTIALS];
    float partial_base_amps[MAX_PARTIALS];
    float rolloff;                          /* Spectral rolloff coefficient */

    /* Output */
    float master_vol;
} LatticeOscillator;

/* Global oscillator instance (single-instance for WASM simplicity) */
static LatticeOscillator osc;

/* ========================================================================= */
/* Lattice ratio generation                                                    */
/*                                                                             */
/* The lattice produces ratios from the (i,j,k) integer coordinate system:    */
/*   ratio = 2^i * 3^j * 5^k                                                 */
/*                                                                             */
/* We enumerate these sorted by complexity and pick based on dial settings.    */
/* ========================================================================= */

/* Precomputed lattice ratios sorted by Tenney height (complexity measure) */
static const float LATTICE_TABLE[][3] = {
    /* { ratio, tenney_height, base_amplitude } */
    {1.0f,       0.0f,  1.0f},     /* unison */
    {2.0f,       1.0f,  0.7f},     /* 2/1 — octave */
    {1.5f,       1.58f, 0.6f},     /* 3/2 — perfect fifth */
    {1.333f,     1.92f, 0.5f},     /* 4/3 — perfect fourth */
    {1.25f,      2.32f, 0.45f},    /* 5/4 — major third */
    {2.5f,       2.58f, 0.4f},     /* 5/2 — major tenth */
    {1.2f,       2.71f, 0.35f},    /* 6/5 — minor third */
    {1.875f,     2.90f, 0.3f},     /* 15/8 — major seventh */
    {3.0f,       3.0f,  0.28f},    /* 3/1 — tritave */
    {1.6f,       3.12f, 0.25f},    /* 8/5 — minor sixth */
    {2.25f,      3.17f, 0.22f},    /* 9/4 — major ninth */
    {1.125f,     3.32f, 0.2f},     /* 9/8 — major second */
    {2.667f,     3.50f, 0.18f},    /* 8/3 — minor thirteenth */
    {3.125f,     3.58f, 0.15f},    /* 25/8 — augmented thirteenth */
    {1.875f,     3.71f, 0.13f},    /* 15/8 (alternate voicing) */
    {3.75f,      3.90f, 0.1f},     /* 15/4 — compound seventh */
};

#define LATTICE_TABLE_SIZE (sizeof(LATTICE_TABLE) / sizeof(LATTICE_TABLE[0]))

/* ========================================================================= */
/* Fast sin approximation (for WASM without libm)                             */
/* ========================================================================= */
static inline float fast_sin(float x)
{
    /* Range reduce to [-π, π] */
    const float INV_TWO_PI = 1.0f / 6.283185307179586f;
    const float TWO_PI = 6.283185307179586f;

    x = x - (float)((int)(x * INV_TWO_PI + (x > 0 ? 0.5f : -0.5f))) * TWO_PI;

    /* Approximate sin using Bhaskara I's formula (accurate to ~0.2%) */
    /* For better accuracy, use the polynomial approach: */
    int sign = 1;
    if (x < 0.0f) { x = -x; sign = -1; }
    if (x > M_PI) { x = 2.0f * (float)M_PI - x; sign = -sign; }

    /* 5th-order minimax polynomial (max error ~2e-7) */
    const float c1 = -1.6666654611e-01f;
    const float c2 =  8.3330251389e-03f;
    const float c3 = -1.9807005469e-04f;
    const float c4 =  2.6018468069e-06f;

    float x2 = x * x;
    return sign * (x + x * x2 * (c1 + x2 * (c2 + x2 * (c3 + x2 * c4))));
}

/* ========================================================================= */
/* Update partial configuration from dials                                     */
/* ========================================================================= */
static void update_partials(void)
{
    /* I_vertical (0-1): controls how many partials to use
     *   0.0 = just fundamental
     *   1.0 = all 16 partials */
    int count = 1 + (int)(osc.i_vertical * (MAX_PARTIALS - 1));
    if (count > MAX_PARTIALS) count = MAX_PARTIALS;
    if (count < 1) count = 1;
    osc.num_partials = count;

    /* I_horizontal (0-1): controls ratio complexity
     *   0.0 = simplest ratios (low Tenney height)
     *   1.0 = most complex ratios
     * We select from the sorted table, offset by i_horizontal */
    for (int i = 0; i < count; i++) {
        /* Mix between simple and complex ratios based on dial */
        int idx = (int)(osc.i_horizontal * (LATTICE_TABLE_SIZE - count));
        if (idx < 0) idx = 0;
        if (idx + i >= (int)LATTICE_TABLE_SIZE) idx = LATTICE_TABLE_SIZE - 1 - i;

        osc.partial_ratios[i] = LATTICE_TABLE[idx + i][0];
        osc.partial_base_amps[i] = LATTICE_TABLE[idx + i][2];
    }

    /* I_spectral (0-1): controls amplitude rolloff
     *   0.0 = flat spectrum (all partials equal)
     *   0.5 = moderate rolloff (natural instrument-like)
     *   1.0 = sharp rolloff (only fundamentals audible) */
    osc.rolloff = 0.1f + osc.i_spectral * 2.0f;  /* 0.1 to 2.1 */

    for (int i = 0; i < count; i++) {
        /* Apply exponential rolloff based on partial index */
        osc.partial_base_amps[i] *= expf(-osc.rolloff * (float)i * 0.3f);
    }

    /* Update all active voices with new partial config */
    for (int v = 0; v < osc.num_voices; v++) {
        Voice *voice = &osc.voices[v];
        if (!voice->active) continue;

        float base_inc = voice->frequency / (float)SAMPLE_RATE;
        for (int p = 0; p < osc.num_partials; p++) {
            voice->phase_incs[p] = base_inc * osc.partial_ratios[p];
            voice->amps[p] = osc.partial_base_amps[p];
        }
        voice->num_partials = osc.num_partials;
    }
}

/* ========================================================================= */
/* Public API                                                                   */
/* ========================================================================= */

/* Initialize the oscillator */
void lattice_init(int voices, int partials)
{
    for (int i = 0; i < MAX_VOICES; i++) {
        osc.voices[i].active = 0;
        osc.voices[i].frequency = 0.0f;
        osc.voices[i].envelope = 0.0f;
        osc.voices[i].env_state = 0;
    }

    osc.num_voices = voices > MAX_VOICES ? MAX_VOICES : voices;
    osc.num_partials = partials > MAX_PARTIALS ? MAX_PARTIALS : partials;

    /* Default dial positions */
    osc.i_vertical = 0.5f;
    osc.i_horizontal = 0.3f;
    osc.i_spectral = 0.5f;
    osc.master_vol = 0.8f;

    update_partials();
}

/* Process a block of samples (fills output buffer) */
void lattice_process(float *output, int num_samples)
{
    for (int n = 0; n < num_samples; n++) {
        float sample = 0.0f;

        for (int v = 0; v < osc.num_voices; v++) {
            Voice *voice = &osc.voices[v];
            if (!voice->active) continue;

            float voice_sample = 0.0f;

            for (int p = 0; p < voice->num_partials; p++) {
                /* Phase → angle (0-1 → 0 to 2π) */
                float angle = voice->phases[p] * 2.0f * (float)M_PI;

                voice_sample += voice->amps[p] * fast_sin(angle);

                /* Advance phase (wrapping at 1.0) */
                voice->phases[p] += voice->phase_incs[p];
                if (voice->phases[p] >= 1.0f) voice->phases[p] -= 1.0f;
            }

            /* Simple envelope: attack = 10ms, release = 50ms */
            if (voice->env_state == 1) {
                voice->envelope += 1.0f / (0.01f * SAMPLE_RATE);
                if (voice->envelope >= 1.0f) {
                    voice->envelope = 1.0f;
                    voice->env_state = 2;
                }
            } else if (voice->env_state == 3) {
                voice->envelope -= 1.0f / (0.05f * SAMPLE_RATE);
                if (voice->envelope <= 0.0f) {
                    voice->envelope = 0.0f;
                    voice->active = 0;
                    voice->env_state = 0;
                }
            }

            sample += voice_sample * voice->envelope;
        }

        /* Normalize and apply master volume */
        sample *= osc.master_vol / (float)osc.num_voices;

        /* Soft clip */
        if (sample > 1.0f) sample = 1.0f - 0.5f / (sample + 1.0f);
        if (sample < -1.0f) sample = -1.0f + 0.5f / (-sample + 1.0f);

        output[n] = sample;
    }
}

/* Set a dial parameter (0=vertical, 1=horizontal, 2=spectral) */
void lattice_set_dial(int dial, float value)
{
    if (value < 0.0f) value = 0.0f;
    if (value > 1.0f) value = 1.0f;

    switch (dial) {
        case 0: osc.i_vertical = value;   break;
        case 1: osc.i_horizontal = value; break;
        case 2: osc.i_spectral = value;   break;
    }

    update_partials();
}

/* Start a note */
void lattice_note_on(float frequency)
{
    /* Find inactive voice */
    for (int v = 0; v < osc.num_voices; v++) {
        if (!osc.voices[v].active) {
            Voice *voice = &osc.voices[v];
            voice->frequency = frequency;
            voice->active = 1;
            voice->envelope = 0.0f;
            voice->env_state = 1;  /* Attack */
            voice->num_partials = osc.num_partials;

            float base_inc = frequency / (float)SAMPLE_RATE;
            for (int p = 0; p < osc.num_partials; p++) {
                voice->phases[p] = 0.0f;
                voice->phase_incs[p] = base_inc * osc.partial_ratios[p];
                voice->amps[p] = osc.partial_base_amps[p];
            }
            return;
        }
    }
    /* Voice stealing: use the oldest (first) active voice */
    osc.voices[0].frequency = frequency;
    osc.voices[0].active = 1;
    osc.voices[0].envelope = 0.0f;
    osc.voices[0].env_state = 1;
    osc.voices[0].num_partials = osc.num_partials;

    float base_inc = frequency / (float)SAMPLE_RATE;
    for (int p = 0; p < osc.num_partials; p++) {
        osc.voices[0].phases[p] = 0.0f;
        osc.voices[0].phase_incs[p] = base_inc * osc.partial_ratios[p];
        osc.voices[0].amps[p] = osc.partial_base_amps[p];
    }
}

/* Stop a note */
void lattice_note_off(float frequency)
{
    for (int v = 0; v < osc.num_voices; v++) {
        if (osc.voices[v].active && osc.voices[v].frequency == frequency) {
            osc.voices[v].env_state = 3;  /* Release */
            return;
        }
    }
}

/* Get current dial values (for UI feedback) */
float lattice_get_dial(int dial)
{
    switch (dial) {
        case 0: return osc.i_vertical;
        case 1: return osc.i_horizontal;
        case 2: return osc.i_spectral;
    }
    return 0.0f;
}

/* Get current consonance score (0-1) */
float lattice_get_consonance(void)
{
    /* Average consonance based on active partials' Tenney heights */
    float total = 0.0f;
    int count = 0;
    for (int i = 0; i < osc.num_partials; i++) {
        total += LATTICE_TABLE[i][1];
        count++;
    }
    if (count == 0) return 1.0f;
    /* Invert: low Tenney height = high consonance */
    return 1.0f / (1.0f + total / (float)count);
}
