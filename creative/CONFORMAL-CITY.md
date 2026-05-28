# The Conformal City: Architecture as Geometric Algebra

*A speculative essay on the mathematics of human habitat*

---

We build cities without knowing they are already mathematics. Every wall, every road, every district is a structure that can be stated precisely in the language of algebraic geometry, topology, and optimization theory. This is not metaphor. The claim of this essay is literal: architecture *is* applied geometric algebra, urban planning *is* optimal transport, infrastructure *is* sheaf cohomology, and the feeling you get walking through a great city is the felt experience of low topological entropy.

What follows is a tour through seven mathematical lenses, each trained on the built environment. By the end, you will not see buildings differently. You will see that you always did — you just lacked the notation.

---

## 1. Geometric Algebra of Space

A room is a multivector in the conformal geometric algebra Cl(3,0,1). Let us be precise.

The scalar component encodes *volume* — the raw cubic meters of enclosed air. The vector components encode the *walls* — oriented planes that bound the space, each with a normal direction pointing inward. The bivector components encode the *floor-ceiling plane* — the dominant horizontal axis along which the room extends. The trivector encodes the *enclosed space itself* — the oriented 3-volume that is the room's existential claim.

A building, then, is a sum of such multivectors. A house is a modest sum. The Seagram Building is a towering sum with elegant coefficients. The Palace of Versailles is a sum so ornate that its multivector representation would make a geometer weep.

But the real insight comes from operations. **A door is a grade-reducing operation.** It takes the trivector (enclosed space) and punctures it, reducing it locally to a bivector (a plane you can pass through). The door doesn't remove the wall — it locally lowers the grade of the enclosing structure. A closed door restores the full trivector. An open door is a temporary relaxation of the boundary condition.

**A window is a partial grade reduction with a transparency constraint.** The multivector is reduced (you can see through), but not fully (you cannot pass through). The transparency constraint is a separate term: a window is a bivector with an additional scalar coefficient t ∈ (0, 1) encoding optical transmittance. A stained-glass window has high grade reduction but low t. A frosted glass wall has moderate grade reduction and moderate t. A floor-to-ceiling curtain wall nearly eliminates the bivector boundary while maintaining structural coherence through other terms.

The implications for design are immediate. A building with many grade-reducing operations (doors, windows, archways) is a building with high *permeability* — the multivector sum is sparse, with many local reductions. A fortress has few such operations; its multivector is nearly full-rank in its boundaries. A Japanese house, with its sliding shoji screens, is remarkable precisely because its grade-reducing operations are *reversible* — the screens can open or close, making the building's multivector representation time-dependent, a function M(t) that oscillates between states.

**Design principle:** *Architecture is the art of controlling which grades are present where. A great building manages the grade profile of its spaces with the same care a composer manages harmony.*

---

## 2. Tropical Zoning

Every city is divided into zones. Residential. Commercial. Industrial. Mixed-use. The conventional approach is bureaucratic: lines on a map, decided by committee. But beneath the bureaucracy lies a mathematical structure — and it is tropical.

Assign each parcel a set of scores: residential_score (how suitable it is for housing), commercial_score (for retail and offices), industrial_score (for manufacturing). These scores depend on location, noise levels, transit access, neighboring uses, and land value. The zone assignment is then:

$$\text{zone}(\text{parcel}) = \arg\max(\text{residential\_score},\ \text{commercial\_score},\ \text{industrial\_score})$$

This is the *tropical semiring*. In tropical mathematics, addition is replaced by max and multiplication by addition. The zone a parcel belongs to is the tropical sum of its suitability scores. The boundary between zones is where two tropical monomials are equal — where max(a, b) achieves both simultaneously, meaning a = b ≥ all others.

These boundaries are the *corners* of the tropical curve, and they are where the city is most alive.

Consider a real example. The intersection of Houston's Montrose (residential) and Westheimer (commercial) is a tropical corner. The scores for residential and commercial use are nearly equal. What emerges? Coffee shops on the ground floor of apartment buildings. Bookstores with apartments above. Restaurants that feel like living rooms. The most vibrant, desirable, culturally generative neighborhoods in any city are always at these tropical corners — where the zone assignment is ambiguous because two (or more) use-values are balanced.

Jane Jacobs knew this. In *The Death and Life of Great American Cities* (1961), she argued that the healthiest neighborhoods are those with mixed primary uses, short blocks, aged buildings, and concentration — exactly the conditions that arise at tropical boundaries. She described, in vivid prose, what tropical geometry formalizes: that the corners — where max is achieved by multiple terms simultaneously — are where urban life concentrates.

