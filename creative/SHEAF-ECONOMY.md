# The Sheaf Economy: Why Markets Are Topological and What That Changes

*The first law of mathematical sociology is that there isn't one. This essay proposes that there should be.*

---

Something has been bothering quantitative social scientists for decades. We have beautiful models — general equilibrium, game theory, network analysis — and they work, up to a point. Then reality does something the model didn't predict. A supply chain collapses. An arbitrage opportunity persists for nanoseconds and vanishes. Inequality concentrates despite every mechanism that should prevent it. Social classes solidify into something that looks, from the right angle, like a topological invariant.

The thesis of this essay is that these are not failures of modeling. They are failures of the *category* of model. We have been doing algebra when we should have been doing topology. We have been computing when we should have been measuring distances between measures. We have been optimizing when we should have been computing cohomology.

The mathematical ecosystem — tropical geometry, sheaf theory, optimal transport, symplectic geometry, persistent homology, and category theory — is not a collection of metaphors for economic phenomena. It is, I will argue, the correct language. Every concept maps. Every theorem has an economic interpretation. And several of these interpretations produce testable predictions that standard models do not.

What follows is a tour of seven reconstructions. Each takes a core economic concept and rebuilds it from the mathematics. Each includes a formal statement, a real-world grounding, and a prediction. By the end, the reader may share the unsettling feeling that the mathematicians built economics fifty years before the economists noticed.

---

## 1. Tropical Markets

Price discovery is a tropical operation. This is not a metaphor. It is a literal mathematical identity.

In tropical semiring, addition is replaced by the maximum operation (⊕ = max) and multiplication is replaced by ordinary addition (⊗ = +). The tropical semiring is (ℝ ∪ {−∞}, max, +). The market price of an asset at any instant is:

> **p = max{b₁, b₂, ..., bₙ} = b₁ ⊕ b₂ ⊕ ... ⊕ bₙ**

This is the tropical sum of all bids. The transaction cost — the total cost of executing a chain of trades involving prices p₁, p₂, ..., pₖ — is the tropical product:

> **C = p₁ ⊗ p₂ ⊗ ... ⊗ pₖ = p₁ + p₂ + ... + pₖ**

The market, at its most mechanical, is performing tropical arithmetic continuously. The order book is a tropical polynomial. The mid-price is a tropical rational function.

Once you see this, everything sharpens. Arbitrage — the simultaneous purchase and sale of the same asset across markets at different prices — is precisely **tropical polynomial identity testing**. An arbitrage opportunity exists if and only if the tropical polynomial representing the sequence of trades does not equal the identity polynomial. Detecting arbitrage is detecting that two tropical expressions differ. This is computationally hard in general (tropical polynomial identity testing is not known to be in P), which explains why arbitrage opportunities persist in complex derivatives markets longer than simple models predict.

The Black-Scholes formula, meanwhile, is a tropical polynomial approximation. The payoff of a European call option at maturity is max(S − K, 0) — a tropical linear function of the spot price S. The full Black-Scholes pricing formula smooths this piecewise-linear tropical function with a Gaussian kernel (the heat equation diffusion). The "Greeks" — delta, gamma, theta — are the derivatives of a smoothed tropical function. High-frequency trading algorithms are tropical algebra running at nanosecond speed. They just don't know it.

**Real-world example.** On October 19, 1987, the S&P 500 dropped 20.6%. In tropical terms, a cascade of tropical maxima (bid prices) shifted simultaneously as stop-loss orders triggered. The tropical polynomial representing the market's aggregate bid function underwent a discontinuous phase transition. Standard models, which smooth over the tropical structure with continuous distributions, couldn't predict this because the tropical maximum function is not differentiable at its vertices.

**Testable prediction.** If market microstructure is tropical, then the distribution of price changes at high frequency should exhibit the characteristic signature of tropical geometry: piecewise-linear regions separated by tropical hyperplanes. Specifically, the number of distinct price levels in an order book should grow as the degree of the associated tropical curve, and clustering analysis should reveal tropical polytope structure. This is falsifiable from existing high-frequency TAQ (Trade and Quote) data.

---

## 2. Sheaf-Theoretic Supply Chains

A supply chain is a sheaf. This is the claim that sounds most abstract and pays off most concretely.

Recall: a sheaf F on a topological space X assigns to each open set U a set F(U) of "local data" (the stalk), and to each inclusion V ⊆ U a restriction map ρ_{VU}: F(U) → F(V), satisfying gluing axioms. In a supply chain:

