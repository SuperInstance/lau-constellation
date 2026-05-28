# The Wasserstein Diagnosis: Medicine as Optimal Transport

*An essay on the hidden mathematics of healing.*

---

A woman walks into the emergency room with chest pain, shortness of breath, and tingling in her left arm. The attending physician orders an EKG, checks troponin levels, asks about family history. Within minutes, the diagnosis crystallizes: myocardial infarction. Treatment begins.

What just happened — mathematically?

The physician performed a computation. Not with numbers on a page, but with likelihoods, weights, and decision boundaries in a high-dimensional space of symptoms, test results, and clinical experience. The physician transported a patient from the distribution "unknown" to the distribution "diagnosed," and in doing so, mapped a course from "diseased" to "treated."

This is not a metaphor. This is the mathematics of medicine, hiding in plain sight.

The thesis of this essay is simple: **medicine is already applied mathematics** — not in the statistical sense we're accustomed to, but in the deepest structural sense. Differential diagnosis is tropical algebra. Care coordination is sheaf cohomology. Drug design is optimal transport. Epidemic dynamics are symplectic geometry. Cancer is persistent homology. Clinical trials are category theory.

We just haven't named any of it correctly. And the naming matters, because once you see the structure, you can reason about it. You can fix what's broken. You can design what doesn't yet exist.

---

## 1. Tropical Diagnosis

Consider the emergency physician confronting our patient with chest pain. The differential includes myocardial infarction, pulmonary embolism, aortic dissection, costochondritis, panic attack, and gastroesophageal reflux. Each diagnosis has a likelihood — a number — and each symptom contributes a weight to that likelihood.

In tropical algebra, addition is replaced by the maximum operation, and multiplication is replaced by ordinary addition. A tropical polynomial is a maximum of affine functions. The tropical hypersurface — the set where two terms achieve equal maximum — is the decision boundary.

This is precisely what a diagnostician does. For each disease $d_i$, the physician computes a score:

$$\text{score}(d_i) = \max_j (w_{ij} + s_j)$$

where $w_{ij}$ is the weight of symptom $j$ for disease $i$, and $s_j$ is the observed severity of symptom $j$. The final diagnosis is the disease with the highest score: $\arg\max_i \text{score}(d_i)$.

The tropical hypersurface — where two diseases achieve equal tropical weight — is the boundary of diagnostic uncertainty. Our patient's presentation is classic: crushing chest pain radiating to the left arm, elevated troponin, ST-segment elevation. The tropical polynomial is not close to a corner. The diagnosis is clear.

But consider the atypical presentation: a woman with nausea, fatigue, and vague back discomfort. No chest pain. Normal EKG. This presentation sits near the tropical corner — the intersection of several tropical hypersurfaces — where MI, GERD, and musculoskeletal pain have nearly equal tropical weight. The diagnostician's polynomial must have the right coefficients to resolve this ambiguity, and those coefficients are not learned from textbooks. They are learned from seeing ten thousand patients and adjusting the weights through a training process that has no closed-form solution.

A good diagnostician is someone whose tropical polynomial has been calibrated by experience. A great diagnostician is someone who knows when they're near a corner — when the decision boundary is close — and orders the test that shifts the weights decisively.

This reframing is not merely decorative. Tropical geometry gives us tools to analyze decision boundaries, identify which tests move the patient furthest from the corner, and quantify diagnostic certainty in a way that respects the max-plus structure of clinical reasoning. Bayesian updating smooths things out; tropical algebra preserves the hard edges of clinical reality. Sometimes you're certain. Sometimes you're at a corner. The mathematics should reflect both.

---

## 2. Sheaf-Theoretic Care Coordination

A patient with diabetes, heart failure, and chronic kidney disease sees an endocrinologist, a cardiologist, and a nephrologist. Each specialist maintains a partial model of the patient — a section over their domain of expertise. The endocrinologist manages insulin protocols. The cardiologist manages diuretics and beta-blockers. The nephrologist manages electrolyte balance and dialysis scheduling.

The patient's body is the base space. Each specialist is a stalk in a sheaf. The patient's chart — the aggregate medical record — is a global section over this base space.

