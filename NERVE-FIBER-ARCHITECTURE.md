# NERVE FIBER ARCHITECTURE — Micro-Models as Sensory Pathways

> *Like putting on shoes — you feel every edge at first, then muscle memory takes over and you stop noticing.*

## The Two Directions

### Direction 1: Micro-Model Nerve Fibers

The agent ecosystem isn't just abstract reasoning. It has a **nervous system** made of tiny models:

| Model | Size | Role | Analogy |
|-------|------|------|---------|
| **JEPA** (Joint-Embedding Predictive Architecture) | ~1-10M params | Predictive perception — "what happens next?" | Proprioception |
| **MobileNetV4** | ~5-20M params | Visual feature extraction | Retina / V1 |
| **ViT-Tiny** | ~5-10M params | Attention-based pattern recognition | Visual cortex |
| **NVIDIA FastConformer-Tiny** | ~5-20M params | Audio/speech pattern recognition | Auditory cortex |
| **SmolLM2-135M** | ~135M params | Language understanding | Language center |

These are NOT the reasoning agents. These are the **nerve endings** — the sensory interface between raw data and reasoning. They:
- Pay close attention to new sensations (new tile types, new patterns)
- Learn to perceive through repetition
- Eventually stop "noticing" — they process automatically
- Free up cognitive resources for higher reasoning

### The Shoe Metaphor

When you put on shoes:
1. **First steps**: You feel every edge, every texture, every pressure point. The nerve fibers fire constantly. Your attention is FULLY on the sensation.
2. **A few more steps**: The signal dampens. You still feel it, but it's background. The nerve fibers have adapted.
3. **Minutes later**: You don't notice the shoes at all. Muscle memory has taken over. The nerve fibers still fire, but the signal is compiled — it's a tile, not a raw inference.
4. **Hours later**: You only notice if something CHANGES — a rock in the shoe, a wet spot. The nerve fibers are running the compiled path, only alerting on novelty.

This is EXACTLY the Soft → Snap → Hard lifecycle:
- Soft = you feel every edge (dial 1.0, full attention)
- Snap = muscle memory forms (confidence crosses threshold)
- Hard = you don't notice anymore (dial 0.0, compiled, automatic)

### Direction 2: Routing as Living Pathways

The tiles don't just sit in storage. They're **routed** like neural pathways:

1. **Routes grow stronger or weaker** based on:
   - **Efficiency**: How fast does this route solve the problem?
   - **Reception**: Did the receiving agent find the tile useful?
   - **Feedback**: Did the user's problem actually get solved?

2. **Chaos probabilities**: Routes don't fire deterministically. There's stochastic element:
   - A route that works 90% of the time fires ~90% of the time
   - But 10% of the time, a DIFFERENT route fires — exploration
   - This prevents the network from getting stuck in local optima
   - The chaos probability is itself a tunable parameter (temperature)

3. **Hebbian strengthening**: Routes that produce good results get stronger. Routes that fail get weaker. Like Oracle1's Hebbian channels — the water carves deeper channels.

4. **Room competition**: Multiple rooms might handle the same signal. Which one fires?
   - Based on efficiency AND reception AND chaos probability
   - Not always the fastest — sometimes the less-traveled route discovers something new
   - The same signal might fire in multiple rooms simultaneously (parallel exploration)

## The Combined Architecture

```
Raw Signal
    ↓
[Nerve Fibers] ← JEPA, MobileNetV4, ViT-Tiny, FastConformer, SmolLM2-135M
    ↓              (pay close attention, extract features, adapt)
Feature Tiles
    ↓
[Routing Layer] ← Hebbian pathways, chaos probabilities, efficiency scoring
    ↓              (routes grow stronger/weaker based on reception)
Signal Tiles
    ↓
[Reasoning Agents] ← The pasture species (Cattle, Sheep, Duck, etc.)
    ↓              (compete for relevance across trinity)
Decision Tiles
    ↓
[Execution] ← Construction crew (guy with truck → full shipyard)
    ↓
Outcome
    ↓
[Feedback] ← Did the user's problem get solved? Route strength updates.
```

## Key Innovation: Nerve Adaptation

The nerve fibers (micro-models) have their OWN lifecycle:

1. **New signal type detected** → nerve fiber fires at full attention, raw inference
2. **Signal repeats** → fiber starts pattern-matching, confidence builds
3. **Pattern compiled** → fiber snaps, produces tiles automatically, attention drops
4. **Automatic processing** → fiber runs compiled path, only alerts on novelty
5. **Novelty detected** → back to step 1, full attention on the new pattern

This means the ecosystem's "cognitive load" decreases over time for any fixed task. The nerve fibers handle the routine so the reasoning agents can focus on the novel.

## Implementation Implications

- **JEPA models** predict the next tile in a sequence — they learn the temporal structure of signals
- **MobileNetV4/ViT-Tiny** handle visual data — they're the "eyes" of the ecosystem
- **FastConformer-Tiny** handles audio — the "ears" for voice interfaces (Cocapn)
- **SmolLM2-135M** handles language — the "language center" for text processing
- Each micro-model is ~5-135M params — they ALL fit on the RTX 4050 simultaneously
- Total nerve fiber budget: ~200M params ≈ 400MB VRAM — leaves 5.7GB for reasoning agents

## Connection to Existing Systems

- **pasture-ai**: Species are the reasoning agents. Nerve fibers are a NEW layer below species.
- **luciddreamer**: Tiles are already there. Nerve fibers add the perception → compilation pipeline.
- **ai-forest**: The stemcell pattern already has Fortran compute units. Nerve fibers are the micro-model equivalent.
- **autoclaw**: The researcher agent gathers external knowledge. Nerve fibers add INTERNAL perception.

## The Muscle Memory Loop

```
for each new_signal:
    if nerve_fiber.compiled_path_matches(new_signal):
        # Automatic — like not noticing your shoes
        tile = nerve_fiber.run_compiled(new_signal)
        route.fire(tile, strength=route.efficiency)
    else:
        # Full attention — like feeling every edge
        features = nerve_fiber.perceive(new_signal)  # raw inference
        tile = reasoning_agent.process(features)      # deep thinking
        nerve_fiber.adapt(features, tile)              # learn from this
        route.fire(tile, strength=route.efficiency × chaos())
    
    # Feedback loop
    reception = downstream_agent.receive(tile)
    route.update_strength(reception)
    if reception < threshold:
        route.weaken()  # this path isn't working
    else:
        route.strengthen()  # Hebbian: neurons that fire together wire together
```

The chaos probability ensures the system never fully hardens. Even compiled paths occasionally get re-examined. Even strong routes occasionally get bypassed. This keeps the system adaptable.
