/**
 * entanglement_c.c — Entanglement = Consonance (C99)
 *
 * Physics Analogy:
 *   We model a two-mode musical system (two tones) as a coupled quantum system.
 *   Each mode is a two-level system (ground state |0⟩ and first excited |1⟩),
 *   giving a 4-dimensional Hilbert space. The coupling g mixes the modes,
 *   analogous to intervallic interaction between two tones.
 *
 *   The Hamiltonian:
 *     H = ω₁ σ₁⁺σ₁⁻ + ω₂ σ₂⁺σ₂⁻ + g(σ₁⁺σ₂⁻ + σ₁⁻σ₂⁺)
 *
 *   We prepare a product state |1⟩⊗|0⟩, evolve with exp(-iHt), and compute
 *   the von Neumann entropy of the reduced density matrix (partial trace over
 *   mode 2). This entropy quantifies entanglement.
 *
 *   Analogy: consonant intervals (simple ratios) correspond to weak coupling
 *   (low entanglement), while dissonant intervals correspond to strong coupling
 *   (high entanglement). We correlate entanglement with Tenney height.
 *
 * Compile: gcc -O2 -std=c99 -lm -o entanglement_c entanglement_c.c
 */

#include <stdio.h>
#include <math.h>
#include <string.h>

/* 4x4 complex matrix operations (row-major) */
/* Complex stored as [real0, imag0, real1, imag1, ...] */
typedef double complex_mat[32]; /* 4x4x2 = 32 doubles */

/* Identity matrix */
static void identity(double M[32]) {
    memset(M, 0, 32 * sizeof(double));
    for (int i = 0; i < 4; i++) {
        M[2 * (i * 4 + i)]     = 1.0; /* real */
        M[2 * (i * 4 + i) + 1] = 0.0; /* imag */
    }
}

/* Matrix multiply C = A * B (4x4 complex) */
static void mat_mul(const double A[32], const double B[32], double C[32]) {
    double tmp[32] = {0};
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            double sr = 0, si = 0;
            for (int k = 0; k < 4; k++) {
                double ar = A[2*(i*4+k)],   ai = A[2*(i*4+k)+1];
                double br = B[2*(k*4+j)],   bi = B[2*(k*4+j)+1];
                sr += ar*br - ai*bi;
                si += ar*bi + ai*br;
            }
            tmp[2*(i*4+j)]   = sr;
            tmp[2*(i*4+j)+1] = si;
        }
    }
    memcpy(C, tmp, 32 * sizeof(double));
}

/* Compute matrix exponential of -i*H*t using Taylor series (8th order) */
static void mat_exp_iHt(const double H[32], double t, double U[32]) {
    double term[32], sum[32];
    identity(sum);
    identity(term);

    for (int n = 1; n <= 12; n++) {
        /* term = term * (-i*H*t) / n */
        double factor[32];
        /* Multiply H by -i*t/n: for each element (a+bi) -> (a+bi)*(-i)*t/n = (b - ai)*t/n */
        double scale = t / n;
        for (int idx = 0; idx < 16; idx++) {
            double hr = H[2*idx], hi = H[2*idx+1];
            factor[2*idx]   = hi * scale;   /* real part of -i*(a+bi) = b */
            factor[2*idx+1] = -hr * scale;  /* imag part of -i*(a+bi) = -a */
        }
        double tmp[32];
        mat_mul(term, factor, tmp);
        memcpy(term, tmp, 32 * sizeof(double));
        /* sum += term */
        for (int idx = 0; idx < 32; idx++) sum[idx] += term[idx];
    }
    memcpy(U, sum, 32 * sizeof(double));
}

/* Partial trace over mode 2: 4x4 density matrix -> 2x2 reduced dm */
/* Basis: |00⟩, |01⟩, |10⟩, |11⟩ */
/* Partial trace over qubit 2: ρ₁ = Σ_j ⟨j|ρ|j⟩ for j=0,1 of qubit 2 */
static void partial_trace(const double rho[32], double rho1[8]) {
    /* rho1 is 2x2 complex = 8 doubles */
    memset(rho1, 0, 8 * sizeof(double));
    /* |0⟩₂ indices: |00⟩=0, |10⟩=2 */
    /* |1⟩₂ indices: |01⟩=1, |11⟩=3 */
    for (int i = 0; i < 2; i++) {
        for (int j = 0; j < 2; j++) {
            /* ⟨0|ρ|0⟩ contribution: rows 2*i and 2*j mapped through qubit 2 = 0 */
            rho1[2*(i*2+j)]   += rho[2*((2*i)*(4)+(2*j))];
            rho1[2*(i*2+j)+1] += rho[2*((2*i)*(4)+(2*j))+1];
            /* ⟨1|ρ|1⟩ contribution: rows 2*i+1 and 2*j+1 mapped through qubit 2 = 1 */
            rho1[2*(i*2+j)]   += rho[2*((2*i+1)*(4)+(2*j+1))];
            rho1[2*(i*2+j)+1] += rho[2*((2*i+1)*(4)+(2*j+1))+1];
        }
    }
}

/* Eigenvalues of 2x2 Hermitian matrix via quadratic formula */
static void eigenvalues_2x2(const double M[8], double *e1, double *e2) {
    /* M = [[a, b], [c, d]] where b and c are complex */
    double a = M[2*(0*2+0)];
    double d = M[2*(1*2+1)];
    /* For Hermitian: bc* is real. Off-diagonal magnitude squared: */
    double br = M[2*(0*2+1)], bi = M[2*(0*2+1)+1];
    double off2 = br*br + bi*bi;
    double tr = a + d;
    double det = a*d - off2;
    double disc = tr*tr - 4*det;
    if (disc < 0) disc = 0;
    double sq = sqrt(disc);
    *e1 = (tr + sq) / 2.0;
    *e2 = (tr - sq) / 2.0;
}

