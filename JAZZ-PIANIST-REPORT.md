# Jazz Pianist Report: Arrangement Pipeline Evaluation

**Date:** 2026-05-22  
**Evaluator:** Jazz pianist/arranger persona  
**Repos evaluated:** holonomy-harmony, counterpoint-engine, groove-analyzer, spline-midi-smooth, constraint-theory-core, plato-room-musician

---

## 1. What I Tried — Step-by-Step Composition Diary

### Goal
Compose a full 5-piece jazz combo arrangement (piano, bass, drums, sax, trumpet) of **Blue Bossa** (Kenny Dorham) in C minor, using the six repos in the workspace.

### Step 1: Harmonic Analysis with holonomy-harmony
- Parsed Blue Bossa's 14-bar form as Roman numerals in C minor: `i i iv iv iiø V7 I I VI VII7 iiø V7 i i`
- Called `analyze_progression()` — got holonomy=0, winding=0.0, type=CHROMATIC_MEDIANT, stability=0.7
- **Result:** Holonomy=0 confirms Blue Bossa is tonally stable (returns home). The stability score of 0.7 correctly reflects the brief major-mode excursion (bars 7-10).
- **Verdict:** The holonomy/winding/stability metrics are intellectually interesting but don't directly help me write an arrangement. They're analytical, not generative.

### Step 2: Walking Bass with counterpoint-engine
- Fed root notes of the progression as a cantus firmus to `CounterpointGenerator`
- It generated a species counterpoint line (1 note per bar) — academically correct but musically useless
- **Had to write a manual walking bass generator** that produces 4 quarter-note walks per bar using chord tones, passing tones, and chromatic approaches
- **Verdict:** counterpoint-engine is built for Palestrina-style species counterpoint, not jazz. The constraint satisfaction approach (SAT/UNSAT) is conceptually interesting but the rules are classical, not jazzy.

### Step 3: Swing Feel with groove-analyzer
- Jazz genre profile correctly specifies ε=40ms, swing_factor=0.75, bpm=120
- `synthesize_groove("Jazz")` generates its own drum patterns — **cannot apply swing to existing MIDI**
- I had to implement swing_tick() manually in the arrangement code
- **Verdict:** Great for *analyzing* grooves. Can't *apply* a groove to your music. That's the opposite of what an arranger needs.

### Step 4: Dynamic Smoothing with spline-midi-smooth
- `smooth_velocity_curve()` crashed with `ValueError: x coordinates must be strictly increasing` on any multi-track MIDI (simultaneous notes at same tick)
- Had to extract velocity data manually and use `cubic_hermite()` directly
- **Verdict:** The spline kernels themselves work well. The MIDI processing wrappers break on real-world multi-track files. No way to write smoothed data back into the original file structure.

