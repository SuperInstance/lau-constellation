/* CUDA Synthesizer - GPU-parallel note synthesis */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#define SR 44100
#define PI 3.14159265358979323846

__global__ void synth_note(double* output, double freq, double amp, int n_samples, int s0, int total) {
    int j = blockIdx.x * blockDim.x + threadIdx.x;
    if (j >= n_samples) return;
    
    double t = (double)j / (double)SR;
    
    /* ADSR envelope */
    int a_s = (int)(0.01 * SR);
    int d_s = (int)(0.05 * SR);
    int r_s = (int)(0.1 * SR);
    double env = 1.0;
    double sustain = 0.7;
    
    if (j < a_s) env = (double)j / a_s;
    else if (j < a_s + d_s) env = 1.0 - (1.0 - sustain) * (j - a_s) / (double)d_s;
    else if (j >= n_samples - r_s) env = sustain * (n_samples - 1 - j) / (double)r_s;
    else env = sustain;
    
    double val = amp * sin(2.0 * PI * freq * t) * env;
    
    int idx = s0 + j;
    if (idx < total) {
        /* Atomic add for mixing */
        unsigned long long* addr = (unsigned long long*)&output[idx];
        unsigned long long old = *addr, assumed;
        do {
            assumed = old;
            double oldval = __longlong_as_double(assumed);
            double newval = oldval + val;
            if (newval > 1.0) newval = 1.0;
            if (newval < -1.0) newval = -1.0;
            old = atomicCAS(addr, assumed, __double_as_longlong(newval));
        } while (assumed != old);
    }
}

int main() {
    int n = SR * 2;  /* 2 seconds for single_440 */
    double* d_output;
    cudaMalloc(&d_output, n * sizeof(double));
    cudaMemset(d_output, 0, n * sizeof(double));
    
    int threads = 256;
    int blocks = (n + threads - 1) / threads;
    
    double freq = 440.0;
    double amp = 100.0 / 127.0;
    
    synth_note<<<blocks, threads>>>(d_output, freq, amp, n, 0, n);
    cudaDeviceSynchronize();
    
    double* output = (double*)malloc(n * sizeof(double));
    cudaMemcpy(output, d_output, n * sizeof(double), cudaMemcpyDeviceToHost);
    
    /* Clip */
    for (int i = 0; i < n; i++) {
        if (output[i] > 1.0) output[i] = 1.0;
        if (output[i] < -1.0) output[i] = -1.0;
    }
    
    /* Write raw */
    FILE* f = fopen("output/cuda/single_440.f64", "wb");
    if (f) {
        fwrite(output, sizeof(double), n, f);
        fclose(f);
    }
    
    free(output);
    cudaFree(d_output);
    printf("CUDA synthesis complete\n");
    return 0;
}