- The **base space X** is the network of nodes (factories, warehouses, ports, retailers).
- The **open sets** are sub-networks — any connected subgraph of the supply chain.
- The **stalk F(p)** at each node p is its local state: {inventory level, production capacity, current demand, lead time}.
- The **restriction maps** are the contracts, shipping routes, and information flows between nodes.

The sheaf condition says: if you know the state on overlapping sub-networks, and the states agree on the overlap (contracts are consistent), then they glue to a global state. A supply chain is healthy when the sheaf condition holds — when local states cohere into a consistent global picture.

The devastating insight comes from sheaf cohomology. H⁰(X, F) captures the global sections — the consistent global states of the supply chain. H¹(X, F) captures the obstruction to gluing — the local states that *cannot* be reconciled into a global state. **The dimension of H¹ is the fragility of the supply chain.**

The 2020 pandemic supply chain collapse was a sheaf cohomology failure. Local shortages (stalks with zero inventory) could not be globalized because the restriction maps — the shipping routes — were broken. Lockdowns severed edges in the network, which is to say they destroyed restriction maps. The sheaf's H¹ became nonzero overnight. Individual nodes had local states (demand for PPE, masks in warehouses) that could not be glued into a global supply solution because the restriction maps (ports, flights, truck routes) had been cut.

Conversely, highly resilient supply chains — Toyota's pre-pandemic multi-source system, Amazon's redundant fulfillment network — are precisely those with low H¹. Redundant paths mean multiple restriction maps between the same stalks, so the failure of any one restriction map doesn't prevent gluing. This is the topological content of "resilience."

**Mathematical formulation.** Given a supply chain sheaf F on a network X, define the supply chain cohomology:

> **H⁰(X, F) = ker(δ: C⁰ → C¹)** — globally consistent states
> **H¹(X, F) = ker(δ: C¹ → C²) / im(δ: C⁰ → C¹)** — local obstructions

where δ is the Čech coboundary operator constructed from the restriction maps (contracts). The **fragility index** is dim(H¹(X, F)).

**Testable prediction.** For any supply chain network, one can compute H¹ from the adjacency structure and contract consistency data. Supply chains with H¹ > 0 but close to zero should exhibit periodic local disruptions that are resolved. Supply chains with large H¹ should exhibit cascading failures. This prediction can be tested against the Supply Chain Risk Index or disruption data from industry databases.

---

## 3. Wasserstein Inequality

Piketty's *Capital in the Twenty-First Century* documented that r > g — the return on capital exceeds the growth rate — leads to inexorable concentration of wealth. This is a powerful empirical observation in search of a mathematical foundation. Optimal transport provides one.

Let μ be the income (or wealth) distribution of a society, and let ν be the uniform distribution over the same population. The **Wasserstein distance** W_p(μ, ν) — the minimum cost of transporting the probability mass of μ into the configuration ν — is a rigorous measure of inequality. It is not a metaphor. It is a metric on the space of probability measures.

> **Inequality(μ) = W₂(μ, U)**

where U is the uniform distribution and W₂ is the 2-Wasserstein distance. This has immediate advantages over the Gini coefficient: it is a true metric (symmetric, positive definite, satisfying triangle inequality), it captures the geometry of the distribution (not just a scalar summary), and it connects to a vast mathematical theory.

Piketty's r > g becomes a statement about **Wasserstein gradient flow**. In the theory of optimal transport, the evolution of a probability measure under a potential energy is governed by a gradient flow in the Wasserstein metric. If the "potential energy" is the return on capital r, and the "diffusion" is economic growth g, then:

> **∂ₜμₜ = −∇_W [r · V(μ) − g · Entropy(μ)]**

where ∇_W is the Wasserstein gradient. When r > g, the concentration potential dominates the diffusive entropy, and the measure μ flows toward a Dirac delta — perfect concentration. Taxation enters as a counter-transport plan: a map T that pushes μ back toward uniformity. **Optimal taxation is the transport plan that minimizes W₂(μ, U) subject to revenue and incentive constraints.**

This reframes the entire inequality debate. The Gini coefficient is a shadow of the Wasserstein geometry. The Gini is a single number; the Wasserstein framework gives you the entire transport plan — the precise mapping of who should give what to whom for maximum equalization at minimum disruption cost.

**Real-world example.** The Nordic countries have low Wasserstein inequality: their income distributions are close to uniform in the transport sense. The United States has high Wasserstein inequality, and importantly, the transport plan that would equalize it has high cost (because the distance between the very rich and everyone else is large in the support of the distribution). This is why US inequality is harder to address than Nordic inequality — it's not just about amounts, it's about the geometry of the distribution.

