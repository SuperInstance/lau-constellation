# Stress Test Re-Test Report

**Date:** 2026-05-22  
**Scope:** All repos in `/home/phoenix/.openclaw/workspace/`  
**Context:** Re-testing after validation fixes were applied

---

## constraint-theory-core

| Test | Status | Detail |
|------|--------|--------|
| `snap(inf, 1.0)` | ✅ PASS | `ValueError: snap() argument 'x' must be finite, got inf` |
| `snap(-inf, 0)` | ✅ PASS | `ValueError: snap() argument 'x' must be finite, got -inf` |
| `snap('a', 'b')` | ✅ PASS | `TypeError: snap() argument 'x' must be a number, got str` |
| `snap(None, None)` | ✅ PASS | `TypeError: snap() argument 'x' must be a number, got NoneType` |
| `snap(0, 0)` | ✅ PASS | Returns `(A2Point(a=0, b=0), 0.0)` — works correctly |
| `is_laman(-1, [])` | ✅ PASS | `ValueError: n_vertices must be a non-negative integer, got -1` |
| `is_laman(2, 'bad')` | ✅ PASS | `TypeError: edges must be a list, got str` |
| `TemporalAgent(decay_rate=nan)` | ✅ PASS | `ValueError: decay_rate must be finite, got nan` |
| `TemporalAgent(epsilon_0=-1)` | ✅ PASS | `ValueError: epsilon_0 must be positive, got -1` |
| `Metronome(T=0)` | ✅ PASS | `ValueError: T must be positive, got 0` |
| `Metronome(T=-1)` | ✅ PASS | `ValueError: T must be positive, got -1` |

### Extra Edge Cases

| Test | Status | Detail |
|------|--------|--------|
| `snap(nan, 1.0)` | ✅ PASS | `ValueError: snap() argument 'x' must be finite, got nan` |
| `snap(1e15, 1.0)` | ✅ PASS | Works fine with large values |
| `is_laman(2.5, [])` | ✅ PASS | `ValueError: n_vertices must be a non-negative integer, got 2.5` |
| `Metronome(T=nan)` | ✅ PASS | `ValueError: T must be finite, got nan` |
| `Metronome(T=1e10)` | ✅ PASS | Works with large T |
| `TemporalAgent(decay_rate=1e15)` | ✅ PASS | Works with large decay |
| `TemporalAgent(decay_rate=0)` | ⚠️ NOTE | Accepted without error — may be intentional (zero decay = no forgetting) |

**constraint-theory-core: All previously reported issues FIXED.** 🎉

---

## counterpoint-engine

> ⚠️ **API mismatch note:** The original stress test used incorrect API calls. The actual API requires `cantus_firmus` and `species` as constructor args to `CounterpointGenerator`, `generate()` is an instance method, `VoiceRange` is in `counterpoint_engine.generator` (not top-level), and `species` must be a `Species` enum (not int).

| Test | Status | Detail |
|------|--------|--------|
| `CounterpointResult` import | ✅ PASS | Available at top level |
| `generate()` returns `CounterpointResult` | ✅ PASS | Correct type returned |
| `result.feasible` exists | ✅ PASS | Returns `True` for valid input |
| `result.to_midi` exists | ✅ PASS | Method exists |
| `Satisfiability.SAT == "SAT"` | ✅ PASS | Backward compat works |
| `VoiceRange(100, 0)` inverted | ✅ PASS | `ValueError: min_pitch (100) must not exceed max_pitch (0)` |
| `VoiceRange('a', 'b')` strings | ✅ PASS | `TypeError: min_pitch must be an integer, got str` |

### Extra Edge Cases

| Test | Status | Detail |
|------|--------|--------|
| Empty cantus_firmus | ✅ PASS | `ValueError: cantus_firmus must not be empty` |
| Single note cantus | ⚠️ NOTE | Accepted — may or may not be valid musically |
| `VoiceRange(60, 60)` same bounds | ✅ PASS | Works fine |
| `VoiceRange(-1, 60)` negative min | ✅ PASS | `ValueError: min_pitch must be in MIDI range 0-127, got -1` |
| `VoiceRange(0, 200)` over MIDI range | ✅ PASS | `ValueError: max_pitch must be in MIDI range 0-127, got 200` |
| `species=99` (raw int) | ✅ PASS | `ValueError: species must be a Species enum, got int` |

**counterpoint-engine: All validations working. API differs from original test assumptions but the typed result system works correctly.** ✅

---

## plato-room-musician

> ⚠️ **API mismatch note:** `NoteEvent` is in `plato_room_musician.score` (not `mapping`). Signature is `(room, channel, pitch, velocity, onset_beats, duration_beats, patch, agent, category)`.

| Test | Status | Detail |
|------|--------|--------|
| `NoteEvent(channel=20)` | ✅ PASS | `ValueError: MIDI channel must be 0-15, got 20` |

### Extra Edge Cases

| Test | Status | Detail |
|------|--------|--------|
| `NoteEvent(channel=-1)` | ✅ PASS | `ValueError: MIDI channel must be 0-15, got -1` |
| `NoteEvent(velocity=-1)` | ⚠️ SILENT | Negative velocity accepted — **not validated** |
| `NoteEvent(duration=-1.0)` | ⚠️ SILENT | Negative duration accepted — **not validated** |
| Valid NoteEvent | ✅ PASS | Works correctly |

**plato-room-musician: Channel validation fixed. ⚠️ New issues found: negative velocity and negative duration are silently accepted.**

---

## groove-analyzer

> ⚠️ **API mismatch note:** `GenreProfile` requires 10 positional args, not just `name, epsilon_ms, bpm`.

| Test | Status | Detail |
|------|--------|--------|
| `GenreProfile(epsilon_ms=-1)` | ✅ PASS | `ValueError: epsilon_ms must be positive, got -1` |
| `GenreProfile(bpm=-1)` | ✅ PASS | `ValueError: bpm must be positive, got -1` |

### Extra Edge Cases

| Test | Status | Detail |
|------|--------|--------|
| `GenreProfile(bpm=nan)` | ✅ PASS | `ValueError: bpm must be a finite positive number, got nan` |
| `GenreProfile(epsilon_ms=nan)` | ✅ PASS | `ValueError: epsilon_ms must be a finite positive number, got nan` |
| `velocity_std=-10` | ⚠️ SILENT | Negative velocity std accepted — **not validated** |
| `swing_factor=2.0` | ⚠️ SILENT | Out-of-range swing factor accepted — **not validated** |
| `name=''` | ⚠️ SILENT | Empty name accepted — **not validated** |

**groove-analyzer: epsilon_ms and bpm validation fixed. ⚠️ New issues found: velocity_std, swing_factor, and name are not validated.**

---

## Summary

| Repo | Original Issues | Fixed | Still Broken | New Issues |
|------|----------------|-------|-------------|------------|
| constraint-theory-core | 11 | **11** | 0 | 0 |
| counterpoint-engine | 5 | **5** | 0 | 0 |
| plato-room-musician | 1 | **1** | 0 | 2 (negative velocity, negative duration) |
| groove-analyzer | 2 | **2** | 0 | 3 (negative vel_std, out-of-range swing, empty name) |

### Overall: 19/19 original issues FIXED ✅

### New issues discovered during re-test:

1. **plato-room-musician `NoteEvent`**: No validation on `velocity` (accepts negative) or `duration_beats` (accepts negative). These could produce invalid MIDI.
2. **groove-analyzer `GenreProfile`**: No validation on `velocity_std` (accepts negative), `swing_factor` (accepts out-of-range), or `name` (accepts empty string). Low severity but worth tightening.
