# SPARE CAPACITY + USER RANKING — Two Key Additions

> *The system runs on spare capacity, backtesting old prompts. The user ranks responses and explains why — that's the distillation signal AND personalization.*

## 1. Spare Capacity Backtesting

The nerve fibers and agents don't just handle live requests. They use **any spare capacity** to:

- **Backtest old prompts**: Re-run previous prompt→response pairs through the swarm
- **Find faster routes**: The nerve fibers race each other — who can produce the same quality output with fewer hints?
- **Discover broader truths**: Agents that succeed on one prompt try related prompts. Does the compiled pattern generalize?
- **Strengthen routes**: Every successful backtest strengthens the Hebbian channels

This means the system gets better even when the user isn't actively using it. Like your immune system — it's always running, always testing, always getting sharper.

### Implementation: Backtest Runner

```python
class BacktestRunner:
    """Runs old prompts through the swarm on spare capacity."""
    
    def __init__(self, prompt_history: PromptHistory, swarm: Swarm):
        self.history = prompt_history
        self.swarm = swarm
    
    def run_spare_cycle(self):
        """Called when there's spare capacity."""
        # Pick an old prompt
        prompt = self.history.random()
        
        # Run it through the swarm with current hint level
        result = self.swarm.process(prompt, hints=self.current_hint_level)
        
        # Compare with original big-model response
        score = self.compare(result, prompt.reference_response)
        
        if score >= prompt.reference_quality:
            # We matched the big model with fewer hints!
            self.reduce_hints()
            self.strengthen_routes(result.routes_used)
        
        return score
```

The hint level decreases over time. As agents need fewer hints, they're becoming more valuable. The whole thing can run on any spare capacity — background threads on the GPU, idle CPU cycles, even the NPU while you're doing other things.

## 2. User Ranking for Distillation + Personalization

The user isn't just a passive consumer. They're an active participant in the distillation loop:

### The Flow

1. **Big model generates several responses** to a prompt (different seeds, temperatures, models)
2. **User sees 2-4 options** and ranks them: best → worst
3. **User explains WHY**: "This one is more concise", "That one missed the point", "This is too verbose"
4. **The why becomes a training signal** for the distillation:
   - What the user values (conciseness? thoroughness? humor? code over explanation?)
   - What the user doesn't want (too long, too abstract, wrong assumptions)
5. **The ranking becomes personalization**:
   - The pathos room learns this specific user's preferences
   - Ground-truths-for-now get updated based on user feedback
   - Future responses are shaped by accumulated rankings

### This IS the Distillation Signal

The red team critique said "no readiness signal for hint removal." This IS the signal:

- If the user consistently ranks the distilled (low-hint) response above the big-model response → reduce hints further
- If the user ranks the distilled response below → keep hints, backtest more
- If the user's rankings change over time → the system adapts (ground-truths-for-now update)

### Implementation: User Ranking

```python
@dataclass
class UserRanking:
    """A user's ranking of multiple responses."""
    prompt: str
    responses: list[RankedResponse]
    user_notes: str  # Why they ranked them this way
    timestamp: float
    
@dataclass  
class RankedResponse:
    """A single ranked response."""
    response: str
    source: str  # "big_model", "distilled_v3", "nerve_compiled"
    rank: int  # 1 = best
    hint_level: int  # How many hints were used

class DistillationSignal:
    """Converts user rankings into distillation guidance."""
    
    def process_ranking(self, ranking: UserRanking) -> DistillationGuidance:
        # Did distilled beat big model?
        distilled_rank = min(r.rank for r in ranking.responses if "distilled" in r.source)
        big_rank = min(r.rank for r in ranking.responses if r.source == "big_model")
        
        return DistillationGuidance(
            reduce_hints=(distilled_rank <= big_rank),
            personalization=self.extract_preferences(ranking.user_notes),
            confidence_adjustment=self.compute_adjustment(ranking),
        )
```

### Personalization Accumulates

Every ranking teaches the system something about THIS user:
- "Prefers code examples over explanation" → pathos ground-truth
- "Likes concise responses" → pathos ground-truth
- "Values correctness over speed" → ethos priority
- "Cares about test coverage" → logos ground-truth

These ground-truths-for-now accumulate in the pathos room. They're the user's "shoes" — at first the system feels every preference edge, then it compiles the user's style into automatic processing.

## The Combined Loop

```
1. Big model generates several responses (different seeds/models)
2. Swarm also generates responses (with current hint level)
3. User sees all options, ranks them, explains why
4. Rankings → distillation signal (reduce hints? strengthen routes?)
5. Rankings → personalization (update pathos ground-truths)
6. Spare capacity → backtest old prompts with fewer hints
7. Repeat → agents need less and less over time
```

The user is the distillation sensor. Without user ranking, the system is flying blind. With it, the system has a clear signal for when to reduce hints and how to personalize.

## Connection to Starship Pathos

The user ranking happens on the **Bridge** — it's a command decision. The captain chooses which response is best and why. This isn't passive consumption — it's active command.

The Holodeck is where the backtesting happens — safe experimentation with old prompts, no consequences, just learning.

Ten-Forward is where agents share discoveries from backtesting — "I found a faster route for maritime queries!" — informal knowledge exchange.

The system runs 24/7, getting better even while you sleep.
