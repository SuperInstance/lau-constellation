% Berry Phase = Pythagorean Comma
% Multiply 440 by 3/2 twelve times, normalize to [440,880].

function berry_phase_oct()
  A4 = 440;
  f = A4;
  freqs = zeros(1, 12);
  note_names = {'C4','C#4','D4','D#4','E4','F4','F#4','G4','G#4','A4','A#4','B4'};

  for i = 1:12
    f = f * 3/2;
    while f >= 880
      f = f / 2;
    end
    freqs(i) = f;
  end

  final_freq = freqs(12);
  comma_ratio = 3^12 / 2^19;
  cents = 1200 * log2(final_freq / A4);

  fprintf('=== Berry Phase = Pythagorean Comma ===\n');
  fprintf('Starting frequency: %.2f Hz\n', A4);
  fprintf('Circle of fifths frequencies:\n');
  for i = 1:12
    fprintf('  Step %2d: %.4f Hz\n', i, freqs(i));
  end
  fprintf('\nFinal frequency: %.4f Hz\n', final_freq);
  fprintf('Pythagorean comma ratio: %.10f\n', comma_ratio);
  fprintf('Exact ratio: 531441/524288\n');
  fprintf('Comma: %.4f cents\n', cents);
  fprintf('Expected: 23.46 cents\n\n');

  % Plot
  figure('Position', [100 100 900 500]);
  equal_temperament = A4 * 2.^([0:11]/12);
  semitones = 0:11;

  subplot(1,2,1);
  plot(semitones, freqs, 'bo-', 'LineWidth', 2, 'MarkerSize', 8);
  hold on;
  plot(semitones, equal_temperament, 'r--', 'LineWidth', 1.5);
  xlabel('Fifth step');
  ylabel('Frequency (Hz)');
  title('Circle of Fifths vs Equal Temperament');
  legend('Pythagorean (3/2)', 'Equal Temperament', 'Location', 'northwest');
  grid on;

  subplot(1,2,2);
  deviation_cents = 1200 * log2(freqs ./ equal_temperament);
  bar(semitones, deviation_cents, 'FaceColor', [0.2 0.6 0.8]);
  xlabel('Fifth step');
  ylabel('Deviation (cents)');
  title('Pythagorean vs Equal Temperament Deviation');
  grid on;

  saveas(gcf, 'berry_phase.png');
  fprintf('Plot saved: berry_phase.png\n');

  % JSON output
  fid = fopen('berry_phase.json', 'w');
  fprintf(fid, '{\n');
  fprintf(fid, '  "experiment": "Berry Phase = Pythagorean Comma",\n');
  fprintf(fid, '  "starting_frequency": %.2f,\n', A4);
  fprintf(fid, '  "frequencies": [');
  for i = 1:12
    fprintf(fid, '%.6f', freqs(i));
    if i < 12, fprintf(fid, ', '); end
  end
  fprintf(fid, '],\n');
  fprintf(fid, '  "final_frequency": %.6f,\n', final_freq);
  fprintf(fid, '  "comma_cents": %.4f\n', cents);
  fprintf(fid, '}\n');
  fclose(fid);
end

berry_phase_oct();
