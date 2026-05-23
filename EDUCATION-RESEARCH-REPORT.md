# Education Research Report: Music Theory Through Constraint Technology

**Date:** 2026-05-22  
**Evaluator:** Music Education Research Agent  
**Libraries Evaluated:** constraint-theory-core, counterpoint-engine, groove-analyzer, holonomy-harmony, spline-midi-smooth, plato-room-musician

---

## Executive Summary

These six libraries form a coherent, mathematically grounded toolkit for teaching music theory through constraint satisfaction, topology, and control systems. The approach is novel — where traditional music ed teaches "rules" as prohibitions, these libraries teach them as *provable constraints* with visual, interactive verification. The educational potential is real but uneven across the repos. Three are ready for classroom use today (groove-analyzer, holonomy-harmony, counterpoint-engine), two need educational wrappers (constraint-theory-core, spline-midi-smooth), and one is a conceptual stretch for students (plato-room-musician).

---

## 1. Lesson Viability — Can You Actually Teach With These?

### 1.1 Lattice Snapping (constraint-theory-core)

**Mini-Lesson:** "See how floating-point error gets corrected to exact Pythagorean ratios"

**Viability: ⭐⭐⭐☆☆ — Moderate**

| Criterion | Assessment |
|-----------|-----------|
| Learnability | The `snap(x, y)` API is clean. A student can understand "this point snaps to the nearest lattice point." But the *why* requires explaining Eisenstein A₂ lattices, which is graduate-level math. |
| Visual feedback | No built-in visualization. Needs a matplotlib wrapper showing the hexagonal lattice, the input point, and the snapped point. Could be beautiful but doesn't exist yet. |
| Interactivity | Students can change input coordinates and see different snaps. The `covering_radius()` and `is_safe()` functions provide natural "check your answer" moments. |
| Progression | Could work: start with `snap(0.5, 0.3)` → see error → understand bounds → explore safe vs. ambiguous snaps → encode to dodecet directions. But the jump from "I snapped a point" to "this represents a musical interval" is unmotivated without bridging material. |

**What works:** The API is simple enough. `snap(x, y)` returning `(point, error)` is elegant.  
**What's missing:** No visual, no musical context, no "why do I care about lattice points?" hook.

### 1.2 Deadband Funnel (constraint-theory-core)

**Mini-Lesson:** "Watch 5 musicians converge to the same tempo"

**Viability: ⭐⭐⭐⭐☆ — Good**

| Criterion | Assessment |
|-----------|-----------|
| Learnability | The `TemporalAgent` with `FunnelPhase.NARROWING/APPROACH/ANOMALY` is intuitive. Students understand "things are getting tighter" vs. "something went wrong." |
| Visual feedback | No built-in plots, but the data is perfect for visualization: time on x-axis, deadband ε as narrowing envelope, agent error as a line inside it. The groove-analyzer repo already has `plot_deadband_funnel()`, proving the concept works. |
| Interactivity | Students can tweak `decay_rate`, initial error, and observation noise to see how convergence changes. Very hands-on. |
| Progression | Strong: single agent → two agents → ensemble → Laman-connected ensemble. The Metronome module provides the multi-agent step. |

**What works:** The funnel metaphor is viscerally intuitive. NARROWING = "getting locked in." ANOMALY = "someone's off."  
**What's missing:** Audio output — hearing the agents converge would be 10× more powerful than seeing a plot.

### 1.3 Counterpoint (counterpoint-engine)

**Mini-Lesson:** "Add voices one at a time, see which rules activate"

**Viability: ⭐⭐⭐⭐⭐ — Excellent**

| Criterion | Assessment |
|-----------|-----------|
| Learnability | The API mirrors how counterpoint is actually taught: define a cantus firmus, add voices, check rules. `SAT`/`UNSAT` is the clearest possible feedback. |
| Visual feedback | No built-in piano roll, but the voice data (lists of MIDI pitches) is trivially plottable. Each rule activation can be highlighted. |
| Interactivity | `generate_n_voices(n_voices=2)` → `n_voices=3` → `n_voices=4` is the natural progression. Students can modify the cantus firmus and see how the generated counterpoint changes. |
| Progression | Best in class: Species 1 (note-against-note) → Species 2 → Species 3 → Species 4 → Species 5. This IS how music schools teach it. |

