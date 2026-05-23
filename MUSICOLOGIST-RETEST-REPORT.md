# 🎼 Musicologist Re-Test Report — Round 8

**Date:** 2026-05-22  
**Tester:** Musicologist subagent  
**Ecosystem:** Constraint-theory music repos (5 repos)

---

## 1. Updated Scores

| Repo | Previous | Current | Δ | Verdict |
|------|----------|---------|---|---------|
| **counterpoint-engine** | 5.5/10 | **7.0/10** | +1.5 | Real improvement, species now differentiated |
| **groove-analyzer** | 7.5/10 | **7.5/10** | — | Stable; round-trip works perfectly |
| **holonomy-harmony** | 6.8/10 | **7.5/10** | +0.7 | README code works, parse_roman handles complex numerals |
| **jazz-voicing-engine** | NEW | **7.5/10** | — | Surprisingly solid for a new repo |
| **style_extractor** | NEW | **6.0/10** | — | DNA concept works but similarity metric is nearly degenerate |

---

## 2. Species Assessment (counterpoint-engine)

### Species 1 (Note-against-note): ✅ Good
- **All constraints satisfied** (29/29)
- Intervals: octave, M6th, m3rd, P5th — proper mix of consonances
- CP stays in a reasonable range (C3–E4)
- No parallel fifths/octaves detected
- **Musical quality: 7/10** — sounds like actual species 1 counterpoint

### Species 2 (Two-against-one): ✅ Decent
- **2× notes per CF note** confirmed (18 CP notes vs 9 CF)
- Strong beats are consonant (octaves, M3rds, m3rds, P5ths)
- Weak beats are stepwise (1-2 semitone moves) — correct passing tones
- **Musical quality: 6/10** — the strong beats tend to cluster at unisons/octaves a bit much. More interval variety on strong beats would help.

### Species 3 (Four-against-one): ✅ Good
- **4× notes per CF note** confirmed (36 CP notes vs 9 CF)
- Strong beats are consonant, subdivisions are mostly stepwise (0-2 semitone moves)
- Some repeated pitches in subdivisions (e.g., [50,50,50,48]) — could use more variety
- **Musical quality: 6/10** — the stepwise motion is correct but the line sometimes stagnates with repeated notes

### Species 4 (Suspensions): ✅ Real Suspensions Now
- **2 actual suspensions detected** at beats 2 and 5
- Pattern: consonant → dissonant → resolve down — this is correct suspension technique
- Beat 2: CP=74 vs CF=64 (interval 10, dissonant), resolves down by 2 semitones
- Beat 5: CP=59 vs CF=65 (interval 6, dissonant), resolves down by 2 semitones
- CP spans a wide range (57–79, 22 semitones) — nice melodic arc
- **Musical quality: 6.5/10** — real suspensions! The preparation-suspension-resolution chain is musically correct. Still a bit jumpy between suspensions.

### Species 5 (Florid): ✅ Works
- **Variable note count** (13 notes for 9 CF notes) — mix of 1-note and 2-note subdivisions
- Strong beats are consonant
- **Musical quality: 6/10** — correctly mixes species 1 and 2 patterns, no 4-note subdivisions in this output

### Species Differentiation: ✅ Confirmed
All 5 species produce **structurally distinct** output:
- Sp1: 9 notes, Sp2: 18 notes, Sp3: 36 notes, Sp4: 9 notes (with suspensions), Sp5: 13 notes

---

## 3. Groove Analyzer Assessment

### Round-trip Test (synthesize → analyze → verify genre): ✅ Perfect
| Genre | Genre Match | Coverage | Coherence |
|-------|-------------|----------|-----------|
| Jazz | Jazz ✅ | 92.3% | 0.972 |
| Funk | Funk ✅ | 96.1% | 0.889 |
| Hip-hop | Hip-hop ✅ | 90.8% | 0.963 |
| EDM | EDM ✅ | 94.7% | 0.995 |
| Latin | Latin ✅ | 91.7% | 0.970 |