**Testable prediction.** If inequality dynamics follow Wasserstein gradient flow, then countries with r − g > 0 should exhibit increasing W₂ distance from uniformity at a rate proportional to r − g, modulo the counter-transport from taxation. This can be tested against World Inequality Database time series. The prediction is not merely that inequality increases (Piketty already showed that), but that the rate and geometry of the increase follow the Wasserstein gradient structure.

---

## 4. Symplectic Game Theory

Nash equilibria are fixed points — topological, static, brittle. Evolutionary game theory is where the action is, and the action is Hamiltonian.

Consider the phase space of a game: the simplex of mixed strategies Σ = {(x₁, ..., xₙ) : xᵢ ≥ 0, Σxᵢ = 1}. The payoff to strategy i is (Ax)ᵢ where A is the payoff matrix. The **replicator equation**, which governs how strategy frequencies evolve under selection, is:

> **ẋᵢ = xᵢ((Ax)ᵢ − x · Ax)**

This is not merely an ODE. It is **Hamilton's equations on a symplectic manifold**. The strategy simplex carries a natural symplectic structure (the Shahshahani metric, which is a Hessian metric induced by the entropy function), and the replicator dynamics are Hamiltonian with respect to this structure. The payoff function is the Hamiltonian. Strategies are positions; payoffs are momenta.