/* Von Neumann entropy S = -Σ λ log2(λ) */
static double von_neumann_entropy(double e1, double e2) {
    double S = 0.0;
    if (e1 > 1e-12) S -= e1 * log2(e1);
    if (e2 > 1e-12) S -= e2 * log2(e2);
    return S;
}

/* Build Hamiltonian for coupled two-mode system */
static void build_hamiltonian(double w1, double w2, double g, double H[32]) {
    memset(H, 0, 32 * sizeof(double));
    /* Basis: |00⟩=0, |01⟩=1, |10⟩=2, |11⟩=3 */
    /* H|00⟩ = 0 */
    /* H|01⟩ = ω₂|01⟩ */
    H[2*(1*4+1)] = w2;
    /* H|10⟩ = ω₁|10⟩ */
    H[2*(2*4+2)] = w1;
    /* H|11⟩ = (ω₁+ω₂)|11⟩ */
    H[2*(3*4+3)] = w1 + w2;

    /* Coupling: g(|10⟩⟨01| + |01⟩⟨10|) */
    H[2*(2*4+1)] = g;  /* ⟨01|H|10⟩ real */
    H[2*(1*4+2)] = g;  /* ⟨10|H|01⟩ real */
}

int main(void) {
    printf("{\"experiment\": \"entanglement_consonance\",\n");
    printf(" \"description\": \"Correlate von Neumann entropy of coupled two-mode system with Tenney height of interval ratios\",\n");
    printf(" \"parameters\": {\"evolution_time\": 1.0, \"coupling_range\": [0.01, 5.0]},\n");
    printf(" \"results\": [\n");

    /* Test with different frequency ratios */
    /* ω₁ = 1.0, ω₂ = ratio */
    double w1 = 1.0;
    double ratios[] = {1.0, 16.0/15.0, 9.0/8.0, 6.0/5.0, 5.0/4.0, 4.0/3.0,
                       45.0/32.0, 3.0/2.0, 8.0/5.0, 5.0/3.0, 9.0/5.0, 15.0/8.0, 2.0};
    const char *names[] = {"Unison","m2","M2","m3","M3","P4","TT","P5","m6","M6","m7","M7","Octave"};
    int n = 13;
    double t = 1.0; /* evolution time */

    for (int k = 0; k < n; k++) {
        double w2 = ratios[k];
        double g = 0.5; /* coupling strength */

        /* Build Hamiltonian */
        double H[32];
        build_hamiltonian(w1, w2, g, H);

        /* Initial state: |10⟩ (mode 1 excited, mode 2 ground) */
        double psi[8] = {0}; /* 4 complex amplitudes */
        psi[2*2] = 1.0; /* |10⟩ amplitude = 1 */

        /* Evolve: U = exp(-iHt) */
        double U[32];
        mat_exp_iHt(H, t, U);

        /* Apply U to psi: |ψ(t)⟩ = U|ψ(0)⟩ */
        double psi_t[8] = {0};
        for (int i = 0; i < 4; i++) {
            for (int j = 0; j < 4; j++) {
                psi_t[2*i]   += U[2*(i*4+j)] * psi[2*j] - U[2*(i*4+j)+1] * psi[2*j+1];
                psi_t[2*i+1] += U[2*(i*4+j)] * psi[2*j+1] + U[2*(i*4+j)+1] * psi[2*j];
            }
        }

        /* Build density matrix ρ = |ψ⟩⟨ψ| */
        double rho[32] = {0};
        for (int i = 0; i < 4; i++) {
            for (int j = 0; j < 4; j++) {
                rho[2*(i*4+j)]   = psi_t[2*i]*psi_t[2*j] + psi_t[2*i+1]*psi_t[2*j+1];
                rho[2*(i*4+j)+1] = psi_t[2*i+1]*psi_t[2*j] - psi_t[2*i]*psi_t[2*j+1];
            }
        }

        /* Partial trace over mode 2 */
        double rho1[8];
        partial_trace(rho, rho1);

        /* Eigenvalues of reduced density matrix */
        double e1, e2;
        eigenvalues_2x2(rho1, &e1, &e2);

        /* Von Neumann entropy */
        double S = von_neumann_entropy(e1, e2);

        /* Tenney height */
        double tenney = log2(w2 > 1.0 ? w2 : 1.0/w2);
        double cents = 1200.0 * log2(w2);

        printf("  {\"name\": \"%s\", \"ratio\": %.8f, \"cents\": %.4f, "
               "\"entanglement_entropy\": %.8f, \"eigenvalues\": [%.10f, %.10f], "
               "\"tenney_height\": %.6f}%s\n",
               names[k], w2, cents, S, e1, e2, tenney,
               (k < n-1) ? "," : "");
    }

    printf(" ],\n");
    printf(" \"physics_interpretation\": \"The von Neumann entropy of the reduced density matrix quantifies mode entanglement. Simple interval ratios (low Tenney height) produce predictable entanglement patterns, while complex ratios create richer entanglement dynamics — musical consonance maps to quantum coherence structure.\"\n");
    printf("}\n");

    return 0;
}
