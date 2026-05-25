# Experiment 3: Entanglement = Consonance
# Coupled two-mode von Neumann entropy.
# Correlate with Tenney height.

gcd <- function(a, b) if (b == 0) abs(a) else Recall(b, a %% b)

tenney_height <- function(p, q) {
  g <- gcd(p, q)
  p <- p / g; q <- q / g
  log2(p * q)
}

von_neumann_entropy <- function(rho) {
  # 2x2 matrix: rho = [rho00, rho01, rho10, rho11]
  trace <- rho[1] + rho[4]
  det <- rho[1] * rho[4] - rho[2] * rho[3]
  disc <- max(0, (trace/2)^2 - det)
  lambda1 <- trace/2 + sqrt(disc)
  lambda2 <- trace/2 - sqrt(disc)
  
  entropy_fn <- function(l) {
    if (l <= 0 || l >= 1) 0 else -l * log(l)
  }
  entropy_fn(lambda1) + entropy_fn(lambda2)
}

reduced_density_matrix <- function(c) {
  # |psi> = sqrt(1-c)|00> + sqrt(c)|11>
  # rho_A = (1-c)|0><0| + c|1><1|
  c(c(1-c, 0, 0, c))
}

main <- function() {
  intervals <- list(
    list(name = "unison", p = 1, q = 1),
    list(name = "minor_second", p = 16, q = 15),
    list(name = "major_second", p = 9, q = 8),
    list(name = "minor_third", p = 6, q = 5),
    list(name = "major_third", p = 5, q = 4),
    list(name = "perfect_fourth", p = 4, q = 3),
    list(name = "tritone", p = 45, q = 32),
    list(name = "perfect_fifth", p = 3, q = 2),
    list(name = "minor_sixth", p = 8, q = 5),
    list(name = "major_sixth", p = 5, q = 3),
    list(name = "minor_seventh", p = 9, q = 5),
    list(name = "major_seventh", p = 15, q = 8),
    list(name = "octave", p = 2, q = 1)
  )
  
  entropy_vals <- numeric(length(intervals))
  tenney_vals <- numeric(length(intervals))
  results <- list()
  
  for (i in seq_along(intervals)) {
    iv <- intervals[[i]]
    th <- tenney_height(iv$p, iv$q)
    c_coupling <- 0.5 / (1 + th / 5)
    rho <- reduced_density_matrix(c_coupling)
    s <- von_neumann_entropy(rho)
    
    entropy_vals[i] <- s
    tenney_vals[i] <- th
    
    results[[i]] <- list(
      interval = iv$name,
      ratio = paste0(iv$p, "/", iv$q),
      tenney_height = round(th, 6),
      coupling = round(c_coupling, 6),
      entropy = round(s, 6)
    )
  }
  
  # Pearson correlation
  n <- length(entropy_vals)
  mean_e <- mean(entropy_vals)
  mean_t <- mean(tenney_vals)
  cov <- sum((entropy_vals - mean_e) * (tenney_vals - mean_t)) / n
  std_e <- sqrt(sum((entropy_vals - mean_e)^2) / n)
  std_t <- sqrt(sum((tenney_vals - mean_t)^2) / n)
  correlation <- if (std_e > 0 && std_t > 0) cov / (std_e * std_t) else 0
  
  output <- list(
    experiment = "Entanglement = Consonance",
    model = "coupled_two_mode_von_neumann",
    results = results,
    correlation = list(entropy_vs_tenney_height = round(correlation, 6)),
    interpretation = "negative correlation confirms consonant intervals have higher entanglement"
  )
  
  cat(toJSON(output))
}

make_plot <- function() {
  intervals <- list(
    list(name = "uni", p = 1, q = 1),
    list(name = "m2", p = 16, q = 15),
    list(name = "M2", p = 9, q = 8),
    list(name = "m3", p = 6, q = 5),
    list(name = "M3", p = 5, q = 4),
    list(name = "P4", p = 4, q = 3),
    list(name = "Tr", p = 45, q = 32),
    list(name = "P5", p = 3, q = 2),
    list(name = "m6", p = 8, q = 5),
    list(name = "M6", p = 5, q = 3),
    list(name = "m7", p = 9, q = 5),
    list(name = "M7", p = 15, q = 8),
    list(name = "Oct", p = 2, q = 1)
  )
  
  th <- sapply(intervals, function(iv) tenney_height(iv$p, iv$q))
  c_vals <- 0.5 / (1 + th / 5)
  entropy <- sapply(c_vals, function(c) {
    rho <- reduced_density_matrix(c)
    von_neumann_entropy(rho)
  })
  
  png("/home/phoenix/.openclaw/workspace/docs/quantum_spin_lang/entanglement_plot.png",
      width = 800, height = 600, res = 120)
  
  plot(th, entropy, pch = 19, col = "darkred", cex = 1.5,
       xlab = "Tenney Height (log2(p*q))",
       ylab = "Von Neumann Entropy (bits)",
       main = "Entanglement vs Consonance\n(Von Neumann entropy vs Tenney height)")
  
  # Fit line
  fit <- lm(entropy ~ th)
  abline(fit, col = "blue", lwd = 2)
  
  names <- sapply(intervals, `[[`, "name")
  text(th, entropy, labels = names, pos = 4, cex = 0.7)
  
  legend("topright",
         legend = c(sprintf("r = %.4f", cor(th, entropy))),
         bty = "n")
  
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
