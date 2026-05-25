% Spin Statistics Consonance
% Fermi-Dirac roughness: w = 1/(exp((|f_i - f_j| - 100)/50) + 1)

function spin_statistics_oct()
  A4 = 440;
  ratios = [1, 16/15, 9/8, 6/5, 5/4, 4/3, 45/32, 3/2, 8/5, 5/3, 9/5, 15/8, 2];
  names = {'unison','m2','M2','m3','M3','P4','TT','P5','m6','M6','m7','M7','P8'};
  semitones = 0:12;

  n = length(ratios);
  roughness = zeros(1, n);
  consonance = zeros(1, n);
  freqs = A4 * ratios;

  for i = 1:n
    delta_f = abs(freqs(i) - A4);
    roughness(i) = 1 / (exp((delta_f - 100) / 50) + 1);
    consonance(i) = 1 - roughness(i);
  end

  fprintf('=== Spin Statistics Consonance ===\n');
  fprintf('%-10s %3s %8s %10s %10s %10s\n', 'Name', 'ST', 'Freq', 'Delta_f', 'Roughness', 'Consonance');
  for i = 1:n
    fprintf('%-10s %3d %8.2f %10.2f %10.6f %10.6f\n', names{i}, semitones(i), freqs(i), abs(freqs(i)-A4), roughness(i), consonance(i));
  end
  fprintf('\n');

  % Plot
  figure('Position', [100 100 900 500]);
  subplot(1,2,1);
  bar(semitones, roughness, 'FaceColor', [0.8 0.3 0.3]);
  set(gca, 'XTick', semitones, 'XTickLabel', names);
  xlabel('Interval');
  ylabel('Roughness (Fermi-Dirac)');
  title('Fermi-Dirac Roughness by Interval');
  grid on;

  subplot(1,2,2);
  bar(semitones, consonance, 'FaceColor', [0.2 0.7 0.3]);
  set(gca, 'XTick', semitones, 'XTickLabel', names);
  xlabel('Interval');
  ylabel('Consonance');
  title('Consonance = 1 - Roughness');
  grid on;

  saveas(gcf, 'spin_statistics.png');
  fprintf('Plot saved: spin_statistics.png\n');

  % JSON
  fid = fopen('spin_statistics.json', 'w');
  fprintf(fid, '{\n  "experiment": "Spin Statistics Consonance",\n  "intervals": [\n');
  for i = 1:n
    fprintf(fid, '    {"name": "%s", "semitones": %d, "roughness": %.6f, "consonance": %.6f}', names{i}, semitones(i), roughness(i), consonance(i));
    if i < n, fprintf(fid, ','); end
    fprintf(fid, '\n');
  end
  fprintf(fid, '  ]\n}\n');
  fclose(fid);
end

spin_statistics_oct();
