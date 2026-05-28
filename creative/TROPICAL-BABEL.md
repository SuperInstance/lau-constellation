# The Tropical Babel: Why Every Language Is a Different Algebra

*A speculative essay on the mathematics hidden in human language.*

---

There is a story, probably apocryphal, that the MIT linguist Kenneth Hale could speak more than fifty languages. When asked how he kept them straight, he reportedly said he didn't — each one rewired his thinking so completely that switching felt less like translation and more like rebooting into a different operating system.

Hale was right, and more right than he knew. What he sensed intuitively — that languages are not different labelings of the same underlying system but genuinely different mathematical structures — can be made precise. The tools come from algebraic geometry, algebraic topology, optimal transport, symplectic geometry, geometric algebra, and category theory. The thesis of this essay is that these are not metaphors. They are literal descriptions of the mathematical structure of natural language, and they yield testable predictions.

The unifying thread is tropical geometry — the geometry of the max-plus semiring — which turns out to be the natural algebra for discrete optimization problems. Language, I will argue, is the most elaborate discrete optimization problem ever evolved.

---

## 1. Tropical Phonology

**Mathematical Claim.** Phonological feature systems are tropical semirings. The relevant operations are tropical addition (max) and tropical multiplication (+). A phonological rule system is a tropical circuit: rules apply in sequence (tropical multiplication) and the output is the winning candidate (tropical addition, i.e., argmax over a ranked constraint system). Sound change over historical time is the degradation of a tropical polynomial — constraints weaken, reorder, or merge, producing regular sound laws that look like piecewise-linear transformations.

**Linguistic Evidence.** Consider Optimality Theory (Prince & Smolensky, 1993), the dominant framework in phonology since the 1990s. In OT, a set of candidates is evaluated by ranked constraints. The winner is the candidate that best satisfies the highest-ranked constraint on which it differs from competitors. This is literally a tropical evaluation: each constraint assigns a violation count (a penalty), the total penalty is the sum (tropical product), and the winner minimizes this sum, which in the max-plus formulation is equivalent to taking the max over satisfied constraints.

But the tropical structure goes deeper. A sound — say, the voiced bilabial stop /b/ — is not a single point in feature space. It is a constellation of acoustic cues: voice onset time, formant transitions, burst amplitude. The listener's task is to recover the intended category from this constellation, and they do it by taking the max over competing interpretations. The [±voice] feature is not a binary switch; it is the tropical sum of multiple continuous cues, thresholded.

Sound change follows. Grimm's Law — the systematic shift of Proto-Indo-European stops in Germanic — is a tropical polynomial transformation. The input stops, parameterized by their feature vectors, are mapped through a piecewise-linear function (tropical polynomials are piecewise-linear) to their Germanic reflexes. The regularity of sound change — the Neogrammarian hypothesis — is a consequence of the piecewise-linearity of tropical maps: small changes in input produce predictable, structured changes in output.

**Testable Prediction.** If phonological rule systems are tropical circuits, then the set of possible phonological inventories should form a tropical variety — a set defined by tropical polynomial equations. Specifically: languages should cluster in the space of possible segment inventories along the strata of a tropical prevariety. Feature combinations that violate the tropical equations should be systematically absent. A computational check: construct the tropical variety defined by the constraint rankings of a sample of languages, and verify that unattested inventories fall outside it. This is a falsifiable empirical claim.

---

## 2. Sheaf Semantics

**Mathematical Claim.** The meaning of a word is not a point in some space of referents. It is a section of a sheaf over a topological space of contexts. Each context (or context type) is an open set. Over each open set, the sheaf assigns a set of possible meanings — the senses that are viable in that context. The gluing condition determines when locally consistent meanings assemble into a global meaning. Polysemy is the failure of the gluing condition: when the sheaf has nonzero first cohomology, there exist words whose meanings cannot be unified into a single global section.

**Linguistic Evidence.** Consider the word "bank." In the context of finance, it means a financial institution. In the context of rivers, it means the edge of a waterway. These are two sections over two overlapping open sets. The overlap — a context where both financial and riverine readings are simultaneously available (a joke about a river bank, a pun about a bank flowing with money) — is where the gluing condition is tested. Most of the time, context disambiguates, and the sections glue trivially. But in poetry, in double entendres, in the deliberate exploitation of ambiguity, the sheaf refuses to glue cleanly. The result is the experience of multiple simultaneous meanings — what William Empson called the seventh type of ambiguity.

