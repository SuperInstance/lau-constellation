% Entanglement = Consonance
% Coupled two-mode von Neumann entropy. S = -sum(lambda * log(lambda))

function entanglement_oct()
  A4 = 440;
  g = 0.5; % coupling strength
  ratios = [1, 16/15, 9/8, 6/5, 5/4, 4/3, 45/32, 3/2, 8/5, 5/3, 9/5, 15/8, 2];
  names = {'unison','m2','M2','m3','M3','P4','TT','P5','m6','M6','m7','M7','P8'};
  semitones = 0:12;
  n = length(ratios);

  entropy_raw = zeros(1, n);
  entropy_norm = zeros(1, n);
  consonance = zeros(1, n);

  for i = 1:n
    omega_b = A4 * ratios(i);
    delta = abs(omega_b - A4);
    d_norm = delta / A4;

    theta = 2 * atan2(g, d_norm + 1e-6);
    lambda1 = (1 + cos(theta)) / 2;
    lambda2 = (1 - cos(theta)) / 2;

    S = 0;
    if lambda1 > 1e-10, S = S - lambda1 * log(lambda1); end
    if lambda2 > 1e-10, S = S - lambda2 * log(lambda2); end

    entropy_raw(i) = S;
    entropy_norm(i) = S / log(2);
    consonance(i) = 1 - entropy_norm(i);
  end

  fprintf('=== Entanglement = Consonance ===\n');
  fprintf('%-10s %3s %10s %10s %10s\n', 'Name', 'ST', 'Entropy', 'Norm_S', 'Consonance');
  for i = 1:n
    fprintf('%-10s %3d %10.6f %10.6f %10.6f\n', names{i}, semitones(i), entropy_raw(i), entropy_norm(i), consonance(i));
  end
  fprintf('\n');

  % Plot
  figure('Position', [100 100 900 500]);
  subplot(1,2,1);
  bar(semitones, entropy_norm, 'FaceColor', [0.5 0.2 0.7]);
  set(gca, 'XTick', semitones, 'XTickLabel', names);
  xlabel('Interval');
  ylabel('Normalized Entropy');
  title('Von Neumann Entropy by Interval');
  grid on;

  subplot(1,2,2);
  bar(semitones, consonance, 'FaceColor', [0.1 0.6 0.8]);
  set(gca, 'XTick', semitones, 'XTickLabel', names);
  xlabel('Interval');
  ylabel('Consonance (1 - S/log2)');
  title('Consonance from Entanglement Entropy');
  grid on;

  saveas(gcf, 'entanglement.png');
  fprintf('Plot saved: entanglement.png\n');

  % JSON
  fid = fopen('entanglement.json', 'w');
  fprintf(fid, '{\n  "experiment": "Entanglement = Consonance",\n  "intervals": [\n');
  for i = 1:n
    fprintf(fid, '    {"name": "%s", "semitones": %d, "entropy": %.6f, "entropy_norm": %.6f, "consonance": %.6f}', names{i}, semitones(i), entropy_raw(i), entropy_norm(i), consonance(i));
    if i < n, fprintf(fid, ','); end
    fprintf(fid, '\n');
  end
  fprintf(fid, '  ]\n}\n');
  fclose(fid);
end

entanglement_oct();
