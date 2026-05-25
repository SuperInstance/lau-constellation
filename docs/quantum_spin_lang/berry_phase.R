# Experiment 1: Berry Phase = Pythagorean Comma
# Start f=440, multiply by 3/2 twelve times, normalize to octave.
# Discrepancy = 23.46 cents (Pythagorean comma).

cents <- function(ratio) 1200 * log2(ratio)

main <- function() {
  base_freq <- 440
  fifth <- 3/2
  n_steps <- 12
  
  # Compute 12 perfect fifths
  frequencies <- numeric(n_steps)
  f <- base_freq
  for (i in 1:n_steps) {
    f <- f * fifth
    frequencies[i] <- f
  }
  
  # Normalize to base octave
  normalized <- sapply(frequencies, function(freq) {
    ratio <- freq / base_freq
    octaves <- floor(log2(ratio))
    freq / (2^octaves)
  })
  
  # Pythagorean comma
  pythagorean_comma_ratio <- (3/2)^12 / 2^7
  pythagorean_comma_cents <- cents(pythagorean_comma_ratio)
  
  # Build results
  steps <- lapply(1:n_steps, function(i) {
    list(step = i, freq = frequencies[i], normalized = normalized[i])
  })
  
  sorted <- sort(normalized)
  
  result <- list(
    experiment = "Berry Phase = Pythagorean Comma",
    base_freq = base_freq,
    fifth_ratio = 1.5,
    steps = n_steps,
    frequencies = steps,
    sorted_normalized = round(sorted, 6),
    pythagorean_comma_ratio = round(pythagorean_comma_ratio, 10),
    pythagorean_comma_cents = round(pythagorean_comma_cents, 4),
    expected_cents = 23.46,
    match = abs(pythagorean_comma_cents - 23.46) < 0.1
  )
  
  cat(toJSON(result))
}

# Minimal JSON serializer (base R)
toJSON <- function(x, indent = 0) {
  pad <- paste(rep("  ", indent), collapse = "")
  pad1 <- paste(rep("  ", indent + 1), collapse = "")
  
  if (is.list(x)) {
    if (!is.null(names(x))) {
      # Named list -> object
      entries <- sapply(names(x), function(nm) {
        val <- toJSON(x[[nm]], indent + 1)
        paste0(pad1, '"', nm, '": ', val)
      })
      paste0("{\n", paste(entries, collapse = ",\n"), "\n", pad, "}")
    } else {
      # Unnamed list -> array of objects
      entries <- sapply(x, function(item) {
        paste0(pad1, toJSON(item, indent + 1))
      })
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

# Plot
make_plot <- function() {
  base_freq <- 440
  fifth <- 3/2
  
  frequencies <- numeric(12)
  f <- base_freq
  for (i in 1:12) { f <- f * fifth; frequencies[i] <- f }
  
  normalized <- sapply(frequencies, function(freq) {
    ratio <- freq / base_freq
    octaves <- floor(log2(ratio))
    freq / (2^octaves)
  })
  
  sorted <- sort(normalized)
  
  png("/home/phoenix/.openclaw/workspace/docs/quantum_spin_lang/berry_phase_plot.png",
      width = 800, height = 600, res = 120)
  
  # Circle of fifths as helix
  angles <- seq(0, 2*pi - pi/6, length.out = 12)
  expected <- base_freq * (2^(0:11/12))
  
  plot(normalized, angles, pch = 19, col = "blue",
       xlab = "Frequency (Hz)", ylab = "Phase angle (rad)",
       main = "Berry Phase: Circle of Fifths\nDiscrepancy = Pythagorean Comma (23.46 cents)")
  points(expected, angles, pch = 17, col = "red")
  legend("topleft", legend = c("Perfect fifths", "Equal temperament"),
         pch = c(19, 17), col = c("blue", "red"))
  
  dev.off()
}

make_plot()
main()