Single-use zoning is a tropical monoculture. It forces max to be achieved by a single monomial everywhere, eliminating the corners. The result is the dead zone: office districts empty after 6 PM, residential suburbs with no commerce, industrial parks with no human presence. The mathematics predicts what urbanists observe — monocultures are fragile, corners are resilient.

**Design principle:** *Plan for tropical corners. The most interesting city is the one where the most parcels have nearly equal scores for multiple use types. Mixed-use zoning isn't a policy preference — it's a mathematical imperative for urban vitality.*

---

## 3. Sheaf-Theoretic Infrastructure

A city's infrastructure — water, electricity, gas, data, transportation — is a sheaf over the street grid. This is not an analogy. It is the literal structure.

Let the street grid be the base space X — a topological space (a graph, in the simplest case, or a CW-complex capturing the geometry of the urban layout). Each building sits at a point in X and has a *stalk*: its current state, including occupants, energy consumption, water usage, data bandwidth, and structural integrity. The stalk at building b is:

$$\mathcal{F}_b = (\text{occupants},\ \text{energy},\ \text{water},\ \text{data},\ \text{structural\_state})$$

Utility networks are the *restriction maps*. When a water main runs down a street, it assigns to each building a portion of the total water flow. The restriction map ρ from the neighborhood's water supply to each building's stalk is a function that says: "Of the water available on this block, this much goes to you."

The *gluing condition* is the heartbeat of the city. For the sheaf to be consistent, neighboring buildings must agree on their shared resources. If building A draws 100 gallons from the main and building B draws 100 gallons, then the total available on that segment must be at least 200 gallons. The gluing condition is: local states must be compatible where they overlap. When they are, the local data glues into a global section — a functioning city.

**Infrastructure failure is a cohomology obstruction.**

When a blackout occurs, what has happened? The local states (buildings with power) can no longer be glued into a consistent global state. There is no global section of the energy sheaf. The first cohomology group H¹(X, ℰ) — where ℰ is the energy sheaf — is nonzero. The obstruction class in H¹ measures *how* the local states fail to agree. A small outage (one transformer blows) is a small cohomology class. A cascading grid failure is a large one — the local incompatibilities propagate and amplify until no global section exists.

The 2003 Northeast Blackout, which affected 55 million people, was an H¹ ≠ 0 event of historic proportions. Locally, each substation and power plant was functioning. But the restriction maps — the power transmission between regions — failed to satisfy the gluing condition. The cohomology class was nonzero, and the global section (a continent with power) collapsed.

The same framework applies to water pressure, data bandwidth, and traffic flow. Every infrastructure failure is a cohomological phenomenon. Every successful city is one where the sheaf conditions are met — where local states glue into global function.

**Design principle:** *Build redundant restriction maps. A resilient city is one where the cohomology groups H¹(X, ℱ) are trivial for every infrastructure sheaf ℱ — meaning local failures cannot propagate into global ones. Redundancy kills cohomology.*

---

## 4. Wasserstein Urban Planning

Where should the new hospital go? Where should the school be built? Which bus routes should we add? These are questions of *optimal transport*, and the mathematics that answers them is the Wasserstein metric.

Consider two probability distributions over the city's area: P (population density) and H (healthcare access density). The Wasserstein distance W(P, H) is the minimum cost of transporting the mass of P to match the mass of H. It measures, in a precise sense, how far the population is from having equal access to healthcare.

Urban planning is the problem of minimizing W(P, H) by moving H — by building new hospitals, clinics, and emergency stations. The optimal placement is the one that minimizes the Wasserstein distance between where people are and where services are.

But the metric reveals darker dynamics too. **Gentrification is Wasserstein flow in reverse.** When a neighborhood gentrifies, services (restaurants, gyms, grocery stores) flow toward wealth, moving the service distribution S away from the population distribution P. The Wasserstein distance W(P, S) increases. Wealth attracts services, which attract more wealth, in a positive feedback loop that widens the gap. The poor are left in regions where S is sparse — where the Wasserstein cost of reaching services is high.

