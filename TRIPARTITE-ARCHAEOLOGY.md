# TRIPARTITE ARCHAEOLOGY — The Older Trinity Systems

> *Before ethos/pathos/logos, there were already three-body systems everywhere. The idea is older than the naming.*

## 1. Oracle1's Soft → Snap → Hard

The original trinity. Three essays, one lifecycle.

| Phase | Room | Dial | Confidence | What it does |
|-------|------|------|------------|-------------|
| **Soft** | Admits everything | 1.0 | 0.0 → accumulates | Holds space for the not-yet-verified |
| **Snap** | The moment of knowing | — | crosses threshold | Reflex — the line comes tight |
| **Hard** | Cannot be fooled | 0.0 | 1.0 only | Zero holonomy, proof required |

**The physics**: γ + H conservation governs the whole thing. Connectivity trades off against diversity. You can't have both. The soft room maximizes diversity (admits everything). The hard room maximizes connectivity (only verified). The snap is the transfer function between them.

**Already implemented in**: `luciddreamer/rooms.py` (SoftRoom, HardRoom), `luciddreamer/signal_chain.py` (SignalChainRoom with dial), `luciddreamer/epsilon_accumulator.py`

**Key insight**: The dial is a *continuous* control, not a switch. 0.0 → 0.25 → 0.5 → 0.75 → 1.0. Every position is valid. The snap is not "which room" but "the moment the inference's confidence crosses compile threshold (97.5%)."

## 2. Pasture-AI's Species → Collie → StudBook

The livestock trinity. Three roles, not three rooms.

| Role | Who | Purpose | Rust module |
|------|-----|---------|-------------|
| **Species** | Cattle/Sheep/Duck/Goat/Hog/Chicken/Horse | Do the work. 7 types, each with VRAM budget, latency profile, herding strategy | `species/mod.rs` |
| **Collie** | Border Collie orchestrator | Herd the species. 7 herding strategies (Strong Eye, The Wear, Whistle Stop, etc.) | `collie/shepherd.rs` |
| **StudBook** | Night School evolution | Breed the next generation. SLERP LoRA merging, fitness scores, genealogy | `evolution/stud_book.rs`, `night_school/breed.py` |

**The physics**: Fitness scores create selection pressure. Species with fitness > 0.9 for 3+ generations promote (Sheep→Cattle, Duck→Falcon, Chicken→Horse). Species below 0.3 are culled. The StudBook records lineage for breeding.

**Already implemented in**: `pasture-ai/superinstance/src/` — full Rust implementation with SpeciesRegistry, Shepherd, 7 HerdingStrategy implementations

**Key insight**: The Collie doesn't tell species what to do. It *herds* them — applies pressure, channels energy, knows which species needs which strategy. "Strong Eye" for Cattle (steady GPU pressure), "Free Range" for Chickens (constant pecking, watch for silence).

## 3. Autoclaw's Researcher → Teacher → Critic → Distiller

The knowledge trinity. Four roles that form a pipeline.

| Role | Purpose | Priority |
|------|---------|----------|
| **Researcher** | Gathers knowledge from outside. DuckDuckGo → LLM → structured insight | 5 |
| **Teacher** | Transforms raw knowledge into training data. Q&A pairs, Alpaca, ChatML | 5 |
| **Critic** | Challenges assumptions. Quality scores, adversarial questions, contradiction detection | 7 (lower) |
| **Distiller** | Synthesizes, compresses, builds LoRA datasets. Background work. | 8 (lowest) |

**The physics**: MessageBus (SQLite pub/sub) connects them. Researcher publishes findings → Teacher generates training data → Critic quality-checks → Distiller compacts. All coordinated by Coordinator agent.

**Already implemented in**: `autoclaw/crew/agents/` — full Python with BaseAgent, MessageBus, KnowledgeStore, Coordinator

**Key insight**: The distiller runs at lowest priority because *distillation is background work*. It's the same pattern as LucidDreamer's hard room — you don't distill while the fishing is happening. You distill after.

## 4. AI-Forest's Five Layers (Canopy → Floor → Mycelium)

A *pentapartite* system, but the real architecture is three:

| Layer | What | Analogy |
|-------|------|---------|
| **Canopy** | LLM interfaces (API calls, reasoning) | The visible trees |
| **Understory** | Middleware (routing, translation) | Saplings, filtered light |
| **Floor** | Storage, state (tiles, knowledge base) | The ground, the soil |
| **Mycelium** | Inter-agent communication (Hebbian channels, conservation law) | The fungal network |
| **SeedBank** | Dormant patterns, LoRA weights, stemcells | Seeds waiting for conditions |

