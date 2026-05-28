# The Category of Justice: Law as Morphism

*Or: What Happens When a Mathematician Reads a Casebook*

---

Lawyers and mathematicians share an odd kinship: both spend their days navigating abstract structures that govern the real world, both argue about what counts as valid reasoning, and both are obsessed with precedent. Yet they rarely speak the same language. This essay attempts a translation — not as metaphor, not as analogy, but as structural claim. The thesis is simple: legal systems are mathematical objects, and the mathematics they most resemble is category theory, algebraic topology, and symplectic geometry.

This is not decorative. If the mapping holds, it offers more than aesthetic satisfaction. It provides diagnostic tools. A legal system with nonzero cohomology is one where local consistency fails to glue into global coherence. A sentencing regime governed by tropical polynomials explains *why* mandatory minimums feel structurally unjust, not merely politically objectionable. A constitutional framework understood as symplectic manifold reveals what, precisely, is lost when one branch cannibalizes another.

Let us proceed section by section.

---

## I. Sheaf-Theoretic Jurisdiction

A sheaf assigns data to open sets of a topological space in a way that is locally consistent and globally compatible. The canonical example: a sheaf of continuous functions on a manifold, where knowing a function locally on overlapping patches and ensuring the patches agree on intersections is sufficient to reconstruct the function globally.

A court is a stalk — the local fiber of the legal sheaf at a point in jurisdiction-space. The law it applies to a particular case is a section: a specific choice of legal interpretation drawn from the fiber. When a trial court in the Southern District of New York rules on a securities question, it produces a local section — an interpretation valid within its geographic and subject-matter open set.

Appeals courts are restriction maps. When the Second Circuit reviews a district court ruling, it does not merely check the section for errors. It projects the lower court's section into a broader context — a larger open set covering multiple districts. The restriction map asks: does this local section extend compatibly to the wider region? If yes, the section is affirmed. If no, it is remanded or reversed.

The Supreme Court sits at the global section. Its role is to ensure that all local sections can be glued into a single, coherent interpretation of federal law across the entire jurisdictional space. When the gluing succeeds — when every circuit's interpretation is compatible with every other's — the legal sheaf has a global section, and the system is coherent.

But sometimes gluing fails. Two circuits interpret the same statute differently. This is a **circuit split**, and in sheaf-theoretic terms, it is an obstruction class: an element of the first cohomology group H¹(Jurisdiction, Law). The cohomology group measures the failure of local data to patch into global data. When H¹ ≠ 0, the legal system contains incompatible local interpretations that cannot be reconciled without intervention.

The Supreme Court's certiorari jurisdiction exists precisely to resolve these obstructions. A petition for certiorari is, in effect, a claim that H¹ ≠ 0 — that local sections conflict and the cohomology class is nontrivial. Granting cert is the Court agreeing to compute the obstruction. Its opinion is the coboundary that trivializes the cohomology class, restoring H¹ = 0.

A healthy legal system has H¹ ≈ 0 most of the time. Minor inconsistencies at the district level are absorbed by the appellate restriction maps. Circuit-level disagreements are rare and resolved quickly. If H¹ is persistently nonzero — if the courts routinely produce incompatible interpretations that the Supreme Court cannot or will not resolve — the legal sheaf is not a sheaf at all, but a presheaf: locally defined data that fails the gluing condition. The system is, in the literal algebraic sense, incoherent.

**Case in point:** The circuit split over the Affordable Care Act's individual mandate, which persisted across multiple circuits before *NFIB v. Sebelius* (2012), was a textbook cohomology obstruction. Different circuits produced genuinely incompatible sections — some upholding the mandate under the Commerce Clause, others rejecting it. The Supreme Court's opinion (upholding it as a tax) was a coboundary operator: it didn't simply pick one circuit's section but constructed a new section compatible with all local data, trivializing the obstruction.

---

## II. Tropical Sentencing

Tropical algebra replaces ordinary addition with maximization and ordinary multiplication with addition. The tropical semiring (ℝ ∪ {−∞}, ⊕, ⊗) is defined by a ⊕ b = max(a, b) and a ⊗ b = a + b. This seemingly exotic structure appears naturally in optimization problems, shortest-path algorithms, and — I will argue — criminal sentencing.

Consider a sentencing guideline system. The sentence imposed is approximately:

> sentence = max(mandatory_minimum, guideline_range × severity, aggravating_factors)

This is a tropical polynomial. The "max" is tropical addition. The multiplication by severity is ordinary (or tropical) scaling. The result is a piecewise-linear function of the input variables — exactly the kind of object tropical geometry studies.