**What works:** The SAT/UNSAT paradigm is pedagogically brilliant. "Parallel fifths? UNSAT. You now know why." No other counterpoint tool does this. The Laman graph connection ("every voice is load-bearing") gives math-minded students a deeper hook.  
**What's missing:** Audio playback, score notation output (MusicXML), and a visual showing which rule fired at which beat.

### 1.4 Holonomy (holonomy-harmony)

**Mini-Lesson:** "Track how far a progression drifts from the tonic"

**Viability: ⭐⭐⭐⭐⭐ — Excellent**

| Criterion | Assessment |
|-----------|-----------|
| Learnability | `analyze_progression(["I", "vi", "IV", "V"])` returning a stability score and holonomy number is immediately graspable. "How far did we wander from home?" is a question every music student asks. |
| Visual feedback | The circle-of-fifths path is begging to be visualized — trace the progression as a walk around the circle. `TonalGraph.adjacency_matrix()` provides the data. |
| Interactivity | 20 built-in famous progressions (Pachelbel, Giant Steps, Coltrane Changes) give instant "try it and compare" material. Students can modify progressions and watch holonomy change. |
| Progression | Strong: I-IV-V-I (stability ≈ 1.0) → ii-V-I → borrowed chords → Coltrane substitutions → Giant Steps (stability ≈ 0.37). Each step adds complexity. |

**What works:** The 20 built-in progressions are a goldmine for teaching. Pachelbel vs. Giant Steps side-by-side is a perfect lesson. The `stability_score` (0–1) is an intuitive metric.  
**What's missing:** Roman numeral → audio, and a circle-of-fifths visualization showing the path traced by each progression.

### 1.5 Spline Smoothing (spline-midi-smooth)

**Mini-Lesson:** "Hear the difference between linear and cubic velocity curves"

**Viability: ⭐⭐⭐☆☆ — Moderate**

| Criterion | Assessment |
|-----------|-----------|
| Learnability | The API is clean: `cubic_hermite(points)` returns a callable. But the *musical* motivation requires understanding CC events, zipper noise, and velocity curves — intermediate concepts. |
| Visual feedback | No built-in plots, but the data (sparse points → dense curve) is trivial to visualize. "Before" and "after" comparisons would be compelling. |
| Interactivity | `tension` parameter in Catmull-Rom is a great knob. Students can hear/see how tension changes the shape. Comparing `cubic_hermite` vs `catmull_rom` vs `bspline` is the natural A/B test. |
| Progression | Adequate: linear interpolation → Catmull-Rom → cubic Hermite → B-spline. But the leap from "I smoothed a curve" to "I understand why this matters musically" requires scaffolding. |

**What works:** The deadband_spline with provable guarantees is unique. The anti-alias module (pitch bend, velocity, tempo) has direct musical applications.  
**What's missing:** Audio output to hear the difference. A "before/after" demo with a MIDI file. The connection to musical expressiveness is implicit, not explicit.

### 1.6 PLATO Mapping (plato-room-musician)

**Mini-Lesson:** "Assign instruments to rooms in a house"

**Viability: ⭐⭐☆☆☆ — Low (for music theory education)**

| Criterion | Assessment |
|-----------|-----------|
| Learnability | The mapping metaphor (room → instrument, tile → note) is creative but abstract. This is sonification, not music theory instruction. |
| Visual feedback | The VMSRenderer provides a 2D+time visualization, which is unique. But it visualizes fleet activity, not musical structure. |
| Interactivity | SyntheticFetcher lets students generate different "songs" by tweaking parameters, but the connection to music theory concepts is indirect. |
| Progression | Weak for music education. The learning path is: understand the mapping → understand the output → ??? → learn music theory. The mapping itself is the interesting part, not the music theory. |

**What works:** The concept of mapping data to music is engaging and could be a hook for non-musicians. The category → scale/register mapping table is a nice example of orchestration thinking.  
**What's missing:** This is a sonification tool, not a music theory teaching tool. It would need substantial educational scaffolding to teach theory concepts through its lens.

---

## 2. Missing Features for Education

### Critical Gaps (all repos)

