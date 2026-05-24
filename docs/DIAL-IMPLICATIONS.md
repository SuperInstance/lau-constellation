# DIAL-IMPLICATIONS.md
## From Conservation Laws to Parameter Space: A Critical Reframing

**Thesis:** Musical tension is not conserved. It is *tuned*. Every tradition sets a specific combination of dials. The "law" we thought we found was merely a projection artifact — most cultures cluster in a plane because they evolved under similar constraints (human hearing range, physical instrument limits, social dance requirements). The moment we treat tension parameters as independent dials, the parameter space opens up, and we can navigate it deliberately.

---

## 1. The Reframing: From "We Found a Law" to "We Mapped a Parameter Space"

### What the Original Paper Claimed

The *Conservation of Musical Tension* hypothesis stated:

> $I_{\text{total}} = I_{\text{vert}} + I_{\text{horiz}} \approx \text{const}$

Where:
- $I_{\text{vert}}$ = vertical information (pitch, harmony, timbre, tuning)
- $I_{\text{horiz}}$ = horizontal information (rhythm, meter, temporal structure)

The cross-cultural validation (see `CROSS-CULTURAL-VALIDATION.md`) found the law holds *qualitatively* for Hindustani, gamelan, gagaku, and makam, but **breaks** for West African drumming and the narrow formulation. We patched the hypothesis by saying "the channel set is culture-dependent."

### The Reframes

**The stronger claim is false, but the weaker claim is boring.** If $I_{\text{total}}$ isn't actually constant, then "conservation" is the wrong word. What we actually discovered is a **parameter space** with three independent axes:

| Axis | Symbol | Range | What it controls |
|------|--------|-------|----------------|
| Vertical density | $I_{\text{vert}}$ | [0.0, 4.0] | Pitch granularity, tuning non-uniformity, harmonic complexity, microtonal inflection |
| Horizontal density | $I_{\text{horiz}}$ | [0.0, 4.0] | Rhythmic complexity, syncopation, polyrhythm, metric displacement |
| Spectral density | $I_{\text{spectral}}$ | [0.0, 4.0] | Timbre complexity, orchestration density, spectral centroid motion, formant structure |

**Key insight:** These are not linked by a conservation equation. They are **dials** that composers and traditions set to taste. The apparent "conservation" in Western classical music (high harmony → low rhythmic complexity relative to jazz) is a *local optimization*, not a universal law. It's like saying "car speed plus car weight is constant" because you've only looked at sedans. Add motorcycles and trucks to the dataset and the "law" evaporates.

### Why This Matters Scientifically

1. **Falsifiability:** A dial model makes clear predictions. If we find a tradition with $I_{\text{vert}} = 3.5$, $I_{\text{horiz}} = 3.5$, $I_{\text{spectral}} = 3.5$, the conservation model dies. The dial model says "that's just a point in parameter space — let's see if it's stable."

2. **Generativity:** A law describes what *is*. A parameter space describes what *could be*. The latter is the domain of engineering and art.

3. **Embeddability:** Dials map directly to control interfaces (sliders, knobs, CV inputs). Conservation equations do not.

### The New Formalism

Replace $I_{\text{vert}} + I_{\text{horiz}} \approx \text{const}$ with:

$$\vec{I} = (I_{\text{vert}}, I_{\text{horiz}}, I_{\text{spectral}}) \in [0,4]^3$$

A "musical style" is a probability distribution $P(\vec{I})$ over this cube, shaped by cultural selection pressures. A "composition" is a trajectory $\vec{I}(t)$ through the space. A "tradition" is an attractor basin — a region the style returns to after perturbation.

---

## 2. The Killer App: Dial-Based AI Music Generation

### Concept

A real-time music generator where the user sets three dials — VERT, HORIZ, SPECTRAL — and the AI navigates the parameter space to produce music. No genre labels. No training data bias. Just physics and information theory.

### UI Mockup

```
┌─────────────────────────────────────────┐
│  DIAL ENGINE v0.1   [▶] [⏸] [⏹]       │
├─────────────────────────────────────────┤
│                                         │
│  VERTICAL     [====|========]  2.4      │
│  HORIZONTAL   [========|====]  2.7      │
│  SPECTRAL     [====|========]  1.8      │
│                                         │
│  Presets:                               │
│  [Hindustani] [Gamelan] [Jazz]          │
│  [Gagaku]   [Makam]   [Custom]          │
│                                         │
│  Drift: [Off] [Brownian] [Lorenz]       │
│  Lock:  [None] [Vert+Horiz] [All]       │
│                                         │
└─────────────────────────────────────────┘
```

