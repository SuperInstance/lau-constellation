# Classical Retest Report: Counterpoint Engine

**Date:** 2026-05-22  
**Cantus Firmus:** C4-D4-E4-F4-G4-F4-E4-D4-C4 (MIDI: 60,62,64,65,67,65,64,62,60)  
**Previous Score:** 3.5/10  

---

## Updated Score: 5.5/10

**+2.0 improvement** — Species 2-5 now generate structurally distinct output instead of all collapsing to Species 1. The engine is now a legitimate multi-species generator, but significant musical quality issues remain.

---

## What Improved

### All 5 Species Produce Different Output
| Species | CP Length | Feasible | Unique? |
|---------|-----------|----------|---------|
| 1 (Note-against-note) | 9 | ✅ | ✅ |
| 2 (Two-against-one) | 18 | ✅ | ✅ |
| 3 (Four-against-one) | 36 | ✅ | ✅ |
| 4 (Suspensions) | 9 | ✅ | ✅ (but see below) |
| 5 (Florid) | 13 | ✅ | ✅ |

**This was the #1 complaint from the previous review and it's fixed.** Each species now produces structurally appropriate output: 1:1, 2:1, 4:1, 1:1 with dissonance, and mixed subdivisions respectively.

### Structural Correctness
- **Species 1:** All 9 intervals consonant. ✅
- **Species 2:** All strong-beat intervals consonant. Weak beats are stepwise passing tones (1-2 semitones from strong). ✅
- **Species 3:** 100% stepwise transitions (35/35). Strong beats all consonant. ✅
- **Species 4:** 4 dissonances detected, all properly prepared as suspensions (preceded by consonance). ✅
- **Species 5:** Subdivision pattern `[1, 1, 4, 1, 2, 1, 1, 1, 1]` — mixes species 1/2/3 patterns. ✅

### 4-Voice Generation Works
Successfully generated 4-voice counterpoint (CF + 3 voices) with all 282/282 constraints satisfied and no parallel fifths/octaves between any voice pair.

---

## Musical Quality Assessment

### Species 1: 6/10 — Decent
- Voice leading is mostly smooth (5/8 transitions are steps of 1-2 semitones)
- One 5-semitone leap (48→53) at beat 1 is acceptable but not ideal
- Good interval variety: 6 different interval classes used across 9 beats
- Feels like actual first-species counterpoint

### Species 2: 5/10 — Structurally Correct, Musically Meh
- Does produce 2:1 counterpoint with consonant strong beats and stepwise weak beats
- Weak beats function as passing tones (all within 1-2 semitones of strong)
- BUT: the counterpoint hovers in a very narrow range (48-53, just 5 semitones)
- Lacks melodic contour — sounds more like an exercise than music
- Run-to-run variety is good (5 unique results in 5 runs)

### Species 3: 4/10 — Mechanically Stepwise
- 100% stepwise — which is *too* stepwise. Real third-species uses leaps occasionally for musical interest
- 36 notes crammed into 5 semitones of range (48-56)
- Sounds like a scale exercise, not melodic counterpoint
- No rhythmic variety within the four-note groups — all equal subdivisions
- The 4:1 ratio is correct but the musical result is monotonous

### Species 4: 2/10 — Busted (Pedal Point, Not Counterpoint)
- **Critical flaw:** The counterpoint is literally one pitch repeated 9 times: `[48, 48, 48, 48, 48, 48, 48, 48, 48]`
- This is a pedal point, not suspension counterpoint
- The "suspensions" are accidental — they happen because the CF moves while CP stays still
- There's no actual syncopation (tied notes across beat boundaries)
- No actual suspension figures (4-3, 7-6, 9-8 patterns)
- No melodic motion whatsoever — the CP voice has zero melodic interest
- The backtracking solver found the laziest possible solution and stopped

### Species 5: 5/10 — Reasonable Mix
- Subdivides appropriately: `[1, 1, 4, 1, 2, 1, 1, 1, 1]`
- 13 notes total vs 9 in CF — correct for a mix
- First and last beats are species-1 style (standard practice) ✅
- The actual melodic content is more varied than species 3
- Still quite limited range

### 4-Voice: 4/10 — Works But No Fugue
- Generates 4 voices that satisfy all pairwise constraints
- Voice 3 (soprano) is suspiciously similar to Voice 0 (CF) — it goes `[64, 65, 67, 65, 64, 62, 64, 65, 67]`, which is basically the CF transposed up a 4th and rearranged
- Not a fugue — there's no subject/answer structure, no stretto, no episode
- The sequential generation approach (voice-by-voice) prevents true fugue architecture
- More like "4-part harmony" than "fugue exposition"

---

## What's Still Missing

### Critical Issues
1. **Species 4 is broken** — produces a single repeated pitch instead of actual suspension chains with melodic motion. Needs: forced melodic variety, explicit suspension patterns (4-3, 7-6, 9-8), tie notation across beats.

2. **No rhythmic differentiation** — Species 3/5 subdivide mechanically (equal note values). Real third-species uses varied rhythmic patterns within the 4-note group.

3. **Voice range is too narrow** — The counterpoint hovers in a 5-6 semitone range. Real counterpoint spans an octave or more. The `VoiceRange` defaults allow this but the solver gravitates to minimum movement.

4. **No fugue architecture** — `generate_n_voices` does sequential voice-by-voice generation, not fugal structure (subject entry, answer, countersubject, episode, stretto).

### Medium Issues
5. **No interval preference** — Too many unisons in the output. Real counterpoint favors imperfect consonances (3rds, 6ths) over perfect consonances (5ths, octaves) for fuller texture.

6. **No melodic climax** — The generated melodies have no arch shape or high point. Real counterpoint has a clear melodic peak.

7. **Deterministic-ish** — Species 1 always produces the same result (no randomness). Species 2/3 are randomized but within very narrow bands.

8. **No mode support** — CF is in C major but there's no awareness of mode-specific rules (e.g., raised leading tone in minor).

### Nice-to-Haves
9. No text underlay / lyric support
10. No MusicXML export
11. No MIDI playback (just file export)
12. No visualization (staff notation)

---

## Remaining Feature Requests (Priority Order)

1. **Fix Species 4** — Force melodic motion, implement real suspension chains with preparation → dissonance → resolution, add tie/across-beat notation
2. **Melodic contour** — Add a "climax" constraint that encourages a single highest point
3. **Interval preference weighting** — Prefer imperfect consonances (3rds/6ths) over perfect ones
4. **Voice range enforcement** — Counterpoint should span at least an octave
5. **Fugue architecture** — Subject/answer/countersubject structure, not sequential voice generation
6. **Species 3 rhythmic variety** — Not just equal subdivisions; allow cambiata, skip-step patterns
7. **Minor mode support** — Harmonic/melodic minor leading tone handling
8. **MusicXML export** — For notation software integration

---

## Summary

The engine went from "all species produce identical output" to "each species produces structurally distinct, constraint-satisfying output." That's genuine progress. Species 1, 2, 3, and 5 produce recognizable (if musically limited) examples of their respective species. The 4-voice generation works mechanically.

However, **Species 4 remains fundamentally broken** — it produces a pedal point, not suspension counterpoint. And the overall musical quality is still more "textbook exercise" than "compositional tool." The voice leading is too cautious, the range too narrow, the melodic shape too flat.

**Score breakdown:**
- Structural correctness: 7/10 (species 4 drags it down)
- Musical quality: 4/10 (pedestrian but functional)
- Constraint satisfaction: 9/10 (thorough, well-implemented)
- Fugue capability: 2/10 (just multi-voice, no fugue logic)
- **Overall: 5.5/10**
