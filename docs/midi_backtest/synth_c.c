/* C99 Synthesizer - reads corpus.json properly */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

#define SR 44100
#define MAX_NOTES 256
#define MAX_SAMPLES (SR * 30)

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double freq, dur, start;
    int vel;
} Note;

typedef struct {
    char name[128];
    int count;
    Note notes[MAX_NOTES];
} TestSeq;

static char* read_file(const char* path) {
    FILE* f = fopen(path, "rb");
    if (!f) return NULL;
    fseek(f, 0, SEEK_END);
    long sz = ftell(f);
    fseek(f, 0, SEEK_SET);
    char* buf = malloc(sz + 1);
    fread(buf, 1, sz, f);
    buf[sz] = 0;
    fclose(f);
    return buf;
}

/* Find next non-whitespace */
static const char* skip_ws(const char* p) {
    while (*p == ' ' || *p == '\n' || *p == '\r' || *p == '\t') p++;
    return p;
}

/* Parse the corpus JSON using a simple recursive descent approach */
int parse_corpus(const char* json, TestSeq* tests, int max_tests) {
    int ntests = 0;
    const char* p = json;
    
    /* Skip to opening { */
    p = strchr(p, '{');
    if (!p) return 0;
    p++;
    
    while (*p && ntests < max_tests) {
        p = skip_ws(p);
        if (*p == '}' || *p == 0) break;
        
        /* Expect "key" : [ ... ] */
        if (*p != '"') { p++; continue; }
        p++;
        const char* q = strchr(p, '"');
        if (!q) break;
        int nlen = (int)(q - p);
        if (nlen >= 128) nlen = 127;
        memcpy(tests[ntests].name, p, nlen);
        tests[ntests].name[nlen] = 0;
        tests[ntests].count = 0;
        p = q + 1;
        
        /* Find : */
        p = strchr(p, ':');
        if (!p) break;
        p++;
        p = skip_ws(p);
        
        /* Now p should point to [ which starts the array of note-tuples */
        if (*p != '[') { p++; continue; }
        p++;
        
        /* Parse note tuples: [freq, dur, vel, start] */
        while (*p) {
            p = skip_ws(p);
            if (*p == ']') { p++; break; }
            if (*p == ',') { p++; continue; }
            
            if (*p == '[') {
                p++;
                double vals[4];
                int vi = 0;
                for (int i = 0; i < 4; i++) {
                    p = skip_ws(p);
                    if (*p == ',' || *p == ']') break;
                    vals[vi++] = strtod(p, (char**)&p);
                    p = skip_ws(p);
                    if (*p == ',') p++;
                }
                /* Skip to closing ] */
                q = strchr(p, ']');
                if (q) p = q + 1;
                
                if (vi == 4 && tests[ntests].count < MAX_NOTES) {
                    Note* note = &tests[ntests].notes[tests[ntests].count++];
                    note->freq = vals[0];
                    note->dur = vals[1];
                    note->vel = (int)vals[2];
                    note->start = vals[3];
                }
            } else {
                p++;
            }
        }
        
        ntests++;
        /* Skip comma between key-value pairs */
        p = skip_ws(p);
        if (*p == ',') p++;
    }
    return ntests;
}

void apply_envelope(double* buf, int n) {
    int a_s = (int)(0.01 * SR);
    int d_s = (int)(0.05 * SR);
    int r_s = (int)(0.1 * SR);
    double sustain = 0.7;
    
    if (a_s > n) a_s = n;
    if (d_s > n - a_s) d_s = n - a_s;
    if (r_s > n - a_s - d_s) r_s = n - a_s - d_s;
    
    for (int i = 0; i < a_s; i++)
        buf[i] *= (double)i / (double)a_s;
    for (int i = 0; i < d_s; i++)
        buf[a_s+i] *= 1.0 - (1.0 - sustain) * i / (double)d_s;
    for (int i = a_s + d_s; i < n - r_s; i++)
        buf[i] *= sustain;
    for (int i = 0; i < r_s; i++)
        buf[n-1-i] *= (double)i / (double)r_s;
}

void synth_test(const TestSeq* test, const char* outdir) {
    double max_end = 0;
    for (int i = 0; i < test->count; i++) {
        double e = test->notes[i].start + test->notes[i].dur;
        if (e > max_end) max_end = e;
    }
    int total = (int)(max_end * SR) + SR;
    if (total > MAX_SAMPLES) total = MAX_SAMPLES;
    
    double* mix = calloc(total, sizeof(double));
    double* buf = malloc(total * sizeof(double));
    
    for (int i = 0; i < test->count; i++) {
        const Note* note = &test->notes[i];
        int n = (int)(note->dur * SR);
        int s0 = (int)(note->start * SR);
        double amp = note->vel / 127.0;
        
        if (s0 >= total) continue;
        if (s0 + n > total) n = total - s0;
        
        for (int j = 0; j < n; j++) {
            double t = (double)j / (double)SR;
            buf[j] = amp * sin(2.0 * M_PI * note->freq * t);
        }
        apply_envelope(buf, n);
        
        for (int j = 0; j < n && (s0+j) < total; j++) {
            mix[s0+j] += buf[j];
        }
    }
    
    for (int i = 0; i < total; i++) {
        if (mix[i] > 1.0) mix[i] = 1.0;
        if (mix[i] < -1.0) mix[i] = -1.0;
    }
    
    char path[512];
    snprintf(path, sizeof(path), "%s/%s.f64", outdir, test->name);
    FILE* f = fopen(path, "wb");
    if (f) {
        fwrite(mix, sizeof(double), total, f);
        fclose(f);
    }
    
    free(mix);
    free(buf);
}

int main(int argc, char** argv) {
    const char* outdir = argc > 1 ? argv[1] : "output/c_O2";
    
    char* json = read_file("corpus.json");
    if (!json) { fprintf(stderr, "Cannot read corpus.json\n"); return 1; }
    
    TestSeq tests[32];
    int ntests = parse_corpus(json, tests, 32);
    free(json);
    
    printf("Parsed %d test sequences\n", ntests);
    
    clock_t t0 = clock();
    for (int i = 0; i < ntests; i++) {
        synth_test(&tests[i], outdir);
        printf("  Synthesized %s (%d notes)\n", tests[i].name, tests[i].count);
    }
    clock_t t1 = clock();
    double elapsed = 1000.0 * (t1 - t0) / CLOCKS_PER_SEC;
    printf("C synthesis complete in %.1f ms\n", elapsed);
    
    return 0;
}