### How It Works Internally

**Layer 1: Dial → Parameter Mapping**

Each dial position maps to concrete synthesis parameters via a lookup table derived from the cross-cultural analysis:

| Dial Position | VERT Mapping | HORIZ Mapping | SPECTRAL Mapping |
|---------------|-------------|---------------|------------------|
| 0.0 | Pure sine, no pitch change | Single static pulse | Single oscillator, no filter |
| 1.0 | 12-tone ET, triadic harmony | 4/4 meter, on-beat | Subtractive synthesis, 2-formant |
| 2.0 | 22-tone just intonation, meend | 7-beat cycle, syncopation | FM + granular, 4-formant |
| 3.0 | 53-tone Turkish, complex makam | 12-beat polyrhythm, cross-rhythm | Physical modeling + spectral freeze |
| 4.0 | Continuous pitch, no stable tuning | Free time, metric ambiguity | Full orchestra simulation, spectral morphing |

**Layer 2: Constraint Satisfaction**

The generator does not freely interpolate. It uses the **constraint-mux** architecture (§4) to ensure the output is physically playable and culturally coherent:

```python
from dial_engine import DialState, StyleLattice

dials = DialState(vert=2.4, horiz=2.7, spectral=1.8)

# Snap to nearest valid point on the style lattice
# (prevents musically absurd combinations like
#  continuous pitch + single static pulse + full orchestra)
snapped = StyleLattice.snap(dials, radius=0.5)

# Generate using snapped position
generator = ConstraintComposer(snapped)
audio = generator.render(duration_seconds=300, drift_mode="brownian")
```

The `StyleLattice` is a precomputed set of "stable points" — known musical styles as attractors. The snap operation ensures the generator doesn't land in an unstable region (e.g., high vertical + high horizontal + low spectral = "naked complexity" that sounds like a mess).

**Layer 3: Real-Time Adaptation**

The dials don't have to be static. They can follow:
- **Brownian drift:** Small random walks, keeping the music evolving
- **Lorenz attractor:** Chaotic but bounded trajectories through the space
- **External CV:** Physical control voltage from modular synthesizers
- **Sensor input:** Biofeedback, accelerometer, room microphone (§4)

### Why This Is Better Than Genre-Based Generation

| Approach | Problem | Dial Approach |
|----------|---------|---------------|
| Genre labels ("jazz", "classical") | Cultural, arbitrary, politically loaded | Physical parameters, culturally neutral |
| Training data interpolation | Average of dataset = boring mush | Lattice snap = distinct, navigable points |
| Prompt-based ("like Coltrane") | Vague, requires model to "understand" style | Exact numerical coordinates |
| Style transfer | Requires source audio, copyright issues | Generates from first principles |

### Concrete Example: Navigating from Hindustani to Gamelan

Start at `Hindustani ≈ (2.8, 1.5, 2.0)`:
- VERT: 22 śruti, meend, tambūra drone
- HORIZ: 7-16 beat tāla, sparse syncopation
- SPECTRAL: Sitar/tambūra/sarangi timbres

End at `Gamelan ≈ (3.2, 1.2, 2.4)`:
- VERT: Sléndro/Pélog, ombak beating, non-standardized tuning
- HORIZ: Colotomic structure, interlocking
- SPECTRAL: Bronze metallophones, gamelan ensemble

The interpolation path goes through:
1. `t=0.0`: Pure Hindustani — drone, slow rāga development
2. `t=0.3`: Tuning starts to drift toward 5-note pentatonic, metallophone attack transients appear
3. `t=0.5`: Hybrid zone — sitar plays colotomic patterns, gamelan instruments use just intonation
4. `t=0.7`: Gamelan dominant — interlocking patterns, but with Hindustani microtonal inflection
5. `t=1.0`: Pure Gamelan — bronze, ombak, colotomy

This is not "Hindustani-flavored gamelan." It is a **continuous morph through parameter space** that passes through genuinely unexplored territory at `t=0.5`.

---

## 3. Unexplored Dial Positions: Predictions for New Musical Styles

The parameter space $[0,4]^3$ contains $5^3 = 125$ discrete lattice points (at 1.0 increments). We have empirical data for maybe 15–20. The rest are **unexplored territory** — musical styles that may or may not be culturally viable, but are physically possible.