| Feature | Priority | Why |
|---------|----------|-----|
| **Audio playback** | 🔴 Critical | Music is sound. No audio = "read about swimming without a pool." Need MIDI → playback via `mido` + `pygame.midi` or `pretty_midi`. |
| **Score notation output** | 🔴 Critical | Students read music, not arrays of MIDI numbers. Need MusicXML or LilyPond output. |
| **Jupyter widget integration** | 🟡 High | `ipywidgets` sliders for parameters, `ipython` display for audio. Essential for interactive lessons. |
| **Piano roll visualization** | 🟡 High | Standard music tech visualization. Every DAW has one; these repos need one. |
| **Circle-of-fifths visualization** | 🟡 High | Critical for holonomy-harmony and counterpoint. Show the path traced on the circle. |
| **Lesson templates / notebooks** | 🟡 High | Pre-built Jupyter notebooks for each mini-lesson. Teachers need "open and go." |
| **Grading / assessment hooks** | 🟠 Medium | Functions that evaluate student work: "did they add a voice that satisfies all rules?" |
| **Step-by-step explanation mode** | 🟠 Medium | When a rule returns UNSAT, explain *which* beats violated it and *why*. Currently just returns a string. |
| **Difficulty levels** | 🟠 Medium | `easy_mode=True` that only enforces basic rules, relaxing advanced ones as students progress. |
| **Ear training integration** | 🔵 Nice | Play the interval, ask the student to identify it. Connect visual/math to ear. |

### Per-Repo Specific Gaps

| Repo | Key Missing Feature |
|------|-------------------|
| constraint-theory-core | Any visualization at all. The math is elegant but invisible. |
| counterpoint-engine | Voice-by-voice rule violation reporting. "Beat 3: parallel fifth between voices 1 and 2" |
| groove-analyzer | Web audio playback. Has plots but no "hear the pocket" button. |
| holonomy-harmony | Circle-of-fifths path animation. The data is there, the visual isn't. |
| spline-midi-smooth | Before/after audio comparison. "Hear the zipper noise, now hear it gone." |
| plato-room-musician | Music theory educational content. Currently a sonification tool, not a teaching tool. |

---

## 3. Jupyter Notebook Potential

### Ready Now (with minimal effort)

| Repo | Effort | What Works |
|------|--------|-----------|
| **holonomy-harmony** | 🟢 Low | Pure Python, no external deps, built-in progressions, rich data structures. Can run `%matplotlib inline` and plot holonomy paths immediately. |
| **counterpoint-engine** | 🟢 Low | Clear API, SAT/UNSAT is visual by nature, trivial to plot piano rolls from voice data. Dependencies are other repos in this suite. |
| **groove-analyzer** | 🟢 Low | Already has `plot_deadband_funnel()` and `plot_groove_comparison()`. Built-in genre examples with .mid files. Matplotlib-native. |

### Needs Work

| Repo | Effort | What's Needed |
|------|--------|--------------|
| **constraint-theory-core** | 🟡 Medium | Needs visualization helpers. The Metronome consensus simulation would make a great animated notebook but needs `matplotlib.animation`. |
| **spline-midi-smooth** | 🟡 Medium | Needs a "demo notebook" showing before/after curves with audio. The API is ready, the notebook isn't. |
| **plato-room-musician** | 🔴 High | Needs SyntheticFetcher in a notebook context, plus educational framing. The tool is designed for data sonification, not teaching. |

### Recommended Notebook Stack

```
Jupyter Lab + ipywidgets + matplotlib + ipython display
  ├── ipywidgets.interact for parameter sliders
  ├── matplotlib for piano rolls, funnels, circle-of-fifths
  ├── IPython.display.Audio for MIDI → audio playback
  └── nbgrader for auto-grading (if used in formal courses)
```

---

## 4. Competing Tools — What Music Ed Platforms Offer

### Direct Competitors

