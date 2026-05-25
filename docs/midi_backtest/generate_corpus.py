#!/usr/bin/env python3
"""Generate 20 diverse MIDI-like test sequences for back-testing."""
import json
import numpy as np

SAMPLE_RATE = 44100

def note_freq(name):
    """Convert note name like 'C4' or 'C#4' to frequency."""
    notes_map = {'C':0,'C#':1,'Db':1,'D':2,'D#':3,'Eb':3,'E':4,'F':5,'F#':6,'Gb':6,'G':7,'G#':8,'Ab':8,'A':9,'A#':10,'Bb':10,'B':11}
    if len(name) == 2:
        note_name = name[0]
        octave = int(name[1])
    else:
        note_name = name[:2]
        octave = int(name[2])
    midi = (octave + 1) * 12 + notes_map[note_name]
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))

def tests():
    corpus = {}

    # 1. Single A4
    corpus["single_440"] = [(440.0, 2.0, 100, 0.0)]

    # 2. Chromatic scale C4-B4
    chrom = ['C4','C#4','D4','D#4','E4','F4','F#4','G4','G#4','A4','A#4','B4']
    corpus["chromatic_scale"] = [(note_freq(n), 0.3, 100, i*0.3) for i,n in enumerate(chrom)]

    # 3. C major chord
    corpus["c_major_chord"] = [(note_freq(n), 2.0, 90, 0.0) for n in ['C4','E4','G4']]

    # 4. Circle of fifths
    fifths = ['C4','G4','D4','A4','E4','B4','F#4','C#4','G#4','D#4','A#4','F4']
    corpus["circle_of_fifths"] = [(note_freq(n), 0.4, 100, i*0.4) for i,n in enumerate(fifths)]

    # 5. Major scale up and down
    mscale = ['C4','D4','E4','F4','G4','A4','B4','C5','B4','A4','G4','F4','E4','D4','C4']
    corpus["major_scale"] = [(note_freq(n), 0.3, 100, i*0.3) for i,n in enumerate(mscale)]

    # 6. A minor scale
    amin = ['A3','B3','C4','D4','E4','F4','G4','A4']
    corpus["minor_scale"] = [(note_freq(n), 0.35, 100, i*0.35) for i,n in enumerate(amin)]

    # 7. Tritone pairs
    corpus["tritone_pairs"] = [
        (note_freq('C4'), 0.5, 100, 0.0),
        (note_freq('F#4'), 0.5, 100, 0.6),
        (note_freq('D4'), 0.5, 100, 1.2),
        (note_freq('G#4'), 0.5, 100, 1.8),
    ]

    # 8. Harmonic series of A4
    corpus["harmonic_series_440"] = [(440.0*(k+1), 2.0, max(10, 120-15*k), 0.0) for k in range(8)]

    # 9. Polyrhythm 3:4
    notes39 = []
    for i in range(4):
        notes39.append((note_freq('C4'), 0.2, 100, i*0.5))
    for i in range(3):
        notes39.append((note_freq('E4'), 0.2, 90, i*(2.0/3)))
    corpus["polyrhythm_3_4"] = notes39

    # 10. Glissando (discretized sweep)
    gliss = []
    t = 0.0
    for f in np.linspace(220, 880, 40):
        gliss.append((float(f), 0.1, 100, t))
        t += 0.05
    corpus["glissando"] = gliss

    # 11. Staccato 16th notes
    corpus["staccato_16th"] = [(note_freq('C4') + i*50, 0.05, 100, i*0.1) for i in range(20)]

    # 12. Legato phrase
    leg = ['C4','E4','G4','A4','G4','E4','C4']
    corpus["legato_phrase"] = [(note_freq(n), 0.4, 100, i*0.35) for i,n in enumerate(leg)]

    # 13. Dynamic sweep
    corpus["dynamic_sweep"] = [(440.0, 0.15, int(v), i*0.15) for i,v in enumerate(np.linspace(1,127,20))]

    # 14. Dense cluster
    corpus["dense_cluster"] = [(note_freq(n), 2.0, 80, 0.0) for n in chrom]

    # 15. Bach chorale (4-voice)
    corpus["bach_chorale"] = [
        (note_freq('C4'), 1.5, 90, 0.0),
        (note_freq('E4'), 1.5, 80, 0.0),
        (note_freq('G4'), 1.5, 85, 0.0),
        (note_freq('C5'), 1.5, 75, 0.0),
    ]

    # 16. Jazz voicing (9th/11th/13th)
    corpus["jazz_voicing"] = [
        (note_freq('C4'), 2.0, 80, 0.0),
        (note_freq('E4'), 2.0, 70, 0.0),
        (note_freq('G4'), 2.0, 70, 0.0),
        (note_freq('B4'), 2.0, 65, 0.0),
        (note_freq('D5'), 2.0, 60, 0.0),
        (note_freq('F5'), 2.0, 55, 0.0),
        (note_freq('A5'), 2.0, 50, 0.0),
    ]

    # 17. Ambient pad
    amb = []
    t = 0.0
    for f in [110, 146.83, 164.81, 220]:
        amb.append((f, 3.0, 60, t))
        t += 0.3
    corpus["ambient_pad"] = amb

    # 18. Percussion pattern (use specific freqs)
    corpus["percussion_pattern"] = [
        (100, 0.1, 127, 0.0), (200, 0.1, 100, 0.25), (100, 0.1, 127, 0.5),
        (300, 0.1, 80, 0.625), (100, 0.1, 127, 0.75), (200, 0.1, 100, 1.0),
        (100, 0.1, 127, 1.25), (150, 0.1, 110, 1.375),
    ]

    # 19. Whole tone scale
    wt = ['C4','D4','E4','F#4','G#4','A#4','C5','D5','E5','F#5','G#5','A#5']
    corpus["whole_tone_scale"] = [(note_freq(n), 0.3, 100, i*0.3) for i,n in enumerate(wt)]

    # 20. Fibonacci rhythm
    fibs = [1,1,2,3,5,8,13,21,34,55]
    fib_notes = []
    t = 0.0
    for i, f in enumerate(fibs):
        freq = 220 + i * 55
        fib_notes.append((float(freq), 0.2, 100, t))
        t += f * 0.1
    corpus["fibonacci_rhythm"] = fib_notes

    return corpus

if __name__ == "__main__":
    corpus = tests()
    with open("corpus.json", "w") as f:
        json.dump(corpus, f, indent=2)
    print(f"Generated {len(corpus)} test sequences")
    for name, notes in corpus.items():
        print(f"  {name}: {len(notes)} notes")
