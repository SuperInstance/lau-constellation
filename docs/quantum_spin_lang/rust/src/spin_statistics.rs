//! Experiment 2: Spin Statistics Consonance
//! Fermi-Dirac roughness for interval ratios.
//! μ=100Hz, kT=50Hz, N=8 harmonics.

fn fermi_dirac(e: f64, mu: f64, kt: f64) -> f64 {
    let x = (e - mu) / kt;
    if x > 500.0 {
        0.0
    } else if x < -500.0 {
        1.0
    } else {
        1.0 / (1.0 + x.exp())
    }
}

/// Roughness between two partials at frequencies f1, f2
/// Based on Plomp-Levelt model: roughness peaks at ~25% bandwidth difference
fn roughness(f1: f64, f2: f64) -> f64 {
    let fmin = f1.min(f2);
    let fmax = f1.max(f2);
    if fmin <= 0.0 {
        return 0.0;
    }
    let d = (fmax - fmin) / fmin;
    // Critical bandwidth ~ 0.25 of center frequency
    let d_max = 0.25;
    // Plomp-Levelt roughness curve
    let x = d / d_max;
    if x <= 0.0 {
        return 0.0;
    }
    let r = (x * (-x.powi(2)).exp()).abs();
    r
}

fn main() {
    let mu: f64 = 100.0; // Hz
    let kt: f64 = 50.0; // Hz
    let n_harmonics = 8;

    // Test interval ratios (just intonation)
    let intervals: Vec<(&str, f64)> = vec![
        ("unison", 1.0),
        ("minor_second", 16.0 / 15.0),
        ("major_second", 9.0 / 8.0),
        ("minor_third", 6.0 / 5.0),
        ("major_third", 5.0 / 4.0),
        ("perfect_fourth", 4.0 / 3.0),
        ("tritone", 45.0 / 32.0),
        ("perfect_fifth", 3.0 / 2.0),
        ("minor_sixth", 8.0 / 5.0),
        ("major_sixth", 5.0 / 3.0),
        ("minor_seventh", 9.0 / 5.0),
        ("major_seventh", 15.0 / 8.0),
        ("octave", 2.0),
    ];

    let mut results: Vec<String> = Vec::new();

    for (name, ratio) in &intervals {
        let f0 = mu; // base frequency = mu
        let mut total_roughness = 0.0;
        let mut total_fd_weight = 0.0;
        let mut count = 0;

        // Compute roughness between all pairs of harmonics from both tones
        for n1 in 1..=n_harmonics {
            let freq1 = f0 * n1 as f64;
            let fd1 = fermi_dirac(freq1, mu, kt);

            for n2 in 1..=n_harmonics {
                let freq2 = f0 * ratio * n2 as f64;
                let fd2 = fermi_dirac(freq2, mu, kt);

                let r = roughness(freq1, freq2);
                let weight = fd1 * fd2;
                total_roughness += r * weight;
                total_fd_weight += weight;
                count += 1;
            }
        }

        let normalized_roughness = if total_fd_weight > 0.0 {
            total_roughness / total_fd_weight
        } else {
            0.0
        };

        results.push(format!(
            "    {{\"interval\": \"{}\", \"ratio\": {:.6}, \"roughness\": {:.6}, \"raw_roughness\": {:.6}, \"fd_weight\": {:.6}}}",
            name, ratio, normalized_roughness, total_roughness, total_fd_weight
        ));
    }

    let json = format!(
        "{{\n  \"experiment\": \"Spin Statistics Consonance\",\n  \"mu\": {:.1},\n  \"kT\": {:.1},\n  \"n_harmonics\": {},\n  \"results\": [\n{}\n  ]\n}}",
        mu, kt, n_harmonics,
        results.join(",\n")
    );

    println!("{}", json);
}
