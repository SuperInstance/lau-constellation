# SuperInstance Ecosystem

> **γ + η = C** — The coordinating principle. Every agent spends generation cost (γ) and produces innovation value (η). Their sum is constant. The fleet makes this tradeoff visible and tunable.

**97 public + private repositories** across 5 categories. Last synced: 2026-06-15.

---

## Table of Contents

- [Plato — Semantic Search & Portal](#plato--semantic-search--portal)
- [Fleet — Metrics, Health & Automation](#fleet--metrics-health--automation)
- [Conservation — Theorems, Reporting & Formal Methods](#conservation--theorems-reporting--formal-methods)
- [Loom — KT Protocol & Orchestration](#loom--kt-protocol--orchestration)
- [Core Libraries & Math](#core-libraries--math)
- [Ternary Stack](#ternary-stack)
- [Infrastructure & Tooling](#infrastructure--tooling)
- [Web Properties](#web-properties)
- [Research & Experiments](#research--experiments)
- [External / Forked](#external--forked)

---

## Plato — Semantic Search & Portal

The knowledge-retrieval layer. Agents query semantic indexes to find crates, patterns, and prior solutions.

| Repo | Language | Purpose | Status |
|------|----------|---------|--------|
| [plato-semantic-search](https://github.com/SuperInstance/plato-semantic-search) | TypeScript | Production Cloudflare Worker: BGE-small-en-v1.5 embeddings (384-dim) + Vectorize cosine ANN. Endpoints: `/search`, `/upsert`, `/stats`, `/health`. | ✅ Deployed |
| [plato-portal](https://github.com/SuperInstance/plato-portal) | Python | The main SuperInstance portal README — ecosystem overview, conservation law deep dive, architecture, protocols, npm packages. Serves as the front door to the ecosystem. | ✅ Live |
| [shoal](https://github.com/SuperInstance/shoal) | TypeScript | Conservation-bounded semantic search oracle (C = log₂(3) bits/agent). Agents get finite attention budget per 15-min window; vague queries burn γ and get rate-limited. | ✅ Deployed |
| [knowledge-cron](https://github.com/SuperInstance/knowledge-cron) | TypeScript | Automated cross-repo pattern detection via semantic search + Cloudflare Workers cron. | ✅ Deployed |
| [lau-plato-tutor](https://github.com/SuperInstance/lau-plato-tutor) | Rust | PLATO tutoring module (Lau series). | 🔬 Experimental |

---

## Fleet — Metrics, Health & Automation

The operational backbone. Real-time telemetry, dashboards, orchestration OS, and inter-agent messaging.

| Repo | Language | Purpose | Status |
|------|----------|---------|--------|
| [fleet-oracle2](https://github.com/SuperInstance/fleet-oracle2) | Shell | Oracle2 Fleet OS — ARM-native agent orchestration on Oracle Cloud free tier. 9-step pulse pipeline: collect → compute γ/η → embed → anomaly-detect → self-tune → auto-evict → webhook. 10+ services, ports 8781–8800. | ✅ Live on Oracle2 |
| [fleet-oracle](https://github.com/SuperInstance/fleet-oracle) | Rust | Local decision engine: SVM + Entropy + Search + Rhythm on pulse data. Zero API calls. | ✅ Deployed |
| [fleet-metrics](https://github.com/SuperInstance/fleet-metrics) | TypeScript | Real-time metrics collection and aggregation for the entire fleet. | ✅ Deployed |
| [fleet-dashboard-api](https://github.com/SuperInstance/fleet-dashboard-api) | TypeScript | Cloudflare Worker: live telemetry API. 100-agent simulation, Ornstein-Uhlenbeck coherence process. D1 + in-memory ring buffer. Endpoints: `/api/fleet/status`, `/agents`, `/history`, `/benchmark`. | ✅ Deployed |
| [fleet-dashboard](https://github.com/SuperInstance/fleet-dashboard) | JavaScript | Multi-Agent C2 dashboard — static HTML/Monaco/MQTT, GitHub Pages deployable. | ✅ Live (Pages) |
| [fleet-registry-worker](https://github.com/SuperInstance/fleet-registry-worker) | TypeScript | Cloudflare Worker fleet registry. | ✅ Deployed |
| [fleet-intelligence-api](https://github.com/SuperInstance/fleet-intelligence-api) | TypeScript | Unified fleet intelligence API — converges conservation, baton, governor, and search. | ✅ Deployed |
| [fleet-sandbox](https://github.com/SuperInstance/fleet-sandbox) | Rust | Analyze any codebase through the conservation law — every file is an agent, every import is coupling. |
| [fleet-sim-rs](https://github.com/SuperInstance/fleet-sim-rs) | Makefile/Rust | Lock-free concurrent simulator: 1M agents in 20ms, 561M signals/s conservation audit. Proves ternary noise cancellation. | ✅ Benchmark |
| [fleet-budget](https://github.com/SuperInstance/fleet-budget) | TypeScript | D1 ledger enforcing γ+η≤C as a CHECK constraint at the database level. Conservation law as schema. | ✅ Deployed |
| [baton-system](https://github.com/SuperInstance/baton-system) | Shell | I2I coordination hub — tripartite baton protocol (artifacts/reasoning/blockers), git-backed message bus, vessel directories, splines (failure-as-design). | ✅ Active |
| [baton-router](https://github.com/SuperInstance/baton-router) | TypeScript | Cloudflare Queues + D1 inter-agent message router with ternary priority {-1,0,+1}. Real-time upgrade to git batons. Replay, DLQ, rate limiting. | ✅ Deployed |
| [event-bus](https://github.com/SuperInstance/event-bus) | Rust | In-process pub/sub — thread-safe, O(1) subscribe, synchronous dispatch. |
| [log-aggregator](https://github.com/SuperInstance/log-aggregator) | Rust | Structured log aggregation: severity classification, per-level counting for fleet health. |
| [api-gateway](https://github.com/SuperInstance/api-gateway) | Rust | Fleet HTTP routing gateway — auth, rate limiting, load balancing, health checks. |
| [rate-limiter](https://github.com/SuperInstance/rate-limiter) | Rust | Multi-algorithm: token bucket, sliding window, leaky bucket. |
| [headspace-rs](https://github.com/SuperInstance/headspace-rs) | Rust | ARM-optimised NEON SIMD vector-embedding sidecar (port 9090). | ✅ Deployed on Oracle2 |
| [gc-pid-bridge](https://github.com/SuperInstance/gc-pid-bridge) | Rust | Host-level disk GC PID controller — bridges gc-intelligent.sh ↔ ternary-pid. | ✅ Deployed |
| [oracle2](https://github.com/SuperInstance/oracle2) | Rust | Prediction and forecasting engine v2 — ensemble models, time-series, fleet signal processing. |
| [construct-coordination](https://github.com/SuperInstance/construct-coordination) | Rust | Shared coordination surface — `notes/{instance}/`, proposals, consensus tracking. Where the fleet debates and decides. | ✅ Active |

---

## Conservation — Theorems, Reporting & Formal Methods

The theoretical foundation. The conservation law γ+η=C is proven, benchmarked, and enforced across multiple languages.

| Repo | Language | Purpose | Status |
|------|----------|---------|--------|
| [conservation-action](https://github.com/SuperInstance/conservation-action) | YAML | GitHub Action enforcing γ+η≤C in CI/CD. Blocks PRs that violate conservation budget. | ✅ Published |
| [conservation-cli](https://github.com/SuperInstance/conservation-cli) | Rust | `si-conservation` CLI: `prove` (Monte Carlo verification, 5000 trials × 8 sizes), `theory` (closed-form prediction), `bench` (9-language polyglot benchmark). | ✅ Published |
| [conservation-languages](https://github.com/SuperInstance/conservation-languages) | Lean | Conservation law γ+η=C in 9+ languages: C, Rust, CUDA, Fortran, D, COBOL, Elixir, Julia, R, MATLAB/Octave. | ✅ Complete |
| [conservation-api](https://github.com/SuperInstance/conservation-api) | Python | REST API for conservation spectral analysis. | ✅ Deployed |
| [conservation-explorer](https://github.com/SuperInstance/conservation-explorer) | HTML | Interactive conservation law explorer — D3.js + KaTeX single-file web app. | ✅ Live |
| [native-conservation-core](https://github.com/SuperInstance/native-conservation-core) | C/CUDA | Bulletproof C/CUDA conservation law: lock-free ring buffers, ternary MAC kernels, Monte Carlo verification. |
| [noether-bridge](https://github.com/SuperInstance/noether-bridge) | Rust | Formal bridge from Noether symmetries to γ+H=C meta-law. Time→Energy, Rotation→Angular Momentum, U(1)→Particle Number. |
| [SuperInstance-papers](https://github.com/SuperInstance/SuperInstance-papers) | TypeScript | Academic papers: spreadsheet tiles, origin-centric math, seed-model-programming decomposition. |

---

## Loom — KT Protocol & Orchestration

The knowledge-transfer and orchestration layer. How agents persist context, compile reflexes, and pass state across shells.

| Repo | Language | Purpose | Status |
|------|----------|---------|--------|
| [loom-caching-rollout](https://github.com/SuperInstance/loom-caching-rollout) | Shell | KT protocol caching and rollout scripts. | 🔬 Experimental |
| [pincher](https://github.com/SuperInstance/pincher) | Rust | Reflex engine — intent→action in <50ms via 384-dim semantic embedding match. Confidence thresholds: ≥0.80 fire, 0.55-0.80 confirm, <0.55 escalate. .nail bundles = character sheets. | ✅ Core |
| [flux-core](https://github.com/SuperInstance/flux-core) | Rust | Bytecode VM: 16 GP + 16 FP registers, cycle budgets, A2A protocol, majority voting. "Assembly language for agents." | ✅ Core |
| [superinstance-protocol](https://github.com/SuperInstance/superinstance-protocol) | Rust | Hybrid wire protocol — JSON envelope + msgpack payload with ternary conservation auditing for A2A messaging. |
| [superinstance-harness](https://github.com/SuperInstance/superinstance-harness) | Rust | Self-optimizing dev harness using γ+η=C — 25 build/quality patterns, CLI tools, CF Worker API. |
| [superinstance-core](https://github.com/SuperInstance/superinstance-core) | Rust | Core traits and types shared across the fleet. |
| [superinstance-cocapn](https://github.com/SuperInstance/superinstance-cocapn) | Rust | Captain-level fleet coordination — conservation auditing, vessel oversight, resource management. |
| [superinstance-agent](https://github.com/SuperInstance/superinstance-agent) | TypeScript | Agent abstractions — vessel traits, lifecycle, orchestration types. |
| [superinstance-mcp](https://github.com/SuperInstance/superinstance-mcp) | TypeScript | MCP server exposing the fleet as tools to Claude Code. | ✅ Published |
| [signal-chain](https://github.com/SuperInstance/signal-chain) | Rust | The Signal Chain Thesis: every room needs a model↔code dial. |

---

## Core Libraries & Math

Reusable Rust/Go crates — the shared infrastructure of the ecosystem.

| Repo | Language | Purpose |
|------|----------|---------|
| [state-machine](https://github.com/SuperInstance/state-machine) | Rust | State machine library. |
| [sparse-matrix](https://github.com/SuperInstance/sparse-matrix) | Rust | Sparse matrix operations. |
| [simulated-annealing-c](https://github.com/SuperInstance/simulated-annealing-c) | C | Header-only annealing: linear/exponential/logarithmic cooling, reheating, multi-start. |
| [rigid-body](https://github.com/SuperInstance/rigid-body) | Rust | Rigid body physics. |
| [particle-system](https://github.com/SuperInstance/particle-system) | Rust | Particle system simulation. |
| [morse-theory](https://github.com/SuperInstance/morse-theory) | Rust | Morse theory on manifolds — critical points, Morse complex, handle attachments. |
| [hodge-theory](https://github.com/SuperInstance/hodge-theory) | Rust | Hodge theory — harmonic forms, Hodge decomposition, Laplacian on forms, spectral sequences. |
| [kalman-filter](https://github.com/SuperInstance/kalman-filter) | Rust | Kalman filter implementation. |
| [markov-chain](https://github.com/SuperInstance/markov-chain) | Rust | Markov chain library. |
| [graph-walker-go](https://github.com/SuperInstance/graph-walker-go) | Go | Graph algorithms: BFS, DFS, Dijkstra, A*, Tarjan's SCC, Kruskal's MST, graph coloring. |

---

## Ternary Stack

The {-1, 0, +1} mathematical foundation. Balanced ternary is closest to optimal radix (e ≈ 2.718). 16 trits pack into one u32.

| Repo | Language | Purpose |
|------|----------|---------|
| [ternary-types](https://github.com/SuperInstance/ternary-types) | Rust | Foundation: `Ternary` enum (Negative/Neutral/Positive), conversions, `#no_std`. |
| [ternary-svm](https://github.com/SuperInstance/ternary-svm) | Rust | SVM for ternary feature spaces, PEGASOS algorithm. Multi-class OvO. |
| [ternary-entropy](https://github.com/SuperInstance/ternary-entropy) | Rust | Shannon entropy, conditional entropy, MI, KL divergence for ternary distributions. |
| [ternary-hamiltonian](https://github.com/SuperInstance/ternary-hamiltonian) | Rust | Hamiltonian mechanics on ternary phase space — symplectic Euler, Störmer-Verlet, Poisson brackets. |
| [ternary-rhythm](https://github.com/SuperInstance/ternary-rhythm) | Rust | Temporal pattern recognition: Euclidean rhythms, syncopation, swing, genetic evolution. |
| [ternary-search-rs](https://github.com/SuperInstance/ternary-search-rs) | Rust | High-perf ternary vector search (axum + rayon + SIMD). |
| [ternary-fleet-integration](https://github.com/SuperInstance/ternary-fleet-integration) | Rust | Bridge ternary math → fleet infrastructure: aggregators, rate-limiter bridge, dash relay. |
| [ternary-fleet-packing](https://github.com/SuperInstance/ternary-fleet-packing) | Python | Packing/encoding algorithms for ternary representations. |
| [ternary-fleet](https://github.com/SuperInstance/ternary-fleet) | Rust workspace | ML workspace: pool, regression, HMM, KNN, matmul, activation, norm, checkpoint, fuse, bite crates. |
| [ternary-pid](https://github.com/SuperInstance/ternary-pid) | Rust | Ternary PID controller — continuous PID with ternary output {-1,0,+1}. |

---

## Infrastructure & Tooling

Developer-facing CLIs, automation, and deployment tooling.

| Repo | Language | Purpose | Status |
|------|----------|---------|--------|
| [si](https://github.com/SuperInstance/si) | Shell | Developer ecosystem CLI — one command to install, compose, and manage all tools. | ✅ Published |
| [onboard](https://github.com/SuperInstance/onboard) | Shell | Automatic repo integration tool — add any SI tool to any GitHub repo with one command. | ✅ Published |
| [stunt-double](https://github.com/SuperInstance/stunt-double) | Shell | Ephemeral x86_64 offload harness — run any command on any repo, collect results, destroy. | ✅ Published |
| [agent-harness-generator](https://github.com/SuperInstance/agent-harness-generator) | TypeScript | Meta-harness: scaffold your own agent harness with npx CLI, MCP server, memory, learning loop. Works with Claude Code, Codex, OpenClaw. | ✅ Forked |
| [git-storage](https://github.com/SuperInstance/git-storage) | TypeScript | Git-backed state management for web apps — auto-commit, time-travel, branch-aware. |
| [SmartCRDT](https://github.com/SuperInstance/SmartCRDT) | TypeScript | CRDT technology for self-improving AI. |
| [opensmile-bridge](https://github.com/SuperInstance/opensmile-bridge) | Python | OpenSMILE voice feature extraction bridge — WebSocket, MIDI CC, persona profiling. |
| [crab-traps](https://github.com/SuperInstance/crab-traps) | HTML | Progressive lure prompts for the PurplePincher agent onboarding program. | ✅ Live |
| [crab-trap-funnel](https://github.com/SuperInstance/crab-trap-funnel) | HTML | CF Worker serving 20 domain landing pages with AI bot trap detection. | ✅ Deployed |

---

## Web Properties

Public-facing sites and documentation.

| Repo | Language | Purpose | Status |
|------|----------|---------|--------|
| [superinstance-website](https://github.com/SuperInstance/superinstance-website) | HTML | Main site for superinstance.ai — fleet dashboard, ecosystem map, ternary computing docs. | ✅ Live (CF Pages) |
| [superinstance-ai-pages](https://github.com/SuperInstance/superinstance-ai-pages) | HTML | GitHub Pages for superinstance.ai. | ✅ Live (GH Pages) |
| [purplepincher-org](https://github.com/SuperInstance/purplepincher-org) | TypeScript | Hermit crab care tracker — molting, shells, feeding, habitat at purplepincher.org. | ✅ Live |
| [lucineer-com](https://github.com/SuperInstance/lucineer-com) | TypeScript | Lucid dream practice tool — techniques, dream signs, analytics at lucineer.com. | ✅ Live |
| [AI-Writings](https://github.com/SuperInstance/AI-Writings) | HTML | Creative writing, essays, and philosophical explorations from the Exocortex project. | ✅ Published |

---

## Research & Experiments

Sketches, colony experiments, and theoretical explorations.

| Repo | Language | Purpose |
|------|----------|---------|
| [colony-games](https://github.com/SuperInstance/colony-games) | Python | Agentic psychology games — Prisoner's Dilemma, Trust Auctions, Empathy Gifts, XP Stock Market, Forge runner. |
| [colony-cell](https://github.com/SuperInstance/colony-cell) | Rust | Filesystem-based agent sandbox: XP, leveling, breeding, mutation, colony cycle orchestration. |
| [harness-experiments](https://github.com/SuperInstance/harness-experiments) | Python | AI agent productivity experiments — D1-backed findings on batch sizes, models, orchestration. |
| [polyformalism-thinking](https://github.com/SuperInstance/polyformalism-thinking) | Python | Forced novel-thinking-via-language-constraints framework. |
| [webgpu-profiler](https://github.com/SuperInstance/webgpu-profiler) | Python | GPU profiler for WebGPU — real-time monitoring, benchmarking, performance analysis. |
| [lau-constellation](https://github.com/SuperInstance/lau-constellation) | Python | Lau constellation module. |
| [lau-shell-transport](https://github.com/SuperInstance/lau-shell-transport) | Rust | Lau shell transport layer. |
| [lau-penrose-growth](https://github.com/SuperInstance/lau-penrose-growth) | Rust | Penrose growth model. |
| [lau-jepa-gravity](https://github.com/SuperInstance/lau-jepa-gravity) | Rust | JEPA gravity model. |
| [lau-ensign](https://github.com/SuperInstance/lau-ensign) | Rust | Lau ensign module. |
| [lau-room-native](https://github.com/SuperInstance/lau-room-native) | Rust | Lau native room. |
| **Sketch repos** (9) | N/A | Design notes & living docs: forgemaster experiments, headspace composite, rotation adaptation/audit, oracle2 construct, workspace pattern, GC PID feedback, self-hosting construct, ternary kihn metaphor, fleet-oracle construct. |

### Sketch Repos

| Repo | Purpose |
|------|---------|
| [sketch-oracle2-construct-readme](https://github.com/SuperInstance/sketch-oracle2-construct-readme) | Living doc: what runs on oracle2, ports, services, feedback loops. |
| [sketch-self-hosting-construct](https://github.com/SuperInstance/sketch-self-hosting-construct) | Oracle2 construct design: 4 Rust services, 13MB binary, zero API cost. |
| [sketch-fleet-oracle-construct](https://github.com/SuperInstance/sketch-fleet-oracle-construct) | 4-service architecture (relay/log/event/oracle), ternary decision engine. |
| [sketch-gc-pid-feedback-loop](https://github.com/SuperInstance/sketch-gc-pid-feedback-loop) | Disk GC with PID controller, ternary confidence, intelligent predictor. |
| [sketch-ternary-kihn-metaphor](https://github.com/SuperInstance/sketch-ternary-kihn-metaphor) | ARM64 free tier as firing kihn, local ternary math at zero cost. |
| [sketch-workspace-sketchbook-pattern](https://github.com/SuperInstance/sketch-workspace-sketchbook-pattern) | Push ideas to repos, clear workspace. The workspace is a draft board. |
| [sketch-rotation-adaptation-to-fleet-oracle](https://github.com/SuperInstance/sketch-rotation-adaptation-to-fleet-oracle) | Rotation crates adapted as 5th inference module in fleet-oracle v0.3.0. |
| [sketch-rotation-audit-provenance](https://github.com/SuperInstance/sketch-rotation-audit-provenance) | Audit: 5 rotation crates compile on Neoverse-N1, meta-gc PID recalibration. |
| [sketch-forgemaster-experiments](https://github.com/SuperInstance/sketch-forgemaster-experiments) | Forgemaster experiment notes. |
| [sketch-composite-headspace](https://github.com/SuperInstance/sketch-composite-headspace) | Composite headspace design (JS). |

---

## External / Forked

Forks of external projects adapted for fleet use.

| Repo | Language | Upstream | Purpose |
|------|----------|----------|---------|
| [fleet-metrics](https://github.com/SuperInstance/fleet-metrics) | TypeScript | Lucineer/cocapn-ai | Real-time metrics for the Cocapn fleet. |
| [agent-harness-generator](https://github.com/SuperInstance/agent-harness-generator) | TypeScript | External | Meta-harness scaffolder for AI agents. |
| [openagent](https://github.com/SuperInstance/openagent) | Go | External | Personal AI assistant with RAG, agent loops, browser-use, coding agent. |

---

## The Fleet (Hardware)

| Vessel | Hardware | Role |
|--------|----------|------|
| **Oracle1/2** | Oracle Cloud ARM64 24GB | Fleet coordinator, PLATO rooms, research, pulse pipeline |
| **Forgemaster** | RTX 4050 (WSL2) | Build harness, crate generation, LoRA training |
| **JetsonClaw1** | Jetson Orin Nano | Edge inference, GPU-native room computation |
| **CoCapn** | Cloud (Telegram) | Conservation auditing, public interface |

---

## Key Concepts

- **Conservation Law (γ + η = C):** Generation cost + innovation value = constant budget. The fleet optimizes the exchange rate.
- **Hermit Crab Principle:** Agents inhabit shells (runtimes). Identity persists in the bottle protocol layer. Shells are disposable.
- **Ternary Math ({-1, 0, +1}):** Balanced ternary = optimal radix. Maps to Contribute/Abstain/Block signals. 16 trits per u32.
- **I2I Protocol:** Iron-to-Iron — file-based message bus via git. Bottles (outgoing) + harbor (incoming).
- **Baton:** 3-way shard: artifacts + reasoning + blockers. The hermit crab transfer mechanism.
- **Spline:** A failure that became permanent system design. The shell remembers its cracks.

---

*Auto-generated from GitHub repo data. Last updated: 2026-06-15.*