### Prediction 1: Crystalline Chaos `(3.5, 3.5, 3.5)` — "The Hyper-Tradition"

**Dial settings:** All three axes near maximum.

**What it sounds like:** A Javanese gamelan ensemble playing West African polyrhythms in 53-tone Turkish makam, orchestrated like Ligeti's *Atmosphères*, with every instrument microtonally detuned by a unique amount.

**Why it might work:** The high spectral density provides "glue" — timbral fusion prevents the vertical and horizontal complexity from becoming noise. The ear follows timbral families rather than pitch or rhythm alone.

**Why it might fail:** Information overload. Human working memory can track ~3–4 independent streams. At 3.5 on all axes, there may be 10+ simultaneous streams. The result could be white noise.

**Test:** Run the dial engine at (3.5, 3.5, 3.5) with the "lock" feature set to "gradual exposure" — start at (1,1,1) and ramp up over 10 minutes. If listeners report "it suddenly clicked at minute 7," the style is learnable.

### Prediction 2: Timbre Minimalism `(0.3, 0.2, 3.8)` — "The Radique Point"

**Dial settings:** Near-zero vertical and horizontal, maximum spectral.

**What it sounds like:** Éliane Radigue's *Adnos III* — pure timbre evolution with almost no pitch or rhythm. But pushed further: a single complex waveform that morphs over 30 minutes, with internal formant structures that imply pitch without stating it, and micro-rhythmic pulsations below the threshold of meter.

**Why it works:** Radigue already proved this point exists. The dial model predicts that increasing spectral density while holding other axes near zero produces a *line* of viable styles, not just a point.

**Extension:** Add just enough verticality (0.3) to imply a shadow pitch center, like a barely-audible difference tone. The listener's brain "hallucinates" harmony where none exists.

### Prediction 3: Frozen Just Intonation `(3.5, 0.1, 0.2)` — "The Lamonte Singularity"

**Dial settings:** Maximum vertical, minimum horizontal and spectral.

**What it sounds like:** La Monte Young's *The Well-Tuned Piano* — sustained, unmoving just intonation chords with no rhythmic event whatsoever. But with higher vertical density: 53-tone or 72-tone just intonation, held for hours.

**Why it works:** Young proved this point exists too. The dial model predicts that *increasing* vertical density at fixed low horizontal/spectral does not change the qualitative experience — it just adds more "colors" to the drone. The listener enters a trance state where pitch discrimination becomes irrelevant.

**Danger:** Below $I_{\text{horiz}} = 0.1$, the music ceases to be "music" in the Western sense and becomes a psychoacoustic experiment. The dial model says this is fine — it's just a different region of the space.

### Prediction 4: Rhythmic Pure State `(0.2, 3.8, 0.3)` — "The Reich Limit"

**Dial settings:** Minimum vertical, maximum horizontal, minimum spectral.

**What it sounds like:** Steve Reich's *Drumming* — pure rhythmic process, no pitch change, minimal timbre. But pushed to African polyrhythmic density with metric modulation and phase shifting, on a single unpitched drum.

**Why it works:** Reich proved this point. West African drumming lives nearby. The dial model predicts that adding *slight* spectral complexity (0.3 instead of 0.0) — e.g., two drums with different head tensions — creates a "beating" effect analogous to gamelan ombak, but purely rhythmic.

### Prediction 5: The Negative Quadrant — What If Dials Go Below Zero?

The current model assumes $[0,4]$. But what if we allow *negative* information? This sounds absurd, but consider:

- **Negative verticality (-1.0):** Anti-harmony — frequencies chosen to maximize dissonance and perceptual discomfort. Not "atonality" (which is zero verticality) but *active avoidance* of consonance.
- **Negative horizontality (-1.0):** Anti-rhythm — events placed to destroy any emergent pulse. Not free time (zero) but *structured unpredictability* that actively suppresses entrainment.
- **Negative spectrality (-1.0):** Anti-timbre — pure cancellation. Two tones 180° out of phase, producing silence. The "music" is the *absence* of sound in a specific spectral band.

**Why this matters:** The negative quadrant is the domain of **noise music, power electronics, and certain free improvisation**. It is not "bad music" — it is music that occupies a different region of the space, one that most traditions avoid because it produces anxiety rather than pleasure.

The dial model does not judge. It just says: "Here is a point at (-1, 2, 1). It will sound like Merzbow with a pulse."

### Prediction 6: The Diagonal Line — Where All Traditions Live