### Step 5: Building the Full MIDI
- Everything had to be assembled manually with `mido` (which isn't even a dependency of most of these repos)
- Wrote 5 tracks: piano (comping), bass (walking), drums (ride pattern), sax (melody), trumpet (harmonized melody)
- Chord voicings: manually defined drop-2 rootless voicings — **no library generates these**
- Comping rhythms: manually coded 4 common jazz patterns — **no library provides these**
- **Verdict:** 90% of the arrangement was manual work. The repos provided ~10% of the value.

### Artifacts Produced
- `blue_bossa_arrangement.py` — Full composition script
- `blue_bossa_arrangement.mid` — 14-bar arrangement, 5 tracks, 6 MIDI tracks

---

## 2. What Worked — What Felt Natural

| Feature | Repo | How it helped |
|---------|------|---------------|
| Holonomy analysis | holonomy-harmony | Quickly confirmed Blue Bossa's tonal stability — would be useful for repertoire analysis |
| Built-in progressions | holonomy-harmony | 20 famous progressions with auto-analysis; great for teaching |
| Tonal graph | holonomy-harmony | Transition probability between chords — interesting for generative work |
| Constraint SAT/UNSAT | counterpoint-engine | The predicate model is clean and extensible |
| Genre profiles | groove-analyzer | Jazz ε=40ms, swing=0.75 — correct parameters, good reference |
| Spline kernels | spline-midi-smooth | cubic_hermite, catmull_rom, bspline all work as advertised |
| Drum synthesis | groove-analyzer | `synthesize_groove("Jazz")` produces a usable ride/hihat/kick pattern |

The *mathematical foundations* are solid. Holonomy as a measure of tonal wandering, deadband as a model of groove pocket, Laman graphs for voice independence — these are genuine theoretical contributions. The problem is the gap between theory and the daily work of a jazz arranger.

---

## 3. What Was Painful — Specific API Pain Points

### holonomy-harmony
- **Roman numeral parser ignores chord quality extensions.** `V7`, `V7alt`, `iiø`, `imaj7` all parse to the same root. Jazz lives in the extensions — a G7 and a G7alt are *completely different* harmonically.
- **No chord symbol input.** Real jazz charts use `Cm7 | F7 | Bbmaj7` not Roman numerals. There's no `analyze_progression(["Cm7", "F7", "Bbmaj7"])` entry point.
- **Purely analytical, not generative.** Can tell you *about* a progression but can't generate voicings, guide tones, or voice leading from it.

### counterpoint-engine
- **1:1 species only.** Walking bass is 4 notes per chord change. Comping can be any number. Jazz is not 1:1.
- **No harmonic context.** The generator knows about scales but not about chord changes, ii-V-I resolution tendencies, or tritone substitutions.
- **Classical rules only.** No parallel fifths? Jazz pianists *love* parallel fifths in open voicings. The SAT/UNSAT rules are counterpoint prohibitions, not jazz conventions.
- **No "jazz species".** Jazz counterpoint has its own rules: guide tone lines, 3-7 voice leading, chromatic approach notes, enclosures.

### groove-analyzer
- **Analysis-only for existing MIDI.** `extract_microtiming()` reads files. `synthesize_groove()` writes its own patterns. But there's no `apply_swing(notes, factor=0.67)` or `humanize_timing(midi, epsilon_ms=40)`.
- **No rhythmic pattern library.** Jazz comping uses specific patterns (Charleston, syncopated, anticipation). No catalog.
- **Swing is a float, not a feel.** swing_factor=0.75 doesn't capture that swing varies by tempo (faster = straighter), style (Basie vs. Tyner), or section (soloist vs. ensemble).

### spline-midi-smooth
- **Crashes on simultaneous notes.** `smooth_velocity_curve()` fails on any multi-track MIDI where two notes share a tick. This is the common case, not the edge case.
- **No velocity presets.** Jazz dynamics have characteristic shapes: forte-piano (loud attack, immediate drop), crescendo to climax, ghost notes. None of these are available.
- **No write-back.** You can smooth a velocity curve but can't easily update the original MIDI with the smoothed values while preserving all other MIDI data.

### Cross-cutting issues
- **No shared music data model.** Each repo has its own representation. `Chord` in holonomy-harmony ≠ chord concept in counterpoint-engine. No shared `Note`, `Voice`, `Score` types.
- **No chord progression object.** Blue Bossa's 14 bars of changes had to be manually encoded as a list of dicts. No `Progression` class with `.voicing_for_instrument()`, `.guide_tones()`, `.voice_lead()`.
- **No MIDI rendering pipeline.** Each repo either doesn't render MIDI or has its own bespoke output. No unified `render_to_midi(score, instruments)`.

---

## 4. Jazz Features Missing — Ranked by Importance

### Critical (Can't arrange without these)

1. **Chord voicing generation** — Drop-2, rootless, quartal, shell, McCoy Tyner, Bill Evans voicings. The single most important thing a jazz arranger needs. Currently: nothing.

2. **Guide tone extraction** — The 3rd and 7th of every chord, automatically connected into smooth voice-leading lines. These are the "skeleton" of any jazz arrangement. Currently: nothing.

3. **Voice leading** — Given two chords, compute the minimal-movement piano voicing. Jazz arranging is 90% voice leading. Currently: nothing.

4. **Walking bass generator** — 4 quarter-notes per bar over chord changes, using chord tones, passing tones, chromatic approaches, and enclosures. Currently: counterpoint-engine does 1:1 species only.

5. **Swing application** — Apply a swing ratio to existing MIDI timing. Not just analyze it. Currently: groove-analyzer can analyze but not apply.

### Important (Would significantly improve the workflow)

6. **Comping rhythm library** — Catalog of common jazz piano comping patterns: Charleston, syncopated, montuno, Freddie Green, Red Garland, etc.

7. **Jazz chord symbol parsing** — Accept `Cm7`, `F7#11`, `Bbmaj7`, `G7alt`, `Dm7b5`, `E7#9` and produce structured chord objects with extensions.

8. **Jazz scale recommendation** — Given a chord, suggest appropriate scales: Dorian for m7, Mixolydian for 7, altered for 7alt, etc.

9. **Drum pattern library** — Ride patterns for swing, bossa, samba, waltz, ballad with brushes, etc.

10. **Section/form support** — A-B-A-C form, head-solos-head structure, intros and endings.

### Nice to Have

11. **Transposition** — Move entire arrangement to a new key, adjusting voicings for range.

12. **Extract arrangement from audio/MIDI** — Reverse-engineer voicings from a recording.

13. **Style templates** — "Make it sound like Bill Evans" / "Make it sound like Art Blakey"

14. **Improvisation generation** — Generate jazz solos over changes with motivic development.

15. **Lead sheet rendering** — Output a printable lead sheet (chords + melody) from the data.

---

## 5. Competitor Comparison

### music21 (MIT)
**What it does:** The 800-pound gorilla of Python music theory. Full musicology toolkit with Roman numeral analysis, voice leading, chord labeling, and notation rendering (via LilyPond/MuseScore).  
**Jazz strengths:** Excellent Roman numeral parser, comprehensive chord quality support (including jazz chords), voice-leading utilities in `music21.voiceLeading`, scale/mode libraries.  
**Jazz weaknesses:** Academic focus — designed for musicologists, not arrangers. No voicing generation, no swing, no groove, no walking bass. Rendering to MIDI requires manual work.  
**Does it better than our repos:** Chord parsing, voice leading analysis, notation rendering, scale theory, corpus analysis (has built-in jazz corpus).  
**What our repos do better:** Holonomy analysis (unique), groove deadband theory (unique), constraint-theory foundations (unique).

### Mingus (Python)
**What it does:** Lightweight music theory library with note/chord/scale/container abstractions plus MIDI I/O via mingus.midi.  
**Jazz strengths:** Has jazz chord symbols, jazz scales (bebop, altered, diminished whole-half), and a straightforward Note/Track/MidiFile pipeline.  
**Jazz weaknesses:** Abandoned since ~2012. Python 2-era code. No voicing generation, no swing, no walking bass.  
**Does it better than our repos:** Chord symbol parsing, scale libraries, basic MIDI rendering, container data model.  
**What our repos do better:** Everything mathematical. Mingus is utility-level; our repos are research-level.

### Improviser (Python)
**What it does:** Jazz improvisation engine using Markov chains over chord-tone targeting.  
**Jazz strengths:** Actually generates jazz lines over changes. Understands chord tones, approach notes, enclosures.  
**Jazz weaknesses:** Single-purpose (solo generation only), no arranging capability, no voicing, no comping.  
**Does it better:** Jazz line generation, motivic development, chord-tone awareness.

### Foxdot / TidalCycles (Python / Haskell)
**What it does:** Live coding music environments. Pattern-based music generation with swing, humanization, and real-time control.  
**Jazz strengths:** Excellent swing/groove handling, pattern transformation, live performance workflow.  
**Jazz weaknesses:** Not theory-aware — doesn't know about chords, voice leading, or chord-scale relationships.  
**Does it better:** Swing timing, rhythmic pattern manipulation, live workflow, humanization.

### PianO支架 / JZZ (JavaScript, Python bindings)
**MIDI manipulation libraries.** Good for reading/writing MIDI but no music theory.

### Key insight
**No Python library generates jazz piano voicings.** This is the biggest gap in the ecosystem. Every jazz pianist I know would use a tool that could take a lead sheet and generate idiomatic Bill Evans / McCoy Tyner / Red Garland voicings. Nobody does this.

---

## 6. Score: 4/10

### Would I use these for real arranging work?

**holonomy-harmony: 5/10** — The only repo I'd actually use in practice, and only for repertoire analysis. "How far does Giant Steps wander from home?" is a genuinely useful analytical question. But I can't *arrange* with it.

**counterpoint-engine: 2/10** — Beautiful math (Laman graphs for voice independence is clever) but the wrong domain. Species counterpoint rules are the opposite of jazz conventions. The SAT/UNSAT framework could be repurposed for jazz, but it would need jazz rules.

**groove-analyzer: 3/10** — The deadband theory is interesting and the genre profiles are correct. But I need to *apply* grooves, not just analyze them. The drum synthesis is a nice demo but too basic for real use.

**spline-midi-smooth: 6/10** — The most practically useful. Spline smoothing of MIDI automation is a real production need. The kernels are solid. Fix the simultaneous-note crash and add velocity presets and this becomes a 7 or 8.

**Overall pipeline: 4/10** — These repos are individually interesting research projects but they don't compose into a workflow. I spent 90% of my time writing manual code (voicings, walking bass, comping rhythms, swing, MIDI assembly) that a proper jazz arranging toolkit should provide.

---

## 7. Top 5 Feature Requests with API Sketches

### 1. Chord Voicing Generator

```python
from jazz_voicings import VoicingGenerator, VoicingStyle

vg = VoicingGenerator()

# Generate idiomatic voicings for a progression
voicings = vg.voice_progression(
    changes=["Cm7", "F7", "Bbmaj7"],
    style=VoicingStyle.ROOTLESS_DROP2,
    voice_lead=True,  # minimize movement between chords
    instrument="piano",
    register="mid",  # low, mid, high
)
# voicings = [
#   Voicing(chord="Cm7", notes=[60, 63, 67, 70], bass=48),
#   Voicing(chord="F7",  notes=[60, 62, 65, 69], bass=53),  # smooth voice leading!
#   Voicing(chord="Bbmaj7", notes=[60, 64, 67, 70], bass=58),
# ]

# Also: guide tones
guides = vg.guide_tones(["Cm7", "F7", "Bbmaj7"])
# guides = [
#   [(63, 70), (65, 71)],  # Eb+Bb → F+B
# ]

# Voicing styles: ROOTLESS_DROP2, SHELL, QUARTAL, 
#                BILL_EVANS, MCCOY_TYNER, RED_GARLAND
```

### 2. Walking Bass Generator

```python
from jazz_bass import WalkingBass

wb = WalkingBass(
    changes=["Cm7", "Fm7", "Dm7b5", "G7", "Cmaj7"],
    beats_per_chord=4,
    register=(36, 55),  # C2-G3
    style="walking",  # walking, two_feel, latin, pedal
)

bass_line = wb.generate(seed=42)
# bass_line = [
#   Note(pitch=36, beat=0.0, duration=1.0, velocity=72),  # C (root)
#   Note(pitch=41, beat=1.0, duration=1.0, velocity=68),  # F (chord tone)
#   Note(pitch=43, beat=2.0, duration=1.0, velocity=70),  # G (5th)
#   Note(pitch=42, beat=3.0, duration=1.0, velocity=74),  # F# (chromatic approach)
#   ...
# ]

# Uses: chord tones, passing tones, chromatic approaches, enclosures
wb.export_midi("bass_track.mid", channel=1, program=32)
```

### 3. Swing/Humanize Transformer

```python
from groove_transform import apply_swing, humanize

# Apply swing to existing MIDI
apply_swing(
    "arrangement.mid",
    "arrangement_swung.mid",
    ratio=0.67,           # triplet swing
    scope="all",          # or ["piano", "bass"]
    exclude_channels=[9], # don't swing the drums (already swung)
)

# Humanize timing and velocity
humanize(
    "arrangement_swung.mid",
    "arrangement_human.mid",
    timing_epsilon_ms=40,     # jazz pocket width
    velocity_variation=10,    # ±10 velocity
    preserve_track="drums",   # keep drums exact
    strategy="gaussian",      # gaussian, triangular, laplace
)
```

### 4. Jazz Chord Symbol Parser

```python
from jazz_harmony import parse_chord_symbol, ChordChanges

# Parse jazz chord symbols
chord = parse_chord_symbol("G7alt")
# Chord(root=7, quality="7alt", 
#        extensions=[b9, #9, b5, #5],
#        guide_tones=[10, 1],  # Bb, Db (b7, b3 implied)
#        scales=["altered", "diminished_whole_tone"])

# Parse a lead sheet
changes = ChordChanges.from_symbols(
    ["Cm7", "Cm7", "Fm7", "Fm7", 
     "Dm7b5", "G7alt", "Cmaj7", "Cmaj7"],
    time_signature=(4, 4),
    beats_per_chord=4,
)

# Analyze
print(changes.key_centers)       # [Cm, Cm, Cm, Cm, Cm, Cm, C, C]
print(changes.secondary_dominants)  # [G7alt]
print(changes.tritone_substitutions) # none in Blue Bossa
print(changes.transpose(target="Bb")) # Transpose to Bb
```

### 5. Comping Rhythm Library + Generator

```python
from jazz_comping import CompingRhythms, comp_over_changes

# Built-in comping patterns
patterns = CompingRhythms.catalog()
# ["charleston", "syncopated", "freddie_green", "red_garland", 
#  "bill_evans_ballad", "wynton_kelly", "montuno", "block_chord"]

# Generate comping over a progression
comping = comp_over_changes(
    changes=["Cm7", "Fm7", "Dm7b5", "G7", "Cmaj7"],
    voicings=voicings,  # from VoicingGenerator
    rhythm="charleston",
    bars_per_chord=2,
    variation=0.3,       # 30% rhythmic variation
    anticipations=True,  # allow beat 4 anticipation of next chord
)

comping.export_midi("comping.mid", channel=0, program=1)
```

---

## Appendix: What a Jazz Arranger Actually Needs

When I sit down to write an arrangement, here's my mental process:

1. **Get the changes.** Read the lead sheet. Parse chord symbols.
2. **Write guide tone lines.** Connect the 3rds and 7ths smoothly — these are the DNA of the arrangement.
3. **Voice the chords.** Piano: rootless drop-2 or quartal. Horns: close harmony or drop-2. Bass: root + 5th on strong beats.
4. **Write the bass line.** Walking, two-feel, or Latin depending on style.
5. **Add comping rhythms.** Syncopated patterns that complement the melody/soloist.
6. **Notate the drums.** Ride pattern, fills, transitions between sections.
7. **Apply dynamics.** Crescendos, accents, ghost notes, shaping phrases.
8. **Apply feel.** Swing, straight, Latin groove, ballad rubato.

Of these 8 steps, the current repos help with:
- Step 1: Partially (holonomy-harmony can parse Roman numerals but not chord symbols)
- Step 7: Partially (spline-midi-smooth can smooth curves but crashes on real files)

Steps 2-6 and 8: **No support at all.**

The mathematical innovations (holonomy, deadband funnels, Laman rigidity) are genuine contributions to music theory. But they answer questions that jazz musicians don't typically ask. The questions jazz musicians *do* ask — "what's the smoothest voice leading from Cm7 to F7?" — remain unanswered.
