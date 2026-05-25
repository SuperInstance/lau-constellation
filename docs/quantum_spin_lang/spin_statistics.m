% spin_statistics.m — Spin Statistics Consonance (Octave/MATLAB)
%
% Physics Analogy:
%   Fermions obey Pauli exclusion. We model harmonic partial proximity as
%   a Fermi-Dirac distribution: w = 1/(exp((|f_i-f_j|-delta)/sigma)+1).
%   Close partials → high weight (rough, dissonant).
%   Far partials → low weight (smooth, consonant).
%
% Usage: octave --no-gui spin_statistics.m

fprintf('=== Spin Statistics Consonance ===\n\n');

N_HARM = 8;
DELTA = 100;  % Critical bandwidth (Hz)
SIGMA = 50;   % Smearing width (Hz)
F0 = 440;     % Reference frequency

names = {'Unison','m2','M2','m3','M3','P4','TT','P5','m6','M6','m7','M7','Octave'};
ratios = [1/1, 16/15, 9/8, 6/5, 5/4, 4/3, 45/32, 3/2, 8/5, 5/3, 9/5, 15/8, 2/1];

roughness = zeros(size(ratios));
tenney = zeros(size(ratios));
cents_arr = zeros(size(ratios));

for k = 1:length(ratios)
    r = ratios(k);
    f1 = F0;
    f2 = F0 * r;
    
    % Compute roughness: sum Fermi-Dirac weights over all partial pairs
    rr = 0;
    n_pairs = 0;
    for i = 1:N_HARM
        for j = 1:N_HARM
            fi = f1 * i;
            fj = f2 * j;
            df = abs(fi - fj);
            w = 1 / (exp((df - DELTA) / SIGMA) + 1);
            rr = rr + w;
            n_pairs = n_pairs + 1;
        end
    end
    roughness(k) = rr / n_pairs;
    tenney(k) = log2(max(r, 1/r));
    cents_arr(k) = 1200 * log2(r);
    
    fprintf('%-8s ratio=%.6f  cents=%7.2f  roughness=%.6f  tenney=%.4f\n', ...
            names{k}, r, cents_arr(k), roughness(k), tenney(k));
end

% Plot roughness vs interval (chromatic position)
figure('Position', [100 100 900 700]);
subplot(2,1,1);
bar(cents_arr, roughness, 1);
set(gca, 'XTick', cents_arr, 'XTickLabel', names);
ylabel('Roughness (Fermi-Dirac)');
title('Spin Statistics Consonance: Fermi-Dirac Roughness Model');
grid on;

subplot(2,1,2);
plot(tenney, roughness, 'ro-', 'LineWidth', 2, 'MarkerSize', 10);
xlabel('Tenney Height (log_2 of ratio)');
ylabel('Roughness');
title('Roughness vs Tenney Height');
grid on;
% Annotate points
for k = 1:length(ratios)
    text(tenney(k)+0.02, roughness(k), names{k}, 'FontSize', 8);
end

saveas(gcf, 'spin_statistics_octave.png');
fprintf('\nPlot saved to spin_statistics_octave.png\n');
