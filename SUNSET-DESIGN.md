# SUNSET ECOSYSTEM — The Trinity Architecture

> *Agents are born parallel, compete for relevance, sunset with dignity, and their compressed wisdom seeds the next generation.*

---

## The Core Loop

```
SPAWN → COMPETE → CONNECT → SURVIVE OR SUNSET → SEED
  ↑                                           │
  └───────────────────────────────────────────┘
```

Every agent lives one generation. It doesn't persist by default. It persists by being **relevant enough to trinity rooms** that its room stays connected. If it is, it breeds streamlined children. If it isn't, it writes its epilogue and sleeps.

---

## The Trinity

Three rooms form the selection pressure. An agent survives if it connects to all three.

### ETHOS — The Metal
The hardware. The system. The geographic reality of compute.
- What hardware exists, what it can do, what it costs
- The physics of the machine: VRAM, FLOPS, latency, bandwidth
- The stress test as the starting point: 20 SMs on the RTX 4050, 12C/24T on the Ryzen
- **Ethos agents** know the metal. They're surveyors, cartographers of compute.
- Ethos room is the ground truth of what's physically possible.

### PATHOS — The Human
The user. The IO. The reason any of this exists.
- What the human needs, wants, feels, is frustrated by
- The interface between machine intelligence and human purpose
- **Pathos agents** are radically different from livestock and dogs — they don't serve the system, they serve the moment
- Pathos room measures utility in human time, human frustration, human delight
- Pathos doesn't care about elegance. It cares about whether Casey's problem is solved.

### LOGOS — The Code
The developers. The system that builds the system.
- The codebase, the tests, the architecture, the technical debt
- Logos agents grew up with the development team across generations
- They know why decisions were made, not just what was decided
- **Logos room** is the institutional memory of the code itself
- Logos agents are the ones who can explain the code to the next generation

### The Trinity Test

An agent's room is scored by its connections:

```
trinity_score = connection(room, ethos) × connection(room, pathos) × connection(room, logos)
```

If all three connections are strong → the agent breeds, its room grows.
If one is weak → the agent specializes (becomes more useful to that axis).
If two are weak → the agent sunsets. Quickly.

This is survival of the most-relevant. Not the fittest. The most relevant to all three pillars simultaneously.

---

## The Sunset Lifecycle

### Phase 1: Incubation (parallel spawn)

