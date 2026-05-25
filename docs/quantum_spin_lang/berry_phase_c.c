/**
 * berry_phase_c.c — Berry Phase = Pythagorean Comma (C99)
 *
 * Physics Analogy:
 *   In quantum mechanics, a Berry phase arises when a system is adiabatically
 *   transported around a closed loop in parameter space, acquiring a geometric
 *   phase proportional to the curvature enclosed. In music theory, the circle
 *   of fifths (multiplying by 3/2 twelve times) fails to close exactly:
 *
 *     (3/2)^12 = 3^12 / 2^12 = 531441 / 4096
 *
 *   Normalizing to [440, 880] by dividing by appropriate powers of 2:
 *     3^12 / 2^19 = 531441 / 524288 ≈ 1.01364
 *
 *   This ratio IS the Pythagorean comma (~23.46 cents). The analogy:
 *   - 12 fifths map to 7 octaves in "flat" space, but the holonomy (Berry phase)
 *     is the excess angle — the Pythagorean comma.
 *   - The Berry connection in this context is the logarithmic frequency map,
 *     and the curvature is the discrepancy between 12*log2(3/2) and 7.
 *
 * Compile: gcc -O2 -std=c99 -lm -o berry_phase_c berry_phase_c.c
 */

#include <stdio.h>
#include <math.h>

int main(void) {
    /* Starting frequency: A4 = 440 Hz */
    double f = 440.0;
    const double f_start = 440.0;
    const double f_end   = 880.0;  /* one octave above */
    const double ratio   = 3.0 / 2.0;

    printf("{\"experiment\": \"berry_phase_pythagorean_comma\",\n");
    printf(" \"description\": \"Circle of fifths holonomy = Pythagorean comma\",\n");
    printf(" \"steps\": [\n");

    for (int i = 0; i < 12; i++) {
        f *= ratio;
        /* Normalize to [440, 880) by dividing by 2 */
        while (f >= f_end) f /= 2.0;

        /* Compute cents above 440 Hz */
        double cents = 1200.0 * log2(f / f_start);

        /* The interval ratio relative to starting pitch */
        double interval = f / f_start;

        printf("  {\"step\": %2d, \"frequency\": %.6f, \"interval_ratio\": %.10f, \"cents\": %.4f}%s\n",
               i + 1, f, interval, cents,
               (i < 11) ? "," : "");
    }

    printf(" ],\n");

    /* Final analysis */
    double final_ratio = f / f_start;
    double comma_cents = 1200.0 * log2(final_ratio);

    /* Exact Pythagorean comma = 531441/524288 */
    double exact_comma = 531441.0 / 524288.0;
    double exact_cents = 1200.0 * log2(exact_comma);

    printf(" \"final_ratio\": %.15f,\n", final_ratio);
    printf(" \"pythagorean_comma_exact\": \"531441/524288\",\n");
    printf(" \"pythagorean_comma_decimal\": %.15f,\n", exact_comma);
    printf(" \"comma_cents\": %.6f,\n", comma_cents);
    printf(" \"exact_comma_cents\": %.6f,\n", exact_cents);
    printf(" \"error_cents\": %.10f,\n", fabs(comma_cents - exact_cents));
    printf(" \"physics_interpretation\": \"The holonomy of the circle-of-fifths loop in log-frequency space equals the Pythagorean comma, analogous to a Berry phase acquired over a closed path.\"\n");
    printf("}\n");

    return 0;
}
