# deadband-rs

Rust implementations of deadband caching, BMA drift detection, and Eisenstein lattice utilities.

## Modules

| Module | Purpose |
|--------|---------|
| `bma` | Bayesian Moving Average drift detection |
| `div360` | 360-degree division utilities |
| `eisenstein` | Eisenstein integer arithmetic (A₂ lattice) |
| `fib_spline` | Fibonacci-based spline interpolation |
| `hpdf` | Heavy-tailed probability density functions |
| `shell` | Shell protocol interface |

## Used By

- **[eisenstein-embed](https://github.com/SuperInstance/eisenstein-embed)** — Deadband caching layer in the 5-layer matching cascade
- **[plato-training](https://github.com/SuperInstance/plato-training)** — Micro model training and deployment

## License

MIT