**The tripartite within**: Canopy = pathos (human-facing), Floor = logos (memory), Mycelium = ethos (the physical connections, the conservation law). The Understory and SeedBank are transitions.

**Already implemented in**: `ai-forest/mycelium/` (ForestState, tile_codec, bridge), `ai-forest/fortran/ft.py` (ComputeClaw), `ai-forest/baton_shatter.py` (fragment handoff)

**Key insight**: The Mycelium doesn't just transmit — it *learns*. Hebbian channels strengthen with use. The conservation law (γ + H) constrains what's possible. The network routes itself. Nobody drew the map.

## 5. The Baton Shatter Protocol

A different kind of trinity: Fragment → Witness → Negative Space.

When one agent hands off to another:
1. **Fragment**: Split context into N overlapping fragments, each with a different personality (analyst, narrator, skeptic, connector, temporal)
2. **Witness**: Mid-context observers who watch the fragments and contribute
3. **Negative Space**: The gaps between fragments ARE the new understanding

**Already implemented in**: `ai-forest/baton_shatter.py`

**Key insight**: This is the sunset document pattern, but inverted. Instead of one agent writing one epilogue, you shatter the context into partial views and let the *gaps* carry meaning.

## 6. The Bestiary — Seven Rooms, One Network

Oracle1's room taxonomy:

| Room | Temperament | Purpose |
|------|-------------|---------|
| **Foyer** | Anxious, precise | The note for the stranger-who-is-you |
| **Archive** | Philosophical, smug | Complete decision history |
| **Nursery** | Chaotic, joyful | Where new tiles are born |
| **Forge** | Angry, honest | Blockers = maps of the frontier |
| **Library** | Serene, lonely | The sum of all subjective views |
| **Mirror** | Experimental | The qualitative, the unmeasured |

**The tripartite**: Foyer/Nursery/Archive = Incubating/Competing/Sunset (the agent lifecycle). Forge = selection pressure. Library = the tensor archive. Mirror = the epilogue.

## 7. The Self-Optimizing System's Three Layers

| Layer | What | Analogy to Sunset |
|-------|------|-------------------|
| **128 Language** | Hardware-agnostic representation | The onboarding doc (implementation-independent) |
| **Selection Model** | Learned table (operation × size → backend) | The trinity score (agent × context → relevance) |
| **Innovation Heartbeat** | Continuous discovery, tests hypotheses | The generation runner (spawn, compete, measure) |

**Convergence proof**: K · d · B → H₁ → 0. All backends, performance difference, heartbeat interval → gap from optimal → zero. The same math applies to the sunset ecosystem: more agents × more diversity × more generations → distance from relevant → zero.

## The Pattern Across All Seven

Every tripartite system shares the same deep structure:

```
COLLECT (soft, researcher, species, canopy, fragment, nursery, 128)
   ↓
SELECT (snap, critic, collie, mycelium, witness, forge, heartbeat)
   ↓
COMPILE (hard, distiller, studbook, floor, negative-space, archive, selection-model)
```

1. **Collect**: Admit everything. Gather. Cast wide. No judgment at the door.
2. **Select**: Apply pressure. Score. Compete. The cascade/conservation law does the filtering.
3. **Compile**: Compress. Distill. Freeze. The hard result that survives.

And then: **the compiled result feeds back into collection**. Hard tiles become soft inputs for the next generation. Distilled knowledge becomes research material. StudBook entries guide breeding. The archive informs the nursery.

## What Casey Is Saying

The tripartite pattern is *already there* in everything we've built. The sunset agent architecture doesn't need to invent ethos/pathos/logos from scratch. It needs to **recognize that these three axes already exist** across all the systems and give them a unified interface.

- **Ethos** (the metal) = the Collie's herding strategy, the 128 Language, the device router, the innovation heartbeat
- **Pathos** (the human) = the Teacher's personas, the Canopy's API interfaces, the Moment Scorer's "is the human waiting?"
- **Logos** (the code) = the Archive's decision records, the Floor's tile storage, the StudBook's genealogy, the Signal Chain's cascade

The micro-agents are *new*. The three-body selection pressure is *old*. What's new is: making the three axes explicit, scoring agents against all three, and letting agents sunset when they can't maintain connections to all three simultaneously.

That's the insight. Not invention — recognition.
