/*
 * lattice.c — Portable Lattice Oscillator Core
 *
 * Constraint-theory additive synthesis with tradition-aware scales,
 * ADSR envelopes, simple delay-based reverb, and WAV export.
 *
 * Build:
 *   WASM:   emcc lattice.c -Os -s WASM=1 -s STANDALONE_WASM \
 *           -s EXPORTED_FUNCTIONS="['_lattice_init','_lattice_process',...]" \
 *           --no-entry -o lattice.wasm
 *   Native: gcc -O3 lattice.c -o lattice_native -lm
 */

#include <stdint.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define MAX_VOICES     8
#define MAX_PARTIALS   16
#define SAMPLE_RATE    44100
#define REVERB_DELAY   4410     /* ~100ms delay line */
#define REVERB_LINES   4
#define MAX_WAV_BYTES  (44100 * 30 * 2 * 2)  /* 30s stereo 16-bit */

/* ========================================================================= */
/* Types                                                                      */
/* ========================================================================= */

typedef struct {
    float attack;
    float decay;
    float sustain;
    float release;
} ADSR;

typedef struct {
    float frequency;
    float phases[MAX_PARTIALS];
    float phase_incs[MAX_PARTIALS];
    float amps[MAX_PARTIALS];
    int   num_partials;
    int   active;
    /* ADSR envelope */
    float envelope;
    float env_state;          /* 0=off, 1=attack, 2=decay, 3=sustain, 4=release */
    float env_target;
    ADSR  adsr;
} Voice;

typedef struct {
    Voice voices[MAX_VOICES];
    int   num_voices;
    int   num_partials;

    /* Dial parameters (0.0 to 1.0) */
    float i_vertical;
    float i_horizontal;
    float i_spectral;

    /* Derived synthesis parameters */
    float partial_ratios[MAX_PARTIALS];
    float partial_base_amps[MAX_PARTIALS];
    float rolloff;

    /* Tradition system */
    int   tradition_id;       /* -1 = free, 0-9 = tradition preset */
    float tradition_blend;    /* 0.0 = pure lattice, 1.0 = pure tradition */

    /* Reverb */
    float delay_lines[REVERB_LINES][REVERB_DELAY];
    int   delay_pos[REVERB_LINES];
    float reverb_mix;         /* 0.0 = dry, 1.0 = wet */

    /* Master */
    float master_vol;
    float peak_level;         /* For normalization / metering */

    /* WAV recording */
    int   recording;
    int16_t *wav_buffer;
    int   wav_samples;        /* Total samples recorded (mono) */
    int   wav_capacity;
} LatticeOscillator;

/* ========================================================================= */
/* Tradition Presets                                                          */
/*                                                                            */
/* Each tradition defines characteristic scale degrees (as frequency ratios)  */
/* and a preferred ADSR envelope + spectral profile.                          */
/* ========================================================================= */

typedef struct {
    const char *name;
    const char *color;
    float       ratios[MAX_PARTIALS];  /* Scale degrees as ratios from root */
    int         num_ratios;
    float       vertical;   /* Default I_vertical */
    float       horizontal; /* Default I_horizontal */
    float       spectral;   /* Default I_spectral */
    ADSR        adsr;
    float       reverb_mix;
} Tradition;