Three-strikes laws are particularly vivid tropical polynomials:

> sentence = max(base_offense, 2 × prior_convictions, 3 × prior_convictions²)

Under ordinary arithmetic, prior convictions might moderately increase a sentence. Under tropical arithmetic, the max operation means that once the "three strikes" term exceeds the base offense, it *dominates* the entire polynomial. A shoplifting charge, which would normally produce a sentence of months, suddenly produces life imprisonment because the prior-conviction term is tropically dominant.

This is not merely a formal trick. It explains *why* mandatory minimums are structurally unjust in a way that guideline ranges are not. A mandatory minimum is a tropical monomial — a constant term that dominates the tropical polynomial regardless of all other variables. In ordinary sentencing, the judge considers a weighted combination of factors. In tropical sentencing, the mandatory minimum *cannot be averaged out*. It is the max, and max is insensitive to everything below it.

The normative argument writes itself. A just sentencing system should be sensitive to the specifics of the case — it should be a smooth function of the input variables, where small changes in circumstance produce proportionally small changes in outcome. Tropical polynomials are piecewise-linear and flat in large regions: above the threshold, nothing matters. This insensitivity is the mathematical structure of injustice.

**Case in point:** *Ewing v. California* (2003) upheld a 25-years-to-life sentence for stealing three golf clubs under California's three-strikes law. The base offense term (shoplifting) might yield a sentence of 6 months. The three-strikes term yielded 25 years to life. The tropical max selected the latter. Every variable specific to the golf clubs — their value, the manner of theft, the defendant's mental state — was tropically irrelevant. The court's majority upheld the sentence, but the structure of their reasoning was essentially: "the tropical polynomial is what the legislature wrote, and we cannot rewrite it." The dissent, without using this language, argued that the tropical dominance of the recidivism term violated the Eighth Amendment's proportionality principle — which is to say, the tropical polynomial was not a faithful model of justice.

---

## III. Wasserstein Rights

Optimal transport theory studies how to move mass from one distribution to another at minimal cost. The Wasserstein distance measures the cheapest way to transform one probability distribution into another. It has become central to modern machine learning, fluid dynamics, and — I claim — constitutional law.

The state possesses power as a distribution: the capability to surveil, detain, tax, regulate, and punish. This power is distributed across the population. The constitution constrains how that power can be transported — how it flows from the state's capabilities to its effects on individuals.

The Fourth Amendment is a constraint on the Wasserstein transport from "state surveillance capability" to "individual privacy violation." The state has the technical capacity to surveil extensively (a high-density source distribution). Individuals have privacy interests (a target distribution the state might wish to reach). The Fourth Amendment requires a warrant — a transport plan that minimizes unnecessary displacement of privacy. The warrant particularizes the search, specifying where the state's surveillance power may flow and to whom. A general warrant — one that allows the state to transport its surveillance power anywhere — is a transport plan with unbounded cost, and it is unconstitutional.

The Fifth Amendment's due process clause is similarly a Wasserstein constraint: the state may deprive you of life, liberty, or property, but only through a transport plan (legal process) that minimizes unnecessary harm. Due process is the requirement that the transport cost be justified by the destination.

The Eighth Amendment's prohibition on cruel and unusual punishment constrains the cost function itself: certain transport routes from "state punishment capability" to "individual suffering" are simply forbidden, regardless of efficiency. The cost function assigns infinite cost to these routes, making them Wasserstein-infeasible.

**Case in point:** *Carpenter v. United States* (2018) held that accessing historical cell-site location information without a warrant violated the Fourth Amendment. The state's surveillance capability (cell tower data) was distributed across millions of Americans. The government's transport plan — collecting this data without particularized suspicion — moved surveillance power indiscriminately across the population. The Court required a warrant, which is to say: the transport plan must be particularized, minimizing the privacy cost imposed on non-targets.

---

## IV. Symplectic Constitutional Balance

A symplectic manifold is a smooth space equipped with a closed, nondegenerate 2-form ω. The symplectic structure pairs position and momentum — you cannot specify both independently. Physical systems with symplectic structure conserve energy; those without it are dissipative.

The separation of powers is a symplectic structure. The Executive is position: action, implementation, the application of force. The Legislative is momentum: law-creation, the generation of policy-direction that shapes future action. The Judicial is the symplectic form ω itself: it measures whether executive action is consistent with legislative direction. It evaluates whether position and momentum are compatible.