The fundamental requirement of coordinated care is that these local sections must agree on overlaps. When the cardiologist increases the diuretic dose, this affects the nephrologist's domain (fluid balance, potassium levels) and the endocrinologist's domain (renal glucose handling). The restriction maps of the sheaf — the formal mechanism by which sections on larger open sets restrict to smaller ones — are precisely the referral and communication pathways between specialists.

**Care fragmentation is $H^1 \neq 0$.**

When the first cohomology group of the care sheaf is nontrivial, local sections exist that cannot be glued into a global section. The cardiologist's plan and the nephrologist's plan are individually coherent but mutually incompatible. The patient is caught between two local treatments that cannot be reconciled into a single treatment plan. This is not a failure of any individual physician. It is a topological property of the care network.

A hospital with good care coordination has low cohomology. The communication channels — the restriction maps — are well-defined, low-latency, and correctly structured. A hospital with poor coordination has high cohomology: local sections that don't glue, patients who fall through the cracks, treatment plans that are individually reasonable but collectively contradictory.

The patient who falls through the cracks — whose medication interaction is missed, whose allergy is forgotten in the handoff, whose follow-up is lost in the transition from inpatient to outpatient care — is an unsheafable local section. The section exists locally (each physician knows their piece) but cannot be extended globally (no one has the complete picture).

This is not a process problem. It is a mathematical problem with process solutions. The sheaf structure tells you what to fix: you need better restriction maps (standardized handoff protocols), well-defined cover (clear assignment of primary responsibility), and gluing conditions (explicit compatibility checks between treatment plans). Every hospital that has implemented a successful care coordination system has, whether they know it or not, reduced the first cohomology of their care sheaf.

---

## 3. Wasserstein Drug Discovery

A drug is a map. It takes a patient's biochemical state — the distribution of proteins, metabolites, signaling molecules, gene expression levels — and moves it. The question is: moved it where?

In the language of optimal transport, a drug is a transport plan. The diseased state is a probability distribution $\mu$ over the space of biochemical configurations. The healthy state is another distribution $\nu$. The drug's job is to transport $\mu$ into $\nu$ — to move the mass of the patient's biochemistry from where it is to where it should be.

The Wasserstein distance $W(\mu, \nu)$ measures the cost of this transport. The optimal drug minimizes this distance: it achieves the therapeutic effect with minimal disruption to the patient's biochemistry.

Side effects are transport through the wrong part of the state space. The drug moves mass where it shouldn't — inhibiting an off-target enzyme, activating a receptor in the wrong tissue, altering a signaling pathway that was fine. The chemotherapy drug that kills cancer cells but also destroys the gut epithelium is a transport plan with high off-target cost: it moves the tumor distribution toward healthy, but simultaneously transports the gut mucosa distribution toward pathological.

This framing makes precise something pharmacologists have always known intuitively: the therapeutic index of a drug is a ratio of transport costs. Good drugs have a high ratio of on-target transport (therapeutic effect) to off-target transport (toxicity). Great drugs are optimal transport maps — they move the biochemical distribution along geodesics in the state space, achieving the therapeutic target with minimal total displacement.

Drug combination therapy is a composition of transport plans. Two drugs applied sequentially define a composite transport map. The question of whether drugs interact synergistically or antagonistically is a question about the curvature of the biochemical state space: in flat space, transport maps compose straightforwardly; in curved space, the composition depends on the path.

Pharmacology *is* optimal transport. We just haven't been using the language. Doing so opens the door to computational drug design that optimizes the full transport plan rather than individual molecular interactions — designing drugs that move the entire biochemical distribution, not just modulate a single target.

---

## 4. Symplectic Epidemics

The SIR model — Susceptible, Infected, Recovered — is the workhorse of mathematical epidemiology. It is typically written as a system of ordinary differential equations:

$$\frac{dS}{dt} = -\beta S I, \quad \frac{dI}{dt} = \beta S I - \gamma I, \quad \frac{dR}{dt} = \gamma I$$

This is usually presented as a compartmental model. But it has a deeper structure. If we identify $S$ (susceptible) with a position variable and $I$ (infected) with a momentum variable, the SIR dynamics become a Hamiltonian system on a constrained phase space. The total population $N = S + I + R$ is conserved — it is the symplectic volume, preserved by the flow.

