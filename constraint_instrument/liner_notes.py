"""
Liner Notes Generator — Every performance gets a unique prose description.

Like the essays on the back of jazz albums.
Not marketing copy — literary music criticism.
"""

import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .goodman import GoodmanEngine


# ── Data ────────────────────────────────────────────────────────────────────

@dataclass
class Performance:
    """Summary of a performance for prose generation."""
    mode: str
    terrain: str
    key: str
    bpm: int
    bars: int
    note_count: int
    notes_per_bar: List[int]
    pitch_range: Tuple[int, int]       # (lowest, highest)
    velocity_range: Tuple[int, int]    # (min, max)
    diagnostic_scores: dict            # {position: 0.89, direction: 0.72, ...}
    flow_score: float                  # 0-1
    dominant_intervals: List[int]      # most common pitch intervals
    density_pattern: str               # 'sparse', 'moderate', 'dense', 'varied'
    phrasing: str                      # 'angular', 'smooth', 'mixed'
    terrain_description: str = ""


# ── Terrain & Mode Imagery ─────────────────────────────────────────────────

TERRAIN_IMAGERY = {
    'blues': {
        'landscape': ["dust", "heat rising off asphalt", "a screened porch at dusk",
                       "muddy water", "a one-room shack", "the last bus out of town"],
        'atmosphere': ["sweat", "smoke from a wood fire", "a screen door banging",
                        "the weight of Sunday", "whiskey breath", "red clay"],
        'light': ["late afternoon gold", "a single bare bulb", "lightning bugs",
                   "dawn breaking through blinds", "firelight on a tin roof"],
    },
    'delta_blues': {
        'landscape': ["cotton fields", "a dirt road disappearing into haze",
                       "the levee at midnight", "a crossroads", "a boxcar rattling south"],
        'atmosphere': ["heat you can taste", "dust in the throat", "a dog barking far off",
                        "kudzu swallowing everything", "the hum of cicadas", "red dirt under fingernails"],
        'light': ["a sliver of moon", "a freight train headlight", "stars thick as seeds",
                   "heat lightning on the horizon", "a kitchen match flaring"],
    },
    'bebop': {
        'landscape': ["52nd Street after midnight", "a cramped bandstand",
                       "the city at 2am", "a basement club with no sign",
                       "the back table at Minton's", "a fire escape overlooking traffic"],
        'atmosphere': ["cigarette smoke", "the clink of glasses", "a subway rumbling beneath",
                        "neon bleeding through rain", "the hiss of a cymbal", "talked-over introductions"],
        'light': ["neon reflecting off wet pavement", "a spotlight cutting smoke",
                   "the glow of a saxophone case", "a streetlamp halo", "the last set, lights half-down"],
    },
    'modal': {
        'landscape': ["open sky", "a wide plain", "the space between things",
                       "an empty highway at dawn", "a frozen lake", "the desert at noon"],
        'atmosphere': ["stillness", "air moving slowly", "a bell fading into nothing",
                        "the hum after a chord dies", "breath", "a room where someone just left"],
        'light': ["a single shaft of light", "the blue hour", "moonlight on water",
                   "dust motes in afternoon sun", "the glow before sunrise"],
    },
    'modal_jazz': {
        'landscape': ["open sky", "a wide plain", "the space between things",
                       "an empty highway at dawn", "a frozen lake", "the desert at noon"],
        'atmosphere': ["stillness", "air moving slowly", "a bell fading into nothing",
                        "the hum after a chord dies", "breath", "a room where someone just left"],
        'light': ["a single shaft of light", "the blue hour", "moonlight on water",
                   "dust motes in afternoon sun", "the glow before sunrise"],
    },
    'classical': {
        'landscape': ["a stone cathedral", "a concert hall before the audience arrives",
                       "a garden maze", "a library with tall windows", "a marble staircase"],
        'atmosphere': ["polished wood", "the scratch of a bow", "a page turning",
                        "the weight of centuries", "a metronome ticking in another room"],
        'light': ["candlelight", "a stained-glass window at noon", "dust in a sunbeam",
                   "a chandelier half-lit", "moonlight through leaded glass"],
    },
    'classical_counterpoint': {
        'landscape': ["a stone cathedral", "a concert hall before the audience arrives",
                       "a garden maze", "a library with tall windows", "a marble staircase"],
        'atmosphere': ["polished wood", "the scratch of a bow", "a page turning",
                        "the weight of centuries", "a metronome ticking in another room"],
        'light': ["candlelight", "a stained-glass window at noon", "dust in a sunbeam",
                   "a chandelier half-lit", "moonlight through leaded glass"],
    },
    'free_jazz': {
        'landscape': ["the edge of a cliff", "a room with no walls",
                       "the eye of a storm", "an empty lot in a burned-out city",
                       "the moment before something breaks"],
        'atmosphere': ["electricity in the air", "a held breath", "glass about to shatter",
                        "the roar behind silence", "chaos finding its own rhythm"],
        'light': ["lightning", "a strobe", "darkness with sudden flashes",
                   "the light behind closed eyelids", "a single match in a black room"],
    },
    'free_improvisation': {
        'landscape': ["the edge of a cliff", "a room with no walls",
                       "the eye of a storm", "an empty lot in a burned-out city",
                       "the moment before something breaks"],
        'atmosphere': ["electricity in the air", "a held breath", "glass about to shatter",
                        "the roar behind silence", "chaos finding its own rhythm"],
        'light': ["lightning", "a strobe", "darkness with sudden flashes",
                   "the light behind closed eyelids", "a single match in a black room"],
    },
    'bluegrass': {
        'landscape': ["a front porch in the hills", "a barn dance",
                       "a mountain road", "a creek bed at low water",
                       "a hayfield at golden hour"],
        'atmosphere': ["fiddles tuning", "the smell of fresh-cut grass",
                        "a dog under the table", "coffee on a wood stove",
                        "a screen door slamming"],
        'light': ["fireflies", "the last light on a ridge", "a lantern",
                   "morning fog burning off", "stars like a spilled salt shaker"],
    },
    'hip_hop_trap': {
        'landscape': ["a parking garage at 3am", "a studio with no windows",
                       "a city block after the clubs close", "a basement with a mic and a dream"],
        'atmosphere': ["bass you feel in your chest", "the hiss of a hi-hat",
                        "a loop playing for the hundredth time", "autotune bending reality",
                        "the weight of repetition"],
        'light': ["the glow of a laptop screen", "neon through blinds",
                   "a phone flashlight in a dark car", "red LED recording light"],
    },
    'afro_cuban': {
        'landscape': ["a street corner in Havana", "a dance floor under ceiling fans",
                       "a courtyard at dusk", "a plaza on festival night"],
        'atmosphere': ["syncopation in the blood", "congas warming up",
                        "the smell of rum and coffee", "heat that makes you move",
                        "a clave like a heartbeat"],
        'light': ["fairy lights strung across a patio", "the flash of white teeth in shadow",
                   "a sunset over the malecón", "candlelight on dark wood"],
    },
    'indian_raga': {
        'landscape': ["the Ganges at dawn", "a temple courtyard",
                       "a banyan tree's shade", "a rooftop at sunset",
                       "the Himalayas through morning mist"],
        'atmosphere': ["a drone like the earth humming", "incense curling",
                        "the patience of centuries", "a sitar string still vibrating",
                        "silence as music"],
        'light': ["dawn breaking over water", "a butter lamp", "golden hour on a temple wall",
                   "stars thick and close", "the last ember of a fire"],
    },
    'chinese_silk_bamboo': {
        'landscape': ["a garden pavilion", "a lake at dawn", "bamboo grove in rain",
                       "a teahouse overlooking mountains", "a bridge over still water"],
        'atmosphere': ["a brushstroke on silk", "tea cooling in a celadon cup",
                        "wind through bamboo", "the discipline of simplicity",
                        "each note placed like a stone in a garden"],
        'light': ["mist rising off a pond", "a paper lantern", "the soft gray of an overcast sky",
                   "moonlight on a tile floor", "the glow of dawn through clouds"],
    },
    'electronic_techno': {
        'landscape': ["a warehouse at 4am", "a dark room full of speakers",
                       "a grid of lights on a console", "a dance floor that never stops",
                       "the space between two heartbeats"],
        'atmosphere': ["the pulse of a kick drum", "sweat and strobes",
                        "repetition as meditation", "a filter slowly opening",
                        "the crowd breathing as one"],
        'light': ["lasers cutting smoke", "a grid of LEDs", "the red of an exit sign",
                   "total darkness between flashes", "a screen of waveforms"],
    },
    'gospel': {
        'landscape': ["a church on Sunday morning", "a revival tent",
                       "a living room full of folding chairs", "the choir loft"],
        'atmosphere': ["voices joining", "a Hammond organ swells",
                        "the feeling just before the shout", "hands clapping on two and four",
                        "the congregation rising"],
        'light': ["sunlight through stained glass", "a spotlight on the soloist",
                   "candlelight during prayer", "morning light through a window",
                   "the glow of open hymnals"],
    },
    'bebop_rich': {
        'landscape': ["52nd Street after midnight", "a cramped bandstand",
                       "the city at 2am", "a basement club with no sign",
                       "the back table at Minton's", "a fire escape overlooking traffic"],
        'atmosphere': ["cigarette smoke", "the clink of glasses", "a subway rumbling beneath",
                        "neon bleeding through rain", "the hiss of a cymbal", "talked-over introductions"],
        'light': ["neon reflecting off wet pavement", "a spotlight cutting smoke",
                   "the glow of a saxophone case", "a streetlamp halo", "the last set, lights half-down"],
    },
}