static const Tradition TRADITIONS[] = {
    /* 0: Pythagorean */
    { "Pythagorean", "#00ff88",
      {1.0f, 9/8.0f, 81/64.0f, 4/3.0f, 3/2.0f, 27/16.0f, 16/9.0f, 2.0f},
      8, 0.4f, 0.2f, 0.5f, {0.01f, 0.1f, 0.7f, 0.3f}, 0.2f },
    /* 1: Just Intonation */
    { "Just Intonation", "#44ff44",
      {1.0f, 9/8.0f, 5/4.0f, 4/3.0f, 3/2.0f, 5/3.0f, 15/8.0f, 2.0f},
      8, 0.3f, 0.15f, 0.4f, {0.005f, 0.15f, 0.8f, 0.4f}, 0.25f },
    /* 2: Meantone */
    { "Meantone", "#88ff00",
      {1.0f, 1.1180f, 1.25f, 1.3333f, 1.4953f, 1.6719f, 1.8692f, 2.0f},
      8, 0.5f, 0.25f, 0.45f, {0.008f, 0.2f, 0.65f, 0.35f}, 0.3f },
    /* 3: Arabic Maqam */
    { "Arabic Maqam", "#ffaa00",
      {1.0f, 1.0667f, 1.1852f, 1.25f, 1.3333f, 1.4222f, 1.5802f, 1.7778f,
       1.8889f, 2.0f},
      10, 0.6f, 0.4f, 0.55f, {0.002f, 0.05f, 0.9f, 0.5f}, 0.35f },
    /* 4: Indian Raga */
    { "Indian Raga", "#ff6600",
      {1.0f, 1.0535f, 1.1111f, 1.1852f, 1.25f, 1.3333f, 1.4222f,
       1.5f, 1.6f, 1.6667f, 1.7778f, 1.875f, 2.0f},
      13, 0.7f, 0.5f, 0.6f, {0.001f, 0.3f, 0.85f, 0.8f}, 0.4f },
    /* 5: Gamelan */
    { "Gamelan", "#ff0044",
      {1.0f, 1.125f, 1.2308f, 1.3636f, 1.5f, 1.6923f, 1.8462f, 2.0f},
      8, 0.8f, 0.6f, 0.7f, {0.001f, 0.01f, 0.5f, 0.05f}, 0.5f },
    /* 6: Japanese */
    { "Japanese", "#ff44aa",
      {1.0f, 1.125f, 1.35f, 1.5f, 1.6875f, 2.0f},
      6, 0.35f, 0.1f, 0.35f, {0.01f, 0.5f, 0.6f, 0.6f}, 0.3f },
    /* 7: Blues */
    { "Blues", "#4488ff",
      {1.0f, 1.0667f, 1.125f, 1.2f, 1.3333f, 1.4222f, 1.5f, 1.6f,
       1.6875f, 1.7778f, 1.875f, 2.0f},
      12, 0.5f, 0.35f, 0.6f, {0.001f, 0.02f, 0.75f, 0.15f}, 0.15f },
    /* 8: Spectral */
    { "Spectral", "#8844ff",
      {1.0f, 1.0144f, 1.5000f, 1.5146f, 2.0f, 2.0145f, 2.5000f, 2.5147f,
       3.0f, 3.5000f, 4.0f, 5.0f, 6.0f, 7.0f, 8.0f},
      15, 0.9f, 0.8f, 0.3f, {0.005f, 0.4f, 0.5f, 0.7f}, 0.6f },
    /* 9: Techno */
    { "Techno", "#00ccff",
      {1.0f, 1.0f, 1.0f, 1.0f, 1.0f, 1.0f, 1.0f, 1.0f},
      8, 0.95f, 0.0f, 0.2f, {0.0005f, 0.01f, 0.9f, 0.05f}, 0.1f },
};

#define NUM_TRADITIONS (sizeof(TRADITIONS) / sizeof(TRADITIONS[0]))

/* ========================================================================= */
/* Lattice ratio generation                                                   */
/* ========================================================================= */

static const float LATTICE_TABLE[][3] = {
    {1.0f,       0.0f,  1.0f},
    {2.0f,       1.0f,  0.7f},
    {1.5f,       1.58f, 0.6f},
    {1.333f,     1.92f, 0.5f},
    {1.25f,      2.32f, 0.45f},
    {2.5f,       2.58f, 0.4f},
    {1.2f,       2.71f, 0.35f},
    {1.875f,     2.90f, 0.3f},
    {3.0f,       3.0f,  0.28f},
    {1.6f,       3.12f, 0.25f},
    {2.25f,      3.17f, 0.22f},
    {1.125f,     3.32f, 0.2f},
    {2.667f,     3.50f, 0.18f},
    {3.125f,     3.58f, 0.15f},
    {1.875f,     3.71f, 0.13f},
    {3.75f,      3.90f, 0.1f},
};

#define LATTICE_TABLE_SIZE (sizeof(LATTICE_TABLE) / sizeof(LATTICE_TABLE[0]))

/* ========================================================================= */
/* Fast sin approximation                                                     */
/* ========================================================================= */
static inline float fast_sin(float x)
{
    const float INV_TWO_PI = 1.0f / 6.283185307179586f;
    const float TWO_PI = 6.283185307179586f;

    x = x - (float)((int)(x * INV_TWO_PI + (x > 0 ? 0.5f : -0.5f))) * TWO_PI;

    int sign = 1;
    if (x < 0.0f) { x = -x; sign = -1; }
    if (x > (float)M_PI) { x = 2.0f * (float)M_PI - x; sign = -sign; }

    const float c1 = -1.6666654611e-01f;
    const float c2 =  8.3330251389e-03f;
    const float c3 = -1.9807005469e-04f;
    const float c4 =  2.6018468069e-06f;

    float x2 = x * x;
    return sign * (x + x * x2 * (c1 + x2 * (c2 + x2 * (c3 + x2 * c4))));
}

