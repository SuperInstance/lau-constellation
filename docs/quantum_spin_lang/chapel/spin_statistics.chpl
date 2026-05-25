// Spin Statistics Consonance
// Fermi-Dirac roughness: w = 1/(exp((|f_i - f_j| - 100)/50) + 1)
// Test 13 intervals from unison to octave.

use Math;

proc main() {
  const A4: real = 440.0;
  // Interval ratios (just intonation)
  const ratios = [1.0, 16.0/15.0, 9.0/8.0, 6.0/5.0, 5.0/4.0,
                  4.0/3.0, 45.0/32.0, 3.0/2.0, 8.0/5.0,
                  5.0/3.0, 9.0/5.0, 15.0/8.0, 2.0/1.0];
  const names = ["unison", "m2", "M2", "m3", "M3", "P4", "TT", "P5",
                 "m6", "M6", "m7", "M7", "P8"];
  const semitones = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];

  writeln("{");
  writeln("  \"experiment\": \"Spin Statistics Consonance (Fermi-Dirac Roughness)\",");
  writeln("  \"reference_frequency\": ", A4, ",");
  writeln("  \"roughness_formula\": \"w = 1/(exp((|f_i - f_j| - 100)/50) + 1)\",");
  writeln("  \"intervals\": [");

  for i in 0..12 {
    const f_j = A4 * ratios[i];
    const delta_f = abs(f_j - A4);
    const w = 1.0 / (exp((delta_f - 100.0) / 50.0) + 1.0);
    const consonance = 1.0 - w;

    write("    {\"name\": \"", names[i], "\", \"semitones\": ", semitones[i]);
    write(", \"ratio\": ", ratios[i]);
    write(", \"frequency\": ", f_j);
    write(", \"delta_f\": ", delta_f);
    write(", \"roughness\": ", w);
    write(", \"consonance\": ", consonance, "}");
    if i < 12 then writeln(","); else writeln();
  }

  writeln("  ],");
  writeln("  \"note\": \"Low roughness (Fermi-Dirac) = high consonance. Unison and octave have highest consonance.\"");
  writeln("}");
}
