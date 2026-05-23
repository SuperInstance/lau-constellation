# Composer MIDI Sources — Raw Materials Inventory

> Comprehensive catalog of public-domain and open-license MIDI/encoded score collections for musical style decomposition research.
> Last updated: 2026-05-22

---

## Table of Contents

1. [Tier 1: Large-Scale Datasets (10,000+ pieces)](#tier-1-large-scale-datasets)
2. [Tier 2: Scholarly Encoded Score Collections](#tier-2-scholarly-encoded-score-collections)
3. [Tier 3: Curated Classical MIDI Archives](#tier-3-curated-classical-midi-archives)
4. [Tier 4: Public Domain Sheet Music with MIDI](#tier-4-public-domain-sheet-music-with-midi)
5. [Tier 5: Specialized Collections by Era](#tier-5-specialized-collections-by-era)
6. [Tier 6: Folk & World Music Collections](#tier-6-folk--world-music-collections)
7. [Tier 7: AI/ML Research Datasets](#tier-7-aiml-research-datasets)
8. [Era Coverage Matrix](#era-coverage-matrix)
9. [Recommended Acquisition Strategy](#recommended-acquisition-strategy)

---

## Tier 1: Large-Scale Datasets

### 1. The Lakh MIDI Dataset (LMD)

- **URL:** https://colinraffel.com/projects/lmd/
- **Pieces:** 176,581 unique MIDI files
- **Composers:** Thousands (mixed popular + classical; artist names in filenames for "Clean MIDI" subset)
- **Format:** Standard MIDI (.mid)
- **License:** CC-BY 4.0
- **Access:** Direct tar.gz download
  - `lmd_full.tar.gz` — all 176,581 files (named by MD5 hash)
  - `lmd_matched.tar.gz` — 45,129 files matched to Million Song Dataset
  - `lmd_aligned.tar.gz` — aligned to audio
  - `clean_midi.tar.gz` — subset with artist/title in filenames
- **Notes:** No quality curation — contains some corrupt files. Enormous variety of genres. Use `clean_midi` subset for labeled data. Metadata via Million Song Dataset.
- **Best for:** General style variety, ML training, broad coverage

### 2. BitMidi

- **URL:** https://bitmidi.com
- **Pieces:** 113,229 MIDI files
- **Composers:** Wide variety (classical, game, pop, film)
- **Format:** Standard MIDI (.mid)
- **License:** Mixed (user-uploaded; individual rights vary)
- **Access:** Individual download via website; no official bulk API (would need scraping)
- **Notes:** Community-curated. Quality varies. Good for finding specific pieces.
- **Best for:** Supplemental searches for specific works

### 3. Kunst der Fuge

- **URL:** https://www.kunstderfuge.com/
- **Pieces:** 20,000+ MIDI files, 1,000+ composers, 400+ pages
- **Composers:** Comprehensive classical — all eras from Medieval to Contemporary
- **Format:** Standard MIDI (.mid)
- **License:** Free for personal use; commercial use restricted
- **Access:** Individual downloads per page; organized by composer
- **Notes:** One of the oldest and most comprehensive classical MIDI archives. Active since 2002, regularly updated.
- **Best for:** Classical era coverage across all periods

---

## Tier 2: Scholarly Encoded Score Collections

### 4. KernScores (Humdrum **kern format)

- **URL:** https://kern.humdrum.org
- **Pieces:** 108,703 files (7,866,496 notes)
- **Composers:** Bach, Beethoven, Mozart, Haydn, Corelli, Vivaldi, Josquin, and many more
- **Format:** Humdrum **kern (convertible to MIDI via `hum2mid`)
- **License:** Free for research use
- **Access:** 
  - Browse at `https://kern.humdrum.org/cgi-bin/browse?type=collection&l=/`
  - Bulk download via zip: `https://kern.humdrum.org/cgi-bin/ksdata?l=<path>&format=zip`
  - Recursive download: `https://kern.humdrum.org/cgi-bin/ksdata?l=<path>&format=recursive`
- **Sub-collections:**
  - `/musedata/bach` — J.S. Bach complete works
  - `/musedata/beethoven` — Beethoven works
  - `/musedata/mozart` — Mozart works
  - `/musedata/haydn` — Haydn works
  - `/musedata/corelli` — Corelli works
  - `/musedata/vivaldi` — Vivaldi works
  - `/ccarh` — Direct CCARH encodings
  - `/jrp` — Josquin Research Project
  - `/osu/chant` — Gregorian chant (from Liber Usualis)
  - `/osu/classical` — Classical music
  - `/osu/densmore` — Native American songs (Frances Densmore collection)
  - `/osu/tonerow` — Tone rows from Schoenberg, Webern, Berg
  - `/essen` — Essen Folksong Collection (thousands of folk songs from all continents)
  - `/koto` — Japanese koto music (Edo period + folk)
  - `/ujag/cant` — Old Polish religious songs
  - `/ujag/zahn` — German Evangelical hymn melodies (1889)
  - `/asm` — American sheet music (Library of Congress)
- **Best for:** High-quality scholarly encodings, comprehensive classical coverage, folk music, chant

### 5. Josquin Research Project (JRP)

- **URL:** https://josquin.stanford.edu/
- **Pieces:** ~340 works attributed to Josquin + works by contemporaries (Ockeghem, Obrecht, Compère, etc.)
- **Composers:** Renaissance masters — Josquin des Prez, Johannes Ockeghem, Jacob Obrecht, Loyset Compère, Antoine Busnoys, and more
- **Format:** Humdrum **kern, MusicXML (exportable), MIDI (via kern conversion)
- **License:** Open access for research
- **Access:** 
  - Browse/search at `https://josquin.stanford.edu/browse`
  - Also available through KernScores: `https://kern.humdrum.org/cgi-bin/browse?l=/jrp`
  - REST-style URLs for programmatic access
- **Notes:** Extremely high editorial quality — entered voice-by-voice, triple-reviewed. Full-text search of melodic/rhythmic patterns. Designed for computational musicology.
- **Best for:** Renaissance polyphony, attribution studies, style analysis

### 6. MuseData (CCARH)

- **URL:** https://musedata.org
- **Pieces:** Hundreds of complete works (full scores)
- **Composers:** Bach (complete), Beethoven (complete symphonies), Haydn (London symphonies), Mozart, Corelli, Vivaldi, Handel (Messiah)
- **Format:** MuseData Stage 2 (.md2), convertible to MIDI, PDF, MusicXML
- **License:** Free for scholarly use
- **Access:**
  - Programmatic via `musesheet` Perl script: `musesheet -d data` to download all source data
  - PDF generation via `muse2ps`
  - Also mirrored in KernScores `/musedata` directory
- **Notes:** Complete orchestral scores with full part detail. Gold standard for Beethoven/Haydn symphonies.
- **Best for:** Complete orchestral works, symphonic style analysis

### 7. music21 Corpus (Python Library)

- **URL:** https://github.com/cuthbertLab/music21 (built into the library)
- **Pieces:** ~2,000+ built-in scores
- **Composers:** Bach (371 chorales + WTC + other), Beethoven, Mozart, Handel, Palestrina, Chopin, Schumann, Schubert, Debussy, Dvorak, and many more
- **Format:** MusicXML, **kern, MIDI, Humdrum
- **License:** BSD (music21 itself); corpus contents are public domain
- **Access:** 
  ```python
  import music21
  corpus = music21.corpus.search('.')  # list all
  for work in corpus:
      score = work.parse()  # parse into music21 stream
      score.write('midi', fp='output.mid')  # export as MIDI
  ```
- **Notes:** Ready-to-use in Python. Includes the complete Bach chorales (371), Well-Tempered Clavier Books I & II, and many other standard works. Ideal for prototyping.
- **Best for:** Rapid prototyping, Python-native analysis, standard repertoire

---

## Tier 3: Curated Classical MIDI Archives

### 8. Classical Archives (MIDI section)

- **URL:** https://www.classicalarchives.com/midi/composers/
- **Pieces:** Thousands (varies by composer; major composers have hundreds each)
- **Composers:** 217+ notable composers spanning all eras:
  - **Medieval/Renaissance:** Landini, Dunstable, Dufay, Ockeghem, Josquin, Byrd, Dowland, Palestrina, Lassus, Victoria, Gabrieli
  - **Baroque:** Bach, Handel, Vivaldi, Corelli, Couperin, Buxtehude, Frescobaldi, Biber, Charpentier, Scarlatti
  - **Classical:** Mozart, Haydn, Beethoven, Clementi, Gluck, Boccherini
  - **Romantic:** Chopin, Liszt, Brahms, Schumann, Schubert, Wagner, Tchaikovsky, Dvořák, Grieg, Debussy, Ravel, Elgar
  - **20th Century:** Bartók, Stravinsky, Gershwin, Joplin, Ives, Barber, Holst, Rachmaninoff
- **Format:** Standard MIDI (.mid)
- **License:** Requires subscription for unlimited downloads; limited free downloads
- **Access:** Individual file download via website; programmatic access would require subscription + scraping
- **Notes:** Most comprehensive single-composer classical MIDI index. Quality is generally good — curated.
- **Best for:** Filling gaps in specific composers, broad era coverage

### 9. Mutopia Project

- **URL:** https://www.mutopiaproject.org/
- **Pieces:** 2,124 pieces
- **Composers (top by count):** J.S. Bach (417), Beethoven (77), Chopin (47), Diabelli (36), Carcassi (29), Czerny (29), Aguado (26), Burgmüller (19), Couperin (7), Buxtehude (7), Brahms (11), Fauré (10), Handel, Mozart, Schubert, Debussy, Dvořák, and many more
- **Format:** PDF, MIDI, LilyPond source (.ly)
- **License:** Public Domain or Creative Commons (varies per piece; clearly labeled)
- **Access:** 
  - Individual download via website
  - Browse by composer: `https://www.mutopiaproject.org/cgibin/make-table.cgi?Composer=BachJS`
  - Bulk: Could scrape all MIDI links from browse pages
- **Notes:** LilyPond source means you can regenerate MIDI with different settings. Good editorial quality.
- **Best for:** High-quality MIDI from typeset editions, Bach-heavy coverage

---

## Tier 4: Public Domain Sheet Music with MIDI

### 10. IMSLP (International Music Score Library Project)

- **URL:** https://imslp.org
- **Pieces:** 700,000+ scores, 85,000+ works, 25,000+ composers
- **Composers:** Essentially every notable classical composer whose works are public domain
- **Format:** Primarily PDF scores; some MIDI files available under "Synthesized/MIDI" tab; also MusicXML and MuseScore (.mscz)
- **License:** Public domain (Canada; works PD in Canada + composer's country of origin)
- **Access:** 
  - Individual pages at `https://imslp.org/wiki/Category:<Composer>`
  - MIDI files specifically: look for "Synthesized/MIDI" category on work pages
  - No bulk API; scraping possible but respect rate limits
- **Notes:** MIDI availability is inconsistent — mostly PDF scores. Some works have MIDI from automated OMR (optical music recognition). Better for PDF → music21 OMR pipeline. Also check for MuseScore (.mscz) files which can be converted to MIDI.
- **Best for:** Comprehensive score catalog, source editions, supplementing MIDI with PDF analysis

### 11. MuseScore Community

- **URL:** https://musescore.com
- **Pieces:** Millions of community-transcribed scores
- **Composers:** All classical + popular + film + game
- **Format:** MuseScore (.mscz), MusicXML, PDF, MIDI (with Pro account)
- **License:** Varies per uploader (some CC, some all-rights-reserved)
- **Access:**
  - API available: `https://musescore.com/api/v2/`
  - Individual downloads (MIDI requires Pro subscription or user-uploaded PD works)
  - MuseScore desktop app can export any opened score as MIDI locally
- **Notes:** Mixed quality (community transcriptions). Covers many works not available elsewhere. Use with quality filtering.
- **Best for:** Filling specific gaps; use quality scores only

---

## Tier 5: Specialized Collections by Era

### Era 1: Medieval & Renaissance (500–1600)

| Source | Composers/Works | Format | URL |
|--------|----------------|--------|-----|
| **Josquin Research Project** | Josquin, Ockeghem, Obrecht, Compère, Busnoys (~340+ works) | kern/MusicXML/MIDI | https://josquin.stanford.edu/ |
| **KernScores /osu/chant** | Gregorian chant (Liber Usualis selections) | kern/MIDI | https://kern.humdrum.org/cgi-bin/browse?l=/osu/chant |
| **KernScores /musedata/corelli** | Corelli works | kern/MIDI | https://kern.humdrum.org/cgi-bin/browse?l=/musedata/corelli |
| **Classical Archives** | Landini, Dunstable, Dufay, Binchois, Busnois, Ockeghem, Josquin, Byrd, Dowland, Tallis, Palestrina, Lassus, Victoria, Gabrieli, Gesualdo | MIDI | https://www.classicalarchives.com/midi/composers/ |
| **Kunst der Fuge** | Palestrina, Byrd, Lassus, Victoria, Dowland, many more | MIDI | https://www.kunstderfuge.com/ |
| **Mutopia** | Dowland (2), Gibbons, Banchieri (6), others | MIDI/LilyPond | https://www.mutopiaproject.org/ |

### Era 2: Baroque (1600–1750)

| Source | Composers/Works | Format | URL |
|--------|----------------|--------|-----|
| **KernScores /musedata/bach** | Bach complete works | kern/MIDI | https://kern.humdrum.org/cgi-bin/browse?l=/musedata/bach |
| **MuseData** | Bach complete, Beethoven, Haydn symphonies, Handel Messiah | .md2/MIDI | https://musedata.org |
| **Mutopia** | J.S. Bach (417!), Handel, Vivaldi, Corelli, Couperin, Buxtehude, Scarlatti, Froberger, Charpentier | MIDI/LilyPond | https://www.mutopiaproject.org/ |
| **Classical Archives** | Bach, Handel, Vivaldi, Corelli, Couperin, Buxtehude, Scarlatti, Lully, Biber, Frescobaldi, Purcell, Pachelbel, Telemann | MIDI | https://www.classicalarchives.com/midi/composers/ |
| **Kunst der Fuge** | Extremely comprehensive Baroque section | MIDI | https://www.kunstderfuge.com/ |

### Era 3: Classical (1750–1820)

| Source | Composers/Works | Format | URL |
|--------|----------------|--------|-----|
| **KernScores /musedata** | Mozart, Haydn, Beethoven (complete) | kern/MIDI | https://kern.humdrum.org/ |
| **MuseData** | Beethoven 9 symphonies, Haydn London symphonies (93-104) | .md2/MIDI | https://musedata.org |
| **Mutopia** | Beethoven (77), Mozart, Haydn, Clementi, Schubert, Diabelli (36) | MIDI/LilyPond | https://www.mutopiaproject.org/ |
| **Classical Archives** | Mozart, Haydn, Beethoven, Clementi, Gluck, Salieri, Boccherini, Hummel | MIDI | https://www.classicalarchives.com/midi/composers/ |
| **music21 corpus** | Beethoven, Mozart, Haydn (built-in) | MusicXML/MIDI | pip install music21 |

### Era 4: Romantic (1820–1900)

| Source | Composers/Works | Format | URL |
|--------|----------------|--------|-----|
| **Mutopia** | Chopin (47), Brahms (11), Schumann, Schubert, Fauré (10), Dvořák (5), Grieg, Mendelssohn, Liszt, Wagner | MIDI/LilyPond | https://www.mutopiaproject.org/ |
| **Classical Archives** | Chopin, Liszt, Brahms, Schumann, Schubert, Wagner, Tchaikovsky, Dvořák, Grieg, Rachmaninoff, Elgar, Verdi, Puccini, Sibelius, Mahler, Bruckner | MIDI | https://www.classicalarchives.com/midi/composers/ |
| **MAESTRO** | Romantic piano repertoire (performances) | MIDI + audio | https://magenta.tensorflow.org/datasets/maestro |
| **Kunst der Fuge** | Comprehensive Romantic section | MIDI | https://www.kunstderfuge.com/ |

### Era 5: Early 20th Century & Jazz

| Source | Composers/Works | Format | URL |
|--------|----------------|--------|-----|
| **Ragtime Music (MacDonald)** | Scott Joplin complete rags, James Scott, Joseph Lamb, other ragtime composers | MIDI | https://www.ragtimemusic.com/ |
| **Classical Archives** | Joplin, Gershwin, Stravinsky, Bartók, Ravel, Debussy, Ives, Holst, Barber, Grainger | MIDI | https://www.classicalarchives.com/midi/composers/ |
| **Lakh MIDI Dataset** | Vast popular/jazz/film collection | MIDI | https://colinraffel.com/projects/lmd/ |
| **Kunst der Fuge** | Ragtime section, early modern | MIDI | https://www.kunstderfuge.com/ragtime.htm |

### Era 6: Folk & World Traditions

| Source | Contents | Format | URL |
|--------|----------|--------|-----|
| **KernScores /essen** (Essen Folksong Collection) | Thousands of folk songs from Europe, Asia, Africa, Americas | kern/MIDI | https://kern.humdrum.org/cgi-bin/browse?l=/essen |
| **KernScores /koto** | Japanese koto music (Edo period 1603-1867, folk, duets) | kern/MIDI | https://kern.humdrum.org/cgi-bin/browse?l=/koto |
| **KernScores /osu/densmore** | Native American songs collected by Frances Densmore | kern/MIDI | https://kern.humdrum.org/cgi-bin/browse?l=/osu/densmore |
| **KernScores /ujag** | Old Polish religious songs, German hymn melodies | kern/MIDI | https://kern.humdrum.org/cgi-bin/browse?l=/ujag |
| **KernScores /asm** | American sheet music (Library of Congress) | kern/MIDI | https://kern.humdrum.org/cgi-bin/browse?l=/asm |
| **KernScores /osu/barbershop** | Barbershop quartets | kern/MIDI | https://kern.humdrum.org/cgi-bin/browse?l=/osu/barbershop |

---

## Tier 6: Folk & World Music Collections

### 12. Essen Folksong Collection (via KernScores)

- **URL:** https://kern.humdrum.org/cgi-bin/browse?l=/essen
- **Pieces:** ~7,000+ folk songs (one of the largest encoded folk collections)
- **Regions:**
  - `/essen/europa` — European folk songs (German, French, Eastern European, etc.)
  - `/essen/america` — North & South American folk songs (USA, Mexico, misc)
  - `/essen/asia` — Asian folk songs (China/Han, China/NatMin, etc.)
  - `/essen/africa` — African folk songs
- **Format:** Humdrum **kern (convertible to MIDI)
- **License:** Free for research
- **Access:** Bulk zip download available: `https://kern.humdrum.org/cgi-bin/ksdata?l=essen&format=zip`
- **Best for:** Folk song style analysis, melodic pattern research, world music traditions

---

## Tier 7: AI/ML Research Datasets

### 13. MAESTRO Dataset (Google Magenta)

- **URL:** https://magenta.tensorflow.org/datasets/maestro
- **Pieces:** ~1,282 performances (V3.0.0)
- **Composers:** Classical piano repertoire — Bach, Beethoven, Chopin, Debussy, Liszt, Mozart, Rachmaninoff, Schubert, Schumann, and others (17th–early 20th century)
- **Format:** MIDI + WAV audio (aligned at ~3ms precision)
- **License:** CC BY-NC-SA 4.0
- **Access:** Direct download
  - MIDI-only: `maestro-v3.0.0-midi.zip` (56MB)
  - Full (audio+MIDI): `maestro-v3.0.0.zip` (101GB)
  - Metadata CSV: `maestro-v3.0.0.csv`
- **Stats:** ~200 hours, train/val/test split provided
- **Best for:** Expressive performance analysis, audio-MIDI alignment, piano style transfer

### 14. Bach Doodle Dataset (Google Magenta)

- **URL:** https://magenta.tensorflow.org/datasets/bach-doodle
- **Pieces:** 21.6 million harmonizations
- **Format:** MIDI (user melody + generated harmonization)
- **License:** See Google terms
- **Access:** Direct download from Google Storage
- **Best for:** Harmonization analysis, Bach style modeling

### 15. CocoChorales (Google Magenta)

- **URL:** https://magenta.tensorflow.org/datasets/cocochorales
- **Pieces:** 240,000 audio mixtures
- **Format:** Audio + MIDI + annotations
- **Style:** Four-part ensembles in Bach chorale style
- **Best for:** Chorale-style generation, source separation, Bach style analysis

### 16. Expanded Groove MIDI Dataset (E-GMD)

- **URL:** https://magenta.tensorflow.org/datasets/e-gmd
- **Pieces:** 444 hours of drum performances
- **Format:** MIDI + audio
- **Best for:** Rhythm/style analysis (drums only)

### 17. NSynth (Google Magenta)

- **URL:** https://magenta.tensorflow.org/datasets/nsynth
- **Pieces:** 305,979 individual notes
- **Format:** Audio + MIDI-like note annotations (pitch, velocity, instrument, timbre)
- **Instruments:** 1,006 instruments from commercial sample libraries
- **Best for:** Timbre analysis, instrument classification

---

## Era Coverage Matrix

| Era | KernScores | Mutopia | Class. Archives | Kunst der Fuge | LMD | MAESTRO | JRP | music21 |
|-----|-----------|---------|-----------------|----------------|-----|---------|-----|---------|
| Medieval (500-1400) | ✅ (chant) | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Renaissance (1400-1600) | ✅ (JRP) | ⚠️ (few) | ✅ | ✅ | ❌ | ❌ | ✅ | ⚠️ |
| Baroque (1600-1750) | ✅ (Bach+) | ✅ (417 Bach) | ✅ | ✅ | ⚠️ | ❌ | ❌ | ✅ |
| Classical (1750-1820) | ✅ (complete) | ✅ (77 Beet.) | ✅ | ✅ | ⚠️ | ❌ | ❌ | ✅ |
| Romantic (1820-1900) | ⚠️ | ✅ (47 Chopin) | ✅ | ✅ | ⚠️ | ✅ | ❌ | ✅ |
| Early 20th C. | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ❌ | ⚠️ |
| Jazz/Ragtime | ⚠️ | ❌ | ✅ (Joplin) | ✅ | ✅ | ❌ | ❌ | ❌ |
| Folk/World | ✅ (Essen) | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ⚠️ |
| Japanese trad. | ✅ (koto) | ❌ | ❌ | ❌ | ⚠️ | ❌ | ❌ | ❌ |
| Native American | ✅ (Densmore) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

Legend: ✅ Strong coverage | ⚠️ Partial | ❌ None/minimal

---

## Recommended Acquisition Strategy

### Phase 1: Quick Start (Day 1)
1. **Install music21** — `pip install music21` — instant access to 2,000+ built-in scores including complete Bach chorales
2. **Download KernScores bulk zips** for core classical: Bach, Beethoven, Mozart, Haydn
3. **Download MAESTRO MIDI-only** (56MB) for expressive piano performances
4. **Download Essen Folksong Collection** zip from KernScores

### Phase 2: Broad Coverage (Day 2-3)
5. **Download Lakh MIDI Clean subset** for broad genre coverage (labeled with artist/title)
6. **Scrape Mutopia MIDI files** for high-quality LilyPond-sourced material
7. **Download JRP complete corpus** for Renaissance polyphony
8. **Scrape ragtimemusic.com** for complete Joplin + classic ragtime

### Phase 3: Deep Fill (Week 2)
9. **Classical Archives subscription** for targeted gaps (217 composers across all eras)
10. **Kunst der Fuge** for specific Medieval/Renaissance/Baroque works
11. **MuseData** for complete orchestral scores (Beethoven/Haydn symphonies)
12. **BitMidi** for any remaining specific works

### Conversion Pipeline

```
**kern → MIDI:  hum2mid (Humdrum toolkit) or music21
MusicXML → MIDI: music21 or MuseScore CLI
LilyPond → MIDI: lilypond --midi
MuseScore → MIDI: mscore --export-to midi
PDF → MIDI: Audiveris (OMR) → music21 → MIDI
```

### Key Tools
- **music21** (Python) — universal converter and analyzer
- **Humdrum Toolkit** — for **kern format processing
- **MuseScore CLI** — for .mscz → MIDI conversion
- **pretty_midi** (Python) — MIDI manipulation and feature extraction
- **miditoolkit** (Python) — MIDI parsing

---

## Format Conversion Reference

| Source Format | To MIDI | Tool |
|--------------|---------|------|
| **kern | `hum2mid` or `music21.converter.parse('file.krn').write('midi')` | Humdrum / music21 |
| MusicXML | `music21.converter.parse('file.xml').write('midi')` | music21 |
| LilyPond (.ly) | `lilypond --midi file.ly` | LilyPond |
| MuseScore (.mscz) | `mscore file.mscz --export-to file.mid` | MuseScore CLI |
| MuseData (.md2) | `muse2ps` or via KernScores | CCARH tools |
| PDF score | Audiveris OMR → MusicXML → MIDI | Audiveris + music21 |

---

## Notes on Quality & Curation

- **Highest quality:** JRP (Renaissance), MuseData (orchestral), Mutopia (LilyPond typeset)
- **Good quality:** KernScores, Classical Archives, Kunst der Fuge
- **Variable quality:** LMD, BitMidi, MuseScore community
- **Performance MIDI (not score):** MAESTRO — captures expressive timing, velocity, pedaling

For style decomposition, prefer **score-based MIDI** (KernScores, Mutopia, MuseData) for structural analysis, and **performance MIDI** (MAESTRO) for expressive style modeling.

---

*This document serves as the raw materials inventory for the musical style decomposition system. Each source should be evaluated for quality and license compliance before integration.*
