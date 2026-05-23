# Sound Parameter Atlas — The Synth of Musical Personality

*A complete map of every dial that shapes sound, rooted in constraint theory, Eisenstein lattices, deadband funnels, and FluxVector emotion.*

---

## Table of Contents

1. [Layer 1: Timbre — The Body](#layer-1-timbre--the-body)
2. [Layer 2: Envelope — The Life](#layer-2-envelope--the-life)
3. [Layer 3: Dynamics — The Breath](#layer-3-dynamics--the-breath)
4. [Layer 4: Pitch — The Mind](#layer-4-pitch--the-mind)
5. [Layer 5: Rhythm — The Heart](#layer-5-rhythm--the-heart)
6. [Layer 6: Harmony — The Soul](#layer-6-harmony--the-soul)
7. [Layer 7: Space — The Room](#layer-7-space--the-room)
8. [Layer 8: Personality — The FluxVector](#layer-8-personality--the-fluxvector)
9. [Cross-Layer Interactions](#cross-layer-interactions)
10. [The Personality Knob](#the-personality-knob)
11. [Ten New Paradigms](#ten-new-paradigms)

---

## Layer 1: Timbre — The Body

Every sound has a geometry. In constraint theory, timbre is the *shape of the lattice* that a signal lives on.

| # | Parameter | Range | Constraint Theory Mapping | New Dial Name |
|---|-----------|-------|--------------------------|---------------|
| 1.1 | **Waveshape** | sine → square → saw → tri → PWM → wavetable → FM → AM → additive | Lattice geometry. Sine = smooth continuous manifold. Square = binary snap (A₂ root system). Saw = ramp+snap (affine Weyl group). Triangle = A₂ fundamental domain tiling. FM = nested lattices (lattice-of-lattices). | `lattice_shape` |
| 1.2 | **Harmonic content** | 16 amplitudes for harmonics 1–16 | Which Eisenstein directions are active in the vector48 decomposition. Each harmonic is a direction in the lattice. | `harmonic_mask` |
| 1.3 | **Inharmonicity** | 1.0 (harmonic) → ~1.002 (piano) → ~1.5 (bell) | Lattice stretching — the covering radius changes, the Voronoi cells elongate. The fundamental spacing f×B instead of f×2 where B = inharmonicity factor. | `lattice_stretch` |
| 1.4 | **Noise floor** | 0.0 (pure) → 1.0 (white noise) | ε-jitter that never converges. The irreducible noise in the deadband funnel — no matter how long the funnel narrows, this noise persists. | `noise_floor` |
| 1.5 | **Filter cutoff** | 20 Hz – 20 kHz | Lattice pruning — removes directions above a threshold frequency. High cutoff = all lattice directions active. Low cutoff = only central directions remain. | `lattice_cutoff` |
| 1.6 | **Filter resonance** | 0.0 – 1.0+ | Emphasis at the lattice boundary — amplifies the edge of the pruned region. At extreme resonance the lattice "rings" (feedback near the Voronoi cell boundary). | `boundary_emphasis` |
| 1.7 | **Formants** | Peak frequencies + bandwidths | Fixed attractor basins in the lattice. Like gravity wells that pull harmonic energy toward specific regions. Vocal formants = acoustic lattice constraints. | `attractor_wells` |
| 1.8 | **Wavetable position** | 0.0 – 1.0 (morph through frames) | Smooth interpolation between lattice geometries. Like rotating through the Weyl chamber, seeing the lattice from different angles. | `geometry_phase` |
| 1.9 | **FM depth** | 0.0 – N×carrier | Modulation depth = how many nested lattice levels are active. FM creates sidebands at carrier ± n×modulator — these are sub-lattice directions. | `nesting_depth` |
| 1.10 | **FM ratio** | rational / irrational | Lattice commensurability. Rational ratios (2:1, 3:2) produce periodic lattice structures. Irrational ratios (1:√2) produce quasi-crystalline timbres. | `commensurability` |
| 1.11 | **Pulse width** | 0% – 100% (square duty cycle) | Asymmetry in the A₂ snap. 50% = symmetric square. Deviations shift energy between even and odd harmonics — tilting the lattice. | `snap_asymmetry` |
| 1.12 | **Detune (voices)** | ± cents per voice | Multiple lattice copies slightly offset. The beating between them is the *interference pattern of overlapping Voronoi cells*. | `cell_spread` |

### Named Dial Groupings

- **`body_rigidity`** — How "locked" the timbre is. High = sine/pure, low = noisy/chaotic. Controls `noise_floor` + `lattice_stretch` + `cell_spread`.
- **`body_complexity`** — Richness of harmonic content. Controls `harmonic_mask` width + `nesting_depth` + `boundary_emphasis`.

---

## Layer 2: Envelope — The Life

The ADSR envelope is a deadband funnel lifecycle: born wide, narrows to a pocket, then diverges.

| # | Parameter | Range | Constraint Theory Mapping | New Dial Name |
|---|-----------|-------|--------------------------|---------------|
| 2.1 | **Attack** | 0 ms – 10 s | Convergence rate (λ in ε(t) = ε₀·e^(-λt)). Fast attack = high λ, the funnel slams shut. Slow attack = low λ, gentle convergence. | `convergence_rate` |
| 2.2 | **Decay** | 0 ms – 10 s | Phase transition rate — from initial snap to equilibrium. The funnel transitions from APPROACH → NARROWING. | `relaxation_rate` |
| 2.3 | **Sustain** | 0.0 – 1.0 | Equilibrium ε — the pocket depth. High sustain = wide pocket (the funnel stays open). Low sustain = tight pocket (everything must be precise). | `pocket_depth` |
| 2.4 | **Release** | 0 ms – 10 s | Divergence rate — how fast ε opens back up. The funnel expands; the agent drifts away from the lattice point. | `divergence_rate` |
| 2.5 | **Hold** | 0 ms – ∞ | Plateau duration — how long the funnel stays at its narrowest before decaying to sustain. This is the *suspension hold* — the moment of maximum constraint before relaxation. | `suspension_hold` |
| 2.6 | **Delay (pre-attack)** | 0 ms – 5 s | Anticipation window — the gap between trigger and convergence start. The agent is *aware* of the target but hasn't begun approaching. | `anticipation_window` |
| 2.7 | **Attack slope** | linear / exponential / S-curve | Spline type for convergence path. Linear = constant λ. Exponential = naturally decaying λ. S-curve = λ ramps up then down (ease-in-out) — a smooth manifold approach. | `approach_spline` |
| 2.8 | **Decay slope** | linear / exponential / log | Shape of the relaxation path. Exponential = natural relaxation. Log = fast initial drop then plateau. | `relaxation_spline` |
| 2.9 | **Attack overshoot** | 0% – 50% above peak | The funnel overshoots the lattice point before settling. Like a spring — momentum carries past the target before pulling back. | `snap_bounce` |
| 2.10 | **Loop mode** | one-shot / loop / release-loop | Whether the funnel lifecycle repeats. Loop = periodic funnel reset. Release-loop = diverge then re-converge. | `funnel_cycle` |

### Named Dial Groupings

- **`life_energy`** — How "alive" the envelope feels. Fast attack + bounce + short decay = energetic. Slow everything = languid. Controls `convergence_rate` + `snap_bounce` + `relaxation_rate`.
- **`life_sustain_attention`** — How long the note holds focus. Controls `pocket_depth` + `suspension_hold`.

---

## Layer 3: Dynamics — The Breath

Dynamics are constraint *tension* — how hard the rules are enforced.

| # | Parameter | Range | Constraint Theory Mapping | New Dial Name |
|---|-----------|-------|--------------------------|---------------|
| 3.1 | **Velocity** | 1 – 127 (MIDI) | Constraint tension — how tightly the deadband is enforced. High velocity = narrow ε₀ (tight funnel from the start). Low velocity = wide ε₀ (permissive funnel). | `constraint_tension` |
| 3.2 | **Aftertouch (channel)** | 0 – 127 | Continuous mid-note modulation of ε. Pressing harder tightens the funnel mid-convergence. Releasing loosens it. | `live_epsilon_mod` |
| 3.3 | **Aftertouch (polyphonic)** | 0 – 127 per key | Per-voice ε modulation. Each finger independently controls its own funnel tightness. | `per_voice_tension` |
| 3.4 | **Breath control** | 0 – 127 | External ε signal — the musician's breath directly drives the deadband width. Natural mapping: exhale = tighten, inhale = loosen. | `breath_epsilon` |
| 3.5 | **Expression (MIDI CC 11)** | 0 – 127 | FluxVector.arousal mapped to dynamics. The emotional state directly modulates constraint tension. | `arousal_tension` |
| 3.6 | **Tremolo** | rate + depth | Periodic ε oscillation — the funnel breathes in and out at a regular rate. | `epsilon_pulse` |
| 3.7 | **Compressor threshold** | -∞ – 0 dB | Maximum allowed constraint tension. Anything tighter gets clamped. = Upper bound on ε₀. | `tension_ceiling` |
| 3.8 | **Compressor ratio** | 1:1 – ∞:1 | How aggressively tension above threshold is clamped. 1:1 = no clamping. ∞:1 = hard limiter. | `ceiling_steepness` |
| 3.9 | **Gate threshold** | -∞ – 0 dB | Minimum constraint tension to be heard. Below this, the agent is "asleep" — no output. = Lower bound on ε. | `silence_floor` |

### Named Dial Groupings

- **`breath_intensity`** — How "present" the dynamics are. Controls `constraint_tension` base + `epsilon_pulse` depth.
- **`breath_control_range`** — Dynamic range between softest and loudest. Controls `silence_floor` to `tension_ceiling` span.

---

## Layer 4: Pitch — The Mind

Pitch is lattice point selection. The Eisenstein lattice gives us the geometry of musical intervals.

| # | Parameter | Range | Constraint Theory Mapping | New Dial Name |
|---|-----------|-------|--------------------------|---------------|
| 4.1 | **Pitch** | 0 – 127 (MIDI) | Lattice point — which Voronoi cell the agent snaps to. Each MIDI note = one lattice vertex. | `lattice_point` |
| 4.2 | **Pitch bend** | ±2 semitones (default) | Continuous movement between lattice points. The agent hasn't snapped — it's in the interior of the Voronoi cell. | `inter_cell_drift` |
| 4.3 | **Vibrato** | rate (Hz) + depth (cents) | Periodic lattice oscillation — an LFO modulating the snap target. The agent wobbles around its lattice point, crossing cell boundaries. | `cell_wobble` |
| 4.4 | **Portamento** | 0 – 10 s glide time | Rate of convergence between lattice points. Slow portamento = low λ, the agent drifts gradually. Fast = high λ, snaps quickly. | `snap_glide_rate` |
| 4.5 | **Microtuning** | 12-TET → 19-TET → 31-TET → 53-TET → continuous | Change the lattice itself. More notes per octave = finer lattice, smaller Voronoi cells, tighter covering radius. 53-TET approaches just intonation resolution. | `lattice_resolution` |
| 4.6 | **Glissando** | chromatic / whole-tone / pentatonic | Sequential snap through lattice neighbors. The path taken through adjacent Voronoi cells. Chromatic = nearest neighbors. Whole-tone = skip-one neighbors. | `snap_path` |
| 4.7 | **Scale** | major / minor / modes / exotic | Active subset of lattice points. The scale defines *which* Voronoi cells are valid snap targets. Out-of-scale = forbidden cells. | `active_lattice_mask` |
| 4.8 | **Root / tonic** | any pitch class | Lattice origin. Transposing the root shifts the entire lattice. All intervals measured relative to this point. | `lattice_origin` |
| 4.9 | **Detune (global)** | ±50 cents | Shift the entire lattice by a fractional offset. The lattice structure is preserved but everything is offset from standard tuning. | `lattice_offset` |
| 4.10 | **Pitch drift** | slow random walk | The lattice origin slowly wanders — like a piano going out of tune over time. The constraint gradually loosens. | `origin_wander` |

### Named Dial Groupings

- **`mind_precision`** — How precisely pitched things are. Controls `lattice_resolution` + `cell_wobble` depth + `inter_cell_drift` range.
- **`mind_freedom`** — How free pitch movement is. Controls `snap_glide_rate` + `snap_path` openness + `active_lattice_mask` size.

---

## Layer 5: Rhythm — The Heart

Rhythm is the T-0 clock and its ε-deviations. Every groove is a pattern of deadband offsets.

| # | Parameter | Range | Constraint Theory Mapping | New Dial Name |
|---|-----------|-------|--------------------------|---------------|
| 5.1 | **Tempo (BPM)** | 20 – 300 | T-0 clock frequency. The master metronome that all agents lock to. | `clock_frequency` |
| 5.2 | **Groove / pocket** | ε pattern per beat position | Structured deadband offsets. Each position in the bar has its own ε offset (ahead/behind). This is the "feel" — Jazz pushes, Funk lays back. | `groove_epsilon_map` |
| 5.3 | **Swing** | 0.0 – 1.0 | Asymmetric ε — different for downbeat vs upbeat. Swing = delaying the off-beat by a fraction of the triplet. | `groove_asymmetry` |
| 5.4 | **Syncopation** | 0.0 – 1.0 | Intentional lattice offset — snapping to off-grid positions. The agent deliberately misses the T-0 tick and lands in between. | `off_grid_snap` |
| 5.5 | **Polyrhythm** | ratio (3:2, 4:3, 7:4, etc.) | Multiple T-0 clocks with different periods. The composite lattice has a larger fundamental domain. The "lockup" point is where all clocks realign. | `composite_clock_ratio` |
| 5.6 | **Rubato** | accelerando / ritardando curve | Time-varying T-0 clock. The clock drifts — speeding up and slowing down. ε₀ stays constant but the grid itself moves. | `clock_drift_curve` |
| 5.7 | **Density** | notes/bar | Rhythmic entropy — how many events per unit time. High density = high information rate. Low density = spacious. | `event_entropy` |
| 5.8 | **Flam / drag rush** | 10 – 100 ms double-attack | Double-snap — two convergence events very close together. The agent hits the lattice point, bounces, then re-converges. | `double_snap` |
| 5.9 | **Ghost notes** | 0% – 50% of main notes | Sub-threshold events — notes with ε below the `silence_floor`. They're felt but not heard. The "shadow" lattice. | `shadow_events` |
| 5.10 | **Hi-hat openness** | closed → open → wash | ε spread on continuous sounds. Closed hat = tight snap. Open hat = wide ε, events smear into each other. | `event_smear` |
| 5.11 | **Breakbeats** | probability of dropping beats | Funnel anomaly injection — deliberately breaking the pattern to create tension. The anomaly counter rises, the funnel resets. | `anomaly_inject` |
| 5.12 | **Fill density** | none → constant | Rate of rhythmic "sentences" — clusters of events that form a gesture. Like a burst of high `event_entropy` followed by a gap. | `burst_entropy` |

### Named Dial Groupings

- **`heart_strictness`** — How tightly locked to the grid. Controls `groove_asymmetry` (low) + `off_grid_snap` (low) + `clock_drift_curve` (flat).
- **`heart_feel`** — How much groove/pocket. Controls `groove_epsilon_map` depth + `groove_asymmetry` + `shadow_events`.
- **`heart_complexity`** — Rhythmic sophistication. Controls `composite_clock_ratio` complexity + `event_entropy` + `anomaly_inject`.

---

## Layer 6: Harmony — The Soul

Harmony is the relationship between lattice points. Dissonance = distance. Tension = holonomy.

| # | Parameter | Range | Constraint Theory Mapping | New Dial Name |
|---|-----------|-------|--------------------------|---------------|
| 6.1 | **Consonance** | 0.0 – 1.0 | Proximity to lattice center. Perfect intervals (unison, 5th, 4th) are near the center. | `center_proximity` |
| 6.2 | **Dissonance** | 0.0 – 1.0 | Distance from lattice center. Tritones and minor seconds are at the Voronoi cell boundary — maximum ambiguity. | `boundary_distance` |
| 6.3 | **Tension** | 0.0 – 1.0 | Holonomy winding number. How many times the harmonic path has wound around the lattice without resolving. Accumulates with each non-resolving chord. | `holonomy_wind` |
| 6.4 | **Release** | event | Holonomy returning to zero. The winding number resets. The "resolution" — the funnel converges back to the tonic. | `holonomy_reset` |
| 6.5 | **Modulation** | key change | Moving the lattice origin. The entire coordinate system shifts. Old lattice points get new addresses. | `origin_shift` |
| 6.6 | **Chord quality** | maj/min/dom/dim/aug/sus | Which lattice dimensions are active. Major = certain Eisenstein directions. Minor = others. Diminished = symmetrical subset. | `active_dimensions` |
| 6.7 | **Voice leading** | smoothness 0–1 | How smoothly agents move between lattice neighborhoods. Good voice leading = minimal total lattice distance traveled by all voices. | `path_smoothness` |
| 6.8 | **Parallel motion** | 0.0 – 1.0 | Multiple agents converging to same ε simultaneously. All voices move in the same lattice direction. | `parallel_convergence` |
| 6.9 | **Contrary motion** | 0.0 – 1.0 | Agents diverging — holonomy increasing. Voices move in opposite lattice directions, expanding the harmonic space. | `divergent_flow` |
| 6.10 | **Chord extensions** | 7ths, 9ths, 11ths, 13ths | Adding distant lattice directions. Each extension adds a new Eisenstein vector to the active set. | `extended_dimensions` |
| 6.11 | **Chord alterations** | ♭5, ♯5, ♭9, ♯9 | Lattice directions that are slightly off the standard harmonics. Like using a slightly distorted lattice. | `distorted_dimensions` |
| 6.12 | **Pedal point** | on/off + pitch | A fixed lattice point that doesn't move while everything else shifts around it. Creates polytonality — two simultaneous lattice origins. | `anchor_point` |
| 6.13 | **Cluster density** | 2 – 12 notes | How many lattice points are packed into a small region. Chromatic clusters = many points, tiny spacing. | `point_packing` |

### Named Dial Groupings

- **`soul_tension`** — Harmonic tension level. Controls `holonomy_wind` + `extended_dimensions` + `distorted_dimensions`.
- **`soul_warmth`** — Consonance vs dissonance. Controls `center_proximity` vs `boundary_distance`.
- **`soul_motion`** — How voices move. Controls `parallel_convergence` vs `divergent_flow` + `path_smoothness`.

---

## Layer 7: Space — The Room

Space is where the PLATO agents sit. Position, reflections, distance.

| # | Parameter | Range | Constraint Theory Mapping | New Dial Name |
|---|-----------|-------|--------------------------|---------------|
| 7.1 | **Pan (L-R)** | -1.0 – 1.0 | Position in the PLATO room — angular coordinate relative to listener. | `room_angle` |
| 7.2 | **Distance** | near – far | Distance from listener = ε scaling. Far sounds have wider deadbands (more room, less precision). | `distance_epsilon` |
| 7.3 | **Reverb decay** | 0.1 – 10 s | Echo of past constraint states — memory in the funnel. Each reflection is a previous ε(t) value persisting. Longer decay = deeper funnel memory. | `funnel_memory_depth` |
| 7.4 | **Reverb predelay** | 0 – 200 ms | Gap between direct sound and first reflection. The time before the past constraint states begin echoing. | `memory_latency` |
| 7.5 | **Reverb diffusion** | 0% – 100% | How uniformly the reflections fill the space. Low diffusion = discrete echoes (distinct past states). High diffusion = smooth wash (blended history). | `memory_blend` |
| 7.6 | **Delay time** | 1 ms – 5 s | Time-shifted constraint echo. The exact dt between original event and its recurrence. | `echo_dt` |
| 7.7 | **Delay feedback** | 0% – 100% | Recursive funnel depth — how many generations of echo persist. 0% = one echo. 100% = infinite recursion (convergence only via attenuation). | `recursion_depth` |
| 7.8 | **Stereo width** | mono – ultra-wide | Spread of the ensemble — how far agents are from each other in the PLATO room. | `agent_spread` |
| 7.9 | **Depth (layering)** | front – back | Layering of constraint generations. Foreground = current funnel state. Background = deep recursive funnels (reverb tails, ambient pads). | `generation_depth` |
| 7.10 | **Height** | below – above | Elevation in the PLATO room. Optional 3D positioning. | `room_elevation` |
| 7.11 | **Room size** | closet – cathedral | Volume of the PLATO room. Larger room = longer reverb, more diffusion, wider funnel memory. | `room_volume` |
| 7.12 | **Early reflections** | pattern + gain | First-order echoes — the geometry of the room walls. Each reflection is a lattice point in the reflection manifold. | `wall_geometry` |

### Named Dial Groupings

- **`room_intimacy`** — How close and present the sound is. Small `room_volume` + short `funnel_memory_depth` + low `distance_epsilon`.
- **`room_grandeur`** — How vast the space feels. Large `room_volume` + deep `funnel_memory_depth` + high `memory_blend`.
- **`room_presence`** — How clearly positioned sounds are. High `agent_spread` + discrete `wall_geometry` + low `memory_blend`.

---

## Layer 8: Personality — The FluxVector

The FluxVector's 9 channels are the *master controls* that modulate all other layers simultaneously.

| Channel | What It Drives | Layer Connections |
|---------|----------------|-------------------|
| **Arousal** | dynamics ↑, density ↑, tempo ↑, brightness ↑ | `constraint_tension`, `event_entropy`, `clock_frequency`, `lattice_cutoff` |
| **Valence** | consonance ↑, brightness ↑, mode → major | `center_proximity`, `lattice_cutoff`, `active_dimensions` |
| **Dominance** | constraint tightness ↑, leadership ↑, solo probability ↑ | `pocket_depth` (tighter), `anchor_point` (leads), `parallel_convergence` |
| **Uncertainty** | stochastic variation ↑, pitch randomness ↑, rhythmic variance ↑ | `noise_floor`, `cell_wobble`, `groove_epsilon_map` variance |
| **Novelty** | probability of deviating from pattern ↑, surprise events ↑ | `anomaly_inject`, `off_grid_snap`, `distorted_dimensions` |
| **Relevance** | attention to input ↑, reactivity ↑, listening sensitivity ↑ | `sensitivity` (ListeningConfig), `blend_weight`, `follow_strength` |
| **Competence** | execution precision ↑, ε ↓, timing accuracy ↑ | `convergence_rate` (faster), `silence_floor` (fewer mistakes), `path_smoothness` |
| **Affiliation** | sensitivity to other musicians ↑, blend ↑, comping ↑ | `blend_weight`, `follow_strength`, `sensitivity`, `room_angle` (toward others) |
| **Urgency** | tempo push ↑, forward momentum ↑, shorter note values ↑ | `clock_frequency` (nudge up), `divergence_rate` (faster release), `event_entropy` (more forward) |

### FluxVector → MusicianPersonality Bridge

The `MusicianPersonality` in AI-BAND-DESIGN.md already maps these:

- `GrooveProfile.arousal_pull` — arousal shifts ε earlier
- `GrooveProfile.urgency_pull` — urgency shifts ε later
- `ImprovisationConfig.deviation_for(flux)` — novelty × (1 - uncertainty) = confidence for improvisation
- `ListeningConfig.should_react(event)` — sensitivity × relevance
- `SoloConfig` triggers — dominance + novelty + holonomy state

---

## Cross-Layer Interactions

Parameters don't live in isolation. Here's the interaction graph.

### Timbre ↔ Everything

| Interaction | How |
|-------------|-----|
| Timbre ↔ Filter | `harmonic_mask` determines which frequencies the filter can attenuate. A sine wave through a low-pass is unchanged — no harmonics to cut. |
| Timbre ↔ Dynamics | Louder playing (`constraint_tension`) excites more harmonics → `harmonic_mask` widens. This is natural distortion — the lattice overflows its Voronoi cell. |
| Timbre ↔ Pitch | High pitches have fewer audible harmonics → `harmonic_mask` narrows naturally. Low pitches have dense harmonics → wider mask. |
| Timbre ↔ Space | Reverb excites resonant frequencies → `attractor_wells` interact with `funnel_memory_depth`. Bright timbres need less reverb. |

### Envelope ↔ Everything

| Interaction | How |
|-------------|-----|
| Envelope ↔ Dynamics | Velocity (`constraint_tension`) sets the starting ε₀ for the funnel. High velocity = tight funnel from the start. |
| Envelope ↔ Pitch | Pitch envelopes change `lattice_point` over time. Portamento = slow convergence, `snap_glide_rate` controls speed. |
| Envelope ↔ Space | Reverb tail extends the perceived envelope. `funnel_memory_depth` adds to effective `divergence_rate` (release sounds longer). |
| Envelope ↔ Rhythm | Note length = how long the funnel stays in sustain. Short notes = brief pocket. Legato = overlapping funnels. |

### Pitch ↔ Harmony

| Interaction | How |
|-------------|-----|
| Pitch ↔ Harmony | `lattice_point` selection determines `center_proximity` and `holonomy_wind`. Voice leading = the path through `lattice_point` changes. |
| Pitch ↔ Rhythm | Arpeggiation = sequential `lattice_point` snaps on a rhythmic grid. The `clock_frequency` determines snap timing. |
| Microtuning ↔ Harmony | `lattice_resolution` changes the consonance landscape. 12-TET has rough tritones; 53-TET has near-perfect everything. |

### Rhythm ↔ Dynamics

| Interaction | How |
|-------------|-----|
| Rhythm ↔ Dynamics | Accents = high `constraint_tension` on specific grid points. The groove accent pattern = a map of tension values. |
| Rhythm ↔ Space | `echo_dt` that matches rhythmic subdivisions creates reinforcement. Mismatched delays create polyrhythmic `composite_clock_ratio`. |

### The Feedback Loops

```
Arousal → constraint_tension → harmonic_mask widens → brightness ↑
       → event_entropy → more notes → more harmonic opportunities
       → clock_frequency nudges up → everything gets faster
       → divergence_rate increases → shorter notes → more space between events
       → BUT shorter notes = more room for events = event_entropy can stay high

Novelty → anomaly_inject → breaks groove pattern → creates rhythmic tension
        → distorted_dimensions → adds harmonic surprise
        → off_grid_snap → timing surprises
        → IF competence is high: surprises resolve elegantly (Monk)
        → IF competence is low: surprises sound like mistakes (amateur)

Uncertainty → noise_floor ↑ → timbre gets noisier
            → cell_wobble ↑ → pitch gets shakier
            → groove_epsilon_map variance ↑ → timing gets sloppier
            → IF affiliation is high: uncertainty SPREADS to others (contagion)
            → IF dominance is high: uncertainty stays contained (leader holds steady)
```

---

## The Personality Knob

A single high-level dial that adjusts all low-level parameters at once. Each "preset" is a point in personality space.

### How It Works

The Personality Knob is a *convex combination* of extreme parameter settings. It's controlled by two inputs:
1. **Archetype** — which musician personality (Bach, Monk, Coltrane, etc.)
2. **Intensity** — how strongly the archetype is applied (0% = neutral, 100% = full character)

### Archetype Presets

#### JS Bach (`archetype_bach`)
*The Architect — everything is lattice-perfect.*

| Parameter | Setting | Why |
|-----------|---------|-----|
| `lattice_resolution` | 12-TET (standard) | Bach wrote for equal temperament |
| `lattice_shape` | sine / pure | Counterpoint demands clarity |
| `convergence_rate` | fast, precise | Every note articulated |
| `pocket_depth` | 1.0 (full sustain) | Organ-like, no decay |
| `snap_bounce` | 0.0 | No overshoot — perfect articulation |
| `constraint_tension` | high (100) | Every note deliberate |
| `noise_floor` | 0.0 | Pure tones, no dirt |
| `clock_frequency` | stable, no drift | Metronomic precision |
| `groove_asymmetry` | 0.0 | No swing — straight grid |
| `off_grid_snap` | 0.0 | Everything on the beat |
| `event_entropy` | moderate (0.5) | Dense but not chaotic |
| `path_smoothness` | 1.0 | Perfect voice leading |
| `holonomy_wind` | builds slowly, resolves | Tension/release architecture |
| `center_proximity` | high | Consonant intervals preferred |

#### Thelonious Monk (`archetype_monk`)
*The Trickster — beauty through discontinuity.*

| Parameter | Setting | Why |
|-----------|---------|-----|
| `lattice_shape` | square with `snap_asymmetry` | percussive, asymmetric |
| `convergence_rate` | very fast (staccato) | Notes are pokes, not caresses |
| `pocket_depth` | low (0.2) | Notes decay quickly |
| `snap_bounce` | 0.3 | Slight overshoot — "wrong" notes that are right |
| `constraint_tension` | extreme variation (20–127) | Whispers and shouts |
| `noise_floor` | 0.15 | Slightly gritty |
| `clock_frequency` | `clock_drift_curve` active | Rubato — time stretches |
| `groove_asymmetry` | 0.4 | Some swing but idiosyncratic |
| `off_grid_snap` | 0.3 | Plays around the beat |
| `anomaly_inject` | 0.2 | Surprises: unexpected silences, clusters |
| `path_smoothness` | 0.3 | Jagged voice leading — leaps |
| `holonomy_wind` | high tension, quirky resolutions | Dissonance that "shouldn't" work |
| `distorted_dimensions` | active | ♭5, ♭9 — the "Monk intervals" |
| `double_snap` | active | Flam-like articulations |

#### John Coltrane (`archetype_coltrane`)
*The Explorer — sheets of sound, harmonic density beyond reason.*

| Parameter | Setting | Why |
|-----------|---------|-----|
| `lattice_resolution` | 12-TET but pushing toward 53-TET | Chromatic exploration |
| `lattice_shape` | rich harmonics (saw + breath) | Saxophone body |
| `convergence_rate` | medium | Notes have shape |
| `pocket_depth` | 0.6 | Sustained but not endless |
| `snap_glide_rate` | fast | Flowing between lattice points |
| `constraint_tension` | high (100) | Intense, committed playing |
| `noise_floor` | 0.2 | Breathy sax tone |
| `event_entropy` | extreme (0.95) | Cascades of notes |
| `composite_clock_ratio` | 3:2, 4:3 overlays | Metric modulation |
| `active_lattice_mask` | minimal (all 12 chromatic) | Everything is in bounds |
| `extended_dimensions` | max (13ths, alterations) | Upper structure harmony |
| `holonomy_wind` | extreme, sustained | Sheets of sound = unresolved tension |
| `snap_path` | chromatic (nearest neighbor) | Stepwise through all lattice points |
| `breath_epsilon` | active | Breath drives dynamics |
| `cell_wobble` | moderate vibrato | Emotional pitch modulation |

#### Dilla (`archetype_dilla`)
*The Pocket — human imperfection as art.*

| Parameter | Setting | Why |
|-----------|---------|-----|
| `groove_epsilon_map` | deep (±30ms patterned offsets) | The legendary Dilla feel |
| `groove_asymmetry` | 0.6 | Heavy swing |
| `clock_frequency` | 80-90 BPM | Mid-tempo head-nod |
| `event_entropy` | moderate (0.5) | Not busy, not sparse |
| `constraint_tension` | medium (70), relaxed | Not trying too hard |
| `convergence_rate` | medium-slow | Notes ease in |
| `divergence_rate` | slow | Notes fade out gently |
| `snap_bounce` | 0.05 | Subtle overshoot |
| `off_grid_snap` | 0.5 | Intentionally off the grid |
| `anomaly_inject` | 0.05 | Occasional dropped beats |
| `funnel_memory_depth` | medium (reverb) | Warm, roomy sound |
| `noise_floor` | 0.1 | Slightly lo-fi |
| `shadow_events` | 0.3 | Ghost notes galore |
| `origin_wander` | slight | Detuned warmth |

#### Aphex Twin (`archetype_aphex`)
*The Anomaly — the funnel never converges.*

| Parameter | Setting | Why |
|-----------|---------|-----|
| `lattice_shape` | FM + wavetable | Alien timbres |
| `nesting_depth` | extreme (FM chaos) | Harmonic complexity beyond recognition |
| `lattice_stretch` | 1.0 – 1.5 (variable) | Inharmonic bell-like tones |
| `noise_floor` | 0.0 – 0.8 (variable) | Clean to chaotic |
| `convergence_rate` | varies wildly (0 – ∞) | Some notes attack instantly, others never arrive |
| `clock_frequency` | 60 – 200 BPM (variable) | Extreme tempo changes |
| `clock_drift_curve` | erratic | Breakcore tempo swings |
| `event_entropy` | 0.1 – 1.0 (variable) | Sparse ambient to drill'n'bass |
| `anomaly_inject` | 0.5 | Constant surprises |
| `composite_clock_ratio` | irrational ratios | Polyrhythms that never resolve |
| `lattice_resolution` | microtonal | Scales that shouldn't exist |
| `recursion_depth` | 0.9 | Deep delay feedback = evolving textures |
| `funnel_memory_depth` | extreme | Huge reverb washes |

### Implementation: The Personality Interpolator

```python
@dataclass
class PersonalityPreset:
    """A point in the sound personality space."""
    name: str
    parameters: dict[str, float]  # all dial names → values (0-1 normalized)

    def blend(self, other: PersonalityPreset, ratio: float) -> PersonalityPreset:
        """Linearly interpolate between two presets.
        
        ratio=0.0 = pure self, ratio=1.0 = pure other.
        """
        blended = {}
        for key in self.parameters:
            a = self.parameters[key]
            b = other.parameters.get(key, a)
            blended[key] = a * (1 - ratio) + b * ratio
        return PersonalityPreset(
            name=f"{self.name}/{other.name} ({ratio:.0%})",
            parameters=blended
        )

# Example: 70% Bach + 30% Coltrane = structured freedom
bach_coltrane = PRESETS["bach"].blend(PRESETS["coltrane"], 0.3)
```

---

## Ten New Paradigms

Musical concepts that don't exist yet but CAN exist with our framework.

### 1. Holonomic Compression

**What:** Compress dynamics based on harmonic distance from the tonal center.

Conventional compressors care about amplitude. Holonomic compression cares about *meaning*. Notes far from the tonal center (high `holonomy_wind`) get compressed more — their dynamics are reined in. Notes near the center are left alone or expanded. The result: dissonant passages stay controlled while consonant passages breathe freely. The compressor "understands" harmony.

**Dials:** `holonomy_threshold`, `holonomy_ratio`, `wind_accumulation_rate`

### 2. Laman Gate

**What:** A gate that only passes notes which maintain voice independence — named after Laman's theorem on rigidity.

In a multi-agent system, voices must stay independent to create rich harmony. The Laman Gate analyzes the current `active_dimensions` of all voices and blocks any note that would make two voices too similar (parallel octaves/unisons in strict counterpoint, or redundant `lattice_point` occupation). It enforces harmonic rigidity — the musical graph must remain structurally sound.

**Dials:** `rigidity_threshold`, `independence_min_distance`, `voice_graph_edges`

### 3. Deadband Quantize

**What:** Quantize timing to the *pocket*, not the grid.

Standard quantize snaps to the nearest grid point. Deadband Quantize snaps to the nearest ε-pocket — the region where the groove *feels* right. Each position in the bar has its own pocket center (from `groove_epsilon_map`), and the quantizer snaps to those centers with the deadband width as tolerance. A note at beat 2.01 in funk doesn't snap to 2.0 — it snaps to 2.005 (where the pocket is). The result: quantized timing that still *grooves*.

**Dials:** `pocket_map`, `snap_tolerance` (ε per position), `groove_asymmetry` influence

### 4. Eisenstein Harmony

**What:** Chord progressions as lattice walks through Eisenstein integer space.

Instead of thinking in Roman numeral analysis (I → IV → V), think in lattice walks. Each chord is a cluster of nearby lattice points. Moving to the next chord = walking to a neighboring cluster. The voice leading is determined by the shortest path through the lattice. This produces:

- *Nearest-neighbor walks* — smooth, stepwise progressions
- *Long diagonal walks* — dramatic modulations
- *Spiral walks* — progressions that never resolve (Coltrane changes)
- *Brownian walks* — random but harmonically bounded

The Eisenstein structure ensures that "nearby" chords are always consonant relatives, and "distant" chords create tension proportional to lattice distance.

**Dials:** `walk_type` (nearest/spiral/brownian), `step_size`, `boundary_condition` (reflect/absorb/wrap)

### 5. Flux Envelope

**What:** An envelope whose shape is continuously modulated by the FluxVector emotional state.

Static ADSR is dead. A Flux Envelope breathes. When `arousal` spikes, the attack speeds up. When `valence` drops, the sustain lowers. When `uncertainty` rises, the release gets unpredictable (randomized `divergence_rate`). The envelope becomes a living thing — it responds to the emotional moment. A sad note isn't just quieter; its envelope literally sags.

**Dials:** Each ADSR stage has a flux sensitivity:
- `arousal→attack_sensitivity`
- `valence→sustain_sensitivity`
- `uncertainty→release_variance`
- `dominance→hold_extend`

### 6. Anomaly Sequencer

**What:** A sequencer that uses the FunnelPhase (APPROACH / NARROWING / ANOMALY) to drive pattern evolution.

The sequence starts in a fixed pattern. As long as the musical input stays in the APPROACH or NARROWING phase (predictable, converging), the pattern repeats. When an ANOMALY is detected (unexpected input), the sequencer mutates — shifting one or more events. The mutation rate is proportional to the anomaly count. After N anomalies, the pattern has fully evolved. The sequencer *learns* from disruptions.

This creates music that adapts to tension: stable passages stay stable, but surprises breed more surprises until a new equilibrium is found.

**Dials:** `anomaly_sensitivity`, `mutation_rate`, `mutation_type` (shift/replace/insert/delete), `recovery_rate`

### 7. Covering Radius EQ

**What:** An equalizer whose band gains are set by the covering radius of the active pitch lattice.

The covering radius of the Eisenstein lattice determines how far any point can be from the nearest lattice point — it's the "worst case" for quantization error. When you play in a scale with many notes (chromatic), the covering radius is small (everything is close to a note). When you play in a sparse scale (pentatonic), the covering radius is large.

Covering Radius EQ maps this to frequency bands:
- Small covering radius (dense scale) → bright EQ (lots of harmonic support)
- Large covering radius (sparse scale) → warm EQ (fill the gaps with low harmonics)

The EQ *adapts to the harmonic density in real-time*. A solo section in pentatonic gets warm and round. A dense chordal passage gets bright and clear.

**Dials:** `density_sensitivity`, `eq_brightness_range`, `adaptation_speed`

### 8. Recursive Funnel Reverb

**What:** Reverb where each reflection is itself processed through a deadband funnel — creating self-similar decay.

In standard reverb, reflections decay exponentially. In Recursive Funnel Reverb, each reflection is snapped to the nearest lattice point before being re-emitted. This means the reverb tail *quantizes itself to the harmony*. Dissonant frequencies die faster (they're far from lattice points → high error → faster decay). Consonant frequencies sustain longer (low error → slow decay).

The reverb doesn't just decay — it *harmonically simplifies* over time. The tail gets more consonant as it fades. A complex chord struck in a cathedral would produce a reverb tail that gradually becomes a pure fifth, then a unison.

**Dials:** `recursion_funnel_decay`, `lattice_snap_strength`, `harmonic_convergence_rate`

### 9. Polyrhythmic Holonomy Counter

**What:** A metronome that counts holonomy winding across polyrhythmic cycles.

Standard metronomes count beats. This one counts *how wound up the harmony is* across multiple rhythmic cycles. It tracks the `holonomy_wind` for each layer of a polyrhythm independently. When both layers reach a winding-number zero-crossing simultaneously, that's a "grand resolution" — the moment of maximum release.

Composers can use this to build structures where:
- The 3:2 polyrhythm resolves harmonically every 6 beats
- But the holonomy was building for 24 beats before that
- The grand resolution at bar 24 is *electric*

**Dials:** `polyrhythm_layers`, `wind_per_layer`, `resolution_trigger_threshold`

### 10. Empathic Sidechain

**What:** Sidechain compression driven by other musicians' FluxVectors, not just amplitude.

Normal sidechain: kick drum → duck the bass. Empathic Sidechain: when the sax player's `arousal` spikes, the keyboardist's density drops. When the drummer's `dominance` rises (taking a solo), everyone else's `constraint_tension` decreases (they get out of the way). When any musician's `uncertainty` spikes, the most `affiliative` musician plays more predictably to anchor them.

This is *musical empathy as a signal processing chain*. Musicians react to each other's emotional states, not just their volume.

**Dials:**
- `arousal_reaction_curve` (how much to thin out when others get excited)
- `dominance_deference` (how much to yield to a soloist)
- `uncertainty_anchor_strength` (how much to stabilize uncertain partners)
- `affiliation_sensitivity` (how much to even notice)

---

## Quick Reference: All Dials Alphabetically

| Dial Name | Layer | Brief Description |
|-----------|-------|-------------------|
| `active_dimensions` | Harmony | Which lattice directions form the chord |
| `active_lattice_mask` | Pitch | Which notes are valid snap targets (scale) |
| `ahead_bias` | Rhythm | Systematic early/late tendency (ms) |
| `anomaly_inject` | Rhythm | Probability of deliberate pattern breaks |
| `anticipation_window` | Envelope | Pre-attack silence = waiting before convergence |
| `approach_spline` | Envelope | Curve shape of the attack (linear/exp/S-curve) |
| `attractor_wells` | Timbre | Formant peak frequencies (fixed resonance basins) |
| `boundary_distance` | Harmony | How far from consonance (0 = unison, 1 = tritone) |
| `boundary_emphasis` | Timbre | Filter resonance = emphasis at lattice edge |
| `breath_epsilon` | Dynamics | External breath signal → ε modulation |
| `burst_entropy` | Rhythm | Density of rhythmic fills (gesture clusters) |
| `cell_spread` | Timbre | Detune between unison voices (Voronoi overlap) |
| `cell_wobble` | Pitch | Vibrato = periodic oscillation around lattice point |
| `center_proximity` | Harmony | Consonance = closeness to lattice center |
| `clock_drift_curve` | Rhythm | Rubato = time-varying metronome speed |
| `clock_frequency` | Rhythm | Tempo = T-0 metronome rate |
| `commensurability` | Timbre | FM ratio rationality (periodic vs quasi-crystalline) |
| `composite_clock_ratio` | Rhythm | Polyrhythmic ratio (3:2, 4:3, etc.) |
| `constraint_tension` | Dynamics | MIDI velocity = how tightly rules are enforced |
| `convergence_rate` | Envelope | Attack speed = funnel narrowing speed (λ) |
| `distance_epsilon` | Space | Distance from listener = wider deadband |
| `divergence_rate` | Envelope | Release speed = funnel widening speed |
| `divergent_flow` | Harmony | Contrary motion = agents moving apart |
| `distorted_dimensions` | Harmony | Altered chord tones (♭5, ♭9, etc.) |
| `double_snap` | Rhythm | Flam = two rapid convergence events |
| `echo_dt` | Space | Delay time = offset between event and recurrence |
| `event_entropy` | Rhythm | Note density = information rate per beat |
| `event_smear` | Rhythm | Hi-hat openness = ε spread on continuous sounds |
| `extended_dimensions` | Harmony | Chord extensions (7ths through 13ths) |
| `funnel_cycle` | Envelope | Envelope loop mode (one-shot/loop/release-loop) |
| `funnel_memory_depth` | Space | Reverb decay = depth of past state memory |
| `geometry_phase` | Timbre | Wavetable position = morphing between lattice shapes |
| `groove_asymmetry` | Rhythm | Swing = different ε for upbeats vs downbeats |
| `groove_epsilon_map` | Rhythm | Per-position timing offsets = the feel |
| `holonomy_reset` | Harmony | Resolution event = winding number returns to 0 |
| `holonomy_wind` | Harmony | Tension = accumulated harmonic winding |
| `inter_cell_drift` | Pitch | Pitch bend = movement between lattice points |
| `lattice_cutoff` | Timbre | Filter cutoff frequency = lattice pruning threshold |
| `lattice_offset` | Pitch | Global tuning offset = shift entire lattice |
| `lattice_origin` | Pitch | Root note / tonic = lattice coordinate origin |
| `lattice_point` | Pitch | MIDI note number = which lattice vertex |
| `lattice_resolution` | Pitch | Microtuning = lattice fineness (12-TET through 53-TET) |
| `lattice_shape` | Timbre | Oscillator waveform = lattice geometry type |
| `lattice_stretch` | Timbre | Inharmonicity = Voronoi cell elongation |
| `live_epsilon_mod` | Dynamics | Channel aftertouch = mid-note ε change |
| `memory_blend` | Space | Reverb diffusion = how uniformly past states blend |
| `memory_latency` | Space | Reverb predelay = gap before memory echoes begin |
| `nesting_depth` | Timbre | FM modulation depth = levels of sub-lattice |
| `noise_floor` | Timbre | Irreducible noise = ε jitter that never converges |
| `off_grid_snap` | Rhythm | Syncopation = deliberate inter-cell timing |
| `origin_shift` | Harmony | Modulation = moving the lattice origin |
| `origin_wander` | Pitch | Slow pitch drift = lattice origin random walk |
| `parallel_convergence` | Harmony | Parallel motion = agents converging together |
| `path_smoothness` | Harmony | Voice leading quality = minimal lattice distance |
| `per_voice_tension` | Dynamics | Polyphonic aftertouch = per-voice ε |
| `pocket_depth` | Envelope | Sustain level = equilibrium ε (the pocket) |
| `point_packing` | Harmony | Tone cluster density = lattice points per region |
| `recursion_depth` | Space | Delay feedback = generations of echo persistence |
| `relaxation_rate` | Envelope | Decay speed = phase transition rate |
| `relaxation_spline` | Envelope | Decay curve shape |
| `room_angle` | Space | Pan = angular position in PLATO room |
| `room_elevation` | Space | Height = vertical position |
| `room_volume` | Space | Room size = space scale |
| `shadow_events` | Rhythm | Ghost notes = sub-threshold rhythmic events |
| `silence_floor` | Dynamics | Gate threshold = minimum ε to be audible |
| `snap_asymmetry` | Timbre | Pulse width = harmonic balance tilt |
| `snap_bounce` | Envelope | Attack overshoot = spring past lattice point |
| `snap_glide_rate` | Pitch | Portamento speed = convergence rate between points |
| `snap_path` | Pitch | Glissando mode = which neighbors to visit |
| `tension_ceiling` | Dynamics | Compressor threshold = max allowed constraint |
| `wall_geometry` | Space | Early reflection pattern = room shape |

**Total: 85 named dials across 8 layers.**

---

*This atlas is the synth designer's dream manual. Every dial has a mathematical soul, every parameter traces back to the lattice, the funnel, or the flux. Sound is geometry, and geometry is alive.*