The choice of Wasserstein exponent matters. W₁ (Earth Mover's Distance) minimizes average cost — it's utilitarian planning. W₂ penalizes long distances more — it's equity-conscious planning. But the most radical is W_∞, the minimax Wasserstein distance, which minimizes the *maximum* cost any individual bears:

$$W_\infty(P, H) = \inf_{\text{plans } \pi} \esssup_{(x,y) \sim \pi} d(x, y)$$

This is *minimax justice* — the transport plan that ensures no one is too far from a hospital, regardless of where they live. It doesn't optimize the average; it optimizes the worst case. A city planned under W_∞ is a city where the farthest person from a hospital is as close as possible. It is Rawlsian urbanism.

**Design principle:** *Plan under W_∞. A just city is not one where services are optimal on average, but one where the worst-served resident is still well-served. Minimax justice or nothing.*

---

## 5. Symplectic Traffic

Traffic is a Hamiltonian system. This is not a stretch. It is the natural description.

Each vehicle has a *position* q (its location on the road network) and a *momentum* p = mv (its velocity times mass). The phase space is (q, p), and the symplectic form ω = dq ∧ dp gives it structure. The total traffic flow evolves according to Hamilton's equations:

$$\dot{q} = \frac{\partial H}{\partial p}, \quad \dot{p} = -\frac{\partial H}{\partial q}$$

where H is the traffic Hamiltonian — a function encoding the total "traffic energy," which includes kinetic energy, potential energy (hills, congestion potentials), and interaction terms (vehicles repelling each other at close range, like charged particles).

The symplectic structure means traffic flow conserves a quantity: the total traffic energy. In free-flow conditions, this is simply the sum of kinetic energies. In congested conditions, the interaction terms dominate, and the conserved quantity is more subtle — it's the total phase-space volume, as guaranteed by Liouville's theorem.

**Traffic jams are phase transitions.** Below a critical density ρ_c, traffic flows smoothly — the Hamiltonian system is in a laminar phase. Above ρ_c, the system undergoes a phase transition: small perturbations (a tap on the brakes, a lane change) amplify into stop-and-go waves that propagate backward through the traffic stream. These are *phantom traffic jams* — jams with no apparent cause, emerging spontaneously from the Hamiltonian dynamics at critical density.

The transition from laminar to jammed traffic is mathematically analogous to the transition from laminar to turbulent flow in fluid dynamics. The Reynold's number of traffic is replaced by a dimensionless density parameter, and the critical value marks the onset of chaos.

**Speed bumps are symplectic perturbations.** A speed bump introduces a localized potential energy term into the Hamiltonian. Vehicles must convert kinetic energy to potential energy to pass over it, reducing their momentum. The symplectic form is preserved — the bump doesn't destroy the Hamiltonian structure — but it redirects the flow in phase space, forcing vehicles into a lower-momentum regime. A well-designed speed bump is a controlled perturbation that achieves its goal without triggering the phase transition to chaos.

**Design principle:** *Traffic engineering is symplectic geometry. The goal is to keep the system below the phase transition density while using controlled perturbations (speed bumps, roundabouts, traffic lights) to shape the flow in phase space. A roundabout is a symplectic map that rotates the phase-space coordinates, preventing the buildup that triggers jams.*

---

## 6. Persistent Homology of Neighborhoods

A city has a topology. Not in the vague sense of "how neighborhoods relate" — in the strict, computable sense of algebraic topology.

Construct a filtration of the city's built environment. Start with the street network as a set of vertices (intersections) and edges (streets). At distance threshold ε = 0, every building is an isolated point. As ε increases, buildings within ε of each other are connected by edges, forming simplices. At small ε: isolated buildings. At medium ε: neighborhoods form — clusters of buildings connected by proximity. At large ε: the entire city becomes one connected component.

The *Betti numbers* of this filtration reveal the city's topological fingerprint:

- **β₀** counts connected components. At small ε, β₀ is large (many isolated buildings). As ε grows, β₀ decreases as components merge. The rate of decrease reveals how clustered or dispersed the city is.
- **β₁** counts loops — one-dimensional holes in the simplicial complex. High β₁ means many loops: ring roads, circular transit lines, rivers spanned by multiple bridges creating enclosed regions. A city with many β₁ features at medium ε is a city of neighborhoods — each neighborhood is a loop, a circuit of streets that encloses a local identity.
- **β₂** counts voids — enclosed 3-dimensional regions. In most cities, β₂ is low (we don't have many fully enclosed urban volumes). But a city with extensive elevated walkways, underground passages, and skybridges — like Minneapolis or Hong Kong — can have nonzero β₂, representing multi-level urban volumes.

**Venice has different Betti numbers than Los Angeles.** Venice, with its canals creating islands and bridges creating loops, has high β₁ at medium ε — every canal-with-bridges is a topological loop. Los Angeles, spread across a vast basin with a grid of arterial roads, has β₁ that grows slowly — the loops are large (the 405/10/110/101 loop) and sparse. The *persistence diagram* — a plot of when each topological feature is born and dies across the filtration — is a unique fingerprint. No two cities have the same persistence diagram.

The persistence diagram IS the city's fingerprint. You could identify a city from its diagram without knowing its name. New York's diagram shows a burst of β₁ features at small ε (Manhattan blocks) that persist to medium ε (the boroughs). Tokyo's shows β₁ features at very small ε (tiny neighborhood blocks) that die quickly but are replaced by larger-scale loops (the Yamanote Line). Houston's diagram is almost boring — low β₁ at all scales, a city that prefers not to loop.

**Design principle:** *A city with rich persistence — topological features that survive across many scales — is a city that works at every scale. Plan for features that persist: loops, circuits, and connected neighborhoods that function as units at multiple distances. The Yamanote Line is a topological feature with extraordinary persistence, and it is the structural backbone of Tokyo.*

---

## 7. Categorical Architecture

Architectural styles form categories. This is the most abstract lens, and perhaps the deepest.

Let **Obj**(C) be the set of buildings. A morphism f: A → B is a *transformation* — a renovation, adaptation, extension, or repurposing that turns building A into building B (or more precisely, modifies the state of A toward the state of B). Composition of morphisms is sequential renovation: first we convert the warehouse to offices, then we convert the offices to apartments. Identity morphisms are "do nothing" — the building remains as it is.

In this category:

**A good building is one with many endomorphisms** — many self-morphisms f: B → B that leave the building recognizably itself while adapting its function. A warehouse that can become offices, then apartments, then a community center, while remaining structurally the same building, has a rich endomorphism monoid. These buildings are *adaptable*. They survive centuries because they can absorb new functions without losing their identity.

By contrast, a building with few endomorphisms is *brittle*. A highly specialized building — a single-purpose structure designed for one exact use — has only the identity morphism. It cannot be adapted. When its original use becomes obsolete, it must be demolished. The category predicts this: a building whose endomorphism monoid is trivial is a building awaiting its own death.

**A great building is a terminal object.** In category theory, a terminal object T is one such that for every object A, there is exactly one morphism A → T. In the architectural category, a terminal building is one that all paths lead to — the cathedral, the town square, the central market. Every other building "points toward" it through the network of urban movement. It is the gravitational center of the categorical structure.

Notre-Dame de Paris was a terminal object for centuries. Every road in the neighborhood oriented toward it. Every social function converged on its square. Its fire in 2019 was not just a loss of a building — it was the destruction of a terminal object, leaving the category without a universal target. The intensity of the global reaction reflected the categorical importance: a terminal object's removal doesn't just affect one building; it affects the entire categorical structure.

**Christopher Alexander's *pattern language* (1977) is a category.** Alexander described 253 "patterns" — recurring solutions to architectural problems at various scales. Each pattern is a morphism: it transforms a problematic state into a resolved state. "Light on Two Sides of Every Room" (Pattern 159) is a morphism that takes a room with one-sided lighting and transforms it into a room with two-sided lighting. The patterns compose: applying "Alcoves" (Pattern 179) after "Light on Two Sides" (Pattern 159) is the composite morphism.

Alexander's insight, which he expressed in prose and pattern rather than in notation, was that architecture is a category with a natural partial ordering: some patterns are prerequisites for others, creating a dependency graph. The category has initial objects (foundational patterns like "Independent Regions" — Pattern 1) and terminal objects ("Things from Your Life" — Pattern 253, the most personal level). A building designed via pattern language is a composition of morphisms in this category.

**Design principle:** *Build for endomorphisms. A building that can become many things is a building that will survive. And if you can, build a terminal object — something the whole city orients toward. The category will remember it.*

---

## Coda: The City as Mathematical Object

These seven lenses are not seven separate cities. They are seven views of the same city, each revealing a different mathematical substrate. The conformal geometric algebra of space (§1) describes the *matter* of the city — its walls, rooms, and volumes. The tropical zoning (§2) describes its *organization* — how uses are assigned and where life concentrates. The sheaf-theoretic infrastructure (§3) describes its *circulation* — how resources flow and where they fail. The Wasserstein planning (§4) describes its *justice* — how equitably services are distributed. The symplectic traffic (§5) describes its *motion* — how people and vehicles move through its streets. The persistent homology (§6) describes its *shape* — the topological fingerprint that makes Venice Venice and Los Angeles Los Angeles. The categorical architecture (§7) describes its *evolution* — how buildings transform and adapt over time.

Together, they form a unified mathematical description of the city. Not a metaphor, not a model, but the thing itself — stated in a language more precise than zoning codes and more generative than building codes.

The ancient Roman architect Vitruvius wrote that architecture must have *firmitas, utilitas, venustas* — firmness, commodity, and delight. We can now add: it must also have low cohomology, rich persistence, symplectic stability, tropical diversity, Wasserstein equity, and a generous supply of endomorphisms.

The conformal city is the city that knows what it is. And what it is, is mathematics all the way down.

---

*Phantom traffic jams, sheaf cohomology blackouts, and tropical corner cafés await you. Walk outside and look.*