Checks and balances are the conservation laws guaranteed by the symplectic structure. Just as Noether's theorem connects symmetries to conserved quantities in physics, the constitutional symplectic structure connects institutional balance to conserved liberties. When the system is symplectic — when all three branches function and check each other — liberty is conserved. Power may flow between branches, but the total "Hamiltonian" (the balance of power) remains constant.

When one branch dominates, the symplectic form degenerates. ω becomes rank-deficient: it can no longer pair position and momentum independently. The system becomes dissipative — it loses the conserved quantity. In physics, dissipation means energy is lost to heat. In governance, dissipation means liberty is lost to authoritarianism. The system appears to function (laws are passed, actions taken) but the structural guarantee of conservation is gone.

**Case in point:** The expansion of executive power through signing statements, unchecked surveillance programs, and extrajudicial killings via drone strikes represents a degeneration of the symplectic form. The Executive has seized both position and momentum — it acts (position) and creates de facto policy through interpretation and non-enforcement (momentum). The Legislative, which should provide momentum, has been reduced to a spectator. The Judicial, which should be ω, frequently defers through doctrines like standing and political question, effectively setting ω = 0 in whole domains of governance. The result is a dissipative system: liberty is not conserved but steadily lost.

---

## V. Persistent Homology of Legal Precedent

Persistent homology studies the birth and death of topological features (connected components, loops, voids) as a filtration parameter varies. Features that persist across a wide range of parameters are signal; those that die quickly are noise.

Case law is a simplicial complex. Cases are vertices. Citations between cases are edges. Multi-case doctrines — established by cases that collectively articulate a principle — are higher simplices. A three-case doctrine (e.g., the *Miranda* trilogy) is a 2-simplex. A sprawling constitutional doctrine built across decades is a higher-dimensional simplex or a complex of simplices.

As we filter this complex — say, by requiring a minimum number of citations for an edge to appear, or by considering only cases within a certain time window — the topology changes. New connected components form as landmark cases appear. Loops form when circular citation patterns emerge (Case A cites B, B cites C, C cites A). Void-like structures appear when multi-case doctrines enclose a region of legal space.

The persistence diagram reveals which legal principles are structurally robust and which are fragile. A principle with high persistence — born early in the filtration and surviving across many thresholds — is deeply embedded in the legal complex. *Marbury v. Madison*'s principle of judicial review has maximal persistence: born in 1803, it has survived every filtration threshold for over two centuries.

When the Supreme Court overrules a precedent, a topological feature dies. *Brown v. Board of Education* (1954) killed *Plessy v. Ferguson*'s "separate but equal" doctrine — that's a persistence death. The feature born in 1896 survived until 1954, giving it moderate persistence. *Dobbs v. Jackson Women's Health Organization* (2022) killed *Roe v. Wade*'s abortion right — a feature born in 1973 that survived 49 years. In persistence homology terms, *Roe* had reasonable persistence but was ultimately not robust to the filtration threshold imposed by a transformed Court.

The "living Constitution" theory can be stated precisely in this framework: the filtration parameters should shift with societal change. What counts as a persistent feature depends on the scale at which you look. Originalists argue for a fixed filtration — the persistence diagram is frozen at the Founding. Living constitutionalists argue that the filtration should be indexed to evolving societal consensus, allowing new features to emerge and old ones to die as the parameter shifts.

**Case in point:** The persistence death of *Lochner*-era substantive due process is instructive. The *Lochner* doctrine (1905–1937) prohibited economic regulations that interfered with "liberty of contract." It had moderate persistence (32 years) but died when the Court switched course in *West Coast Hotel Co. v. Parrish* (1937) and related cases. In the persistence diagram, *Lochner* is a dot in the upper-left quadrant: born around 1905, dead by 1937, with a lifetime that is moderate but not extraordinary. It is distinguished from *Marbury*, which sits far to the right — its death has not yet occurred.

---

## VI. Categorical Legislation

A category consists of objects and morphisms between them, equipped with a composition law that is associative and has identities. A bill is a morphism: it maps the current state of the law to a proposed new state. Formally, a bill B: Law_current → Law_proposed.

An amendment is a 2-morphism — a morphism between morphisms. If the original bill B maps Law_0 → Law_1, and an amendment A modifies B, then A is a morphism from B to B', where B' is the amended bill. The legislative process — committee markup, floor votes, conference committee reconciliation — is the composition law that determines whether and how these morphisms compose into a final enacted law.