MODE_PERSONALITY = {
    'parker': {
        'verb_energy': ['tears into', 'attacks', 'launches', 'dives', 'pounces', 'storms'],
        'pace': ['relentless', 'breathless', 'unruly', 'fidgety', 'compulsive'],
        'character': 'urgent, probing, never settling — always chasing the next idea before the current one lands',
    },
    'miles': {
        'verb_energy': ['drifts into', 'floats through', 'breathes', 'waits', 'surfaces', 'emerges'],
        'pace': ['spacious', 'patient', 'unhurried', 'meditative', 'calculating'],
        'character': 'spacious, deliberate — each note chosen not for what it says, but for the silence it leaves',
    },
    'ellington': {
        'verb_energy': ['arranges', 'layers', 'orchestrates', 'builds', 'paints', 'composes'],
        'pace': ['architectural', 'dramatic', 'structured', 'grand', 'theatrical'],
        'character': 'architectural, dramatic — every section placed with a composer\'s ear for the whole',
    },
    'basie': {
        'verb_energy': ['comping behind', 'nodding through', 'grins through', 'swings into', 'punctuates'],
        'pace': ['conversational', 'democratic', 'relaxed', 'in-the-pocket', 'collective'],
        'character': 'conversational, in the pocket — making everyone else sound better by knowing when not to play',
    },
    'goodman': {
        'verb_energy': ['diagnoses', 'measures', 'examines', 'tests', 'evaluates', 'checks'],
        'pace': ['clinical', 'precise', 'analytical', 'methodical', 'sharp'],
        'character': 'clinical, precise — hearing what\'s missing before anyone else knows something\'s wrong',
    },
    'armstrong': {
        'verb_energy': ['sings through', 'bellows', 'soars over', 'preaches', 'testifies', 'celebrates'],
        'pace': ['joyful', 'boisterous', 'grounded', 'celebratory', 'larger-than-life'],
        'character': 'joyful, rooted, larger than life — turning every note into a story with a beginning, middle, and grin',
    },
    'ella': {
        'verb_energy': ['weaves', 'sculpts', 'threads', 'curves', 'flows through', 'scats across'],
        'pace': ['fluid', 'playful', 'effortless', 'nimble', 'deceptively simple'],
        'character': 'fluid, playful, deceptively effortless — making the hardest thing in the world look like humming',
    },
}