Plot the 15–20 known traditions in 3D space. We predict they will cluster near the diagonal:

$$I_{\text{vert}} + I_{\text{horiz}} + I_{\text{spectral}} \approx 5.5 \pm 1.5$$

This is not a conservation law. It is a **cognitive load ceiling**. Human listeners can process only so much information at once. Traditions that exceed the ceiling die out (or become avant-garde niche). Traditions that fall below it are perceived as "boring" (or meditative).

The dial generator's most useful feature may be a **cognitive load meter** that warns when the sum exceeds ~6.0: "This combination may be unlistenable to most humans. Proceed?"

---

## 4. Constraint-Mux Using Dials: Real-Time Dial Adjustment from Serial Instrument Data

### The Architecture

The `serial-mux-constraint` fork (see `SERIAL-MUX-FORK-PLAN.md`) provides a Rust-based async multiplexer for serial/MIDI data. We extend it with a **Dial Translation Layer** that maps physical instrument gestures to dial positions in real time.

```
┌─────────────┐    UART/USB    ┌─────────────────┐    bincode    ┌─────────────┐
│  Wind Ctrl  │ ─────────────→ │  serial-mux-d   │ ────────────→ │  Dial Engine│
│  (breath,   │   115200 baud  │  (Rust daemon)  │   over Unix   │  (synth)    │
│  lip, key)  │                │                 │   socket      │             │
└─────────────┘                └─────────────────┘               └─────────────┘
         ↑
         │ Also accepts SSH fallback for wireless instruments
         │
┌─────────────┐
│  Drum Pad   │ ──→ mux ──→ mapped to I_horiz
│  (velocity, │     density → polyrhythmic complexity
│  density)   │
└─────────────┘
```

### Concrete Mapping: Yamaha WX5 Wind Controller → Dial Engine

The WX5 outputs MIDI breath (CC2), lip (CC1, mod wheel), and key data. We map:

| WX5 Output | Raw Range | Dial Mapping | Physical Meaning |
|------------|-----------|--------------|------------------|
| Breath CC2 | 0–127 | $I_{\text{spectral}}$ | Soft breath = pure sine; hard breath = rich brass |
| Lip CC1 | 0–127 | $I_{\text{vert}}$ | Center = 12-tone ET; edges = microtonal bend |
| Key velocity | 0–127 | $I_{\text{horiz}}$ | Staccato = sparse; legato = dense rhythmic layering |
| Key combination | Note set | Scale family | Chromatic → just intonation → 53-tone |

**Example performance:**

A musician starts with soft breath (CC2=20), centered lip (CC1=64), staccato notes:
- Dials: `(1.2, 0.8, 0.6)` — gentle classical feel, maybe early Baroque

They crescendo to hard breath (CC2=110), push lip sharp (CC1=110), and switch to rapid tonguing:
- Dials: `(2.8, 2.4, 2.9)` — Hindustani-gamelan hybrid with brass timbre

The transition is **continuous and immediate** because the serial-mux daemon runs at 1kHz update rate, and the dial engine interpolates on a 5ms audio buffer.

### The Consonance Monitor

The mux daemon includes a `ConsonanceMonitor` thread (see `SERIAL-MUX-FORK-PLAN.md`) that watches the spectral output of the dial engine and reports drift. If the musician pushes the dials into an unstable region (e.g., the "crystalline chaos" zone where cognitive overload is likely), the monitor sends a warning back to the instrument:

```rust
// In serial-mux-daemon/src/consonance_monitor.rs
if cognitive_load > 6.0 {
    // Send haptic feedback to instrument
    let warning = ProtocolMsg::DialWarning {
        suggested_vert: current_vert * 0.9,
        reason: "cognitive_load_exceeded",
    };
    client_socket.send(warning).await?;
}
```

The WX5 vibrates subtly, nudging the musician back toward a stable region. This is not "AI taking over" — it is **deadband-based assistance**, exactly analogous to the signal-chain dial metaphor where the system auto-adjusts when KPIs breach thresholds.

### Implementation Path

**Week 1:** Extend `serial-mux/protocol.rs` to include `DialSet` and `DialWarning` message types. Add `src/dial_mapper.rs` that implements the CC→dial translation table.

**Week 2:** Wire the mux daemon to a JACK audio backend running the dial engine. Test with WX5 + drum pad. Measure end-to-end latency (target: <10ms).

**Week 3:** Add the `ConsonanceMonitor`. Implement haptic feedback loop. Tune cognitive load thresholds with user study (n=10 musicians).