The sheaf-theoretic view predicts a precise taxonomy of ambiguity. When H¹ = 0 for a given word, all its contextual meanings can be glued into a single global section — the word is merely vague, not genuinely polysemous. When H¹ ≠ 0, the word is truly polysemous: its meanings cannot be unified. The dimension of H¹ measures the degree of polysemy. A word like "set" (which the OED gives 430 distinct senses for) has high-dimensional cohomology.

**Testable Prediction.** Construct a simplicial complex of contexts for a corpus (contexts are vertices; shared words between contexts are edges; overlapping usage patterns fill in higher simplices). Define a sheaf by assigning to each context the set of senses attested there. Compute the sheaf cohomology. Words with large H¹ should correlate with: (a) higher dictionary sense counts, (b) greater processing time in psycholinguistic experiments on ambiguity resolution, and (c) higher frequency in literary corpora (because literature exploits nontrivial cohomology). The cohomological dimension of a text's sheaf could serve as a quantitative measure of its "poetic density."

---

## 3. Wasserstein Translation

**Mathematical Claim.** Translation is optimal transport between probability distributions over meaning spaces. The source language defines a distribution μ over a meaning space M_s. The target language defines a distribution ν over a meaning space M_t. A translation is a transport plan T: M_s → M_t that maps meanings from the source distribution to the target, minimizing the Wasserstein distance W(μ, ν) — the cost of moving the semantic mass from one distribution to the other.

**Linguistic Evidence.** The Sapir-Whorf hypothesis, in its weak form, claims that different languages partition the semantic space differently. Russian has two words for blue — *sinij* (dark blue) and *goluboj* (light blue) — where English has one. The German *Schadenfreude* has no single-word English equivalent. These are not mere gaps in vocabulary; they reflect genuinely different distributions over the semantic space. The English distribution for "blue" is a single Gaussian centered on the concept. The Russian distribution is bimodal.

A translator faces an optimal transport problem. They must move the semantic mass of the source text into the target language while minimizing distortion. When the distributions are similar — English "cat" to French "chat" — the transport cost is low. When they differ — English "blue" to Russian, or any language to one without a word for *Schadenfreude* — the cost is high, and the translator must choose: spread the mass (a descriptive phrase), concentrate it (pick the nearest word, losing nuance), or leave it unmoved (borrow the word outright).

Untranslatable words are transport bottlenecks. In optimal transport theory, a bottleneck is a region where mass must flow through a narrow corridor — the cost is high because the feasible maps are constrained. An untranslatable word is exactly this: semantic mass that cannot be transported to the target distribution without significant distortion. The Monge formulation (deterministic map) fails; the Kantorovich formulation (probabilistic coupling) is needed, allowing one source meaning to split across multiple target meanings.

**Testable Prediction.** Define a metric on meaning space using contextual embeddings (e.g., from a large language model). Compute the Wasserstein distance between the semantic distributions of cognate word sets across languages. The prediction: Wasserstein distances should correlate with (a) translator difficulty ratings, (b) frequency of borrowing or loanwords, and (c) the number of words a bilingual speaker reports needing to translate a given concept. Furthermore, the optimal transport map itself should predict the multi-word expressions translators actually use for difficult words. This is directly computable from existing models and corpora.

---

## 4. Geometric Grammar

**Mathematical Claim.** Syntactic structures are multivectors in a geometric (Clifford) algebra. Noun phrases, verb phrases, and other constituents are grade-1 vectors. The combination of constituents is the geometric product, which decomposes into a scalar inner product (semantic compatibility) and a bivector outer product (the syntactic relationship). Chomsky's Merge operation is the wedge (outer) product. Syntactic dependencies are bivectors. Center-embedding and recursive structures arise from the iterative application of the outer product.

**Linguistic Evidence.** The geometric product of two vectors a and b is ab = a·b + a∧b. The dot product a·b measures how much the two vectors align — their semantic compatibility. The wedge product a∧b is a bivector — an oriented plane — representing the irreducible relational structure between them. When you merge a noun phrase "the cat" with a verb phrase "sat on the mat," you get: a scalar (the sentence makes sense, the selectional restrictions are met) plus a bivector (the subject-verb relationship, which is an asymmetric, directed relation).

Recursion falls out naturally. The outer product is associative: (a∧b)∧c = a∧(b∧c). Embedding a relative clause inside a noun phrase is just applying the outer product iteratively. The center-embedding limitation — the fact that humans struggle with more than two or three levels of embedding — corresponds to the geometric fact that in a low-dimensional space, repeated wedge products eventually vanish. The grade of the resulting multivector cannot exceed the dimension of the space. If the syntactic space has dimension ~7 (corresponding to the number of simultaneous dependencies humans can track), then the eighth embedding produces zero — it cannot be parsed.

