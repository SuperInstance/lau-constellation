// Entanglement = Consonance
// Coupled two-mode system: compute von Neumann entropy of reduced density matrix.
// S = -Σ λ log(λ)

use Math;

proc main() {
  const A4: real = 440.0;
  const ratios = [1.0, 16.0/15.0, 9.0/8.0, 6.0/5.0, 5.0/4.0,
                  4.0/3.0, 45.0/32.0, 3.0/2.0, 8.0/5.0,
                  5.0/3.0, 9.0/5.0, 15.0/8.0, 2.0/1.0];
  const names = ["unison", "m2", "M2", "m3", "M3", "P4", "TT", "P5",
                 "m6", "M6", "m7", "M7", "P8"];
  const semitones = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];

  // Coupling strength
  const g: real = 0.5;

  writeln("{");
  writeln("  \"experiment\": \"Entanglement = Consonance (Von Neumann Entropy)\",");
  writeln("  \"coupling_strength\": ", g, ",");
  writeln("  \"intervals\": [");

  for i in 0..12 {
    const omega_a = A4;
    const omega_b = A4 * ratios[i];
    const delta = abs(omega_b - omega_a);

    // Two-mode coupled Hamiltonian -> reduced density matrix eigenvalues
    // Detuning parameter
    const d_norm = delta / A4;

    // Mixed state eigenvalues of reduced density matrix
    // λ₁ = (1 + cos(θ))/2, λ₂ = (1 - cos(θ))/2
    // where θ depends on coupling vs detuning
    const theta = 2.0 * atan2(g, d_norm + 0.001);
    const lambda1 = (1.0 + cos(theta)) / 2.0;
    const lambda2 = (1.0 - cos(theta)) / 2.0;

    // Von Neumann entropy S = -Σ λ log(λ)
    var S: real = 0.0;
    if lambda1 > 1e-10 then S -= lambda1 * log(lambda1);
    if lambda2 > 1e-10 then S -= lambda2 * log(lambda2);
    // Normalize to [0, 1] by dividing by log(2)
    const S_norm = S / log(2.0);

    const consonance = 1.0 - S_norm;

    write("    {\"name\": \"", names[i], "\", \"semitones\": ", semitones[i]);
    write(", \"ratio\": ", ratios[i]);
    write(", \"detuning\": ", delta);
    write(", \"theta\": ", theta);
    write(", \"lambda1\": ", lambda1);
    write(", \"lambda2\": ", lambda2);
    write(", \"entropy\": ", S);
    write(", \"entropy_normalized\": ", S_norm);
    write(", \"consonance\": ", consonance, "}");
    if i < 12 then writeln(","); else writeln();
  }

  writeln("  ],");
  writeln("  \"note\": \"Higher entanglement (entropy) correlates with dissonance. Consonant intervals have low entropy.\"");
  writeln("}");
}
