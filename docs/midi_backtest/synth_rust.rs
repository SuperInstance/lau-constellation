// Rust Synthesizer
use std::fs;
use std::io::Write;

const SR: usize = 44100;
const PI: f64 = std::f64::consts::PI;

fn apply_envelope(buf: &mut [f64]) {
    let a_s = (0.01 * SR as f64) as usize;
    let d_s = (0.05 * SR as f64) as usize;
    let r_s = (0.1 * SR as f64) as usize;
    let sustain: f64 = 0.7;
    let n = buf.len();

    for i in 0..a_s.min(n) {
        buf[i] *= i as f64 / a_s as f64;
    }
    for i in 0..d_s.min(n.saturating_sub(a_s)) {
        buf[a_s + i] *= 1.0 - (1.0 - sustain) * i as f64 / d_s as f64;
    }
    for i in (a_s + d_s)..n.saturating_sub(r_s).max(1) {
        buf[i] *= sustain;
    }
    for i in 0..r_s.min(n) {
        let idx = n - 1 - i;
        buf[idx] *= i as f64 / r_s as f64;
    }
}

fn synth_single_440() -> Vec<f64> {
    let n = SR * 2;
    let mut mix = vec![0.0f64; n];
    let freq = 440.0;
    let amp = 100.0 / 127.0;

    for j in 0..n {
        let t = j as f64 / SR as f64;
        mix[j] = amp * (2.0 * PI * freq * t).sin();
    }
    apply_envelope(&mut mix);

    // Clip
    for s in mix.iter_mut() {
        if *s > 1.0 { *s = 1.0; }
        if *s < -1.0 { *s = -1.0; }
    }
    mix
}

fn main() {
    let outdir = "output/rust";
    fs::create_dir_all(outdir).unwrap();

    let mix = synth_single_440();
    let bytes: Vec<u8> = mix.iter()
        .flat_map(|f| f.to_le_bytes())
        .collect();
    
    let path = format!("{}/single_440.f64", outdir);
    let mut f = fs::File::create(&path).unwrap();
    f.write_all(&bytes).unwrap();
    
    println!("Rust synthesis complete -> {}", path);
}
