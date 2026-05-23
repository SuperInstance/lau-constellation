# Style Extractor

Extract **musical style DNA** from MIDI files as a `StyleTile` — a compact, serializable representation of a composer or piece's essential musical characteristics.

## Concept

Every composer has a fingerprint: the intervals they favor, their rhythmic feel, how consonant their harmony tends to be. Style Extractor distills MIDI performances into a `StyleTile` capturing:

- **Melodic DNA** — interval distribution, range, step-vs-leap tendency
- **Rhythmic DNA** — duration patterns, syncopation rate, note density, rhythmic entropy
- **Harmonic DNA** — consonance vs dissonance ratios
- **Timing DNA** — timing precision, swing factor
- **Register DNA** — pitch center and range
- **Density** — notes per bar

## StyleTile as Musical DNA

A `StyleTile` is to music what a color palette is to visual design. It captures the *what* and *how* of musical expression in a format that can be:

1. **Compared** — cosine similarity between tiles tells you how alike two styles are
2. **Serialized** — save/load as JSON for sharing and persistence
3. **Applied** — use as constraints to transform generated music toward a target style

## Composer Decomposition

Feed multiple MIDI files from the same composer to extract their aggregate style. The more files, the more representative the tile. Compare Bach vs Beatles vs Dilla — each will have a distinct rhythmic entropy, consonance rate, and interval fingerprint.

## Style Morphing

Two StyleTiles define a space. By interpolating between them, you can morph from one style to another — imagine a slider between "Bach" and "J Dilla" that smoothly adjusts syncopation, consonance, and swing.

## Quick Start

```python
from style_extractor import StyleExtractor

extractor = StyleExtractor()
tile = extractor.extract(
    ["bach_invention_1.mid", "bach_invention_8.mid"],
    composer="Bach",
    era="Baroque"
)

tile.to_json("bach_style.json")
print(f"Bach's consonance rate: {tile.consonance_rate}")
print(f"Similarity to itself: {tile.similarity(tile)}")
```

## Installation

```bash
pip install -e ".[dev]"
pytest tests/
```

## License

MIT