**Testable Prediction.** Represent sentences as elements of a geometric algebra. Define basis vectors for syntactic categories (N, V, Adj, etc.) with the metric tensor encoding selectional preferences (N·V is large for compatible N-V pairs, small for incompatible ones). Parse sentences by computing their geometric products. The prediction: parsing difficulty in self-paced reading experiments should correlate with the grade of the resulting multivector. Sentences that produce high-grade multivectors (many nested dependencies) should be harder to process, with a sharp cliff at the grade corresponding to the dimension of the syntactic space — providing a precise, numerical prediction for the psycholinguistic "embedding limit."

---

## 5. Symplectic Pragmatics

**Mathematical Claim.** A conversation is a Hamiltonian system on a symplectic manifold. The speaker's intent is the position variable q. The listener's interpretation is the momentum variable p. The symplectic form ω = dq ∧ dp encodes the coupling between production and comprehension. Successful communication follows a trajectory that preserves ω — the conversation flows without loss of mutual understanding. Misunderstanding is a violation of the symplectic structure — the phase space trajectory diverges from the Hamiltonian flow.

**Linguistic Evidence.** In a well-functioning conversation, there is a conserved quantity: mutual understanding, or more formally, the amount of shared information (common ground) accumulated per unit of conversational time. This is the Hamiltonian H(q, p) — the total energy of the system. The equations of motion are:

