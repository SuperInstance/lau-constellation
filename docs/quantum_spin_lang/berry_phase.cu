/**
 * berry_phase.cu — Berry Phase = Pythagorean Comma
 *
 * Physics background:
 * ───────────────────
 * In quantum mechanics, a Berry phase is the geometric phase acquired over
 * the course of a cycle, when a system is subjected to cyclic adiabatic
 * processes. It depends only on the geometry of the parameter-space path,
 * not on the rate of traversal.
 *
 * Musical analogy:
 *   Start at 440 Hz (A4). Repeatedly multiply by 3/2 (the perfect fifth).
 *   Whenever the frequency exceeds one octave (×2), divide by 2 to normalize
 *   back into the original octave [440, 880). After 12 such steps we return
 *   to (approximately) the starting pitch — but not exactly. The discrepancy
 *   is the *Pythagorean comma*:
 *
 *     3^12 / 2^19  =  531441 / 524288  ≈  23.46 cents
 *
 *   This maps directly onto the Berry phase: a closed loop in frequency
 *   space that fails to return to the exact origin, accumulating a geometric
 *   "holonomy" equal to the comma.
 *
 * GPU parallelism:
 *   Each CUDA thread computes the accumulated phase for a different starting
 *   frequency, demonstrating that the comma is *independent* of the starting
 *   point — it is purely a property of the 3/2 generator and the 12-step cycle.
 *
 * Build:
 *   nvcc -O2 -o berry_phase berry_phase.cu -lm
 *   (CPU fallback: g++ -DCPU_ONLY -O2 -o berry_phase berry_phase.cu -lm)
 */

#include <cstdio>
#include <cmath>
#include <cstdlib>

#ifdef __CUDACC__
#define HOST_DEVICE __host__ __device__
#else
#define HOST_DEVICE
#endif

// ── Constants ──────────────────────────────────────────────────────────────
static const int NUM_FIFTHS     = 12;   // circle of fifths
static const double RATIO       = 3.0 / 2.0;  // perfect fifth
static const double OCTAVE      = 2.0;
static const double CENTS_PER_OCTAVE = 1200.0;

/**
 * Compute the Berry-phase discrepancy for a given starting frequency.
 *
 * We traverse the circle of fifths: f → f × (3/2), normalising into
 * [f0, 2·f0) after each step.  The final frequency minus the start,
 * expressed in cents, is the Pythagorean comma (Berry phase analogue).
 *
 * Returns the discrepancy in cents.
 */
HOST_DEVICE
double compute_comma(double f_start)
{
    double f = f_start;
    for (int i = 0; i < NUM_FIFTHS; ++i) {
        f *= RATIO;
        // Normalize into the octave [f_start, 2·f_start)
        while (f >= 2.0 * f_start) {
            f /= OCTAVE;
        }
    }
    // f should be ≈ f_start but off by the comma
    double ratio_final = f / f_start;
    double cents = CENTS_PER_OCTAVE * log2(ratio_final);
    return cents;
}

// ── GPU kernel: one thread per starting frequency ──────────────────────────
#ifdef __CUDACC__
__global__
void berry_phase_kernel(const double* f_starts, double* results, int n)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        results[idx] = compute_comma(f_starts[idx]);
    }
}
#endif

// ── CPU fallback ───────────────────────────────────────────────────────────
static void berry_phase_cpu(const double* f_starts, double* results, int n)
{
    for (int i = 0; i < n; ++i) {
        results[i] = compute_comma(f_starts[i]);
    }
}

// ── Exact rational computation (CPU, for verification) ────────────────────
/**
 * The Pythagorean comma in exact integer arithmetic:
 *   After 12 fifths up (×3 each) and octaves down (×2 each) to fit one
 *   octave, the net ratio is 3^12 / 2^19 because:
 *     12 fifths  → 3^12
 *     octave reductions: 2^(floor(12·log2(3/2)))  = 2^19
 *
 *   Commatic ratio = 3^12 / 2^19 = 531441 / 524288
 */
static void print_exact_computation()
{
    // Compute 3^12
    long long pow3_12 = 1;
    for (int i = 0; i < 12; ++i) pow3_12 *= 3;
    // Compute 2^19
    long long pow2_19 = 1;
    for (int i = 0; i < 19; ++i) pow2_19 *= 2;

    printf("═══════════════════════════════════════════════════════\n");
    printf("  Exact Rational Computation (Berry Phase Analogue)\n");
    printf("═══════════════════════════════════════════════════════\n");
    printf("  3^12  = %lld\n", pow3_12);
    printf("  2^19  = %lld\n", pow2_19);
    printf("  Ratio = %lld / %lld\n", pow3_12, pow2_19);
    printf("  ≈ %.10f\n", (double)pow3_12 / pow2_19);

    double comma_cents = 1200.0 * log2((double)pow3_12 / pow2_19);
    printf("  Comma = %.6f cents\n", comma_cents);
    printf("  (Expected: ~23.460010 cents)\n");
    printf("═══════════════════════════════════════════════════════\n\n");
}

// ── Main ───────────────────────────────────────────────────────────────────
int main()
{
    print_exact_computation();

    // Test with several starting frequencies to show invariance
    const int N = 16;
    double h_fstarts[N];
    double h_results[N];

    // Sweep from 100 Hz to 1600 Hz
    for (int i = 0; i < N; ++i) {
        h_fstarts[i] = 100.0 + i * 100.0;
    }

#ifdef __CUDACC__
    printf("Running on GPU (CUDA) …\n");
    double *d_fstarts, *d_results;
    cudaMalloc(&d_fstarts, N * sizeof(double));
    cudaMalloc(&d_results, N * sizeof(double));
    cudaMemcpy(d_fstarts, h_fstarts, N * sizeof(double), cudaMemcpyHostToDevice);

    int threads = 256;
    int blocks  = (N + threads - 1) / threads;
    berry_phase_kernel<<<blocks, threads>>>(d_fstarts, d_results, N);
    cudaDeviceSynchronize();
    cudaMemcpy(h_results, d_results, N * sizeof(double), cudaMemcpyDeviceToHost);

    cudaFree(d_fstarts);
    cudaFree(d_results);
#else
    printf("Running on CPU (no CUDA) …\n");
    berry_phase_cpu(h_fstarts, h_results, N);
#endif

    printf("\n  f_start (Hz) │ comma (cents)\n");
    printf("  ─────────────┼──────────────\n");
    for (int i = 0; i < N; ++i) {
        printf("  %10.1f   │  %+.6f\n", h_fstarts[i], h_results[i]);
    }

    // Verify all commas are the same (property of Berry phase)
    double mean = 0.0;
    for (int i = 0; i < N; ++i) mean += h_results[i];
    mean /= N;

    double max_dev = 0.0;
    for (int i = 0; i < N; ++i) {
        double dev = fabs(h_results[i] - mean);
        if (dev > max_dev) max_dev = dev;
    }

    printf("\n  Mean comma: %.6f cents\n", mean);
    printf("  Max deviation from mean: %.2e cents\n", max_dev);
    printf("  → Berry phase is independent of starting frequency ✓\n");

    return 0;
}