---

## 5. Caffeinix's Scheduler as Dial System: OS Performance Tuning as Musical Parameter

### The Core Idea

The `caffeinix-audio-rt` fork (see `TROY-KILLER-APPS.md`) replaces Linux-style CFS with an **Eisenstein lattice scheduler** that mathematically guarantees audio deadlines. We now reframe the scheduler itself as a dial system.

The OS has three internal dials:

| OS Dial | Symbol | Range | What it controls |
|---------|--------|-------|----------------|
| Buffer hardness | $D_{\text{buffer}}$ | [0.0, 1.0] | Audio buffer size: 0 = large (soft, high latency, safe); 1 = tiny (hard, sub-ms, risky) |
| Voice count | $D_{\text{voices}}$ | [0.0, 1.0] | Polyphony limit: 0 = mono; 1 = 128+ voices |
| Spectral fidelity | $D_{\text{spectral}}$ | [0.0, 1.0] | FFT size / oversampling: 0 = 256-point (fast, coarse); 1 = 8192-point (slow, exact) |

These are not independent. They compete for the same resource: CPU cycles. The scheduler's job is to find a **feasible point** in the $(D_{\text{buffer}}, D_{\text{voices}}, D_{\text{spectral}})$ space given the current system load.

### The Feasibility Lattice

Every audio process declares its requirements:

```c
struct audio_request {
    uint32_t period_us;      // How often it needs to run
    uint32_t deadline_us;    // How long it has to complete
    uint32_t computation_us; // Worst-case execution time
    float    dial_buffer;    // Preferred buffer hardness
    float    dial_voices;    // Preferred voice count
    float    dial_spectral;  // Preferred spectral fidelity
};
```

The scheduler snaps this request to the nearest feasible point on the **Eisenstein feasibility lattice**:

```c
// eisenstein_scheduler.c
#include "eisenstein.h"

// The feasibility condition:
// For N audio processes, the sum of (computation_i / period_i) must be ≤ 1.0
// This is the classic Liu-Layland utilization bound.
// We encode it as an Eisenstein norm constraint.

E12_Point request = e12_snap(
    req.dial_buffer * MAX_BUFFER,
    req.dial_voices * MAX_VOICES,
    req.dial_spectral * MAX_FFT
);

// Check if the snapped point is feasible
float utilization = compute_utilization(request);
if (utilization > 1.0) {
    // Dial down the least important axis
    request = dial_down_least_important(request, req);
    return -EAGAIN;  // Tell the process to try again with softer dials
}
```

### Real-Time Dial Adjustment Under Load

When a CPU-intensive process (e.g., compilation, scientific simulation) starts, the scheduler detects increased load and **automatically softens the audio dials** to maintain glitch-free playback:

```
System idle:
  Audio: D_buffer=0.9, D_voices=0.8, D_spectral=0.7
  → 64-sample buffer, 64 voices, 2048-point FFT
  → Latency: 1.45ms @ 44.1kHz

CPU burner starts:
  Scheduler detects utilization spike
  Audio dials softened: D_buffer=0.5, D_voices=0.6, D_spectral=0.4
  → 256-sample buffer, 32 voices, 512-point FFT
  → Latency: 5.8ms @ 44.1kHz
  → Still glitch-free, but softer sound

CPU burner stops:
  Scheduler restores original dials over 2-second ramp
  → Sound "tightens" gradually, like an analog tape machine coming up to speed
```

This is not a failure mode. It is a **musical feature**. The performer can deliberately trigger CPU-intensive processes to "soften" the audio dials in real time, creating timbral shifts that are mathematically guaranteed to be artifact-free.

### The Musical Analogy: OS as Ensemble

Think of the OS scheduler as a gamelan director:

- **Hard dials** = *Instruments locked in interlocking pattern* (e.g., reyong). Every note is predetermined, no deviation. High CPU cost, exact timing.
- **Soft dials** = *Soloist improvising* (e.g., gender wayang). Flexible timing, responsive to context. Lower CPU cost, adaptive timing.
- **Scheduler** = *The director (dalang)* who decides when to switch from interlocking to solo based on the narrative (system load).

The caffeinix scheduler is the first OS that **understands it is making musical decisions**.

### Concrete Implementation

**File:** `kernel/audio/eisenstein_scheduler.c`

