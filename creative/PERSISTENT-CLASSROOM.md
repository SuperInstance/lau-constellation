# The Persistent Classroom: How Children Would Learn If We Taught the Shape of Thought

*An essay in seven lessons*

---

There is a moment—every teacher has seen it—when a child's face changes. Not the crumple of frustration or the brightening of a correct answer. Something else. A tilt of the head, a widening of the eyes, as though a door they didn't know existed has just swung open onto a landscape they somehow already recognized. That moment is not learning. It is *naming*. The child already knew the thing. They just didn't have the word for it.

What follows is an argument that our entire educational apparatus is built on a naming failure of staggering proportions. We teach children arithmetic before we teach them what arithmetic is *for*. We teach them to collaborate before we teach them what collaboration *is*. We teach them to play, to move, to make friends, to understand themselves—and we treat all of these as though they were separate activities, each with its own siloed logic, each unworthy of the language that could make them legible.

But mathematics—the real mathematics, not the worksheet arithmetic that passes for it—is the language of structure. And children are structural thinkers. They have to be. The world is a firehose of pattern, and any creature that survives childhood has already developed sophisticated tools for swimming in it.

What if we named those tools? What if we taught the shape of thought itself?

---

## I. Tropical Kindergarten

Consider the following conversation, which happens in every kindergarten classroom on Earth:

"Who's the tallest?"

A child stands up. Measures against the wall. Another child stands up. The class agrees: this one is taller. A third. No—shorter than the second. The tallest-so-far remains.

What just happened? The children computed **max**. Not addition. Not multiplication. Max.

Now consider: "How many days until my birthday?"

The child counts forward from today. Fifteen. Tomorrow is one closer—fourteen. Each day *subtracts* one from the count.

What happened here? Tropical addition. In the tropical semiring, addition is max (or min) and multiplication is ordinary addition. "Counting forward" is tropical multiplication. "Who is tallest" is tropical addition. The tropical semiring is, in a precise mathematical sense, *simpler* than the ring of integers. It has fewer operations, fewer axioms, fewer opportunities for error.

We do not start with tropical mathematics because it is easier. We start with ordinary arithmetic because of the printing press, the merchant's ledger, the tax collector's spreadsheet. History chose addition first. Cognitive science would not.

Imagine a tropical-first curriculum. Age five: comparison. Max, min. Who is tallest, who arrived first, which bowl has more grapes? Age six: counting-forward as multiplication. Days until birthday, steps to the door, hops to the next square. Age seven: the revelation. *There is another algebra*, the children learn, where addition means something different. Where you combine things by putting them together rather than comparing them. Standard arithmetic is introduced not as the foundation of all mathematics, but as a *dual*—a mirror image of the tropical world they already inhabit.

Some children struggle with carrying in addition. They never struggled with "who has more?" We already know which algebra comes naturally. We simply refused to name it.

---

## II. Sheaf Group Projects

Every teacher who has assigned a group project knows the particular agony of watching students partition work like diplomats dividing territory. You take section one. I'll take section three. We'll staple it together Thursday night. What arrives is a Frankenstein document—seams visible, voices mismatched, each section written as though the others didn't exist.

The students are not lazy. They lack a vocabulary for what they're attempting.

In mathematics, a **sheaf** is a tool for gluing local information into a global picture. Each point in a space has a stalk—a collection of local data. The sheaf tells you when those local pieces are *compatible*, when they agree on their overlaps and can be seamlessly combined into a global section. When they can't—when the local pieces contradict each other in the places where they meet—the obstruction is measured by something called sheaf cohomology, specifically the first cohomology group H¹.

A group project *is* a sheaf. Each student is a stalk with local knowledge—their section of the report, their expertise, their understanding of the problem's corner. The overlaps are the places where their work must agree: shared definitions, consistent assumptions, a narrative arc that threads through every section. The global section is the completed project—a coherent whole that could not have been produced by any single student alone.

And the teacher? The teacher is sheaf cohomology.

When a teacher circulates during group work, identifying contradictions and gently redirecting—"Your section says the experiment started Tuesday, but theirs says Monday"—the teacher is computing H¹. They are finding the obstructions to gluing and helping students resolve them.

