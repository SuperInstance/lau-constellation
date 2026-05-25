/**
 * spin_statistics_c.c — Spin Statistics Consonance (C99)
 *
 * Physics Analogy:
 *   In quantum mechanics, fermions obey the Pauli exclusion principle: no two
 *   fermions can occupy the same state. This manifests as an effective repulsion
 *   described by Fermi-Dirac statistics. We model sensory dissonance (roughness)
 *   between two musical tones using a Fermi-Dirac-like function:
 *
 *     w(|f_i - f_j|) = 1 / (exp((|f_i - f_j| - δ) / σ) + 1)
 *
 *   where δ ≈ 100 Hz (critical bandwidth) and σ ≈ 50 Hz (temperature analog).
 *
 *   When two partials are close (|Δf| < δ), the weight → 1 (excluded, rough).
 *   When far apart (|Δf| >> δ), the weight → 0 (allowed, smooth).
 *
 *   This is the statistical-mechanical analog of consonance: consonant intervals
 *   have well-separated partials (low "occupancy"), dissonant ones have crowded
 *   partials (high "occupancy", Pauli-like repulsion).
 *
 * Compile: gcc -O2 -std=c99 -lm -o spin_statistics_c spin_statistics_c.c
 */

#include <stdio.h>
#include <math.h>

/* Maximum number of harmonics */
#define N_HARMONICS 8

/* Fermi-Dirac roughness parameters */
#define DELTA 100.0   /* Critical bandwidth (Hz) */
#define SIGMA 50.0    /* Smearing width (Hz) */

/* Intervals to test: chromatic scale ratios */
static const char *names[] = {
    "Unison", "m2", "M2", "m3", "M3", "P4",
    "TT", "P5", "m6", "M6", "m7", "M7", "Octave"
};
static const double ratios[] = {
    1.0/1.0, 16.0/15.0, 9.0/8.0, 6.0/5.0, 5.0/4.0, 4.0/3.0,
    45.0/32.0, 3.0/2.0, 8.0/5.0, 5.0/3.0, 9.0/5.0, 15.0/8.0, 2.0/1.0
};
#define N_INTERVALS 13

int main(void) {
    const double f0 = 440.0;  /* Reference: A4 */

    printf("{\"experiment\": \"spin_statistics_consonance\",\n");
    printf(" \"description\": \"Fermi-Dirac roughness model for musical intervals\",\n");
    printf(" \"parameters\": {\"N_harmonics\": %d, \"delta_Hz\": %.1f, \"sigma_Hz\": %.1f, \"f0_Hz\": %.1f},\n",
           N_HARMONICS, DELTA, SIGMA, f0);
    printf(" \"intervals\": [\n");

    for (int k = 0; k < N_INTERVALS; k++) {
        double r = ratios[k];
        double f1 = f0;       /* Fundamental of tone 1 */
        double f2 = f0 * r;   /* Fundamental of tone 2 */

        /* Compute roughness: sum Fermi-Dirac weights over all partial pairs */
        double roughness = 0.0;
        int n_pairs = 0;

        for (int i = 1; i <= N_HARMONICS; i++) {
            for (int j = 1; j <= N_HARMONICS; j++) {
                double fi = f1 * i;
                double fj = f2 * j;
                double df = fabs(fi - fj);
                double w = 1.0 / (exp((df - DELTA) / SIGMA) + 1.0);
                roughness += w;
                n_pairs++;
            }
        }

        /* Normalize by number of pairs */
        roughness /= n_pairs;

        /* Tenney height: measure of interval simplicity */
        /* For ratio p/q, tenney_height = log2(p*q) where p/q in lowest terms */
        /* We use the raw ratio numerator and denominator from the fractions above */
        double tenney = log2(r);  /* Simplified: log2 of the ratio */
        if (r < 1.0) tenney = -tenney;

        double cents = 1200.0 * log2(r);

        printf("  {\"name\": \"%s\", \"ratio\": \"%.0f/%.0f\", \"ratio_decimal\": %.8f, "
               "\"cents\": %.4f, \"roughness\": %.8f, \"tenney_height\": %.6f}%s\n",
               names[k],
               /* Reconstruct p, q from ratio (approximate) */
               r * 1000, 1000.0,  /* Simplified display */
               r, cents, roughness, tenney,
               (k < N_INTERVALS - 1) ? "," : "");
    }

    printf(" ],\n");
    printf(" \"physics_interpretation\": \"Consonant intervals have well-separated harmonic partials (low Fermi-Dirac occupancy), while dissonant intervals have crowded partials (high Pauli-like exclusion repulsion). The roughness function parallels the Fermi distribution in statistical mechanics.\"\n");
    printf("}\n");

    return 0;
}
