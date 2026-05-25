# Experiment 2: Spin Statistics Consonance
# Fermi-Dirac roughness for interval ratios.
# mu=100Hz, kT=50Hz, N=8 harmonics.

fermi_dirac <- function(e, mu, kt) {
  x <- (e - mu) / kt
  if (x > 500) return(0)
  if (x < -500) return(1)
  1 / (1 + exp(x))
}

roughness <- function(f1, f2) {
  fmin <- min(f1, f2)
  fmax <- max(f1, f2)
  if (fmin <= 0) return(0)
  d <- (fmax - fmin) / fmin
  d_max <- 0.25
  if (d <= 0) return(0)
  x <- d / d_max
  abs(x * exp(-x^2))
}

main <- function() {
  mu <- 100
  kt <- 50
  n_harmonics <- 8
  
  intervals <- list(
    list(name = "unison", ratio = 1),
    list(name = "minor_second", ratio = 16/15),
    list(name = "major_second", ratio = 9/8),
    list(name = "minor_third", ratio = 6/5),
    list(name = "major_third", ratio = 5/4),
    list(name = "perfect_fourth", ratio = 4/3),
    list(name = "tritone", ratio = 45/32),
    list(name = "perfect_fifth", ratio = 3/2),
    list(name = "minor_sixth", ratio = 8/5),
    list(name = "major_sixth", ratio = 5/3),
    list(name = "minor_seventh", ratio = 9/5),
    list(name = "major_seventh", ratio = 15/8),
    list(name = "octave", ratio = 2)
  )
  
  results <- lapply(intervals, function(iv) {
    f0 <- mu
    total_r <- 0
    total_w <- 0
    for (n1 in 1:n_harmonics) {
      freq1 <- f0 * n1
      fd1 <- fermi_dirac(freq1, mu, kt)
      for (n2 in 1:n_harmonics) {
        freq2 <- f0 * iv$ratio * n2
        fd2 <- fermi_dirac(freq2, mu, kt)
        r <- roughness(freq1, freq2)
        w <- fd1 * fd2
        total_r <- total_r + r * w
        total_w <- total_w + w
      }
    }
    norm_r <- if (total_w > 0) total_r / total_w else 0
    list(
      interval = iv$name,
      ratio = round(iv$ratio, 6),
      roughness = round(norm_r, 6),
      raw_roughness = round(total_r, 6),
      fd_weight = round(total_w, 6)
    )
  })
  
  output <- list(
    experiment = "Spin Statistics Consonance",
    mu = mu,
    kT = kt,
    n_harmonics = n_harmonics,
    results = results
  )
  
  cat(toJSON(output))
}

make_plot <- function() {
  mu <- 100; kt <- 50; n_harmonics <- 8
  
  intervals <- list(
    list(name = "unison", ratio = 1),
    list(name = "min2", ratio = 16/15),
    list(name = "Maj2", ratio = 9/8),
    list(name = "min3", ratio = 6/5),
    list(name = "Maj3", ratio = 5/4),
    list(name = "P4", ratio = 4/3),
    list(name = "Trit", ratio = 45/32),
    list(name = "P5", ratio = 3/2),
    list(name = "min6", ratio = 8/5),
    list(name = "Maj6", ratio = 5/3),
    list(name = "min7", ratio = 9/5),
    list(name = "Maj7", ratio = 15/8),
    list(name = "Oct", ratio = 2)
  )
  
  roughness_vals <- sapply(intervals, function(iv) {
    total_r <- 0; total_w <- 0
    for (n1 in 1:n_harmonics) {
      fd1 <- fermi_dirac(mu * n1, mu, kt)
      for (n2 in 1:n_harmonics) {
        fd2 <- fermi_dirac(mu * iv$ratio * n2, mu, kt)
        r <- roughness(mu * n1, mu * iv$ratio * n2)
        w <- fd1 * fd2
        total_r <- total_r + r * w; total_w <- total_w + w
      }
    }
    if (total_w > 0) total_r / total_w else 0
  })
  
  png("/home/phoenix/.openclaw/workspace/docs/quantum_spin_lang/spin_statistics_plot.png",
      width = 800, height = 600, res = 120)
  
  par(mar = c(8, 4, 4, 2))
  names <- sapply(intervals, `[[`, "name")
  barplot(roughness_vals, names.arg = names, col = "steelblue",
          las = 2, main = "Fermi-Dirac Weighted Roughness by Interval",
          ylab = "Normalized Roughness")
  
  dev.off()
}

# JSON serializer (base R)
toJSON <- function(x, indent = 0) {
  pad <- paste(rep("  ", indent), collapse = "")
  pad1 <- paste(rep("  ", indent + 1), collapse = "")
  
  if (is.list(x)) {
    if (!is.null(names(x))) {
      entries <- sapply(names(x), function(nm) {
        val <- toJSON(x[[nm]], indent + 1)
        paste0(pad1, '"', nm, '": ', val)
      })
      paste0("{\n", paste(entries, collapse = ",\n"), "\n", pad, "}")
    } else {
      entries <- sapply(x, function(item) paste0(pad1, toJSON(item, indent + 1)))
      paste0("[\n", paste(entries, collapse = ",\n"), "\n", pad, "]")
    }
  } else if (is.numeric(x)) {
    if (length(x) == 1) {
      if (x == round(x) && abs(x) < 1e15) as.character(x) else sprintf("%.6f", x)
    } else {
      vals <- sapply(x, function(v) if (v == round(v) && abs(v) < 1e15) as.character(v) else sprintf("%.6f", v))
      paste0("[", paste(vals, collapse = ", "), "]")
    }
  } else if (is.logical(x)) {
    tolower(as.character(x))
  } else if (is.character(x)) {
    paste0('"', x, '"')
  } else {
    paste0('"', as.character(x), '"')
  }
}

make_plot()
main()