/* ========================================================================= */
/* Global instance                                                            */
/* ========================================================================= */
static LatticeOscillator osc;

/* ========================================================================= */
/* Reverb processing (simple delay-based)                                     */
/* ========================================================================= */
static float process_reverb(float input)
{
    float output = input;
    for (int i = 0; i < REVERB_LINES; i++) {
        int read_pos = osc.delay_pos[i] - (REVERB_DELAY / (i + 1));
        if (read_pos < 0) read_pos += REVERB_DELAY;

        float delayed = osc.delay_lines[i][read_pos];
        /* Feedback with low-pass (average with previous) */
        osc.delay_lines[i][osc.delay_pos[i]] =
            input + delayed * (0.6f - i * 0.1f);
        output += delayed * (0.25f - i * 0.04f);

        osc.delay_pos[i] = (osc.delay_pos[i] + 1) % REVERB_DELAY;
    }
    return input * (1.0f - osc.reverb_mix) + output * osc.reverb_mix;
}

/* ========================================================================= */
/* ADSR envelope processing (per sample)                                      */
/* ========================================================================= */
static float process_adsr(Voice *v)
{
    float rate;
    switch ((int)v->env_state) {
        case 1: /* Attack */
            rate = v->adsr.attack > 0.0f ? 1.0f / (v->adsr.attack * SAMPLE_RATE) : 1.0f;
            v->envelope += rate;
            if (v->envelope >= 1.0f) {
                v->envelope = 1.0f;
                v->env_state = 2;
            }
            break;
        case 2: /* Decay */
            rate = v->adsr.decay > 0.0f ? 1.0f / (v->adsr.decay * SAMPLE_RATE) : 1.0f;
            v->envelope -= rate;
            if (v->envelope <= v->adsr.sustain) {
                v->envelope = v->adsr.sustain;
                v->env_state = 3;
            }
            break;
        case 3: /* Sustain — hold */
            v->envelope = v->adsr.sustain;
            break;
        case 4: /* Release */
            rate = v->adsr.release > 0.0f ? 1.0f / (v->adsr.release * SAMPLE_RATE) : 1.0f;
            v->envelope -= rate;
            if (v->envelope <= 0.0f) {
                v->envelope = 0.0f;
                v->active = 0;
                v->env_state = 0;
            }
            break;
    }
    return v->envelope;
}

