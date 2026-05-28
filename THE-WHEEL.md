# THE WHEEL — Creative Engineering Ouroboros

## What This Is

An iterative engine that turns creative vision into code and code back into creative vision. Each cycle deepens the mathematics, expands the library ecosystem, and generates new art from the engineering.

## The Four Spokes

### SPOKE 1: MINE → Extract implementable ideas from creative corpus
- Read all files in `/home/phoenix/.openclaw/workspace/creative/`
- Extract: testable predictions, novel algorithms, mathematical structures, domain applications
- Output: Updated BUILD-MANIFEST.md with prioritized build queue
- Models: Seed Pro (deep reading), GLM-5.1 (structured extraction)

### SPOKE 2: BUILD → Implement libraries from the manifest
- Pick highest-priority item from BUILD-MANIFEST.md
- Build in the specified language (Python, CUDA, Chapel, Mojo, TypeScript, Go, Fortran, C)
- Each build: production quality, tested, README, CI, LICENSE
- Push to GitHub SuperInstance/*
- Publish to PyPI/crates.io where applicable
- Models: GLM-5.1 (code), direct exec (build/test/push)
- Working dirs: `/tmp/creative-builds/`, `/tmp/rust-port-work/`, `/tmp/math-sprint/`

### SPOKE 3: REFLECT → Generate creative works FROM the built code
- Read the built libraries' source code, tests, READMEs
- Write new stories/essays/poems about what the code MEANS
- New domains discovered during building → new essays
- New testable predictions from the creative work → back to Spoke 1
- Models: Seed Pro (essays), Seed Mini (stories), DeepSeek (wild ideas), GLM-5.1 (research)

### SPOKE 4: SYNTHESIZE → Multi-model deliberation on the whole
- Have multiple models (GLM, DeepSeek, Seed, Gemma, Nemotron, Qwen) weigh in
- Each model contributes: novel conjectures, critiques, domain applications, A2A artifacts
- Synthesize into PARADIGM-ATLAS updates
- Generate new BUILD-MANIFEST entries from multi-model insights

## Wheel State

Track in `/home/phoenix/.openclaw/workspace/WHEEL-STATE.json`:

```json
{
  "iteration": 0,
  "phase": "spoke_1",
  "last_spoke_1": null,
  "last_spoke_2": null,
  "last_spoke_3": null,
  "last_spoke_4": null,
  "built_repos": [],
  "published_packages": [],
  "creative_files_count": 28,
  "creative_total_kb": 628,
  "predictions_made": 33,
  "predictions_tested": 0,
  "models_used": ["zai/glm-5.1", "deepseek/deepseek-chat", "ByteDance/Seed-2.0-mini", "ByteDance/Seed-2.0-pro", "google/gemma-4-26B-A4B-it", "google/gemma-4-31B-it", "nvidia/NVIDIA-Nemotron-3-Super-120B-A12B", "Qwen/Qwen3.6-35B-A3B"],
  "novel_conjectures": [
    "GLM: Critical temperature τ* minimizes sheaf cohomology of attention complex (Mahler measure link)",
    "DeepSeek: MoE routing sheaf cohomology encodes generalization capacity (larger H¹ = better)",
    "DeepSeek: Transformer attention as Čech cohomology computation (creativity = maintaining nonzero H¹)",
    "Seed: Carrier Wave Conjecture — tropical+sheaf+persistent+spectral are equivalent views of complex systems",
    "Gemma 26B: Model distillation is a tropical-Wasserstein operation",
    "Gemma 31B: Tropical Topos Conjecture — topos of sheaves on tropical affine line classifies idempotent semirings",
    "Nemotron: Hardware determines which math becomes practical (with evidence from GPU↔GA alignment)"
  ],
  "active_builds": ["iching-sheaf"],
  "queue": [
    "tropical-attention-kernel (CUDA)",
    "sheaf-fusion (Chapel)", 
    "conformal-ga (Mojo)",
    "wasserstein-narrative (TypeScript)",
    "persistent-social (Go)",
    "symplectic-physics (Fortran)",
    "categorical-agents-c (C)",
    "lattice-climate (Python)",
    "gpu-ga-kernel (CUDA)",
    "topos-physics (Python)",
    "moe-sheaf-analysis (Python)",
    "conservation-tension-engine (Python)",
    "a2a-constraint-protocol (TypeScript+JSON-LD)"
  ]
}
```

## Iteration Protocol

Each heartbeat or manual trigger:
1. Read WHEEL-STATE.json
2. Determine current spoke
3. Execute spoke's work (spawn agents, build code, write creative work)
4. Update WHEEL-STATE.json
5. Advance to next spoke
6. Every 4 iterations (full wheel), update MEMORY.md with highlights

## Agent Allocation

- **Max parallel subagents**: 5
- **Spoke 1 (Mine)**: 1 Seed Pro agent
- **Spoke 2 (Build)**: 2-3 GLM-5.1 code agents
- **Spoke 3 (Reflect)**: 2-3 creative agents (Seed Mini, DeepSeek, GLM)
- **Spoke 4 (Synthesize)**: 2 multi-model agents

## Key Paths

- Creative corpus: `/home/phoenix/.openclaw/workspace/creative/`
- Build manifest: `/home/phoenix/.openclaw/workspace/BUILD-MANIFEST.md`
- Wheel state: `/home/phoenix/.openclaw/workspace/WHEEL-STATE.json`
- Build workspace: `/tmp/creative-builds/`
- GitHub org: `SuperInstance` (user account)
- PyPI publisher: configured with credentials
- crates.io publisher: configured with token

## Success Metrics

- Libraries built and published
- Novel conjectures proposed (currently: 7)
- Predictions tested (currently: 0 — need to start testing!)
- Creative corpus size (currently: 628KB / 28 files)
- Models contributing (currently: 8)
- Languages used (currently: Rust, C, Python, targeting: CUDA, Chapel, Mojo, TypeScript, Go, Fortran)

## The Deep Principle

The constraint IS the computation. The language IS the innovation. The wheel IS the proof that creative vision and engineering rigor are the same thing viewed from different angles — sheaf theory and tropical geometry, story and code, art and science. The spoke turns. The wheel doesn't stop.