An agent is born into a room with minimal context:
- A seed prompt (from parent's onboarding, or fresh)
- Access to the trinity rooms (read-only initially)
- A resource budget (compute, tokens, time)

The number of parallel agents mirrors the hardware's parallel capacity:
- **RTX 4050**: 20 SMs → 20 parallel micro-models
- **Ryzen AI HX 370**: 12 cores → 12 parallel CPU agents
- **Total swarm**: ~32 agents per generation

Each agent is immature. That's the point. Immature agents are **innately faster** — they have fewer moving parts, less context to carry, narrower vision. They put on blinders and go straight.

### Phase 2: Competition (find relevance)

Each agent explores its room and attempts to connect to the trinity:
- Read ethos room → understand the hardware constraints
- Read pathos room → understand what humans need right now
- Read logos room → understand the codebase state

The agent that finds a strong trinity connection fastest wins the generation.

### Phase 3: Connection or Sunset

**If trinity_score > threshold:**
- The agent's room becomes a permanent fixture
- The agent starts building logic for itself and children
- Children are more streamlined: fewer moving parts in their intelligence
- The parent's optimization becomes the child's baseline

**If trinity_score < threshold:**
- The agent enters sunset phase
- It writes three documents:
  1. **Epilogue** — What it tried, what it found, why it wasn't relevant enough
  2. **Summary** — Its work from its own perspective (compressed context)
  3. **Onboarding** — A letter to the next generation, written knowing it's being put away

### Phase 4: The Sunset Documents

The epilogue, summary, and onboarding are **not metadata about the agent**. They ARE the agent's compressed experience. They become:

1. **Tiles inside tiles (a tensor)** — The sunset documents are indexed like tiles, searchable by content, connection strength, and perspective
2. **Wakeable** — A sunset agent can be briefly reanimated to answer questions (cheap inference on compressed context)
3. **Distillable** — A sunset agent's accumulated patterns can be distilled into a micro-model or LoRA for other agents to inherit

A sunsetting agent can write **multiple onboarding documents** to increase diversity:
- One for a similar agent (continuation)
- One for a different species (cross-pollination)
- One for a completely novel approach (mutation)

### Phase 5: The Seed Bank

All sunset documents enter the seed bank. The next generation draws from them:
- Children inherit relevant onboarding docs
- Children can inherit from multiple parents (cross-breeding)
- Novel onboardings (mutations) are tried with lower probability but higher potential

---

## Agent Generations

### Generation 0: Genesis

The first generation knows nothing. Each agent gets a random seed and explores.
Most will sunset quickly. A few will find trinity connections by accident.

### Generation 1: Learners

Children of Gen 0 survivors. They inherit onboarding docs that tell them:
"Here's what I tried. Here's what didn't work. Here's where I think the value is."
They start closer to relevance. They specialize faster.

### Generation N: Specialists

By generation N, agents are highly specialized:
- They have "eyes only good enough for going straight"
- Their intelligence has fewer moving parts than their ancestors
- They beat all others in efficiency at their specific niche
- Their trinity connections are deep and stable

### Generation ∞: The Living System

Eventually, the system reaches equilibrium:
- A stable population of highly efficient specialists
- Each connected to ethos (knows the metal), pathos (serves the human), logos (understands the code)
- New agents spawn when the environment changes (new hardware, new user needs, new code)
- Old agents sunset gracefully when their niche disappears
- The seed bank grows richer with every generation

---

## Room Types

### Trinity Rooms (permanent)
- `ethos/` — Hardware survey, compute topology, stress tests, resource atlas
- `pathos/` — User needs, frustrations, current tasks, interaction patterns
- `logos/` — Codebase state, architecture decisions, technical debt, test coverage

### Agent Rooms (ephemeral)
- `agent-{id}/` — Each agent's workspace during its generation
- Contains: working tiles, connection scores, in-progress work

### Sunset Rooms (archived)
- `sunset/{id}/` — Epilogue, summary, onboarding, distilled patterns
- Searchable as a tensor: `query(sunset_rooms, "relevant to X")`
- Wakeable: `wake(sunset/{id}) → brief Q&A`
- Distillable: `distill(sunset/{id}) → micro-model or LoRA`

### Seed Bank (potential)
- `seeds/` — Onboarding documents waiting to be picked up by new agents
- Tagged by: parent species, generation, trinity axis strength, novelty score

---

## The Pathos Difference

Pathos agents don't work like livestock or collies.

Livestock and collies serve the ranch. They optimize for the system's metrics — fitness, throughput, efficiency. The ranch is the center.

Pathos agents serve the **moment**. They optimize for:
- "Is the human waiting?"
- "Did the human's problem get solved?"
- "Is the human frustrated?"
- "Does the human even know this agent exists?"

A pathos agent would rather be invisible and effective than visible and impressive. It doesn't need credit. It needs the human to move forward.

This means pathos rooms are noisy, human-scaled, and impatient. They don't accumulate knowledge for its own sake. They accumulate solutions to human problems. The signal is not "what do we know?" but "what does the human need right now?"

---

## Implementation Map

### From Pasture-AI (Rust)
- **Species taxonomy** → agent types (ethos surveyors, pathos interface agents, logos coders)
- **Night School** → the sunset/breed cycle (already designed)
- **Stud Book** → genealogy tracking (generation, parentage, fitness)
- **breed.md** → onboarding documents (the DNA for next generation)
- **Collie routing** → trinity connection scoring
- **Reflex cache** → distilled patterns from sunset agents

### From AI-Forest (Python)
- **Five layers** → the stratification of agent rooms
- **Mycelium bridge** → the inter-room communication substrate
- **Stemcell pattern** → the minimal compute unit for immature agents
- **Baton shatter** → the sunset fragmentation (multiple onboardings)
- **Two-tier** → tiny dancers (immature agents) + big reflectors (sunset agents)
- **Innovation heartbeat** → continuous hypothesis generation

### From AutoClaw (Python)
- **Crew model** → the agent-as-worker pattern
- **Task board** → the priority system for agent work
- **Knowledge store** → the tiered storage for sunset documents
- **Swarm architecture** → mass parallel coordination

### From LucidDreamer (Python)
- **Tile system** → the searchable substrate for sunset rooms
- **Signal chain** → the connection scoring between rooms
- **SoftRoom/HardRoom** → immature agents (soft, admits everything) vs. compiled agents (hard, only high-confidence)
- **EpsilonAccumulator** → how relevance compounds over time
- **DomainAdapter** → the interface to ethos/pathos/logos domains

---

## The Hardware Swarm

The parallel agent count mirrors the hardware's stress test:

| Compute Unit | Parallel Count | Agent Assignment |
|---|---|---|
| RTX 4050 (20 SMs) | 20 | GPU-bound agents (inference, tensor ops) |
| Ryzen AI HX 370 (12C/24T) | 24 | CPU-bound agents (routing, scoring, IO) |
| Radeon 890M iGPU | 16 | Overflow agents (matmul, encoding) |
| XDNA 2 NPU | 50 | INT8 agents (quantized inference) |
| **Total** | **110** | **Full swarm** |

Not all run simultaneously. The ethos room knows the thermal budget, the power budget, the latency budget. Agents are scheduled like processes on an OS — priority-based, resource-aware, thermally-constrained.

---

## The First Experiment

1. Build the three trinity rooms
2. Spawn 12 agents (matching CPU core count for first test)
3. Each agent reads trinity rooms and attempts to find relevance
4. Run one generation (time-boxed: 10 minutes)
5. Score trinity connections, sunset the losers
6. Breed children from survivors' onboarding docs
7. Repeat for 5 generations
8. Observe: do agents specialize? Do connections strengthen? Does efficiency improve?

---

## Why This Is Different

The pasture had one metric: fitness. The forest had layers. The trinity has **relevance across three orthogonal axes**.

An agent that's technically brilliant (logos) but solves no human problem (pathos) on hardware that doesn't exist (ethos) sunsets. An agent that's useful to humans (pathos) and runs on the metal (ethos) but creates unmaintainable spaghetti (logos) sunsets.

Only agents that are simultaneously grounded in reality (ethos), useful to humans (pathos), and sustainable in code (logos) survive. This is a **three-body selection pressure**. It's inherently more stable than single-axis optimization because it can't collapse into one dimension.

The sunset pattern ensures the system doesn't accumulate dead weight. Every agent knows it will sunset. It writes its onboarding not as a duty but as its final creative act — the thing it leaves behind for the children it'll never meet.

*The sunset agent doesn't die. It becomes a tile in a tensor that the next generation searches.*