/* ========================================================================= */
/* Update partial configuration from dials                                    */
/* ========================================================================= */
static void update_partials(void)
{
    int count = 1 + (int)(osc.i_vertical * (MAX_PARTIALS - 1));
    if (count > MAX_PARTIALS) count = MAX_PARTIALS;
    if (count < 1) count = 1;
    osc.num_partials = count;

    /* If a tradition is active and blend > 0, use tradition ratios */
    if (osc.tradition_id >= 0 && osc.tradition_id < (int)NUM_TRADITIONS) {
        const Tradition *t = &TRADITIONS[osc.tradition_id];
        int trad_count = t->num_ratios < count ? t->num_ratios : count;

        for (int i = 0; i < count; i++) {
            float lattice_ratio, trad_ratio, lattice_amp;

            /* Lattice ratios */
            int idx = (int)(osc.i_horizontal * (LATTICE_TABLE_SIZE - count));
            if (idx < 0) idx = 0;
            if (idx + i >= (int)LATTICE_TABLE_SIZE) idx = LATTICE_TABLE_SIZE - 1 - i;
            lattice_ratio = LATTICE_TABLE[idx + i][0];
            lattice_amp = LATTICE_TABLE[idx + i][2];

            /* Tradition ratios */
            if (i < trad_count) {
                trad_ratio = t->ratios[i];
            } else {
                trad_ratio = t->ratios[trad_count - 1] * (1.0f + (i - trad_count) * 0.5f);
            }

            /* Blend */
            float blend = osc.tradition_blend;
            osc.partial_ratios[i] = lattice_ratio * (1.0f - blend) + trad_ratio * blend;
            osc.partial_base_amps[i] = lattice_amp;
        }
    } else {
        /* Pure lattice mode */
        for (int i = 0; i < count; i++) {
            int idx = (int)(osc.i_horizontal * (LATTICE_TABLE_SIZE - count));
            if (idx < 0) idx = 0;
            if (idx + i >= (int)LATTICE_TABLE_SIZE) idx = LATTICE_TABLE_SIZE - 1 - i;
            osc.partial_ratios[i] = LATTICE_TABLE[idx + i][0];
            osc.partial_base_amps[i] = LATTICE_TABLE[idx + i][2];
        }
    }

    /* Spectral rolloff */
    osc.rolloff = 0.1f + osc.i_spectral * 2.0f;
    for (int i = 0; i < count; i++) {
        osc.partial_base_amps[i] *= expf(-osc.rolloff * (float)i * 0.3f);
    }

    /* Update active voices */
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
/* Public API                                                                 */
/* ========================================================================= */

void lattice_init(int voices, int partials)
{
    memset(&osc, 0, sizeof(osc));

    for (int i = 0; i < MAX_VOICES; i++) {
        osc.voices[i].active = 0;
        osc.voices[i].frequency = 0.0f;
        osc.voices[i].envelope = 0.0f;
        osc.voices[i].env_state = 0;
        osc.voices[i].adsr = (ADSR){0.005f, 0.1f, 0.7f, 0.3f};
    }

    osc.num_voices = voices > MAX_VOICES ? MAX_VOICES : voices;
    osc.num_partials = partials > MAX_PARTIALS ? MAX_PARTIALS : partials;
    osc.i_vertical = 0.5f;
    osc.i_horizontal = 0.3f;
    osc.i_spectral = 0.5f;
    osc.master_vol = 0.8f;
    osc.tradition_id = -1;
    osc.tradition_blend = 0.0f;
    osc.reverb_mix = 0.2f;
    osc.peak_level = 0.0f;
    osc.recording = 0;
    osc.wav_buffer = 0;
    osc.wav_samples = 0;
    osc.wav_capacity = 0;

    memset(osc.delay_lines, 0, sizeof(osc.delay_lines));
    memset(osc.delay_pos, 0, sizeof(osc.delay_pos));

    update_partials();
}

void lattice_process(float *output, int num_samples)
{
    float peak = 0.0f;

    for (int n = 0; n < num_samples; n++) {
        float sample = 0.0f;

        for (int v = 0; v < osc.num_voices; v++) {
            Voice *voice = &osc.voices[v];
            if (!voice->active) continue;

            float voice_sample = 0.0f;
            for (int p = 0; p < voice->num_partials; p++) {
                float angle = voice->phases[p] * 2.0f * (float)M_PI;
                voice_sample += voice->amps[p] * fast_sin(angle);
                voice->phases[p] += voice->phase_incs[p];
                if (voice->phases[p] >= 1.0f) voice->phases[p] -= 1.0f;
            }

            float env = process_adsr(voice);
            sample += voice_sample * env;
        }

        /* Normalize: divide by active voice count */
        int active = 0;
        for (int v = 0; v < osc.num_voices; v++) if (osc.voices[v].active) active++;
        if (active > 1) sample /= (float)sqrtf((float)active);

        /* Apply master volume */
        sample *= osc.master_vol;

        /* Reverb */
        sample = process_reverb(sample);

        /* Soft clip (tanh approximation) */
        if (sample > 1.0f) sample = 1.0f - 0.5f / (sample + 1.0f);
        if (sample < -1.0f) sample = -1.0f + 0.5f / (-sample + 1.0f);

        output[n] = sample;

        /* Track peak */
        float abs_s = sample < 0 ? -sample : sample;
        if (abs_s > peak) peak = abs_s;

        /* Record to WAV buffer */
        if (osc.recording && osc.wav_buffer &&
            osc.wav_samples < osc.wav_capacity) {
            float clamped = sample < -1.0f ? -1.0f : (sample > 1.0f ? 1.0f : sample);
            osc.wav_buffer[osc.wav_samples++] = (int16_t)(clamped * 32767.0f);
        }
    }

    /* Update peak level with decay */
    osc.peak_level = peak > osc.peak_level ? peak : osc.peak_level * 0.995f;
}

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

void lattice_note_on(float frequency)
{
    for (int v = 0; v < osc.num_voices; v++) {
        if (!osc.voices[v].active) {
            Voice *voice = &osc.voices[v];
            voice->frequency = frequency;
            voice->active = 1;
            voice->envelope = 0.0f;
            voice->env_state = 1;
            voice->num_partials = osc.num_partials;

            /* Apply tradition ADSR if active */
            if (osc.tradition_id >= 0 && osc.tradition_id < (int)NUM_TRADITIONS) {
                voice->adsr = TRADITIONS[osc.tradition_id].adsr;
            }

            float base_inc = frequency / (float)SAMPLE_RATE;
            for (int p = 0; p < osc.num_partials; p++) {
                voice->phases[p] = 0.0f;
                voice->phase_incs[p] = base_inc * osc.partial_ratios[p];
                voice->amps[p] = osc.partial_base_amps[p];
            }
            return;
        }
    }
    /* Voice stealing */
    Voice *voice = &osc.voices[0];
    voice->frequency = frequency;
    voice->active = 1;
    voice->envelope = 0.0f;
    voice->env_state = 1;
    voice->num_partials = osc.num_partials;
    if (osc.tradition_id >= 0 && osc.tradition_id < (int)NUM_TRADITIONS) {
        voice->adsr = TRADITIONS[osc.tradition_id].adsr;
    }
    float base_inc = frequency / (float)SAMPLE_RATE;
    for (int p = 0; p < osc.num_partials; p++) {
        voice->phases[p] = 0.0f;
        voice->phase_incs[p] = base_inc * osc.partial_ratios[p];
        voice->amps[p] = osc.partial_base_amps[p];
    }
}

void lattice_note_off(float frequency)
{
    for (int v = 0; v < osc.num_voices; v++) {
        if (osc.voices[v].active && osc.voices[v].frequency == frequency) {
            osc.voices[v].env_state = 4; /* Release */
            return;
        }
    }
}

float lattice_get_dial(int dial)
{
    switch (dial) {
        case 0: return osc.i_vertical;
        case 1: return osc.i_horizontal;
        case 2: return osc.i_spectral;
    }
    return 0.0f;
}

float lattice_get_consonance(void)
{
    float total = 0.0f;
    int count = 0;
    for (int i = 0; i < osc.num_partials; i++) {
        total += LATTICE_TABLE[i][1];
        count++;
    }
    if (count == 0) return 1.0f;
    return 1.0f / (1.0f + total / (float)count);
}

float lattice_get_pleasantness(void)
{
    /* Neural-ish model: weighted combination of consonance, spectral balance,
       and voice activity. Returns 0.0–1.0. */
    float consonance = lattice_get_consonance();
    float brightness = 1.0f - osc.i_spectral;  /* Less rolloff = brighter */
    float complexity = osc.i_vertical * 0.3f + osc.i_horizontal * 0.2f;

    /* Pleasantness peaks at moderate complexity with high consonance */
    float opt_complexity = 1.0f - fabsf(complexity - 0.35f) * 2.0f;
    if (opt_complexity < 0.0f) opt_complexity = 0.0f;

    return consonance * 0.4f + opt_complexity * 0.3f +
           brightness * 0.15f + (1.0f - osc.reverb_mix) * 0.15f;
}

/* Tradition control */
void lattice_set_tradition(int id)
{
    if (id >= (int)NUM_TRADITIONS) id = -1;
    osc.tradition_id = id;
    if (id >= 0) {
        osc.tradition_blend = 0.8f;
        const Tradition *t = &TRADITIONS[id];
        osc.i_vertical = t->vertical;
        osc.i_horizontal = t->horizontal;
        osc.i_spectral = t->spectral;
        osc.reverb_mix = t->reverb_mix;
    } else {
        osc.tradition_blend = 0.0f;
    }
    update_partials();
}

int lattice_get_tradition(void) { return osc.tradition_id; }

float lattice_get_peak(void) { return osc.peak_level; }

void lattice_set_reverb(float mix)
{
    osc.reverb_mix = mix < 0.0f ? 0.0f : (mix > 1.0f ? 1.0f : mix);
}

void lattice_set_master_vol(float vol)
{
    osc.master_vol = vol < 0.0f ? 0.0f : (vol > 1.0f ? 1.0f : vol);
}

/* WAV recording */
void lattice_start_recording(int max_seconds)
{
    if (osc.wav_buffer) { /* free previous */ }
    osc.wav_capacity = max_seconds * SAMPLE_RATE;
    if (osc.wav_capacity > SAMPLE_RATE * 30) osc.wav_capacity = SAMPLE_RATE * 30;
    osc.wav_samples = 0;
    osc.recording = 1;
}

void lattice_stop_recording(void) { osc.recording = 0; }

int lattice_get_recording_samples(void) { return osc.wav_samples; }

/* Build WAV header into provided buffer (44 bytes). Returns total WAV size. */
int lattice_build_wav(uint8_t *header, int num_samples)
{
    int data_size = num_samples * 2;  /* 16-bit mono */
    int file_size = 36 + data_size;

    /* RIFF header */
    header[0] = 'R'; header[1] = 'I'; header[2] = 'F'; header[3] = 'F';
    header[4] = (file_size) & 0xFF;
    header[5] = (file_size >> 8) & 0xFF;
    header[6] = (file_size >> 16) & 0xFF;
    header[7] = (file_size >> 24) & 0xFF;
    header[8] = 'W'; header[9] = 'A'; header[10] = 'V'; header[11] = 'E';

    /* fmt chunk */
    header[12] = 'f'; header[13] = 'm'; header[14] = 't'; header[15] = ' ';
    header[16] = 16; header[17] = 0; header[18] = 0; header[19] = 0;
    header[20] = 1; header[21] = 0;                     /* PCM */
    header[22] = 1; header[23] = 0;                     /* mono */
    header[24] = (SAMPLE_RATE) & 0xFF;
    header[25] = (SAMPLE_RATE >> 8) & 0xFF;
    header[26] = (SAMPLE_RATE >> 16) & 0xFF;
    header[27] = (SAMPLE_RATE >> 24) & 0xFF;
    int byte_rate = SAMPLE_RATE * 2;
    header[28] = (byte_rate) & 0xFF;
    header[29] = (byte_rate >> 8) & 0xFF;
    header[30] = (byte_rate >> 16) & 0xFF;
    header[31] = (byte_rate >> 24) & 0xFF;
    header[32] = 2; header[33] = 0;                     /* block align */
    header[34] = 16; header[35] = 0;                    /* bits per sample */

    /* data chunk */
    header[36] = 'd'; header[37] = 'a'; header[38] = 't'; header[39] = 'a';
    header[40] = (data_size) & 0xFF;
    header[41] = (data_size >> 8) & 0xFF;
    header[42] = (data_size >> 16) & 0xFF;
    header[43] = (data_size >> 24) & 0xFF;

    return 44 + data_size;
}

/* Get pointer to recorded samples */
int16_t* lattice_get_wav_data(void) { return osc.wav_buffer; }

/* Allocate WAV buffer — call before recording */
void lattice_alloc_wav_buffer(int samples)
{
    osc.wav_buffer = (int16_t*)malloc(samples * sizeof(int16_t));
    osc.wav_capacity = samples;
    osc.wav_samples = 0;
}

void lattice_free_wav_buffer(void)
{
    if (osc.wav_buffer) {
        free(osc.wav_buffer);
        osc.wav_buffer = 0;
    }
    osc.wav_samples = 0;
    osc.wav_capacity = 0;
}

/* Get tradition info for UI */
int lattice_get_num_traditions(void) { return (int)NUM_TRADITIONS; }

/* Fill caller-provided arrays with tradition info */
void lattice_get_tradition_info(int id, float *vert, float *horiz, float *spec,
                                 float *r, float *g, float *b)
{
    if (id < 0 || id >= (int)NUM_TRADITIONS) return;
    const Tradition *t = &TRADITIONS[id];
    *vert = t->vertical;
    *horiz = t->horizontal;
    *spec = t->spectral;

    /* Parse hex color */
    const char *c = t->color;
    if (c[0] == '#') c++;
    unsigned int rgb = 0;
    for (int i = 0; c[i]; i++) {
        rgb *= 16;
        if (c[i] >= '0' && c[i] <= '9') rgb += c[i] - '0';
        else if (c[i] >= 'a' && c[i] <= 'f') rgb += c[i] - 'a' + 10;
        else if (c[i] >= 'A' && c[i] <= 'F') rgb += c[i] - 'A' + 10;
    }
    *r = ((rgb >> 16) & 0xFF) / 255.0f;
    *g = ((rgb >> 8) & 0xFF) / 255.0f;
    *b = (rgb & 0xFF) / 255.0f;
}

/* ========================================================================= */
/* Native-only: main() for testing                                            */
/* ========================================================================= */
#ifdef NATIVE_TEST
#include <stdio.h>
int main(void) {
    lattice_init(4, 16);
    lattice_note_on(440.0f);

    float buf[256];
    for (int i = 0; i < 44100 * 2 / 256; i++) {
        lattice_process(buf, 256);
    }

    printf("Peak level: %.4f\n", lattice_get_peak());
    printf("Consonance: %.4f\n", lattice_get_consonance());
    printf("Pleasantness: %.4f\n", lattice_get_pleasantness());
    printf("Traditions: %d\n", lattice_get_num_traditions());
    printf("OK\n");
    return 0;
}
#endif
