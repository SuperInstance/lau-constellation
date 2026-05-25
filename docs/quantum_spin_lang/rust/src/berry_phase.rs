//! Experiment 1: Berry Phase = Pythagorean Comma
//! Start f=440, multiply by 3/2 twelve times, normalize to octave.
//! Discrepancy = 23.46 cents (Pythagorean comma).

use std::f64::consts::LOG2_E;

const LN2: f64 = std::f64::consts::LN_2;

fn cents(ratio: f64) -> f64 {
    1200.0 * ratio.log2()
}

fn main() {
    let base_freq = 440.0;
    let fifth = 3.0_f64 / 2.0;
    let n_steps = 12;

    // Compute 12 perfect fifths
    let mut frequencies: Vec<f64> = Vec::with_capacity(n_steps);
    let mut f = base_freq;
    for i in 0..n_steps {
        f *= fifth;
        frequencies.push(f);
    }

    // Normalize all to base octave [base_freq, 2*base_freq)
    let normalized: Vec<f64> = frequencies
        .iter()
        .map(|&freq| {
            let ratio = freq / base_freq;
            let octaves = ratio.log2().floor() as i32;
            freq / (2.0_f64.powi(octaves))
        })
        .collect();

    // The 12th fifth should land near 2*base_freq (7 octaves up)
    // (3/2)^12 = 531441/4096 ≈ 129.746
    // 2^7 = 128
    // Ratio: 531441/4096 / 128 = 531441/524288
    let pythagorean_comma_ratio = (3.0_f64 / 2.0).powi(12) / 2.0_f64.powi(7);
    let pythagorean_comma_cents = cents(pythagorean_comma_ratio);

    // Sort normalized frequencies to see the circle of fifths scale
    let mut sorted = normalized.clone();
    sorted.sort_by(|a, b| a.partial_cmp(b).unwrap());

    // Build JSON output
    let freqs_json: Vec<String> = frequencies
        .iter()
        .enumerate()
        .map(|(i, f)| format!("{{\"step\": {}, \"freq\": {:.6}, \"normalized\": {:.6}}}", i + 1, f, normalized[i]))
        .map(|s| s)
        .collect();

    let sorted_json: Vec<String> = sorted
        .iter()
        .map(|f| format!("{:.6}", f))
        .collect();

    let json = format!(
        "{{\n  \"experiment\": \"Berry Phase = Pythagorean Comma\",\n  \"base_freq\": {:.1},\n  \"fifth_ratio\": 1.5,\n  \"steps\": {},\n  \"frequencies\": [\n    {}\n  ],\n  \"sorted_normalized\": [{}],\n  \"pythagorean_comma_ratio\": {:.10},\n  \"pythagorean_comma_cents\": {:.4},\n  \"expected_cents\": 23.46,\n  \"match\": {}\n}}",
        base_freq,
        n_steps,
        freqs_json.join(",\n    "),
        sorted_json.join(", "),
        pythagorean_comma_ratio,
        pythagorean_comma_cents,
        (pythagorean_comma_cents - 23.46).abs() < 0.1
    );

    println!("{}", json);
}
