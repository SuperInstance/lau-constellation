// Berry Phase = Pythagorean Comma
// Multiply 440 by 3/2 twelve times, normalize to [440,880].
// The discrepancy is the Pythagorean comma: 3^12/2^19 = 531441/524288 ≈ 23.46 cents.

use Math;

proc main() {
  const A4: real = 440.0;
  var f: real = A4;
  var frequencies: [0..11] real;

  for i in 0..11 {
    f = f * 3.0 / 2.0;
    // Normalize to [440, 880)
    while f >= 880.0 do f = f / 2.0;
    frequencies[i] = f;
  }

  const finalFreq = frequencies[11];
  const commaRatio = (3.0**12) / (2.0**19);
  const cents = 1200.0 * log2(finalFreq / A4);

  writeln("{");
  writeln("  \"experiment\": \"Berry Phase = Pythagorean Comma\",");
  writeln("  \"starting_frequency\": ", A4, ",");
  writeln("  \"circle_frequencies\": [");
  for i in 0..11 {
    write("    ", frequencies[i]);
    if i < 11 then writeln(","); else writeln();
  }
  writeln("  ],");
  writeln("  \"final_frequency\": ", finalFreq, ",");
  writeln("  \"pythagorean_comma_ratio\": ", commaRatio, ",");
  writeln("  \"comma_numerator\": 531441,");
  writeln("  \"comma_denominator\": 524288,");
  writeln("  \"comma_cents\": ", cents, ",");
  writeln("  \"expected_cents\": 23.46,");
  writeln("  \"note\": \"After 12 perfect fifths (3/2), we don't return to the octave. The gap is the Pythagorean comma.\"");
  writeln("}");
}

proc log2(x: real): real {
  return log(x) / log(2.0);
}