A filibuster is a refusal to compose. The morphism exists — the bill has been proposed, it has support — but the composition law cannot be applied because a procedural rule requires supermajority consent to proceed. The morphism is in the category but not in the subcategory of composable morphisms. Gridlock is a category with objects (areas of law needing reform) but no composable morphisms (no bills that can survive the legislative gauntlet). A healthy legislature has a rich hom-set — many morphisms between any two objects, providing multiple paths from the current state of the law to a better one.

Riders and earmarks are coproducts in the categorical sense: they combine unrelated morphisms into a single package. The legislator who attaches a rider to a must-pass bill is exploiting the categorical structure: if B: Law → Law' is a bill that will definitely compose (it has the votes), and R: Law → Law'' is a rider that would not compose on its own, then attaching R to B creates a coproduct B + R that composes because B is essential. This is not a bug in the categorical structure — it is an exploit of its composition law.

**Case in point:** The difficulty of passing standalone immigration reform in the United States, despite broad agreement that the system needs reform, is a case of categorical gridlock. The objects exist (everyone agrees the immigration system is an object in need of morphisms). Proposed morphisms exist (comprehensive immigration bills have been drafted). But the composition law — the legislative process — prevents them from composing. The result is a degenerate category where immigration law remains at a fixed point, unable to transition despite the existence of candidate morphisms.

---

## VII. The Conservation of Justice

If the legal system is symplectic, then by Darboux's theorem, the symplectic structure is locally standard — it looks the same everywhere. More importantly, symplectic systems conserve their Hamiltonian quantity. Justice, if it is the conserved quantity of a symplectic legal system, cannot be created or destroyed — only transformed.

This is not merely a mathematical conceit. It is a deep normative claim. You cannot create justice for one group by destroying it for another. You can redistribute it, transform it, move it through phase space. But the total quantity is conserved.

Mass incarceration is a symplectic violation. It appears to create justice (public safety, punishment, deterrence) but actually destroys more than it creates. The United States incarcerates more people per capita than any nation in history, yet the benefits in safety are marginal and unevenly distributed, while the costs — to families, communities, the incarcerated themselves, and the legitimacy of the legal system — are enormous. The Hamiltonian has increased on paper (more people punished) but the symplectic structure has degenerated (the system no longer conserves justice — it destroys it). Mass incarceration is dissipative: energy goes in, heat comes out, and the system is poorer for it.

Restorative justice is symplectic. It transforms harm without destroying the total justice of the system. The offender makes amends (a transformation of the offender's position in phase space). The victim receives acknowledgment (a transformation of the victim's position). The community is involved in the process (the symplectic form is maintained — all relevant coordinates are still coupled). No justice is destroyed; it is moved from one configuration to another. The Hamiltonian is conserved.

The normative implication is radical: any legal intervention that claims to produce justice but does so by inflicting irrecoverable harm — to the convicted, to their families, to their communities, to the social fabric — is not producing justice at all. It is running a dissipative process and calling the heat "justice." A genuinely just system must be symplectic: it must conserve the total quantity it claims to produce.

**Case in point:** South Africa's Truth and Reconciliation Commission was an attempt at a symplectic transformation. The apartheid regime had produced enormous harm. The retributive approach (Nuremberg-style trials) would have destroyed justice in one dimension (retribution served) while potentially destabilizing the system in others (civil conflict, continued division). The restorative approach — truth-telling in exchange for amnesty — transformed the harm into a new configuration: public acknowledgment, victim testimony, historical record. The total justice was conserved, but its form changed. Whether the transformation was fully symplectic — whether all the harm was genuinely transformed rather than merely displaced — remains contested. But the attempt was structurally sound in a way that purely retributive alternatives were not.

---

## Coda: Why This Matters

The purpose of this essay is not to reduce law to mathematics. Law is irreducibly human — it deals with persons, purposes, and values that no formalism can fully capture. The purpose is to show that the *structure* of legal reasoning has mathematical content, and that attending to that content yields genuine insight.

When a lawyer says "this circuit split needs resolving," she is identifying a cohomology obstruction. When a judge says "the mandatory minimum produces an unjust result in this case," she is observing tropical dominance. When a civil libertarian says "the surveillance state has gone too far," she is complaining about an unconstrained Wasserstein transport. When a constitutional scholar warns of executive overreach, she is diagnosing a degeneration of the symplectic form.

These are not metaphors. They are structural correspondences. The mathematics was always there. We are only now learning to read it.

A law professor who finishes this essay and sees their field differently has not learned new mathematics. They have learned to see the mathematics they already knew.

---

*The author invites correspondence from both lawyers who know category theory and mathematicians who know law. Both groups, the author suspects, are larger than either discipline realizes.*