| Platform | Type | Strengths | Gaps These Repos Fill |
|----------|------|-----------|----------------------|
| **music21** (MIT) | Python library | Comprehensive musicology, score parsing, MusicXML, 700+ corpus works. Industry standard. | No constraint theory, no SAT/UNSAT paradigm, no deadband/funnel metaphor, no holonomy concept. These repos offer a *mathematical depth* that music21 doesn't attempt. |
| **PyTheory** | Python library | Notes, scales, chords, synthesis. Beginner-friendly. | No counterpoint, no harmony analysis, no visualization. Very shallow compared to these repos. |
| **Musicpy** | Python DSL | Music as code, MIDI I/O, concise syntax. | No pedagogical structure, no constraint verification, no topological analysis. |
| **Tonara** | Commercial app | AI-powered practice tracking, gamification, teacher dashboards, real-time feedback. | No mathematical depth, no constraint theory, closed-source. Can't be extended or used in a Python curriculum. |
| **Soundfly** | Online courses | Structured lessons, adaptive difficulty, video content. | Not interactive in the code sense. Students watch, they don't experiment. |
| **teoria.com** | Web exercises | Ear training, scale identification, interval drills. | Drill-based, not exploratory. No connection to underlying math. |
| **musictheory.net** | Web lessons | Free, polished lessons with interactive exercises. | Beginner-level only. No counterpoint, no advanced harmony, no computational approach. |
| **Hooktheory** | Web/app | Data-driven harmony analysis, song decomposition, interactive piano roll. | Closest competitor to holonomy-harmony. But no holonomy/winding number concept, no constraint verification. |

### Unique Differentiators of This Toolkit

1. **SAT/UNSAT paradigm** — No other music tool presents rules as constraint satisfaction. This is genuinely novel pedagogy.
2. **Mathematical guarantees** — Covering radius bounds, deadband proofs, Laman rigidity. These repos don't just work; they *prove* they work.
3. **Unified constraint theory** — The same math (lattices, deadbands, rigidity) applies across timing (groove), harmony (holonomy), and voice-leading (counterpoint). No other toolkit offers this unifying perspective.
4. **Topological approach to harmony** — Holonomy and winding numbers are standard in differential geometry but completely novel in music education.

### What Commercial Platforms Have That These Don't

- **Gamification** (points, badges, streaks)
- **Adaptive learning** (difficulty adjusts to student)
- **Teacher dashboards** (track student progress)
- **Mobile apps** (iOS/Android)
- **Video lessons** (human instructors)
- **Community** (forums, sharing)
- **Ear training** (interval/chord identification)
- **Sight-reading exercises**
- **MusicXML integration** (read/write standard notation)

---

## 5. Curriculum Proposal — 12-Week Course

### Course: "Constraint Theory for Musicians" (or "The Mathematics of Musical Rules")

**Target audience:** Undergraduate music majors with basic Python, or CS students interested in music.  
**Prerequisites:** None (Python bootcamp in week 1).  
**Format:** 2× 90-min sessions/week (lecture + lab).  

| Week | Topic | Library | Lesson |
|------|-------|---------|--------|
| 1 | **Python for Musicians** | — | Python basics through music: define notes as numbers, intervals as differences, scales as lists. Jupyter setup. |
| 2 | **The Geometry of Intervals** | constraint-theory-core | Eisenstein lattice, `snap()`, covering radius. Visualize the hexagonal grid. Understand why some intervals are "closer" than others. |
| 3 | **What Is a Rule?** | counterpoint-engine | SAT/UNSAT paradigm. Define consonance as a constraint. Test intervals. Understand "prohibition = predicate." |
| 4 | **Two-Voice Counterpoint** | counterpoint-engine | Species 1: note-against-note. Generate counterpoint to a cantus firmus. Identify which rules fire at which beats. |
| 5 | **Adding Voices, Building Rigidity** | counterpoint-engine | Multi-voice counterpoint. Laman graphs: "every voice is load-bearing." Remove a constraint, watch a voice drift. |
| 6 | **How Groove Works** | groove-analyzer | Microtiming extraction. Fit a deadband. Understand EDM vs. Jazz pockets. Visualize funnels. |
| 7 | **Ensemble Convergence** | constraint-theory-core + groove-analyzer | Deadband funnels in action. The Metronome: 5 agents converging to one tempo. Decay rate as "how fast do we lock in?" |
| 8 | **Midterm Project** | All so far | Students compose a 16-bar piece using counterpoint rules, analyze its groove, and present findings. |
| 9 | **How Far Did We Wander?** | holonomy-harmony | Circle of fifths as a topological space. Holonomy = "did we get home?" Pachelbel vs. Giant Steps. Stability scores. |
| 10 | **Modulation Detection** | holonomy-harmony | When holonomy ≠ 0, you've modulated. Analyze real songs. Build tonal graphs. Detect modal interchange. |
| 11 | **Smooth Curves, Smooth Music** | spline-midi-smooth | Zipper noise. Linear vs. cubic vs. B-spline. Velocity curves. Deadband guarantees. "The math of musical smoothness." |
| 12 | **Sonification & Final Project** | plato-room-musician + all | PLATO room mapping as creative exercise. Final project: students build an interactive lesson using any combination of tools. |

