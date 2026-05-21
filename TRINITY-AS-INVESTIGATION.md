# TRINITY AS INVESTIGATION — Not Scoring, But Grounding

> *Each axis isn't a score. It's a question the agent must actually answer.*

## The Misunderstanding

The trinity score looks like: `score = ethos × pathos × logos`

But that's the OUTPUT, not the process. The process is three INVESTIGATIONS:

## Ethos: The Hardware Functional

**Question**: What is the actual fastest compute path for THIS task on THIS hardware RIGHT NOW?

This is NOT:
- "Does the agent use the GPU?" (too vague)
- "Is the agent efficient?" (meaningless without measurement)

This IS:
- The agent runs the innovation heartbeat on the actual hardware
- It discovers: Fortran wins at 1000×1000, NEON wins at gradient ops, CUDA wins at penrose
- It MEASURES, not assumes
- The result is a functional: `f(task, size, hardware_state) → backend, latency, throughput`

The ethos investigation produces a **concrete compute plan** for this specific task on this specific hardware at this specific moment. Not a score. A plan.

*Maps to*: Self-optimizing system (Paper 18), Know-thyself (Paper 2), device-router

## Pathos: The Ground-Truth-For-Now

**Question**: What does THIS user need RIGHT NOW, given their current best assumptions?

"Ground-truth-for-now" is the key phrase. These are:
- **Hardcoded** — baked into the system, treated as fact
- **Temporary** — true until proven wrong, then recompiled
- **User-specific** — Casey's ground truth is different from yours

Examples of ground-truth-for-now:
- "The RTX 4050 is my GPU" (true until hardware changes)
- "I'm building a maritime intelligence system" (true until the project pivots)
- "ONNX FP32 is faster than INT8 for micro-models" (true until proven otherwise at a different scale)
- "Python 3.10 is my runtime" (true until upgrade)

The pathos investigation:
- Identifies which ground-truth-for-now assumptions are RELEVANT to this task
- Checks whether the agent's output is consistent with those assumptions
- Detects when a ground-truth-for-now might be WRONG (evidence contradicts it)
- Measures: did the agent actually solve the user's problem, or just a technically correct problem?

When a ground-truth-for-now breaks: the tile snaps, the assumption gets recompiled, the system updates.

*Maps to*: LucidDreamer domain adapters (verify() method), autoclaw critic agent, Oracle1's snap

## Logos: The Institutional Memory

**Question**: What does the codebase actually support? What decisions were made and why?

The code IS the accumulated wisdom. Not documentation — code. Every function signature is a decision. Every import is a dependency. Every test is a constraint.

The logos investigation:
- Surveys the actual codebase state (files, tests, architecture patterns)
- Identifies which past decisions are relevant to this task
- Checks: can this agent's output integrate cleanly, or does it fight the grain?
- Finds: where are the TODOs, FIXMEs, HACKs? Those are the frontier.
- Reads: decision logs, generation memory, sunset documents from previous agents

A logos-strong agent doesn't just write code that works — it writes code that FITS. Code that the next agent can understand, modify, and build on. Code that respects the accumulated wisdom without being paralyzed by it.

*Maps to*: Autoclaw knowledge store, AI-forest archive room, LucidDreamer tile store, Oracle1's bestiary

## The Trinity as Methodology

```
1. INVESTIGATE ethos → produce compute_plan (measured, not assumed)
2. INVESTIGATE pathos → identify ground_truths_for_now, verify relevance
3. INVESTIGATE logos → survey codebase, find constraints, read institutional memory
4. COMBINE → can this agent's work satisfy all three simultaneously?
5. SCORE → trinity_score = does_compute_plan_work × does_user_need_exist × does_codebase_accept
```

If any investigation fails:
- Ethos fails: the compute plan doesn't fit the hardware → agent is too slow/wasteful
- Pathos fails: the agent solves a problem the user doesn't have → technically correct, practically useless
- Logos fails: the agent's output fights the codebase → works today, breaks tomorrow

## The Deeper Insight

The trinity is the SAME pattern as Soft → Snap → Hard:

1. **Ethos is the Soft Room** — the agent must explore all possible compute paths (admit everything, dial at 1.0) before selecting the best one
2. **Pathos is the Snap** — the moment the agent's output connects to a real user need (the line comes tight)
3. **Logos is the Hard Room** — the output must pass the codebase's constraints (zero holonomy, cannot be fooled)

The trinity IS the signal chain, applied to agents instead of inferences.

## What This Means for Implementation

Each agent doesn't just "have a trinity score." Each agent RUNS three investigations:

```python
class Agent:
    def investigate_ethos(self, hardware: HardwareProfile) -> ComputePlan:
        """Run the innovation heartbeat. Measure. Find the real fastest path."""
        
    def investigate_pathos(self, user: UserContext) -> list[GroundTruth]:
        """Identify which ground-truths-for-now are relevant. Verify them."""
        
    def investigate_logos(self, codebase: CodebaseState) -> IntegrationPlan:
        """Survey the code. Find constraints. Read institutional memory."""
    
    def trinity_score(self) -> float:
        """Product of three investigation results. Any failure → zero."""
        return (
            self.ethos_investigation.passed * 
            self.pathos_investigation.passed * 
            self.logos_investigation.passed
        )
```

The score is EMERGENT from the investigations, not assigned. An agent that didn't investigate gets zero — not because it's bad, but because it didn't look.
