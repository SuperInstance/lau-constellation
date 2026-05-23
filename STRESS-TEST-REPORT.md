# Stress Test Report

**Date:** 2026-05-22  
**Packages tested:** 6  
**Total test cases:** 98  

## Summary

| Severity | Count | Description |
|----------|-------|-------------|
| **CRASH** | 3 | Unhandled exceptions that should be caught |
| **SILENT** | 11 | Invalid input accepted without error (potential data corruption) |
| **BAD_MSG** | 1 | Error raised but message is unhelpful/misleading |
| **OK** | 83 | Handled correctly (proper error or correct result) |

---

## 1. constraint-theory-core

### ✅ Tests Passed (handled correctly)
- `lattice.snap(NaN)` → `ValueError: cannot convert float NaN to integer` ✅
- `lattice.snap(Inf)` → `ValueError: cannot convert float infinity to integer` ✅
- `lattice.snap(0,0)` → Works correctly ✅
- `lattice.snap(1e15, 1e15)` → Works correctly ✅
- `lattice.snap(1e-15, 1e-15)` → Works correctly ✅
- `rigidity.1_vertex` → `is_laman(1, [])` works ✅
- `rigidity.2_vertex` → Works ✅
- `rigidity.100_vertex` → Works ✅
- `rigidity.cyclic_triangle` → Works ✅
- `rigidity.disconnected` → Works ✅
- `metronome.0_agents` → Works ✅
- `metronome.1_agent` → Works ✅
- `metronome.1000_agents` → Works ✅
- `metronome.already_converged` → Works ✅
- `holonomy.empty_cycle` → `holonomy = 0` ✅
- `holonomy.single_element` → Works ✅
- `holonomy.1000_element` → Works ✅
- `holonomy.all_same` → `holonomy = 0` ✅
- `holonomy.mismatched_len` → `ValueError` ✅
- `holonomy.bad_direction` → `ValueError` ✅