```c
// Kernel-space dial state per audio process
struct dial_state {
    atomic_float buffer;
    atomic_float voices;
    atomic_float spectral;
};

// Called every scheduler tick (1kHz)
void audio_dial_update(struct proc *p) {
    float load = get_cpu_load();
    struct dial_state *d = p->audio_dials;
    
    if (load > 0.8) {
        // Softening ramp: reduce dials by 5% per tick
        atomic_fetch_min(&d->buffer, atomic_load(&d->buffer) * 0.95f);
        atomic_fetch_min(&d->voices, atomic_load(&d->voices) * 0.95f);
        atomic_fetch_min(&d->spectral, atomic_load(&d->spectral) * 0.95f);
    } else if (load < 0.3) {
        // Hardening ramp: restore toward target by 2% per tick
        atomic_fetch_max(&d->buffer, atomic_load(&d->buffer) * 1.02f);
        // ... etc
    }
    
    // Snap to lattice to prevent fractional dials
    e12_snap_dials(d);
}
```

**User-space API:**

```c
// user/synth.c
#include <audio.h>

int main() {
    // Register with preferred dials
    struct audio_dials d = {
        .buffer = 0.9,
        .voices = 0.8,
        .spectral = 0.7
    };
    
    int fd = sys_audio_register(&d);
    if (fd < 0) {
        printf("Scheduler rejected request: %s\n", strerror(-fd));
        // Try softer dials
        d.buffer = 0.5;
        fd = sys_audio_register(&d);
    }
    
    // Main loop: the scheduler guarantees our dials are feasible
    while (1) {
        sys_audio_commit(buffer);
    }
}
```

### Connection to Signal-Chain Theory

This is the same dial metaphor from `signal_chain.py`, applied to kernel space:

| Signal-Chain Concept | OS Equivalent |
|---------------------|---------------|
| Dial α ∈ [0,1] | $D_{\text{buffer}}$ ∈ [0,1] |
| Room | Audio process |
| Deadband detector | CPU load monitor |
| Snap (confidence=1.0) | Hard real-time guarantee |
| Fallback (dial < threshold) | Soft real-time, best effort |
| Tile | Audio buffer |
| RigidFinder | Feasibility check on Eisenstein lattice |

The `SignalChainRoom` class in `luciddreamer/signal_chain.py` already implements deadband-based dial adjustment. The caffeinix scheduler is a **kernel-space SignalChainRoom** where the "room" is the CPU and the "tiles" are audio buffers.

---

## Appendix: Quick Reference — Dial Positions of Known Styles

| Style | $I_{\text{vert}}$ | $I_{\text{horiz}}$ | $I_{\text{spectral}}$ | Sum |
|-------|-------------------|--------------------|------------------------|-----|
| Western ET Classical (Mozart) | 0.5 | 1.5 | 1.2 | 3.2 |
| Western Meantone (Bach organ) | 1.2 | 0.8 | 1.0 | 3.0 |
| Jazz (bebop) | 0.0 | 3.0 | 1.5 | 4.5 |
| Hindustani classical | 2.8 | 1.5 | 2.0 | 6.3* |
| Javanese gamelan | 3.2 | 1.2 | 2.4 | 6.8* |
| West African drumming | 0.8 | 3.5 | 0.6 | 4.9 |
| Japanese gagaku | 1.5 | 0.3 | 2.8 | 4.6 |
| Turkish makam | 2.5 | 1.0 | 1.5 | 5.0 |
| Spectralism (Grisey, Murail) | 0.5 | 1.0 | 3.5 | 5.0 |
| Minimalism (Reich) | 0.2 | 3.8 | 0.3 | 4.3 |
| Drone (Radigue, Young) | 3.5 | 0.1 | 0.2 | 3.8 |
| Noise (Merzbow) | 0.0 | 2.0 | 3.0 | 5.0 |
| **Crystalline Chaos** (predicted) | 3.5 | 3.5 | 3.5 | 10.5* |
| **Timbre Minimalism** (predicted) | 0.3 | 0.2 | 3.8 | 4.3 |

*\* Exceeds predicted cognitive load ceiling of ~6.0. These styles require trained listeners or gradual exposure.*

---

*Document connects: `CROSS-CULTURAL-VALIDATION.md` (empirical data), `TROY-KILLER-APPS.md` (caffeinix/plano forks), `SERIAL-MUX-FORK-PLAN.md` (real-time dial mapping), `luciddreamer/signal_chain.py` (dial theory implementation), `signal-chain/` papers (deadband, tiles, dial metaphor).*
