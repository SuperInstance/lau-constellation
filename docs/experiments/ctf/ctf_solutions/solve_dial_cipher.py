#!/usr/bin/env python3
"""Solution for Challenge 5: The Dial Cipher"""
import math

TRADITIONS = {
    "western": (2.72, 2.05, 1.80), "carnatic": (2.77, 3.63, 2.80),
    "jazz": (2.30, 2.50, 2.10), "gamelan": (1.40, 1.20, 2.90),
    "blues": (2.10, 2.80, 1.60), "arabic": (2.50, 3.10, 2.30),
    "japanese": (1.80, 1.50, 2.20), "throat_singing": (2.90, 0.80, 3.00),
}

TRADITION_KEYS = {
    "western": ord('W'), "carnatic": ord('C'), "jazz": ord('J'),
    "gamelan": ord('G'), "blues": ord('B'), "arabic": ord('A'),
    "japanese": ord('J'), "throat_singing": ord('T'),
}

def nearest_tradition(v, h, s):
    best_name = "unknown"
    best_dist = float('inf')
    for name, (tv, th, ts) in TRADITIONS.items():
        dist = math.sqrt((v - tv)**2 + (h - th)**2 + (s - ts)**2)
        if dist < best_dist:
            best_dist = dist
            best_name = name
    return best_name

# Encoded data from the cipher file
encoded = [
    (2.72, 2.05, 1.80, 35),
    (1.40, 1.20, 2.90, 47),
    (2.10, 2.80, 1.60, 39),
    (2.50, 3.10, 2.30, 30),
    (2.77, 3.63, 2.80, 47),
    (2.72, 2.05, 1.80, 54),
    (2.90, 0.80, 3.00, 32),
    (2.30, 2.50, 2.10, 62),
    (1.80, 1.50, 2.20, 35),
    (2.72, 2.05, 1.80, 52),
    (2.72, 2.05, 1.80, 50),
    (1.40, 1.20, 2.90, 24),
    (2.10, 2.80, 1.60, 48),
    (2.50, 3.10, 2.30, 36),
    (2.77, 3.63, 2.80, 46),
    (2.72, 2.05, 1.80, 50),
    (2.90, 0.80, 3.00, 57),
    (2.30, 2.50, 2.10, 40),
    (1.80, 1.50, 2.20, 47),
    (2.72, 2.05, 1.80, 37),
    (2.50, 3.10, 2.30, 50),
]

message = ""
for v, h, s, encoded_char in encoded:
    trad = nearest_tradition(v, h, s)
    key = TRADITION_KEYS[trad]
    decoded = encoded_char ^ key
    message += chr(decoded)

print(f"Decoded: {message}")
print(f"Flag: flag{{{message}}}")