dq/dt = ∂H/∂p (the speaker adjusts their utterance based on the listener's interpretation)
dp/dt = -∂H/∂q (the listener updates their interpretation based on the speaker's utterance)

This is Grice's cooperative principle, made mathematical. The maxims of conversation (quantity, quality, relation, manner) are constraints on the Hamiltonian: they ensure the system evolves toward a state of maximal mutual understanding with minimal expenditure of cognitive energy.

Sarcasm is a canonical transformation — a coordinate change that preserves the symplectic form but alters the trajectory. The speaker says one thing (the surface form) but means another (the deep form). The listener must apply the inverse canonical transformation to recover the intended meaning. This is why sarcasm is harder to process: it requires computing a coordinate transformation on the fly. It is also why sarcasm is culturally specific: the canonical transformation is learned, not universal.

**Testable Prediction.** Code a conversational agent as a Hamiltonian system. Define q as the speaker's intent vector and p as the listener's belief state vector. Define H as the negated KL-divergence between them. Evolve the system via Hamilton's equations. The prediction: the trajectories of real conversations (coded from dialogue corpora with intent and belief annotations) should lie close to the Hamiltonian flow. Conversational breakdowns — points where participants report misunderstanding — should correspond to violations of the symplectic condition (measurable as the failure of the area form dq∧p to be preserved). This provides a quantitative, differential-geometric theory of conversational dynamics.

---

## 6. Persistent Topology of Narrative

**Mathematical Claim.** A narrative is a filtered simplicial complex. Characters are vertices. Their interactions (shared scenes, dialogues) are edges. Multi-character relationships (love triangles, rival factions) are higher simplices. The narrative unfolds in time, and the filtration parameter is narrative time. Persistent homology tracks which topological features — connected components, cycles (loops of relationship), voids (enclosed social structures) — persist across the narrative and which are transient. The persistence diagram of a narrative is its topological fingerprint.

**Linguistic Evidence.** Consider *Romeo and Juliet*. The Montagues and Capulets form two initially disconnected components (H₀ has two generators). Romeo and Juliet's relationship creates a bridge — the components merge. The feud creates a cycle: Romeo → Juliet → Capulets → Montagues → Romeo. This cycle (a generator of H₁) persists through most of the play. The deaths in the final act break the cycle — the H₁ generator dies. The persistence diagram records: the feud-cycle was born early and died late — high persistence. The minor characters' interactions (Servant A, Servant B) create edges that appear and vanish quickly — low persistence.

Now consider a Marvel movie. Many characters, many interactions, but the relational structure is shallow: characters team up, fight, team up again. The H₁ generators are short-lived (alliances form and break within scenes). The persistence diagram is concentrated near the diagonal — low persistence. Shakespeare has points far from the diagonal. Marvel has points near it. This is not aesthetic judgment; it is a topological measurement.

The "shape" of a story — the distribution of its persistence diagram — correlates with its genre and quality. Tragedies have high-persistence H₁ generators (enduring conflicts that only resolve in catastrophe). Comedies have low-persistence generators (misunderstandings that resolve quickly). Epic narratives have high-persistence H₀ generators (factions that remain distinct throughout). Soap operas have many short-lived H₁ generators (transient romantic entanglements).

**Testable Prediction.** Construct filtered simplicial complexes from narrative texts: characters as vertices, shared scenes as edges (weighted by scene duration or dialogue length), multi-character scenes as higher simplices. Compute persistence diagrams. The prediction: the statistical distribution of persistence lifetimes will cluster by genre in a statistically significant way, outperforming bag-of-words genre classifiers on small datasets. Furthermore, critically acclaimed narratives should have higher average persistence (enduring relational structures) than formulaic ones. This is computable from existing annotated corpora (e.g., the Literary Plot Summaries dataset) and could serve as a quantitative metric for narrative complexity.

---

## 7. Categorical Linguistics

**Mathematical Claim.** Languages are categories. Words (or morphemes) are objects. Syntactic rules are morphisms. Composition of rules is composition of morphisms. Translation between languages is a functor. A good translation is a functor that preserves limits (the structure of meaning — products correspond to conjunctions, equalizers to disambiguations) and colimits (the accumulation of context — coproducts correspond to alternatives, coequalizers to contextual resolution). The existence of multiple non-isomorphic functors between two languages is why there are multiple valid translations of the same text.

**Linguistic Evidence.** A functor F: L_s → L_t between source and target language categories must map each object (word) to an object and each morphism (syntax rule) to a morphism, preserving composition. The requirement that F preserve composition is the requirement that the translation of a sentence equals the composition of the translations of its parts — this is the principle of compositionality, which every theory of translation assumes implicitly.

But functors can be non-isomorphic. Consider translating the English sentence "I love you" into Japanese. The functor must map the English pronoun system to the Japanese one, but Japanese pronominals are far more context-dependent and socially marked. There are multiple valid functors: one that maps "I" to *watashi* (formal), another to *boku* (informal masculine), another to *ore* (very informal masculine). Each is a valid functor — each preserves the compositional structure — but they are not isomorphic. They produce genuinely different translations. The space of valid translations is the space of structure-preserving functors.

Limits and colimits capture deeper translation properties. The product A × B in a language category represents the joint meaning of A and B (conjunction). A functor preserving products preserves joint meaning — the translation of "cats and dogs" should represent the conjunction faithfully. A functor preserving equalizers preserves distinctions — if the source language distinguishes two readings of a word, the target should maintain the distinction (or explicitly collapse it, which is a non-full functor). Languages without certain limits or colimits — languages that cannot make certain distinctions or accumulate certain kinds of context — are harder to translate into, because the functor cannot preserve structure that doesn't exist in the target.

**Testable Prediction.** Formalize a fragment of two languages as categories (this has been done for fragments of English and Japanese in categorial grammar). Compute the category of functors between them. The prediction: the number of non-isomorphic functors should correlate with the number of distinct published translations of literary works between those languages. For a concrete test: take a literary work translated into multiple languages by multiple translators (e.g., Kafka's *Metamorphosis*). For each target language, compute the space of admissible functors from a formalized German fragment. The prediction is that languages with more non-isomorphic functors from German will have greater variance in their translations — more translatorly choices, more distinct published versions.

---

## Coda: The Tower, Rebuilt

The biblical story of Babel has God confounding human language to prevent the construction of a tower to heaven. The irony is that confounding language didn't prevent the construction — it multiplied it. Every language is its own tower, built from its own algebraic materials, reaching toward the same sky by a different structural path.

What the mathematics in this essay suggests is that these paths are not arbitrary. They are constrained by deep geometric, algebraic, and topological principles. Phonology is tropical. Semantics is sheaf-theoretic. Translation is optimal transport. Syntax is geometric algebra. Pragmatics is symplectic. Narrative is topological. The whole edifice is categorical.

These are not analogies. Each claim comes with a testable prediction: tropical varieties should constrain phonological inventories; sheaf cohomology should predict polysemy and poetic density; Wasserstein distances should predict translation difficulty; geometric algebra grades should predict parsing load; symplectic preservation should track conversational success; persistence diagrams should classify narrative genre; and functor spaces should predict translational variance.

If even a fraction of these predictions hold, they would constitute evidence that human language is not merely *describable* by advanced mathematics — it *is* an advanced mathematical structure, evolved under pressure to optimize communication over a noisy channel with finite resources. The tropical semiring, the sheaf condition, the Wasserstein metric, the geometric product, the symplectic form, persistent homology, and categorical functoriality are not tools we impose on language from outside. They are the algebra of what language has always been doing.

Every language is a different algebra. The miracle is that we can learn each other's.

---

*Essay composed May 2026. All mathematical frameworks referenced are active research areas. The linguistic claims are speculative but falsifiable, which is the only honest thing a mathematical theory of language can be.*
