/**
 * spin_statistics.cu — Spin Statistics Consonance
 *
 * Physics background:
 * ───────────────────
 * Fermions obey the Pauli exclusion principle: two identical fermions cannot
 * occupy the same quantum state.  The occupation probability follows the
 * Fermi-Dirac distribution:
 *
 *   n(ε) = 1 / (exp((ε − μ) / kT) + 1)
 *
 * We map this onto psychoacoustics:
 *   • Each pair of harmonics (f_i, f_j) from two tones has a "energy"
 *     separation ε = |f_i − f_j|.
 *   • The "chemical potential" μ is set to the critical bandwidth
 *     (~100 Hz for the mid-range), the window within which the ear
 *     cannot resolve two sinusoids.
 *   • The "thermal energy" kT ≈ 50 Hz models perceptual noise.
 *   • The Fermi-Dirac "roughness" w(ε) = 1 / (exp((|Δf| − μ) / kT) + 1)
 *     is ≈ 1 when |Δf| < μ (clashing harmonics) and ≈ 0 when |Δf| > μ
 *     (resolved harmonics).
 *   • Total roughness = Σ_{i,j} w(|f_i − f_j|) over all harmonic pairs.
 *
 * Lower roughness ⟹ more consonant interval.
 * This parallels how spin-statistics governs occupancy: fermions (roughness)
 * "fill up" available states (critical bandwidth).
 *
 * GPU parallelism:
 *   Each CUDA thread independently computes the roughness for one musical
 *   interval (ratio p/q).  This embarassingly-parallel computation maps
 *   perfectly onto GPU architectures.
 *
 * Build:
 *   nvcc -O2 -o spin_statistics spin_statistics.cu -lm
 */

#include <cstdio>
#include <cmath>
#include <cstdlib>

#ifdef __CUDACC__
#define HOST_DEVICE __host__ __device__
#else
#define HOST_DEVICE
#endif

// ── Psychoacoustic Parameters ─────────────────────────────────────────────
static const double MU    = 100.0;   // Critical bandwidth (Hz), "chemical potential"
static const double KT    = 50.0;    // Perceptual noise floor (Hz), "thermal energy"
static const int    NHARM = 8;       // Number of harmonics per tone
static const double F_REF = 440.0;   // Reference frequency (Hz)

// ── Test intervals (p/q ratios) ───────────────────────────────────────────
// 13 classic just-intonation intervals ordered roughly by consonance
struct Interval {
    int p, q;
    const char* name;
};

static const Interval INTERVALS[13] = {
    { 1,  1, "Unison (1/1)" },
    { 1,  2, "Octave (1/2)" },
    { 2,  3, "Perfect fifth (2/3)" },
    { 1,  3, "Twelfth (1/3)" },
    { 3,  4, "Perfect fourth (3/4)" },
    { 4,  5, "Major third (4/5)" },
    { 5,  6, "Minor third (5/6)" },
    { 3,  5, "Major sixth (3/5)" },
    { 5,  8, "Minor sixth (5/8)" },
    { 8,  9, "Major second (8/9)" },
    { 5,  9, "Minor seventh (5/9)" },
    { 9, 16, "Major seventh (9/16)" },
    {15, 16, "Minor second (15/16)" },
};

static const int NUM_INTERVALS = 13;

/**
 * Compute total Fermi-Dirac roughness for interval with ratio p/q.
 *
 * Harmonics of tone 1: f_ref × n  for n = 1 … NHARM
 * Harmonics of tone 2: f_ref × (p/q) × n  for n = 1 … NHARM
 *
 * For each pair (i,j), compute roughness:
 *   w = 1 / (exp((|f1_i − f2_j| − μ) / kT) + 1)
 */
HOST_DEVICE
double compute_roughness(int p, int q, double f_ref)
{
    double roughness = 0.0;

    // Harmonics of the lower tone (frequency = f_ref)
    for (int i = 1; i <= NHARM; ++i) {
        double f1 = f_ref * i;

        // Harmonics of the upper tone (frequency = f_ref * p / q)
        for (int j = 1; j <= NHARM; ++j) {
            double f2 = f_ref * ((double)p / q) * j;

            double delta_f = fabs(f1 - f2);

            // Fermi-Dirac occupation → roughness
            // w = 1 / (exp((ε − μ) / kT) + 1)
            double arg = (delta_f - MU) / KT;
            // Clamp to avoid overflow
            if (arg > 50.0) {
                // roughness ≈ 0
                continue;
            }
            double w = 1.0 / (exp(arg) + 1.0);
            roughness += w;
        }
    }

    return roughness;
}