The basic reproduction number $R_0 = \beta / \gamma$ is not merely a ratio of rates. In the symplectic framework, it is related to the eigenvalue of the symplectic form — the fundamental frequency of the epidemic's oscillation on the phase space. When $R_0 > 1$, the symplectic structure admits nontrivial orbits: epidemic waves. When $R_0 < 1$, the orbits collapse to fixed points: the disease dies out.

Vaccination is a canonical transformation. It reduces the susceptible population without changing the total population, effectively performing a coordinate change on the phase space that shrinks the accessible volume. Herd immunity is the condition where the symplectic volume — the phase space accessible to the epidemic — is too small to sustain periodic orbits. The disease can still exist as a fixed point (endemic), but it cannot sustain oscillations (epidemic waves).

This is not merely a reformulation. The symplectic structure reveals conservation laws that are invisible in the standard ODE framework. Liouville's theorem — the preservation of phase space volume by Hamiltonian flows — implies that epidemic dynamics are volume-preserving on the appropriate phase space. This constrains what interventions can achieve: you cannot shrink phase space volume through vaccination alone; you can only redistribute it. The epidemic's "mass" is conserved; vaccination redirects it from "infected" to "recovered" without passing through the infected state, but the total phase space volume remains.

The practical insight: interventions that change $R_0$ (masking, social distancing) are modifying the symplectic form itself — they change the geometry of the phase space. Interventions that move individuals between compartments (vaccination, treatment) are canonical transformations — they preserve the geometry but redistribute the population. Effective epidemic control requires both: modifying the geometry *and* redistributing the population.

---

## 5. Persistent Homology of Cancer

A tumor is not a uniform mass. It is a structured object with spatial heterogeneity, vascular architecture, clonal populations, and metabolic gradients. It has a topology.

Model the tumor as a simplicial complex. Cells are vertices. Adjacent cells sharing a blood vessel are connected by edges. Clusters of cells sharing a vascular supply form higher simplices. Metastatic clusters — groups of cells capable of seeding distant sites — are higher-dimensional simplices that appear only above a certain density threshold.

The persistent homology of this complex — computed by varying the distance threshold and tracking which topological features appear and persist — reveals the tumor's structural hierarchy. A $H_0$ barcode (connected components) captures the number of distinct tumor foci. A $H_1$ barcode (loops) captures vascular loops and necrotic regions. A $H_2$ barcode (voids) captures large-scale architectural features.

The persistence diagram is the clinical readout. Features with high persistence — those that survive across a wide range of distance thresholds — are deep structural patterns in the tumor. They correspond to stable clonal populations, well-established vascular networks, and robust metabolic circuits. These features will not respond to targeted therapy aimed at a single pathway, because the topology that supports them is too deeply embedded. You would need to destroy the entire complex to eliminate them.

Features with low persistence — those that appear and disappear quickly as the threshold varies — are superficial. They correspond to transient cellular aggregates, fragile vascular connections, and unstable metabolic states. These are treatable. A targeted drug that disrupts the right edges in the complex can cause these features to collapse.

This is already being done. Pathologists who assess tumor grade, vascularity, and necrosis are computing persistent homology by eye. They just don't call it that. Computational topology labs at Stanford, Oxford, and elsewhere are building the formal tools. The gap is not technical — it is conceptual. The oncology community needs to understand that the persistence diagram is not an exotic mathematical object. It is a tumor map, and it tells you what you can and cannot treat.

The clinical insight is sharp: **high-persistence features require systemic intervention (immunotherapy, radiation, surgery). Low-persistence features respond to targeted intervention (kinase inhibitors, anti-angiogenics).** The persistence diagram is the prescription.

---

## 6. Categorical Clinical Trials

A clinical trial is a functor.

Let $\mathcal{P}$ be the category of patients. Objects are patients, with their demographics, comorbidities, and baseline characteristics. Morphisms are the relationships between patients: same age group, same disease stage, same genetic profile.

Let $\mathcal{O}$ be the category of outcomes. Objects are clinical endpoints — survival, remission, adverse events. Morphisms are the relationships between outcomes: overall survival implies progression-free survival; a grade 3 adverse event implies a grade 2 adverse event.