### ⚠️ Silent Failure
| Test | Input | Behavior | Fix |
|------|-------|----------|-----|
| `temporal.neg_epsilon` | `TemporalAgent(epsilon_0=-0.1)` | **Silently accepted** — negative epsilon makes no mathematical sense (deadband width can't be negative) | Add `if epsilon_0 < 0: raise ValueError("epsilon_0 must be non-negative")` in `TemporalAgent.__init__` |

---

## 2. counterpoint-engine

### ✅ Tests Passed
- `cf.empty` → `ValueError: cantus_firmus must not be empty` ✅
- `cf.1_note` → Generates counterpoint ✅
- `cf.100_note_construct` → Constructs OK ✅
- `cf.all_same` → Generates or returns None ✅
- `cf.chromatic` → Returns None (unSAT) ✅
- `cf.random` → Generates or returns None ✅
- `species.{0,-1,6,999}` → Accepts as IntEnum members (since `Species` is `IntEnum`, any int is technically valid) ✅ (debatable)
- `voice.inverted` → `ValueError: min_pitch must not exceed max_pitch` ✅
- `voice.no_overlap` → Returns None (correct, no valid candidates) ✅

### ⚠️ Silent Failures
| Test | Input | Behavior | Fix |
|------|-------|----------|-----|
| `key.-1` | `Scale(tonic=-1)` | **Silently accepted** — produces scale with pitch classes offset by -1 (wraps via modular arithmetic, equivalent to tonic=11 but confusing) | Add `if not 0 <= tonic <= 11: raise ValueError("tonic must be a pitch class 0-11")` in `Scale.__post_init__` |
| `key.12` | `Scale(tonic=12)` | **Silently accepted** — equivalent to tonic=0 via `% 12` | Same fix |
| `key.100` | `Scale(tonic=100)` | **Silently accepted** — `100 % 12 = 4`, so tonic=100 ≈ tonic=4 | Same fix |

### 🔴 Bad Error Message
| Test | Input | Error | Fix |
|------|-------|-------|-----|
| `key.str_C` | `Scale(tonic="C")` | `TypeError: can only concatenate str (not "int") to str` — **completely opaque**; doesn't mention `tonic` or expected type | Add type check: `if not isinstance(tonic, int): raise TypeError("tonic must be an integer pitch class 0-11")` |

---

## 3. groove-analyzer

### ✅ Tests Passed
- `midi.empty_tracks` → Works (no tracks = handled by mido) ✅
- `midi.metadata_only` → **Warning** issued, returns empty `GrooveTiming` ✅
- `midi.1_note` → Works ✅
- `midi.10k_notes` → Works ✅
- `midi.overlapping` → Works ✅
- `extreme.bpm_300` → Works ✅
- `extreme.default_bpm` → Works with default tempo ✅
- `file.nonexistent` → `FileNotFoundError` (from mido) ✅
- `file.corrupted` → Error raised ✅
- `grid.div_0` → `ValueError: grid_division must be positive` ✅
- `grid.div_1` → Works ✅
- `grid.div_1000` → Works ✅

### 💥 Crash
| Test | Input | Error | Fix |
|------|-------|-------|-----|
| `extreme.bpm_1` | `_make_midi_file(notes=[...], bpm=1)` | `ValueError: attribute must be in range 0..16777215` — raised by **mido** when `bpm2tempo(1)` = 60,000,000 µs/beat exceeds the 3-byte MIDI tempo limit of 16,777,215 | This is actually a **mido** limitation, not groove-analyzer. The groove-analyzer API itself doesn't create MIDI files, so this is a test harness issue. However, `extract_microtiming` should be tested with extremely slow MIDI files. **Rating: BAD_MSG** — if a user encounters a MIDI file with a very slow tempo, the error from mido is confusing. |

---

## 4. holonomy-harmony

### ✅ Tests Passed
- `prog.single` → Works ✅
- `prog.1000_chords` → Works ✅
- `prog.all_same` → Works ✅
- `prog.random_chromatic` → Works ✅
- `roman.empty` → `ValueError: Cannot parse Roman numeral` ✅
- `roman.H` → `ValueError: Cannot parse Roman numeral` ✅
- `roman.epsilon` → `ValueError: Cannot parse Roman numeral` ✅
- `prog.secondary_doms` → Works ✅

### 💥 Crash
| Test | Input | Error | Fix |
|------|-------|-------|-----|
| `prog.empty` | `analyze_progression([])` | `ValueError: roots list is empty` — raised by `compute_holonomy`, which is called internally. **Rating: OK-ish** but the error message doesn't mention the caller's context. | Should be caught in `analyze_progression` with: `if not symbols: raise ValueError("progression must not be empty")` |

### ⚠️ Silent Failures
| Test | Input | Behavior | Fix |
|------|-------|----------|-----|
| `roman.V99` | `parse_roman("V99")` | **Silently accepted** — parsed as V with suffix "99", quality falls through to "maj" (uppercase heuristic). A user typo like "V99" should be rejected. | Add validation for unknown suffixes: `if suffix and suffix not in mapping: raise ValueError(f"Unknown chord suffix: {suffix!r}")` |
| `key.-1` | `analyze_progression([...], key_tonic=-1)` | **Silently accepted** — same as counterpoint-engine, wraps via modular arithmetic | Add `if not 0 <= key_tonic <= 11: raise ValueError(...)` |
| `key.12` | `key_tonic=12` | **Silently accepted** | Same fix |
| `key.100` | `key_tonic=100` | **Silently accepted** | Same fix |

### 🔴 Bad Error Message
| Test | Input | Error | Fix |
|------|-------|-------|-----|
| `key.str_C` | `key_tonic="C"` | `TypeError: can only concatenate str (not "int") to str` — same opaque error as counterpoint-engine | Add type check before arithmetic |

---

## 5. spline-midi-smooth

### ✅ Tests Passed
- `interp.0_pts_hermite` → `ValueError: cubic_hermite requires at least 2 points` ✅
- `interp.0_pts_catmull` → `ValueError: catmull_rom requires at least 2 points` ✅
- `interp.1_pt_hermite` → `ValueError: cubic_hermite requires at least 2 points` ✅
- `interp.1_pt_catmull` → `ValueError: catmull_rom requires at least 2 points` ✅
- `interp.2_identical` → `ValueError: x coordinates must be strictly increasing` ✅
- `interp.1k_points` → Works ✅
- `interp.non_increasing_x` → `ValueError: x coordinates must be strictly increasing` ✅
- `interp.dup_x` → `ValueError: x coordinates must be strictly increasing` ✅
- `interp.large_y` → Works ✅
- `interp.nan_y` → `ValueError: Input contains NaN or Inf values` ✅
- `interp.inf_y` → `ValueError: Input contains NaN or Inf values` ✅
- `tension.{neg, high, 100}` → All work (catmull_rom doesn't validate tension range — tension=100 just produces wild curves, which is mathematically valid) ✅
- `bspline.deg0` → `ValueError: bspline needs at least 1 points for degree 0` ✅
- `bspline.deg20` → Works (but extremely slow for high degrees due to recursive Cox-de-Boor) ✅

**Performance note:** B-spline evaluation with high degrees (≥20) is exponentially slow due to recursive `_cox_de_boor`. This is a known limitation of the naive implementation — not a bug, but worth documenting.

**Overall: Best-tested package.** All edge cases are properly validated with clear error messages.

---

## 6. plato-room-musician

### ✅ Tests Passed
- `rooms.empty` → Works (empty score) ✅
- `rooms.1000` → Works (1000 events) ✅
- `rooms.unicode` → Works (emoji room names) ✅
- `rooms.empty_name` → Works ✅
- `rooms.long_name` → Works (10K char room name) ✅
- `tiles.extra_fields` → Works (extra fields ignored) ✅
- `channels.20_rooms` → Works (channels cycle via modulo) ✅
- `renderer.empty_midi` → Works ✅
- `renderer.empty_tensor` → Works ✅
- `fetcher.synthetic_rooms` → `get_rooms()` works ✅

### 💥 Crash (Package Bug)
| Test | Input | Error | Fix |
|------|-------|-------|-----|
| `fetcher.synthetic_tiles` | `SyntheticFetcher.get_room("forgemaster-cadence", limit=5)` | `TypeError: not all arguments converted during string formatting` in `_make_tile()` | **Root cause:** `TILE_SEEDS` contains format strings with different numbers of placeholders (1 to 3), but `_make_tile` always passes 5 arguments via `self.rng.choice(TILE_SEEDS) % (room_name, randint, random, randint, agent)`. Seeds with fewer placeholders crash. **Fix:** Use a single consistent format string, or wrap each seed with its own parameter list, or use `{}` / `.format()` with kwargs. |
| `fetcher.synthetic_all` | `SyntheticFetcher.get_all_tiles()` | Same as above | Same fix |

### ⚠️ Silent Failures
| Test | Input | Behavior | Fix |
|------|-------|----------|-----|
| `tiles.neg_confidence` | `confidence=-0.5` | **Silently accepted** — velocity clipped to 1 (via `int(max(1, min(127, confidence * 127)))`), but negative confidence has no semantic meaning | Add validation: `if not 0 <= confidence <= 1: raise ValueError("confidence must be between 0 and 1")` |
| `tiles.high_confidence` | `confidence=1.5` | **Silently accepted** — velocity clipped to 127 | Same fix |
| `tiles.no_fields` | `map_tile("test-room", {})` | **Silently accepted** — returns a dict with defaults ( KeyError for missing fields is caught internally or defaults used) | Should either validate required fields or document which fields are optional |

---

## Findings by Severity

### 🔴 CRASH (3 total)

| # | Package | Test | Root Cause |
|---|---------|------|------------|
| 1 | **plato-room-musician** | `fetcher.synthetic_tiles` | `TILE_SEEDS` format strings have inconsistent placeholder counts; `%` operator crashes when seed has fewer `%` than args passed |
| 2 | **plato-room-musician** | `fetcher.synthetic_all` | Same as above |
| 3 | **groove-analyzer** | `extreme.bpm_1` | `mido.bpm2tempo(1)` exceeds MIDI 3-byte tempo limit; error from mido is confusing |

### 🟡 SILENT (11 total)

| # | Package | Test | Issue |
|---|---------|------|-------|
| 1 | **constraint-theory-core** | `temporal.neg_epsilon` | Negative epsilon accepted |
| 2 | **counterpoint-engine** | `key.-1` | `tonic=-1` silently wraps |
| 3 | **counterpoint-engine** | `key.12` | `tonic=12` silently wraps |
| 4 | **counterpoint-engine** | `key.100` | `tonic=100` silently wraps |
| 5 | **holonomy-harmony** | `roman.V99` | Invalid suffix "99" silently treated as "maj" |
| 6 | **holonomy-harmony** | `key.-1` | `key_tonic=-1` silently wraps |
| 7 | **holonomy-harmony** | `key.12` | `key_tonic=12` silently wraps |
| 8 | **holonomy-harmony** | `key.100` | `key_tonic=100` silently wraps |
| 9 | **plato-room-musician** | `tiles.neg_confidence` | `confidence=-0.5` silently clipped |
| 10 | **plato-room-musician** | `tiles.high_confidence` | `confidence=1.5` silently clipped |
| 11 | **plato-room-musician** | `tiles.no_fields` | Empty tile dict silently processed |

### 🟠 BAD_MSG (2 total)

| # | Package | Test | Error Message | Should Be |
|---|---------|------|---------------|-----------|
| 1 | **counterpoint-engine** | `key.str_C` | `TypeError: can only concatenate str (not "int") to str` | `TypeError: tonic must be an integer pitch class 0-11, got str` |
| 2 | **holonomy-harmony** | `key.str_C` | `TypeError: can only concatenate str (not "int") to str` | `TypeError: key_tonic must be an integer pitch class 0-11, got str` |

---

## Recommendations (Priority Order)

1. **🔴 Fix `TILE_SEEDS` format strings** (plato-room-musician) — This crashes on every call to `SyntheticFetcher.get_room()` or `get_all_tiles()`. The fix is straightforward: make all format strings accept the same args, or use named placeholders.

2. **🟡 Add `tonic`/`key_tonic` range validation** — Both counterpoint-engine and holonomy-harmony silently accept any integer (even negative). Add `if not 0 <= tonic <= 11: raise ValueError(...)`.

3. **🟡 Add `epsilon_0` non-negative check** (constraint-theory-core) — Negative deadband width is nonsensical.

4. **🟡 Validate `confidence` range** (plato-room-musician) — Should be `[0, 1]`, not silently clipped.

5. **🟠 Add type checks for `tonic`/`key_tonic`** — `str` input crashes with an opaque `TypeError` about string concatenation. Check `isinstance(tonic, int)` first.

6. **🟡 Validate Roman numeral suffixes** (holonomy-harmony) — Unknown suffixes like "99" should be rejected, not silently mapped to "maj".

7. **📋 Document B-spline degree performance** (spline-midi-smooth) — Degrees > ~10 are extremely slow with the recursive Cox-de-Boor. Consider noting this in docstrings or adding a warning.

---

*Report generated by adversarial stress testing on 2026-05-22.*