**All 5 genres round-trip correctly.** The deadband theory works — each genre's synthesized groove is identified back to itself.

### API Issue (minor)
`prove_groove_is_deadband()` returns a `dict`, not a typed object. The dict has useful keys (`coverage`, `genre_match`, `genre_coherence`) but lacks a proper dataclass. The docstring reference to `DeadbandFit`/`EnsembleFunnel` types doesn't match runtime behavior.

### Test Suite: 11/11 passing

---

## 4. Holonomy-Harmony Assessment

### parse_roman: ✅ Handles Complex Numerals
| Input | Root | Quality | Diatonic | Notes |
|-------|------|---------|----------|-------|
| `bVII` | A# | maj | No | Correct — flattened 7th |
| `#IV` | F# | maj | No | Correct — sharpened 4th |
| `V7` | G | 7 | Yes | Correct dominant 7th |
| `V/vi` | E | maj | No | Secondary dominant to vi — correct! |
| `ii7` | D | 7 | Yes | Correct |
| `bVI` | G# | maj | No | Correct borrowed chord |
| `III` | E | min | Yes | Correct — mediant is minor in... wait, this should be iii not III. In C major, III would be E major (not diatonic). **Bug**: uppercase III is parsed as diatonic minor. Should be non-diatonic major. |

### Built-in Progressions: ✅
- **19 progressions** including Pachelbel, Giant Steps, Coltrane changes, Autumn Leaves
- All parse and analyze without errors
- Stability scores are reasonable (Pachelbel: 0.35, Blues: 0.50, Giant Steps: 0.38)

### README Code: ✅ Works as documented

### Test Suite: 94/94 passing

---

## 5. Jazz Voicing Engine Assessment (NEW)

### Chord Parsing: ✅ Strong
- `Cm7` → C, min7, [0,3,7,10] ✅
- `G7alt` → G, 7alt, [3,5,7,11] ✅ (altered 5th and 9th implied)
- `F#maj7#11` → F#, maj7, alterations=('#11',), [0,1,5,6,10] ✅
- `Dm7b5` → D, m7b5, [0,2,5,8] ✅
- `Bb7#9` → A#, 7, alterations=('#9',), [1,2,5,8,10] ✅ (Hendrix chord!)

### Voicing Styles: ✅ All Working
- **Drop-2**: Correctly drops 2nd voice an octave, nice spread
- **Rootless**: Omits root, plays 3-7+extensions with bass note — authentic jazz piano style
- **Quartal**: Stacks perfect 4ths — McCoy Tyner vibes
- **Shell**: 3rd + 7th only — Freddie Green style
- **Guide tones**: Same as shell (appropriate)

### Voice Leading: ✅ Smooth
- ii-V-I (Dm7→G7→Cmaj7): voicings show minimal semitone movement between chords
- Algorithm prefers nearest chord tones from previous voicing

### Walking Bass: ✅ Idiomatic
- 16 notes over 4 bars with 7 chords
- Starts on root (A=45)
- Uses chord tones, 5ths, and chromatic approach notes on beat 4
- Stays in bass register (28-48 MIDI range)
- Different player styles (Ray Brown, Paul Chambers, Ron Carter)

### Comping: ✅ Stylish
- 6 pianist styles (Bill Evans, Herbie Hancock, Freddie Green, etc.)
- Rhythmic patterns match style descriptions
- Velocity variation within style-appropriate ranges
- Voice-led voicings applied to rhythm patterns

### Test Suite: 26/26 passing

### Jazz Musician Verdict: **7.5/10**
This is genuinely useful. A jazz pianist could use the voicing generator to explore drop-2/rootless/quartal options. The walking bass generates idiomatic lines. The comping styles capture real pianist personalities. The main gaps: no tritone substitution awareness, limited upper structure triads, no root movement patterns (e.g., "Autumn Leaves" bass line should outline the cycle of 4ths more explicitly).

---

## 6. Style Extractor Assessment (NEW)