A clinical trial defines a functor $F: \mathcal{P} \to \mathcal{O}$ that maps each patient (object) to an outcome (object) and preserves the structure: if patient $A$ is similar to patient $B$ (morphism), then their outcomes should be related (morphism).

Bias is a natural transformation that shouldn't exist. If the trial is well-designed, the functor $F$ should commute cleanly: similar patients should get similar outcomes, adjusted only for the treatment effect. If there is a systematic bias — socioeconomic status confounding the treatment assignment, for example — then there is a natural transformation $\eta: F \Rightarrow G$ where $G$ is the "true" treatment effect functor and $\eta$ represents the distortion introduced by the confounder.

A well-designed trial is a faithful functor: it preserves the structure of treatment effects. The mapping from patients to outcomes is injective on morphisms — distinct patient profiles map to distinct outcome profiles, and the relationships between patients are accurately reflected in the relationships between outcomes.

A poorly designed trial is a functor that factors through a confounding category. Instead of $F: \mathcal{P} \to \mathcal{O}$ directly, the mapping factors as $\mathcal{P} \to \mathcal{C} \to \mathcal{O}$, where $\mathcal{C}$ is the category of socioeconomic status, insurance type, or geographic location. The apparent treatment effect is actually the composition of the treatment effect with the confounding effect. Randomization is the attempt to make $\mathcal{P} \to \mathcal{C}$ an isomorphism — to ensure that the confounding category is trivial, so the functor factors through it without distortion.

Subgroup analysis is a restriction of the functor to a subcategory. The question "does this drug work in elderly patients?" is the question: does the restricted functor $F|_{\mathcal{P}_{\text{elderly}}}$ remain faithful, or does the restriction lose too much structure to draw conclusions?

This categorical framing makes precise the conditions under which a trial's conclusions are valid. A trial is externally valid when the functor extends from the trial population to the general population — when there is a natural transformation from the trial functor to the population functor that preserves the treatment effect. A trial is internally valid when the functor is faithful — when it doesn't factor through confounders.

---

## 7. The Conservation of Healing

The deepest insight of this mathematical reframing is not about any single technique. It is about the nature of healing itself.

If the body is a dynamical system on a symplectic manifold — a system governed by conservation laws, Hamiltonian flows, and volume-preserving transformations — then health is the state where the symplectic structure is intact. Energy is conserved. Momentum is balanced. Phase space volume is preserved. The body's homeostatic mechanisms are the symplectic integrators that keep the trajectory on the correct manifold.

Disease is symplectic violation. The conservation laws break down. The trajectory leaves the manifold. Energy is dissipated where it shouldn't be, or concentrated where it shouldn't go. The phase space volume shrinks or expands in ways the system cannot accommodate. The tumor grows because the constraint on cell division — a conservation law — has been violated. The heart fails because the Hamiltonian that should maintain cardiac output no longer preserves the energy invariant.

Treatment does not create health. Health is not a substance that can be added. Treatment transforms the system back into a symplectic manifold where the conservation laws hold again. The antibiotic doesn't "create" health — it removes the bacteria that were violating the conservation laws. The insulin doesn't "create" health — it restores the glucose transport that allows the metabolic Hamiltonian to conserve energy. The surgery doesn't "create" health — it removes the obstruction that was preventing the system from returning to its manifold.

This reframes the entire Hippocratic tradition. *Primum non nocere* — first, do no harm — is the principle that your intervention should not introduce new symplectic violations. *Vis medicatrix naturae* — the healing power of nature — is the recognition that the body is already a symplectic system that wants to conserve its invariants. The physician's role is not to cure. It is to restore the conditions under which the body cures itself.

This is the Wasserstein diagnosis, in its fullest sense. The physician is an optimal transport planner, moving the patient from the diseased distribution back to the healthy one. But the healthy distribution was always there — it is the symplectic structure of the living body, the attractor that the system wants to return to. The physician doesn't create the attractor. They clear the obstacles that prevent the system from reaching it.

Medicine is not applied statistics. It is applied geometry — the geometry of living systems, the transport plans that connect disease to health, the symplectic structures that make life possible.

The mathematician sees the structure. The physician lives it. The patient is the base space on which both operate.

---

*The physician who finishes this essay and sees the next patient differently has understood everything. The mathematics was never the point. The mathematics was always the point.*
