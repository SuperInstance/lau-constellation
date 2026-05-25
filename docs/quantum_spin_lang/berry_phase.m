% berry_phase.m — Berry Phase = Pythagorean Comma (Octave/MATLAB)
%
% Physics Analogy:
%   The circle of fifths traces a path in log-frequency space. After 12 steps
%   of multiplying by 3/2 and normalizing to [440,880), the path should close
%   but the holonomy (Berry phase) equals the Pythagorean comma:
%   3^12 / 2^19 = 531441/524288 ≈ 23.46 cents.
%
% Usage: octave --no-gui berry_phase.m

fprintf('=== Berry Phase = Pythagorean Comma ===\n\n');

f_start = 440;
f_end = 880;
f = f_start;
ratio = 3/2;

freqs = zeros(12, 1);
intervals = zeros(12, 1);
cents_vals = zeros(12, 1);

for i = 1:12
    f = f * ratio;
    while f >= f_end
        f = f / 2;
    end
    freqs(i) = f;
    intervals(i) = f / f_start;
    cents_vals(i) = 1200 * log2(f / f_start);
    fprintf('Step %2d: f=%.4f Hz, interval=%.10f, cents=%.4f\n', ...
            i, f, intervals(i), cents_vals(i));
end

% Final analysis
final_ratio = f / f_start;
comma_cents = 1200 * log2(final_ratio);
exact_comma = 531441 / 524288;
exact_cents = 1200 * log2(exact_comma);

fprintf('\n=== Analysis ===\n');
fprintf('Final ratio: %.15f\n', final_ratio);
fprintf('Pythagorean comma (exact): 531441/524288 = %.15f\n', exact_comma);
fprintf('Computed comma: %.6f cents\n', comma_cents);
fprintf('Exact comma:    %.6f cents\n', exact_cents);
fprintf('Error:          %.10f cents\n', abs(comma_cents - exact_cents));

% Plot: Circle of fifths in log-frequency space
figure('Position', [100 100 800 600]);
subplot(2,1,1);
plot(0:12, [0; cents_vals], 'bo-', 'LineWidth', 2, 'MarkerSize', 8);
hold on;
plot([0 12], [0 1200], 'r--', 'LineWidth', 1.5);
xlabel('Step (circle of fifths)');
ylabel('Cents above A4');
title('Berry Phase: Circle of Fifths Holonomy');
legend('Actual path', 'Expected (flat)', 'Location', 'northwest');
grid on;

subplot(2,1,2);
bar(1:12, cents_vals);
hold on;
yline(comma_cents, 'r--', sprintf('Pythagorean comma: %.2f cents', comma_cents), ...
     'LineWidth', 2, 'LabelHorizontalAlignment', 'left');
xlabel('Step');
ylabel('Cents');
title('Cumulative Phase Accumulation');
grid on;

saveas(gcf, 'berry_phase_octave.png');
fprintf('\nPlot saved to berry_phase_octave.png\n');