### DNA Concept: ✅ Works
Extracts meaningful features from MIDI:
- **Melodic**: interval distribution, range (15 semitones for drums), step-vs-leap ratio
- **Rhythmic**: syncopation rate (Jazz: 0.74, Funk: 0.37), duration distribution, density
- **Harmonic**: consonance rate, dissonance rate
- **Timing**: swing factor, timing precision
- **Register**: pitch center, pitch range

### JSON Roundtrip: ✅ Perfect
`to_json()` → `from_json()` preserves all fields, including tuple conversion.

### Similarity Metric: ⚠️ Nearly Degenerate
- Jazz vs Funk: **0.9896**
- Jazz vs EDM: **0.9895**
- Funk vs EDM: **1.0000** (!)
- Jazz vs Jazz: 1.0000 ✅

**The cosine similarity over numeric features cannot distinguish genres.** Funk and EDM are scored as identical despite being musically very different. This is because the numeric vector is dominated by register/range features (pitch_center, pitch_range) which are similar across drum patterns. The interval and rhythm features get drowned out.

### Root Cause
The `_numeric_vector()` puts features on wildly different scales. `melodic_range_semitones` (15) and `pitch_center` (55) dominate the cosine similarity, while `syncopation_rate` (0.37-0.74) and `swing_factor` (0-0.43) contribute negligibly.

### Style Musician Verdict: **6.0/10**
The DNA concept is sound and the feature extraction is solid. But the comparison/similarity metric needs normalization or feature weighting to be useful. Currently can't tell jazz from EDM.

---

## 7. Overall Ecosystem Score

### If a musicologist encountered this on GitHub: **7.0/10**

**Strengths:**
1. **Theoretical coherence** — The ecosystem has a clear thesis: music = constraint satisfaction = Laman rigidity / deadband funnels / holonomy. Each repo proves a specific claim.
2. **All test suites pass** — 109 + 11 + 94 + 26 = **240 tests, all green**. That's impressive.
3. **Counterpoint actually works** — Species 1-5 all generate valid, differentiated output. Species 4 has real suspensions.
4. **Jazz voicing is production-quality** — Chord parsing, voicing styles, walking bass, and comping are genuinely useful for musicians.
5. **Groove round-trip is perfect** — 5/5 genres correctly identified after synthesis.
6. **19 built-in progressions** in holonomy-harmony, from Pachelbel to Coltrane.

**Weaknesses:**
1. **Style extractor similarity is broken** — Cosine similarity can't distinguish genres (Funk ≈ EDM = 1.0).
2. **Counterpoint range issues** — Species 4 sometimes jumps 20+ semitones between notes (79→74→74→72→59). Species 2 strong beats cluster around unisons.
3. **parse_roman bug** — Uppercase `III` in major is treated as diatonic minor; should be non-diatonic major.
4. **No MIDI output from walking bass** — The bass generator returns (pitch, time) tuples but doesn't write MIDI files directly.
5. **Groove API inconsistency** — `prove_groove_is_deadband` returns dict, not the typed object suggested by imports.

---

## 8. Top Remaining Gaps (Priority Order)

1. **🔴 Style extractor: fix similarity metric** — Normalize features or use weighted cosine. Currently useless for comparison.
2. **🟡 Counterpoint: constrain melodic leaps in Species 4** — The jump from 79 to 59 is a 20-semitone leap that no singer could execute. Add max_leap constraints within species 4 framework.
3. **🟡 holonomy-harmony: fix III parsing** — Uppercase Roman numerals should default to major quality regardless of mode, for non-diatonic chords.
4. **🟡 Jazz voicing: add tritone substitution and upper structure triads** — These are essential for jazz beyond basic ii-V-I.
5. **🟢 Groove analyzer: type the return of prove_groove_is_deadband** — Return a proper DeadbandResult dataclass instead of dict.
6. **🟢 Counterpoint Species 2: improve strong-beat interval variety** — Too many octaves/unisons on strong beats.

---

*Report generated by musicologist subagent, round 8 of ecosystem testing.*