### Assessment Strategy

| Component | Weight | Description |
|-----------|--------|-------------|
| Weekly notebooks | 40% | Completed Jupyter notebooks with code + written reflections |
| Midterm project | 20% | Compose + analyze piece using constraint tools |
| Final project | 30% | Build an interactive lesson module |
| Participation | 10% | Code reviews, peer feedback |

---

## 6. Top 10 Feature Requests (Education Use Case)

### Ranked by Impact

| # | Feature | For Which Repos | Effort | Impact |
|---|---------|----------------|--------|--------|
| 1 | **Audio playback in Jupyter** (`IPython.display.Audio` wrapper) | All | Low | 🔴 Transformative — turns "read about music" into "hear music" |
| 2 | **Piano roll visualization** (matplotlib) | counterpoint-engine, plato-room-musician | Medium | 🔴 Essential — standard visualization students expect |
| 3 | **Circle-of-fifths path animation** | holonomy-harmony | Medium | 🟡 High — makes holonomy viscerally intuitive |
| 4 | **Beat-level rule violation reporting** | counterpoint-engine | Low | 🟡 High — "Beat 3, voices 1-2: parallel fifth" enables self-correction |
| 5 | **Pre-built Jupyter lesson notebooks** (one per module) | All | Medium | 🟡 High — teachers need "open and teach," not "build from scratch" |
| 6 | **`ipywidgets` parameter sliders** for all user-facing functions | All | Low | 🟡 High — instant interactivity without code changes |
| 7 | **MusicXML/LilyPond export** | counterpoint-engine, holonomy-harmony | Medium | 🟡 High — lets students see standard notation, not just MIDI numbers |
| 8 | **Funnel animation** (agents converging over time) | constraint-theory-core, groove-analyzer | Medium | 🟠 Medium — powerful for intuition but not strictly necessary |
| 9 | **Difficulty/pedagogy mode** (relax rules progressively) | counterpoint-engine | Low | 🟠 Medium — enables "easy → hard" progression in exercises |
| 10 | **Ear training bridge** (play interval → identify → verify with API) | constraint-theory-core, counterpoint-engine | High | 🔵 Long-term — connects mathematical understanding to aural skills |

---

## Appendix A: Competing Platforms Quick Reference

| Platform | Free? | Python? | Counterpoint | Harmony Analysis | Visualization | Audio | Gamification |
|----------|-------|---------|-------------|-----------------|---------------|-------|-------------|
| **music21** | ✅ | ✅ | Basic | ✅ Strong | Plots (no audio) | Via MIDI | ❌ |
| **PyTheory** | ✅ | ✅ | ❌ | Basic | ❌ | Via synth | ❌ |
| **Tonara** | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Hooktheory** | Freemium | ❌ | ❌ | ✅ | ✅ Piano roll | ✅ | Partial |
| **musictheory.net** | ✅ | ❌ | ❌ | Basic | ✅ | ✅ | Partial |
| **This toolkit** | ✅ | ✅ | ✅ Novel | ✅ Novel (holonomy) | Partial (groove) | ❌ | ❌ |

## Appendix B: What music21 Offers That These Don't

music21 remains the gold standard for computational musicology:
- **Corpus access:** 700+ encoded scores (Bach, Beethoven, etc.)
- **MusicXML I/O:** Read/write standard notation
- **Musicology tools:** Roman numeral analysis, voice-leading spacing, cadence detection
- **MuseScore/Jupyter integration:** Render scores inline

**However**, music21 treats counterpoint rules as *checkable properties*, not *constraint predicates*. It tells you a rule was broken; it doesn't frame the entire exercise as SAT/UNSAT constraint satisfaction. This is a genuine philosophical difference, not just an API difference.

**Recommendation:** These repos should interoperate with music21 where possible (read music21 streams, output MusicXML) rather than compete with it.

---

*Report generated by OpenClaw education research subagent.*