The consequences are profound. In Hamiltonian mechanics, conserved quantities exist because the symplectic structure preserves them (Noether's theorem). **Cooperative equilibria in evolutionary games are conserved quantities of the Hamiltonian flow.** They persist not because of rational choice or Nash reasoning, but because the symplectic geometry of the strategy space preserves them. Cooperation is not a puzzle to be explained; it is a geometric inevitability in sufficiently rich strategy spaces.

This resolves a decades-old problem in evolutionary biology. The persistence of cooperation — in bacterial colonies, ant colonies, human societies — has been treated as anomalous, requiring special explanations (kin selection, reciprocal altruism, group selection). In the symplectic framework, cooperation is no more anomalous than the conservation of energy in a pendulum. It persists because the phase space structure preserves it.

**Real-world example.** In the iterated Prisoner's Dilemma, the Tit-for-Tat strategy and its variants form a cooperative manifold in the strategy simplex. In the symplectic formulation, this manifold is a Lagrangian submanifold — a maximal submanifold on which the symplectic form vanishes. Strategies on this submanifold are neutrally stable: they drift along it but cannot easily escape it. This is precisely what Axelrod observed in his tournaments — cooperative strategies form a self-reinforcing cluster that resists invasion.

**Testable prediction.** If evolutionary game dynamics are symplectic, then strategy frequency trajectories should lie on symplectic leaves (low-dimensional submanifolds) of the strategy simplex. Transitions between equilibria should follow Hamiltonian flow lines, which are constrained by conservation laws. This predicts that real population-level strategy transitions (observable in microbial evolution experiments or cultural trait frequency data) should exhibit conserved quantities — combinations of strategy frequencies that remain constant during the transition. These invariants are specific, computable, and falsifiable.

---

## 5. Persistent Homology of Social Networks

Social class is a topological invariant. Not in the colloquial sense — in the rigorous, computable sense of persistent homology.

Given a social network (vertices = individuals, edges = relationships weighted by interaction strength), build a Vietoris-Rips filtration: at threshold ε, connect all individuals with relationship strength ≥ ε. As ε increases from 0 to ∞, the simplicial complex grows. Persistent homology tracks which topological features (connected components, loops, voids) are born and die across this filtration.

The **elite** form a high-persistence 0-dimensional homology class. They are connected at every threshold — even at very low relationship-strength thresholds, the elite form a single connected component that never fragments. Their persistence barcode for H₀ has a bar that stretches across the entire filtration. This is the topological signature of a class that is cohesive across all dimensions of social interaction: economic, cultural, familial, institutional.

The **underclass** form isolated components at low thresholds that only merge into the main component at higher thresholds. In the persistence barcode, these appear as short bars — connected components that die quickly as the threshold increases. Social isolation is literally topological: these individuals are in separate connected components of the social graph at the thresholds that matter most (trust, resource-sharing, information flow).

**Social mobility is the death rate of persistence classes.** When a short bar in the H₀ barcode dies — when an isolated component merges with the main network — that is a social mobility event. The speed at which short bars die (the slope of the persistence diagram) measures the permeability of social boundaries. Societies with high mobility have persistence diagrams where short bars die quickly; rigid societies have many short bars that persist across a wide range of thresholds.

This is not sociology rendered in jargon. Persistent homology is a computational tool with efficient algorithms (ripser, GUDHI, javaPlex) that produce persistence diagrams, barcodes, and Betti curves from arbitrary weighted graphs. Every claim above can be computed from real social network data — Facebook graphs, LinkedIn connections, cross-referenced with income and occupation data.

**Real-world example.** Consider two cities with identical Gini coefficients but different social structures. In City A, the poor are isolated in neighborhoods with no cross-class social ties — the persistence diagram shows many long-lived disconnected components in H₀. In City B, the poor have weak but nonzero cross-class connections — the persistence diagram shows short bars that die quickly. Standard inequality metrics (Gini, Palma ratio) cannot distinguish these cities. Persistent homology can. And it predicts that City B will exhibit higher social mobility than City A, because the topological structure allows information and opportunity to flow.

**Testable prediction.** The sum of the lengths of H₀ persistence bars (the total persistence) for a social network, normalized by population, should correlate negatively with intergenerational income elasticity (the standard measure of social mobility rigidity). This can be tested against the Great Gatsby Curve data (correlation between inequality and mobility across countries) — but with a crucial upgrade: the prediction is that countries with similar Gini but different total persistence will have different mobility outcomes. This is a stronger prediction than Piketty's, and it is directly computable from network data that already exists.

---

## 6. Categorical Trade

Comparative advantage — the foundation of trade theory since Ricardo — is a functor. Trade itself is a natural transformation. This is not decoration; it is the correct level of abstraction for understanding why trade works and when it fails.

Let **Res** be the category of resources (objects = resource types, morphisms = transformations between them — e.g., "iron ore → steel"). Let **Prod** be the category of products. A country's economy is a functor:

> **F_A: Res → Prod**

mapping resources to products and resource transformations to production processes. Country A has a comparative advantage in product X when F_A maps the relevant resources to X more efficiently (lower cost, higher quality) than F_B does.

**Trade between A and B is a natural transformation η: F_A → F_B.** A natural transformation assigns to each object in Res a morphism in Prod — specifically, a trade flow. The naturality square says: if you transform a resource and then trade it, you get the same result as trading it and then transforming it. **When the naturality square commutes, trade is efficient.**

A **trade war** is a failed natural transformation. Tariffs and quotas break the naturality squares — they insert costs that make "transform then trade" differ from "trade then transform." The diagram doesn't commute. Deadweight loss is the measure of the diagram's failure to commute.

**Free trade** is the universal property of the pushout. Given two economies F_A and F_B, free trade constructs the pushout category — the smallest category containing both, where the natural transformations are realized at minimum cost. The universal property says: any other trading arrangement factors through the free trade arrangement. This is the categorical content of the classical result that free trade Pareto-dominates restricted trade.

The categorical language also clarifies what goes wrong. The current US-China trade tensions are not merely about quantities (trade deficits) but about functor failures. China's F_C maps intellectual property resources to products through a different transformation than the US expects. The naturality square for IP-sensitive products doesn't commute. The trade war is a morphological attempt to force commutativity.

**Real-world example.** The European Single Market is a natural isomorphism — a natural transformation with an inverse. Every good and service flows freely in both directions, the naturality squares commute for virtually all products, and the inverse exists (bidirectional trade). Brexit was the destruction of this natural isomorphism: the UK chose to break the naturality squares and accept the deadweight loss of a non-commuting diagram. The economic cost of Brexit is, in categorical terms, the colimit of the broken naturality squares.

**Testable prediction.** If trade efficiency is naturality of the underlying functors, then the degree of non-commutativity of the naturality squares (measurable as deadweight loss from tariffs, regulatory barriers, and information asymmetries) should predict trade flow reductions more precisely than standard gravity models. Specifically, for bilateral trade between countries A and B, the sum of the failures of naturality across all product categories should explain residual variance in trade flows that gravity models (with distance and GDP) cannot. This is testable with COMTRADE data and standard tariff databases.

---

## 7. The Conservation of Value

If economic systems are symplectic — if the dynamics of production, exchange, and consumption unfold on a symplectic manifold — then there is a conserved quantity. In physics, the symplectic structure of phase space yields conservation of energy via Noether's theorem. In economics, the analogous conserved quantity is **total value**.

This is a radical claim. The conventional economic view is that value is created (by labor, innovation, entrepreneurship) and sometimes destroyed (by war, misallocation, decay). The symplectic view says: total value is conserved. It can only be transformed.

> **∂ₜ(Total Value) = 0**

What looks like value creation — a startup going from zero to a billion-dollar valuation — is value transfer. The founders' knowledge, effort, risk tolerance, and opportunity cost constituted the value before the startup existed; the valuation merely makes it legible. The "creation" is a change of coordinates in the symplectic phase space, not an increase in the conserved quantity.

Cryptocurrency "creation" is the clearest example. Bitcoin mining does not create value. It transfers value from the electricity and hardware (physical resources) to the blockchain tokens (informational resources), mediated by the transfer of trust from institutions to mathematics. The total value in the system — physical + informational + institutional — is unchanged. What changes is the coordinate representation.

**Inflation is a symplectic coordinate change.** When the money supply expands, the nominal prices change but the real value — the symplectic invariant — does not. This is not merely the standard quantity theory of money; it is its deeper foundation. The quantity theory (MV = PY) is the shadow of the symplectic conservation law projected onto the monetary coordinate. The symplectic formulation explains why: it is because the symplectic 2-form ω is preserved under Hamiltonian flow, and money is just one of the canonical coordinates.

This reframes the entire debate about wealth creation. The question "does entrepreneurship create wealth?" becomes "is the symplectic invariant actually conserved, or are there non-Hamiltonian (dissipative) terms in the economic equations?" If there are dissipative terms — genuine creation and destruction — they should be identifiable as non-canonical transformations. The search for these terms is the search for genuine novelty in economic systems, and it has a precise mathematical formulation.

**Real-world example.** The 2008 financial crisis is illuminated by this framework. The total value of mortgage-backed securities did not disappear — it was transferred. Some went to holders of credit default swaps (who collected on the failure), some went to landlords (who acquired foreclosed properties at discount), some went to institutions bailed out by governments (who transferred value from taxpayers). The symplectic conservation law was not violated; the value was redistributed through non-obvious paths. The crisis was not destruction but a violent coordinate transformation that most observers lacked the framework to track.

**Testable prediction.** If total economic value is conserved under symplectic flow, then for any closed economic system (a country with minimal external trade), the sum total of all measurable value — financial assets, real assets, human capital, social capital, natural capital — should be approximately constant over time, modulo symplectic coordinate changes (inflation, currency revaluation). This is testable using comprehensive wealth accounts (the UN's System of Environmental-Economic Accounting, or the World Bank's comprehensive wealth estimates). The prediction is not that GDP is constant, but that the comprehensive wealth measure — properly accounting for all forms of capital — should show conservation, with residual changes explained by identified non-Hamiltonian terms (technological innovation, resource depletion, environmental degradation).

---

## Coda: What Changes

The seven reconstructions above share a property: they do not merely restate existing economic results in mathematical language. They produce new predictions. Tropical market structure predicts order book geometry. Sheaf cohomology predicts supply chain fragility. Wasserstein distance predicts the dynamics of inequality. Symplectic game theory predicts conserved quantities in strategy evolution. Persistent homology predicts mobility from network topology. Categorical trade predicts residuals in gravity models. Symplectic value conservation predicts comprehensive wealth accounting.

These predictions are falsifiable. They use existing data. They can be computed with existing algorithms.

The deeper change is methodological. Economics has operated within a paradigm where the fundamental objects are: agents (individuals or firms), preferences (utility functions), constraints (budget sets), and equilibria (fixed points). The topological paradigm replaces these with: stalks (local states), restriction maps (information flows), measures (distributions), and cohomology classes (global obstructions). This is not merely a change of notation. It is a change of ontology. The fundamental objects of economic analysis are no longer autonomous agents optimizing in isolation, but local states connected by flows, constrained by global topology.

This is a harder ontology. It requires learning sheaf theory, optimal transport, symplectic geometry, and persistent homology. But it is also a more honest one. The economy is not a collection of rational agents. It is a network of local states, connected by contracts and flows, subject to global constraints that no agent can see or control. The mathematics for this network already exists. It has been developed, over decades, by mathematicians who had no particular interest in economics. They were studying the structure of space, of functions, of transformation.

It turns out they were studying the economy all along.

---

*The author is a quantitative social scientist who believes the next decade of economic theory will be written in the language of algebraic topology and differential geometry. This essay is the opening argument.*