# Interval names for specific musical details
INTERVAL_NAMES = {
    1: "a half-step",
    2: "a whole step",
    3: "a minor third",
    4: "a major third",
    5: "a perfect fourth",
    6: "a tritone",
    7: "a perfect fifth",
    8: "a minor sixth",
    9: "a major sixth",
    10: "a minor seventh",
    11: "a major seventh",
    12: "an octave",
}

NOTE_NAMES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']


def _note_name(midi: int) -> str:
    octave = (midi // 12) - 1
    return f"{NOTE_NAMES[midi % 12]}{octave}"


def _pick(lst, rng=random):
    return lst[rng.randint(0, len(lst) - 1)] if lst else ""


# ── Performance Builder ────────────────────────────────────────────────────

def build_performance(notes: list, mode: str, terrain: str, key: int,
                      bpm: int, bars: int, terrain_description: str = "") -> Performance:
    """Analyze raw notes and build a Performance summary."""
    if not notes:
        return Performance(
            mode=mode, terrain=terrain, key=_note_name(key),
            bpm=bpm, bars=bars, note_count=0,
            notes_per_bar=[], pitch_range=(key, key),
            velocity_range=(0, 0), diagnostic_scores={},
            flow_score=0.0, dominant_intervals=[],
            density_pattern='sparse', phrasing='smooth',
            terrain_description=terrain_description,
        )

    # Per-bar note counts
    bar_duration = 4.0 * 60.0 / bpm
    notes_per_bar = []
    for bar_idx in range(bars):
        start = bar_idx * bar_duration
        end = start + bar_duration
        count = sum(1 for n in notes if start <= n['start_time'] < end)
        notes_per_bar.append(count)

    # Pitch and velocity ranges
    pitches = [n['pitch'] for n in notes]
    velocities = [n['velocity'] for n in notes]

    # Intervals between consecutive notes
    sorted_by_time = sorted(notes, key=lambda n: n['start_time'])
    intervals = []
    for i in range(1, len(sorted_by_time)):
        intervals.append(abs(sorted_by_time[i]['pitch'] - sorted_by_time[i-1]['pitch']))

    # Dominant intervals (top 3)
    from collections import Counter
    interval_counts = Counter(intervals)
    dominant = [iv for iv, _ in interval_counts.most_common(3)] if intervals else []

    # Density pattern
    if not notes_per_bar:
        density_pattern = 'sparse'
    else:
        avg = sum(notes_per_bar) / len(notes_per_bar)
        if avg <= 3:
            density_pattern = 'sparse'
        elif avg <= 7:
            density_pattern = 'moderate'
        elif avg <= 12:
            density_pattern = 'dense'
        else:
            density_pattern = 'dense'
        # Check if varied
        if max(notes_per_bar) - min(notes_per_bar) > avg * 0.8 and avg > 2:
            density_pattern = 'varied'

    # Phrasing
    if intervals:
        avg_interval = sum(intervals) / len(intervals)
        large_leaps = sum(1 for i in intervals if i > 7) / len(intervals)
        if large_leaps > 0.3:
            phrasing = 'angular'
        elif large_leaps < 0.1 and avg_interval < 4:
            phrasing = 'smooth'
        else:
            phrasing = 'mixed'
    else:
        phrasing = 'smooth'

    # Diagnostic scores
    goodman = GoodmanEngine()
    try:
        report = goodman.diagnose(notes)
        diag_scores = {}
        for o in report.orders:
            key_name = o.name.lower()
            diag_scores[key_name] = o.score
        flow_score = report.overall_score
    except Exception:
        diag_scores = {'position': 0.5, 'direction': 0.5, 'curvature': 0.5, 'structure': 0.5}
        flow_score = 0.5

    return Performance(
        mode=mode,
        terrain=terrain,
        key=_note_name(key),
        bpm=bpm,
        bars=bars,
        note_count=len(notes),
        notes_per_bar=notes_per_bar,
        pitch_range=(min(pitches), max(pitches)),
        velocity_range=(min(velocities), max(velocities)),
        diagnostic_scores=diag_scores,
        flow_score=flow_score,
        dominant_intervals=dominant,
        density_pattern=density_pattern,
        phrasing=phrasing,
        terrain_description=terrain_description,
    )


# ── Liner Notes Generator ──────────────────────────────────────────────────

class LinerNotesGenerator:
    """Generate unique prose descriptions for performances.
    
    Like the essays on the back of jazz albums.
    Not marketing copy — literary music criticism."""

    def __init__(self, seed=None):
        self._rng = random.Random(seed)

    def generate(self, performance: Performance) -> str:
        """Generate 80-150 word liner notes for this performance.
        
        Includes:
        - Description of the opening
        - One specific musical detail
        - The emotional arc
        - A closing image or metaphor
        """
        p = performance
        mode_info = MODE_PERSONALITY.get(p.mode, MODE_PERSONALITY['ella'])
        terrain_img = TERRAIN_IMAGERY.get(p.terrain, TERRAIN_IMAGERY.get('blues', {}))

        # ── The Opening ──
        opening_verbs = {
            'sparse': ['A single note opens', 'It starts with one gesture',
                        'The first sound arrives alone'],
            'moderate': ['The solo begins with a measured phrase',
                         'It opens mid-thought',
                         'A cluster of notes leads off'],
            'dense': ['The first bar erupts', 'It starts at a dead sprint',
                      'Notes pour in from the first beat'],
            'varied': ['The opening is unpredictable — a whisper that might become a shout',
                       'It starts tentatively, feeling for the edges'],
        }
        opening = _pick(opening_verbs.get(p.density_pattern, opening_verbs['moderate']), self._rng)

        # Describe the first bar's character
        if p.notes_per_bar and p.notes_per_bar[0] > 0:
            first_bar_density = p.notes_per_bar[0]
            if first_bar_density >= 10:
                opening += f", {p.note_count} notes packed into {p.bars} bars of {p.terrain.replace('_', ' ')}."
            elif first_bar_density <= 2:
                opening += f", spare and deliberate across {p.bars} bars."
            else:
                opening += f", winding through {p.bars} bars at {p.bpm} BPM."
        else:
            opening += f" — {p.bars} bars, {p.key}, {p.bpm} beats per minute."

        # ── Specific Musical Detail ──
        detail_parts = []
        if p.dominant_intervals:
            # Skip 0 (repeated notes) for the primary interval description
            intervals_desc = [i for i in p.dominant_intervals if i > 0]
            if intervals_desc:
                top_interval = intervals_desc[0]
                interval_name = INTERVAL_NAMES.get(top_interval, f"a {top_interval}-semitone leap")
                detail_parts.append(f"The phrasing leans on {interval_name}")
                if len(intervals_desc) > 1:
                    second = intervals_desc[1]
                    second_name = INTERVAL_NAMES.get(second, f"and {second} semitones")
                    detail_parts[-1] += f", with {second_name} close behind"
                detail_parts[-1] += "."
            elif p.dominant_intervals[0] == 0:
                detail_parts.append("The phrasing clings to repeated notes — hammering the same pitch like a point it refuses to drop.")

        # Pitch range detail
        if p.pitch_range[1] - p.pitch_range[0] > 24:
            detail_parts.append(f"The range spans over two octaves — from {_note_name(p.pitch_range[0])} to {_note_name(p.pitch_range[1])}.")
        elif p.pitch_range[1] - p.pitch_range[0] > 12:
            detail_parts.append(f"It covers an octave and change, {_note_name(p.pitch_range[0])} to {_note_name(p.pitch_range[1])}.")
        elif p.pitch_range[1] - p.pitch_range[0] <= 5:
            detail_parts.append(f"The notes stay close, mostly between {_note_name(p.pitch_range[0])} and {_note_name(p.pitch_range[1])}.")

        # Velocity/dynamics detail
        vel_span = p.velocity_range[1] - p.velocity_range[0]
        if vel_span > 60:
            detail_parts.append("The dynamics swing from whisper to shout.")
        elif vel_span < 15:
            detail_parts.append("The dynamics hold steady — even-tempered throughout.")

        detail = " " + " ".join(detail_parts[:2]) if detail_parts else ""

        # ── The Arc ──
        arc_phrases = {
            'sparse': [
                "The space between notes says as much as the notes themselves.",
                "Rests become part of the architecture — every silence intentional.",
                "It breathes. The music is in what gets left out.",
            ],
            'moderate': [
                "The middle bars settle into a conversation — not trying to prove anything.",
                "It finds its footing in the middle, then lets go.",
                "A groove surfaces and submerges, never quite settling.",
            ],
            'dense': [
                "The density doesn't let up — idea chasing idea, no room for breath.",
                "It piles up, layer on layer, until the structure almost buckles.",
                "There's a breathlessness to it, like a story told in one exhalation.",
            ],
            'varied': [
                "The arc is uneven — that's the point. Dense bars collapse into space, then rebuild.",
                "It gathers and releases, never settling into a single gear.",
                "The tension lives in the contrast — crowded passages giving way to sudden emptiness.",
            ],
        }
        arc = _pick(arc_phrases.get(p.density_pattern, arc_phrases['moderate']), self._rng)

        # ── Closing Image ──
        landscape = _pick(terrain_img.get('landscape', []), self._rng) if terrain_img else ""
        atmosphere = _pick(terrain_img.get('atmosphere', []), self._rng) if terrain_img else ""
        light = _pick(terrain_img.get('light', []), self._rng) if terrain_img else ""

        closings = []
        if landscape:
            closings.append(f"Like {landscape} — {mode_info['character']}.")
        if atmosphere:
            closings.append(f"It leaves behind the smell of {atmosphere}.")
        if light:
            closings.append(f"The last note dissolves into {light}.")
        closings.append(f"A performance in {p.terrain.replace('_', ' ')} territory — {mode_info['character'].split('—')[0].strip()}.")

        closing = _pick(closings, self._rng)

        # ── Assemble ──
        # Mode character sentence
        mode_sentence = f"The {p.mode} engine is {mode_info['character'].split('—')[0].strip()}."

        # Phrasing detail
        phrasing_sentence = ""
        if p.phrasing == 'angular':
            phrasing_sentence = "The lines are angular — more Thelonious than Nat King Cole."
        elif p.phrasing == 'smooth':
            phrasing_sentence = "The phrasing runs smooth, legato, like water finding its level."
        else:
            phrasing_sentence = "The phrasing shifts between smooth runs and sudden jumps, never committing to either."

        # Diagnostics nod
        diag_sentence = ""
        if p.diagnostic_scores:
            best = max(p.diagnostic_scores, key=p.diagnostic_scores.get)
            best_score = p.diagnostic_scores[best]
            worst = min(p.diagnostic_scores, key=p.diagnostic_scores.get)
            worst_score = p.diagnostic_scores[worst]
            if best_score > 0.8 and worst_score < 0.5:
                diag_sentence = f"The {best} is confident but the {worst} falters — a performance with a hole in it."
            elif best_score > 0.7:
                diag_sentence = f"The {best} holds everything together."

        # Build the paragraph
        sentences = [opening]
        if detail:
            sentences.append(detail.strip())
        sentences.append(mode_sentence)
        if phrasing_sentence:
            sentences.append(phrasing_sentence)
        sentences.append(arc)
        if diag_sentence:
            sentences.append(diag_sentence)
        sentences.append(closing)

        # Join and ensure it feels like one flowing paragraph
        text = " ".join(sentences)
        # Clean up any double spaces or awkward joins
        text = text.replace("  ", " ").strip()

        return text

    def generate_short(self, performance: Performance) -> str:
        """One sentence. Like a radio DJ intro."""
        p = performance
        mode_info = MODE_PERSONALITY.get(p.mode, MODE_PERSONALITY['ella'])
        terrain_img = TERRAIN_IMAGERY.get(p.terrain, TERRAIN_IMAGERY.get('blues', {}))

        templates = [
            lambda: f"Coming up now — the {p.mode} engine, {_pick(mode_info['pace'], self._rng)}, walking through {p.terrain.replace('_', ' ')} in {p.key}.",
            lambda: f"Next: {p.bars} bars of {p.terrain.replace('_', ' ')} at {p.bpm} BPM, the {p.mode} mode doing what it does — {mode_info['character'].split(',')[0].strip()}.",
            lambda: f"Listen for this — {p.mode} mode in {p.key}, {_pick(mode_info['pace'], self._rng)} as a {p.terrain.replace('_', ' ')} night.",
            lambda: f"{p.key}. {p.bpm} beats per minute. {p.mode} in {p.terrain.replace('_', ' ')} territory. Pay attention to the {p.phrasing} phrasing.",
            lambda: f"A {p.mode} performance in {p.terrain.replace('_', ' ')} — {_pick(mode_info['pace'], self._rng)}, {p.note_count} notes, one chance to get it right.",
        ]

        return _pick(templates, self._rng)()

    def generate_review(self, performance: Performance) -> str:
        """200-word review. Like a DownBeat magazine review.
        Includes: what worked, what didn't, rating (1-5 stars), recommendation."""
        p = performance
        mode_info = MODE_PERSONALITY.get(p.mode, MODE_PERSONALITY['ella'])
        terrain_img = TERRAIN_IMAGERY.get(p.terrain, TERRAIN_IMAGERY.get('blues', {}))

        # Determine rating from diagnostic scores
        scores = p.diagnostic_scores
        if scores:
            avg = sum(scores.values()) / len(scores)
            if avg > 0.85:
                rating, rating_word = 5, "essential"
            elif avg > 0.7:
                rating, rating_word = 4, "strong"
            elif avg > 0.55:
                rating, rating_word = 3, "promising"
            elif avg > 0.4:
                rating, rating_word = 2, "uneven"
            else:
                rating, rating_word = 1, "rough"
        else:
            rating, rating_word = 3, "incomplete"

        stars = "★" * rating + "☆" * (5 - rating)

        # What worked
        worked_parts = []
        if p.flow_score > 0.7:
            worked_parts.append("The overall flow is cohesive — these notes belong together")
        if p.phrasing == 'smooth' and p.density_pattern in ('moderate', 'sparse'):
            worked_parts.append("The phrasing breathes naturally")
        elif p.phrasing == 'angular':
            worked_parts.append("The angular phrasing keeps you on your toes")
        if p.density_pattern == 'varied':
            worked_parts.append("The dynamic contour — dense passages giving way to space — shows real architectural thinking")
        if not worked_parts:
            worked_parts.append("There are genuine ideas in here, even if they don't all land")

        # What didn't
        didnt_parts = []
        if scores:
            worst = min(scores, key=scores.get)
            worst_val = scores[worst]
            if worst_val < 0.5:
                didnt_parts.append(f"the {worst} never quite commits — it hovers at {worst_val:.0%}, which is the difference between a story and a sketch")
        if p.note_count < 10:
            didnt_parts.append("the performance is too brief to develop its ideas fully")
        if p.density_pattern == 'dense' and p.phrasing == 'angular':
            didnt_parts.append("the density and angularity compete rather than cooperate — at times it feels like a flood of notes searching for a melody")
        if not didnt_parts:
            didnt_parts.append("it plays it safe — more competence than revelation")

        # Build review
        review_parts = []
        review_parts.append(f"The {p.mode} engine in {p.terrain.replace('_', ' ')} territory, {p.key}, {p.bpm} BPM, {p.bars} bars. {p.note_count} notes to make a statement.")

        review_parts.append(f"What works: {worked_parts[0]}.")
        if len(worked_parts) > 1:
            review_parts[-1] += f" {worked_parts[1]}."

        review_parts.append(f"What doesn't: {didnt_parts[0]}.")

        # Recommendation
        if rating >= 4:
            review_parts.append(f"Recommended for anyone who wants to hear what {p.terrain.replace('_', ' ')} sounds like through the lens of {p.mode}. This is a {rating_word} performance — the kind you return to.")
        elif rating >= 3:
            review_parts.append(f"Worth hearing, especially for the moments where the {p.mode} engine forgets to be careful. A {rating_word} session with flashes of something real.")
        elif rating >= 2:
            review_parts.append(f"An {rating_word} outing — more sketch than finished work. But there's something in the rough that's worth following up on.")
        else:
            review_parts.append(f"A {rating_word} take. The ideas haven't found their legs yet. Come back with more bars or a different terrain.")

        review_parts.append(f"\nRating: {stars}")

        return " ".join(review_parts)
