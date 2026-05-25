# CTF Hints — Progressive Clues

**Warning:** Read one hint at a time. Each subsequent hint reveals more.

---

## Challenge 1: The Hidden Message

**Hint 1:** Each note has a consonance score between 0 and 1. How could you convert that range to printable ASCII?

**Hint 2:** The formula is: `ASCII_code = round(consonance_score * 95) + 32`. This maps 0.0→space, 1.0→DEL.

**Hint 3:** The positions are given in the challenge file. Compute the consonance score for each and apply the formula.

**Hint 4:** The message starts with 'T' and ends with 'Y'. It's an 8-letter word about music theory.

<details>
<summary>Solution</summary>

The message is **TONALITY**. `flag{tonality}`

```python
positions = [
    (2.392, 2.941, 0.050), (0.179, 1.205, 1.557),
    (0.259, 2.346, 1.791), (1.090, 0.219, 0.447),
    (2.959, 0.906, 0.329), (1.750, 0.100, 0.787),
    (1.944, 1.096, 0.675), (1.134, 2.773, 2.825),
]
for v, h, s in positions:
    score = consonance_score(v, h, s)
    print(chr(round(score * 95) + 32), end='')
# Output: TONALITY
```

</details>

---

## Challenge 2: The Lost Tradition

**Hint 1:** You have 8 points in 3D space. They cluster together.

**Hint 2:** Compute the centroid (arithmetic mean) of each axis independently.

**Hint 3:** Sum each column and divide by 8.

**Hint 4:** The answer is approximately (2.52, 1.89, 2.74).

<details>
<summary>Solution</summary>

`flag{2.52_1.89_2.74}` — the lost tradition lives in the unexplored region between Japanese, Western, and Gamelan.

</details>

---

## Challenge 3: The Scheduler's Secret

**Hint 1:** The log shows process names and their "affinity" to pitch classes. The schedule executes processes in PID order.

**Hint 2:** Each process name relates to a musical concept. What are they collectively doing?

**Hint 3:** The scheduler is C-SCHED (Consonance Scheduler). What musical concept does scheduling processes map to?

**Hint 4:** The processes are: Harmonic, Arpeggio, Cadence, Glissando, Echo, Dynamics, Resonance, Overtone, Vibrato, Interval, Melody — all components of...?

<details>
<summary>Solution</summary>

The scheduler is composing **harmony**. `flag{harmony}`

The process names are all musical terms that are components of harmony. The C-SCHED system treats CPU scheduling as musical composition, and the "secret" is that the scheduler's purpose is harmony — both in the OS sense and the musical sense.

</details>

---

## Challenge 4: The Anti-Music Detector

**Hint 1:** Anti-music has consonance below 0.15 (the random threshold). Odd-numbered samples are music, even-numbered are anti-music.

**Hint 2:** Write a script that computes consonance for each sample's lattice position. Or analyze the frequency spectrum — anti-music sounds like noise.

**Hint 3:** The classification alternates: music, anti-music, music, anti-music...

**Hint 4:** Samples 1, 3, 5, 7, 9 are music (at tradition landmarks). Samples 2, 4, 6, 8, 10 are anti-music (near the origin, far from all traditions).

<details>
<summary>Solution</summary>

Classification: `1010101010` → `flag{1010101010}`

```python
# Anti-music files: 2, 4, 6, 8, 10
# Music files: 1, 3, 5, 7, 9
# Bit string (1=music, 0=anti-music): 1010101010
```

</details>

---

## Challenge 5: The Dial Cipher

**Hint 1:** Each position maps to the nearest tradition. The tradition's first letter is the XOR key.

**Hint 2:** Tradition first letters: W(estern), G(amelan), B(lues), A(rabic), C(arnatic), T(hroat_singing), J(azz), J(apaneSE).

**Hint 3:** XOR the encoded value with the tradition key letter's ASCII code to get the plaintext character.

**Hint 4:** The message starts with "the_" and ends with "remembers".

<details>
<summary>Solution</summary>

The message is **the_lattice_remembers**. `flag{the_lattice_remembers}`

```python
for v, h, s, encoded in cipher_data:
    trad = nearest_tradition(v, h, s)
    key = ord(trad[0].upper())  # First letter
    char = chr(encoded ^ key)
```

</details>