// ── GPU kernel: one thread per interval ────────────────────────────────────
#ifdef __CUDACC__
__global__
void roughness_kernel(const int* p_arr, const int* q_arr,
                      double* roughness_arr, int n, double f_ref)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        roughness_arr[idx] = compute_roughness(p_arr[idx], q_arr[idx], f_ref);
    }
}
#endif

// ── CPU fallback ───────────────────────────────────────────────────────────
static void roughness_cpu(const int* p_arr, const int* q_arr,
                          double* roughness_arr, int n, double f_ref)
{
    for (int i = 0; i < n; ++i) {
        roughness_arr[i] = compute_roughness(p_arr[i], q_arr[i], f_ref);
    }
}

// ── Main ───────────────────────────────────────────────────────────────────
int main()
{
    printf("══════════════════════════════════════════════════════════\n");
    printf("  Spin-Statistics Consonance (Fermi-Dirac Roughness)\n");
    printf("  Parameters: μ = %.0f Hz, kT = %.0f Hz, NHARM = %d\n",
           MU, KT, NHARM);
    printf("  Reference:  %.0f Hz\n", F_REF);
    printf("══════════════════════════════════════════════════════════\n\n");

    int h_p[13], h_q[13];
    double h_roughness[13];

    for (int i = 0; i < NUM_INTERVALS; ++i) {
        h_p[i] = INTERVALS[i].p;
        h_q[i] = INTERVALS[i].q;
    }

#ifdef __CUDACC__
    printf("Running on GPU (CUDA) …\n\n");
    int *d_p, *d_q;
    double *d_roughness;
    cudaMalloc(&d_p, NUM_INTERVALS * sizeof(int));
    cudaMalloc(&d_q, NUM_INTERVALS * sizeof(int));
    cudaMalloc(&d_roughness, NUM_INTERVALS * sizeof(double));
    cudaMemcpy(d_p, h_p, NUM_INTERVALS * sizeof(int), cudaMemcpyHostToDevice);
    cudaMemcpy(d_q, h_q, NUM_INTERVALS * sizeof(int), cudaMemcpyHostToDevice);

    int threads = 256;
    int blocks  = (NUM_INTERVALS + threads - 1) / threads;
    roughness_kernel<<<blocks, threads>>>(d_p, d_q, d_roughness,
                                          NUM_INTERVALS, F_REF);
    cudaDeviceSynchronize();
    cudaMemcpy(h_roughness, d_roughness, NUM_INTERVALS * sizeof(double),
               cudaMemcpyDeviceToHost);

    cudaFree(d_p);
    cudaFree(d_q);
    cudaFree(d_roughness);
#else
    printf("Running on CPU (no CUDA) …\n\n");
    roughness_cpu(h_p, h_q, h_roughness, NUM_INTERVALS, F_REF);
#endif

    // Sort by roughness (simple bubble sort — only 13 items)
    int idx[13];
    for (int i = 0; i < NUM_INTERVALS; ++i) idx[i] = i;
    for (int i = 0; i < NUM_INTERVALS - 1; ++i) {
        for (int j = 0; j < NUM_INTERVALS - 1 - i; ++j) {
            if (h_roughness[idx[j]] > h_roughness[idx[j+1]]) {
                int tmp = idx[j]; idx[j] = idx[j+1]; idx[j+1] = tmp;
            }
        }
    }

    printf("  Rank │ %-22s │ Roughness │ Verdict\n", "Interval");
    printf("  ─────┼────────────────────────┼───────────┼───────────\n");
    for (int rank = 0; rank < NUM_INTERVALS; ++rank) {
        int i = idx[rank];
        const char* verdict = (rank < 4)  ? "consonant" :
                              (rank < 9)  ? "moderate"  : "dissonant";
        printf("  %4d │ %-22s │ %9.4f │ %s\n",
               rank + 1, INTERVALS[i].name, h_roughness[i], verdict);
    }

    printf("\n  Physics interpretation:\n");
    printf("  Lower roughness → harmonics \"avoid\" each other (Pauli-like).\n");
    printf("  Higher roughness → harmonics \"collide\" within critical bandwidth.\n");
    printf("  The Fermi-Dirac distribution models the sharp transition at μ.\n");

    return 0;
}