This reframing has a practical implication. A well-designed group project should have *exactly the right amount of H¹*. Too little obstruction, and the project is trivial—each student's work is independent, and collaboration is performative. Too much, and the project is impossible—the local sections can never agree, and the group dissolves into frustration. The art of assignment design is the art of calibrating obstruction: enough to require genuine negotiation, not so much that the task collapses.

Teach students this language, and something shifts. They stop seeing disagreement as failure. "Our sections don't glue yet" is not a crisis—it is a diagnostic. It means there is cohomological work to do. The obstruction is not between *them*, personally. It is between their *local sections*, structurally. And structures can be repaired.

---

## III. Wasserstein Grading

The problem with grades is not that they are numbers. The problem is that they are *the wrong kind* of numbers.

A student who scores 80/100 on a test has been reduced to a scalar. But what does 80 mean? Perhaps they aced eight topics and failed two entirely. Perhaps they are mediocre at all ten. Perhaps they understood everything but made arithmetic errors. The scalar conceals all of this. Two students with identical scores may be nothing alike.

In optimal transport theory, the **Wasserstein distance** measures the cost of transforming one probability distribution into another. It doesn't ask "are these distributions the same number?" It asks: *how much work would it take to reshape this distribution into that one?*

Apply this to grading. Each student has a distribution over skills—a landscape of competence with peaks and valleys. The target is the mastery distribution: what a fully educated person should look like across all relevant dimensions. The grade is the Wasserstein distance between the student's distribution and the target.

This changes everything. A student who has mastered eight of ten topics perfectly has a distribution that is close to the target in most coordinates but has two deep valleys. The Wasserstein distance captures that their valleys are narrow and deep—concentrated gaps that could, in principle, be filled efficiently. A student who is mediocre at all ten has a distribution that is uniformly too low—every skill needs lifting, and the transport cost reflects this different shape entirely.

Same total points. Completely different students. Completely different interventions.

Under Wasserstein grading, the teacher's job becomes legible: identify the shape of each student's distribution and plan the most efficient transport toward mastery. Tutoring fills deep valleys. Review lifts the entire landscape. Enrichment raises peaks higher. Each intervention is a different kind of transport operation, and the Wasserstein framework tells you which one is needed.

Students, too, gain clarity. "I'm an 80" tells you nothing. "My distribution is strong in algebra but has a valley in geometry" tells you exactly where you stand and where to walk.

---

## IV. The Geometric Algebra of Play

Watch a child with building blocks. They don't think in terms of individual pieces. They think in terms of *arrangements*—a tower, a bridge, a wall, a fort. Each arrangement has a structure that is more than the sum of its blocks. A tower is not "block plus block plus block." It is a specific ordering in space, a configuration with emergent properties (it's tall, it's unstable, it falls over if you bump it).

In geometric algebra, a multivector is a sum of objects of different grades: scalars (grade 0), vectors (grade 1), bivectors (grade 2), and so on. A single block is a grade-1 object. An arrangement of blocks—an L-shape, a line, a cube—is a higher-grade object with its own algebraic properties. The child is not stacking blocks. They are composing multivectors.

Give a child Play-Doh, and the operation becomes conformal. In conformal geometric algebra, you embed your space in a higher-dimensional one where spheres become vectors and all transformations—translation, rotation, scaling—become simple operations. A child rolling a ball of dough and stretching it into a snake is performing conformal transformations. The dough doesn't care about coordinates. It deforms continuously, and the child's hands are the motors—the rotation-translation operators of conformal geometry.

Tag is a rotor. The child chasing another around the playground is tracing a rotation in the plane. The geometry is simple—minimize the angle between chaser and target—but the dynamics are rich: acceleration, deceleration, feints. Every child who has ever played tag has executed a real-time optimization over rotations.

Hide-and-seek is the dual operation. In geometric algebra, the dual of a multivector is its complement—the thing that is not it, computed relative to the full space. The seeker's task is to compute the dual of the hider's position: given what I've already checked (the known), what remains (the complement)? Each location eliminated shrinks the search space. The game is the progressive computation of a complement, and the moment of finding is the moment the dual collapses to a point.

We do not need to *teach* geometric algebra to five-year-olds. They are already doing it. We need to *name* it. We need to say: "You just built a bivector. The shape you made has a structure, and that structure has a name." The naming does not kill the play. It elevates it. It tells the child that their play is not separate from mathematics—that mathematics is what they have been doing all along.

