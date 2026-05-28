"""
Dial Oracle — a snarky, opinionated music critic who lives in dial space.

Provides witty commentary on musical traditions, blend compatibility, and
 groove quality using templates and randomisation.
"""

from __future__ import annotations

import random
from typing import Optional

import numpy as np

from .dials import DialPosition, DIAL_RANGES, compute_dial_distance


class DialOracle:
    """A witty, snarky music critic who reads dial positions like tea leaves.

    Parameters
    ----------
    seed : int
        Random seed for reproducible sass.
    """

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self._rng = random.Random(seed)

    # ------------------------------------------------------------------
    # Templates
    # ------------------------------------------------------------------
    _TRADITION_TEMPLATES: dict[str, list[str]] = {
        "Jazz": [
            "You're basically a smoky basement at 2 AM. Nice.",
            "Your harmonic tension could talk its way out of a parking ticket.",
            "Jazz. Cool. Just don't improvise over the salad course.",
        ],
        "Classical": [
            "Ah, European art-music. You've got *structure*. Try loosening that cravat.",
            "Your balance is so perfect it's suspicious. Are you a robot?",
            "Four movements, zero surprises. We get it, you read sheet music.",
        ],
        "Gamelan": [
            "You sound like a room full of bronze cash registers having an epiphany.",
            "Interlocking rhythms? Fancy. Can you do it while carrying a temple?",
            "Gamelan: proving you don't need a bass drop to drop jaws.",
        ],
        "Gagaku": [
            "The 'most pleasing' point in dial space. Even your brags are humble.",
            "You float like a spectral butterfly made of silk and patience.",
            "Gagaku: slower than dial-up, prettier than broadband.",
        ],
        "Hindustani": [
            "Raga by day, tala by night, caffeine always.",
            "Your microtones have microtones. Respect.",
            "Hindustani classical: where a single note goes to grad school.",
        ],
        "African Polyrhythm": [
            "You've got more cross-rhythms than a angry intersection.",
            "One drummer? Cute. Call us when you have twelve.",
            "Your groove is so deep it needs a ladder.",
        ],
        "EDM": [
            "Beep boop wub wub. There, I wrote your next drop.",
            "Your spectral density is visible from orbit.",
            "EDM: proving that loud and repetitive is a valid life choice.",
        ],
        "Blues": [
            "You've got 99 problems and a blue note is all of them.",
            "Your groove is so authentic it owes back taxes.",
            "Blues: the original 'it be like that sometimes' genre.",
        ],
        "Hip-hop": [
            "Your flow is tighter than a metronome with OCD.",
            "Beats so hard they need a helmet.",
            "Hip-hop: making spoken word feel guilty since 1973.",
        ],
        "Latin": [
            "Your clave is so on point it teaches geometry.",
            "Latin: where every measure is a fiesta and every rest is a siesta.",
            "You've got syncopation in places syncopation shouldn't be. Nice.",
        ],
    }

    _BLEND_POSITIVE: list[str] = [
        "These two would make beautiful babies. Musical babies.",
        "Blend them like a smoothie: unexpected, but delicious.",
        "They fit together like a tritone resolving to a third. *Chef's kiss*.",
        "Go for it. What's the worst that could happen? (Famous last words.)",
    ]

    _BLEND_NEGATIVE: list[str] = [
        "Mixing these is like putting pineapple on pizza: controversial and regrettable.",
        "They go together like a kazoo and a funeral. Hard pass.",
        "The dial-space distance between them is basically a restraining order.",
        "Nope. Not even with a ten-foot MIDI cable.",
    ]

    _BLEND_MEH: list[str] = [
        "They might blend. Or they might just awkwardly share a stage. 50/50.",
        "It won't be terrible. It won't be great. It'll be *fusion*.",
        "Like room-temperature water: inoffensive, but why bother?",
    ]

    _GROOVE_TEMPLATES: dict[str, list[str]] = {
        "tight": [
            "Your groove is tighter than a metronome with OCD.",
            "Tighter than a drumhead in a sauna. Respect.",
            "Not a single atom out of place. Are you human?",
        ],
        "loose": [
            "Your groove is so loose it needs a belt.",
            "Swing is good. This is… *drifting*.",
            "Relaxed? Yes. Pocket? Maybe in another pair of pants.",
        ],
        "complex": [
            "Your rhythm is doing calculus while everyone else is still on addition.",
            "Impressive. Confusing. But impressive.",
            "Polyrhythms? More like *poly-problems* for the dancer.",
        ],
        "simple": [
            "Simple. Effective. Like a hammer made of velvet.",
            "Not every groove needs to be a thesis statement.",
            "Minimalism is a choice. You're making it work.",
        ],
        "dense": [
            "Your spectral density is giving me claustrophobia.",
            "So much timbre. So little time. Breathe.",
            "It's not muddy, it's *rich*. (It's a little muddy.)",
        ],
        "sparse": [
            "Your spectral density is so low I can hear my own thoughts.",
            "Minimal. Haunting. Possibly just the HVAC system.",
            "Less is more, but this is pushing it.",
        ],
    }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def what_tradition_am_i(self, position: DialPosition) -> str:
        """Identify the closest tradition and deliver a snarky verdict.

        Parameters
        ----------
        position : DialPosition
            The dial position to diagnose.

        Returns
        -------
        str
            A witty one-liner naming the tradition.
        """
        closest_name = "Unknown"
        min_dist = float("inf")
        for name, profile in DIAL_RANGES.items():
            centre = DialPosition.from_array(profile["center"], tradition_name=name)
            dist = compute_dial_distance(position, centre)
            if dist < min_dist:
                min_dist = dist
                closest_name = name

        # If we're far from everything, we're a rebel
        if min_dist > 2.5:
            rebels = [
                f"You're so far out even GPS gave up. Closest known tradition is {closest_name}, but honestly? You're on your own.",
                f"Tradition? You *are* the tradition. (Nobody knows you yet.)",
                f"Closest match: {closest_name} — if you squint. Hard.",
            ]
            return self._rng.choice(rebels)

        templates = self._TRADITION_TEMPLATES.get(closest_name, ["You exist. How daring."])
        return self._rng.choice(templates)

    def will_these_blend(self, a: DialPosition, b: DialPosition) -> str:
        """Predict whether two dial positions will blend harmoniously.

        Parameters
        ----------
        a, b : DialPosition
            The two positions to compare.

        Returns
        -------
        str
            A snarky compatibility report.
        """
        dist = compute_dial_distance(a, b)
        if dist < 1.0:
            return self._rng.choice(self._BLEND_POSITIVE)
        if dist > 2.5:
            return self._rng.choice(self._BLEND_NEGATIVE)
        return self._rng.choice(self._BLEND_MEH)

    def rate_my_groove(self, position: DialPosition) -> str:
        """Rate a groove on tightness, complexity, and spectral density.

        Parameters
        ----------
        position : DialPosition
            The dial position representing the groove.

        Returns
        -------
        str
            A multi-sentence snarky review.
        """
        parts: list[str] = []

        rc = position.rhythmic_complexity
        ht = position.harmonic_tension
        sd = position.spectral_density

        # Rhythm category
        if rc < 1.5:
            parts.append(self._rng.choice(self._GROOVE_TEMPLATES["simple"]))
        elif rc < 3.5:
            parts.append(self._rng.choice(self._GROOVE_TEMPLATES["tight"]))
        else:
            parts.append(self._rng.choice(self._GROOVE_TEMPLATES["complex"]))

        # Spectral category
        if sd < 2.0:
            parts.append(self._rng.choice(self._GROOVE_TEMPLATES["sparse"]))
        elif sd < 3.5:
            parts.append("Your timbral balance is… acceptable. Don't let it go to your head.")
        else:
            parts.append(self._rng.choice(self._GROOVE_TEMPLATES["dense"]))

        # Overall verdict
        score = (rc + ht + sd) / 15.0
        if score < 0.4:
            parts.append("Overall: C-. I've heard metronomes with more soul.")
        elif score < 0.6:
            parts.append("Overall: B. Solid. Unremarkable. Like a slice of white bread.")
        elif score < 0.8:
            parts.append("Overall: A-. Almost great. Try turning the self-doubt up to 11.")
        else:
            parts.append("Overall: A+. I'm not saying it's perfect, but I'm also not *not* saying that.")

        return " ".join(parts)