---

## V. Symplectic Physical Education

A soccer field is a phase space. Each player has a position (where they are) and a momentum (how fast and in what direction they're moving). The pair—position and momentum—is a point in phase space, and the rules of the game define a Hamiltonian: a function whose level sets are the surfaces of constant total energy.

This is not a metaphor. It is a literal description. The conservation of energy in a soccer game is not approximate. Players get tired—yes—but in the short term, every sprint is a transfer of chemical energy to kinetic energy, every collision conserves momentum (adjusted for friction and deformation), and the total "game energy" (players plus ball plus field) is approximately conserved.

The symplectic structure of phase space has a profound property: it preserves volume. You cannot compress a region of phase space without expanding another. On the field, this means: you cannot speed up without slowing something else down. You cannot change direction without transferring momentum. Every dodge, every pass, every shot on goal is a symplectic transformation—a transformation that preserves the deep structure of the phase space.

Children know this intuitively. The eight-year-old who learns to "read the game" is learning to see the symplectic structure. They anticipate where the ball will go not by tracking its trajectory alone, but by sensing the flow of the phase space—the configuration of players, their momenta, the constraints of the field. A good pass is one that exploits the symplectic structure, sending the ball along a trajectory that the phase-space flow makes favorable.

Physical education that names this becomes something extraordinary. "Conservation of energy" is not a physics lecture—it is a description of what happens in every game they play. "You can't speed up without slowing something else down" is not a law imposed from outside—it is the shape of their own bodies in motion. A child who understands symplectic structure through soccer has learned more physics than a child who memorizes formulas from a textbook, because the soccer player has *embodied* the mathematics. The knowledge is in their legs, not just their head.

Imagine coaching that says: "You're off-balance because your position and momentum are fighting each other. Shift your weight—there, now your phase-space point is on a better trajectory." Absurd? Perhaps. But no more absurd than coaching that says "keep your eye on the ball" without ever explaining *why*—which is that the ball's trajectory in phase space is predictable when you attend to it, and unpredictable when you don't. The coaching we already do is informal physics. We might as well make it formal.

---

## VI. Persistent Homology of Friendship

A friend group has a topology.

Start with vertices: the individual members. Add edges: the pairwise friendships. Add triangles: the three-way bonds, the trios where every pair is close. In the language of topological data analysis, a friend group is a simplicial complex— vertices, edges, triangles, and higher-order simplices, each one a relationship of increasing dimensionality.

This is not merely decorative. The topology of a friend group has functional consequences. A group that is a complete graph—everyone close to everyone else—has high connectivity and resilience. Remove one vertex, and the remaining structure is still strong. A group that is a cycle—A friends with B, B with C, C with D, D with A, but A and C barely know each other—is fragile. Remove B, and the cycle breaks. The topology predicts the group's response to disruption.

**Persistent homology** tracks how topological features—connected components, loops, voids—appear and disappear as you vary a parameter. In the social context, the parameter is closeness. At low closeness thresholds, everyone is friends with everyone—giant simplicial complex, no holes. As the threshold rises, some relationships drop out. Loops form: A-B-C-D-A, where the diagonals are missing. Voids form: a group of five where the interior is empty, everyone friends with everyone on the surface but no one seeing into the center.

When a friend leaves, the topology changes. A loop may break—a trio becomes a pair, and the triangle that held them collapses to an edge. A void may open—the space where that person sat at lunch becomes a hole in the social geometry. Persistent homology gives us a vocabulary for what children already feel but cannot articulate: *something is missing that used to be there, and the shape of the group is different now.*

Teaching children to recognize the topology of their social world is not abstracting away their feelings. It is the opposite. It is giving them a language for the *structure* of loneliness and belonging. "I feel left out" becomes legible: "There's a void in the complex, and I'm on its boundary—I can see the group but I'm not inside it." "We all used to be close" becomes: "The simplicial complex has lost dimensionality. The triangles have become edges."

This is not clinical. It is empowering. A child who understands that social structures have shapes—that belonging is topological, that loneliness is the experience of being on the wrong side of a boundary—has tools for navigating the social world that go beyond "be nice" and "include everyone." They can see *why* inclusion matters: because a complex without holes is stronger, more resilient, more capable of withstanding the departure of any single member. Inclusion is not just kindness. It is structural integrity.

And when a friendship ends—as friendships do—the topological vocabulary offers something that raw emotion cannot: a way to understand what happened without blaming anyone. The complex changed. That is neither good nor bad. It is simply what complexes do, as they evolve through time. The child who can say "the topology shifted" is not suppressing grief. They are holding it in a frame large enough to contain it.

---

## VII. The Categorical Student

There is a category whose objects are *things you know*. And there is a category whose objects are *things you can do*. A student is a **functor** between them.

This is not a glib analogy. It is a precise description of what learning is. A functor maps objects to objects (knowing a concept maps to being able to apply it) and morphisms to morphisms (understanding the relationship between two concepts maps to being able to transfer that relationship into action). A functor that preserves structure—one where the image of a composition is the composition of the images—is a student who has not just memorized facts but understood their *connections*.

This reframing dissolves the most persistent false dichotomy in education: knowledge versus skills. In the categorical view, they are the same thing viewed from different categories. Knowledge is the domain. Skills are the codomain. The functor is the student. A "good" student is not one with many objects in their domain (many facts known) or many objects in their codomain (many skills performed). A good student is one whose functor is *rich*—one with many morphisms, many connections, many paths from knowing to doing.

**Transfer learning**—the holy grail of education, the ability to apply knowledge in novel contexts—is, in this framework, functor extension. The student's functor has been defined on a subcategory: the domain of things they've explicitly studied. Transfer occurs when the functor extends naturally to a new category, mapping unfamiliar objects to appropriate actions because the *structure* of the mapping, not the specific objects, is what the student has internalized.

This has immediate implications for assessment. A test that measures only objects—"Do you know this fact? Can you perform this skill?"—is a test of the functor's behavior on isolated points. It reveals nothing about the morphisms. A student who has memorized a hundred facts but understands none of their connections will ace a pointwise test and fail in every novel situation. A categorical assessment would test morphisms: "You know A and you know B. What is the relationship between them? You can do X and you can do Y. How would you combine them?"

This is what good teachers already do, informally. They probe for understanding, not just recall. They ask "why?" and "how are these related?" and "can you apply this to a different problem?" The categorical framework simply names what they are doing: testing the richness of the functor, not just the size of its image.

And it offers a vision of what education *is*. Education is not filling a student with facts. It is enriching a functor—adding morphisms, strengthening the mapping between knowing and doing, extending the domain so that the functor applies to ever-wider categories of experience. A well-educated person is not one who knows many things. It is one whose functor is so rich, so densely connected, so structurally sound, that *any* new domain can be mapped to *appropriate* action.

This is what we have always meant by "understanding." We just didn't have the mathematics for it.

---

## The Shape of the Argument

I am not proposing that we teach sheaf cohomology to first graders. I am proposing something more radical: that we recognize they are *already computing it*.

Every child who has ever felt left out is computing the topology of their social world. Every child who has ever built a tower of blocks is composing multivectors. Every child who has ever asked "who is tallest?" is working in the tropical semiring. Every child who has ever sprinted down a soccer field is a symplectic integrator running at twenty frames per second. Every child who has ever struggled to glue their section of a group report to someone else's is wrestling with H¹.

The mathematics is already there. It is in their bodies, their play, their conflicts, their questions. What we call "education" is the process of refusing to name it—of taking the richest mathematical minds on Earth and teaching them to think of mathematics as something that happens on worksheets, with pencils, in silence.

Children are not blank slates. They are walking, talking, playing, fighting, crying, building, running mathematical structures. Our job is not to pour mathematics into them. It is to help them see what they already are.

The persistent classroom is the one that names the shape of thought. And in naming it, gives children back the mathematics that was always theirs.

---

*What would it look like? A kindergarten where "who is tallest?" is celebrated as the first algebraic operation. A middle school where group projects come with a vocabulary for obstruction and repair. A high school where grading captures the landscape of understanding, not just its average elevation. A gym class where conservation laws are not taught from a textbook but felt in the legs. A playground where the topology of friendship is as legible as the rules of tag.*

*It would look like children who grow up knowing that mathematics is not a subject. It is the shape of everything they have already been doing.*

*It would look like trust.*
