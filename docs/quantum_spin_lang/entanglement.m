% entanglement.m — Entanglement = Consonance (Octave/MATLAB)
%
% Physics Analogy:
%   Two coupled quantum oscillators (musical modes). Coupling g mixes
%   |01> and |10> states. In the 2-level subspace, exact Rabi oscillation:
%     Omega_R = sqrt(delta^2 + 4g^2), delta = w2 - w1
%   Von Neumann entropy of reduced state quantifies entanglement.
%   Correlated with Tenney height of interval ratio.
%
% Usage: octave --no-gui entanglement.m

fprintf('=== Entanglement = Consonance ===\n\n');

names = {'Unison','m2','M2','m3','M3','P4','TT','P5','m6','M6','m7','M7','Octave'};
ratios = [1/1, 16/15, 9/8, 6/5, 5/4, 4/3, 45/32, 3/2, 8/5, 5/3, 9/5, 15/8, 2/1];

w1 = 1.0;
g = 0.5;
t = 1.0;

entropies = zeros(size(ratios));
tenney = zeros(size(ratios));
cents_arr = zeros(size(ratios));
eigenvalues_all = zeros(length(ratios), 2);

for k = 1:length(ratios)
    w2 = ratios(k);
    
    % Detuning and Rabi frequency
    delta_val = w2 - w1;
    Omega_R = sqrt(delta_val^2 + 4*g^2);
    
    % Exact 2-level solution in {|01>, |10>} subspace
    % |psi(t)> = [cos(Ot/2) + i*(delta/Omega)*sin(Ot/2)] |10>
    %           + [-i*(2g/Omega)*sin(Ot/2)] |01>
    c10_re = cos(Omega_R * t / 2);
    c10_im = (delta_val / Omega_R) * sin(Omega_R * t / 2);
    c01_re = 0;
    c01_im = -(2*g / Omega_R) * sin(Omega_R * t / 2);
    
    % Probabilities
    p10 = c10_re^2 + c10_im^2;
    p01 = c01_re^2 + c01_im^2;
    
    % Von Neumann entropy
    S = 0;
    if p01 > 1e-12, S = S - p01 * log2(p01); end
    if p10 > 1e-12, S = S - p10 * log2(p10); end
    
    entropies(k) = S;
    tenney(k) = log2(max(w2, 1/w2));
    cents_arr(k) = 1200 * log2(w2);
    eigenvalues_all(k, :) = [p01, p10];
    
    fprintf('%-8s ratio=%.6f  cents=%7.2f  S=%.6f  eigen=[%.6f, %.6f]\n', ...
            names{k}, w2, cents_arr(k), S, p01, p10);
end

% Compute correlation
corr_coeff = corr(tenney', entropies');
fprintf('\nCorrelation(Tenney height, Entropy) = %.6f\n', corr_coeff);

% Plots
figure('Position', [100 100 900 800]);

subplot(3,1,1);
bar(cents_arr, entropies, 1);
set(gca, 'XTick', cents_arr, 'XTickLabel', names);
ylabel('Entanglement Entropy S');
title('Entanglement Entropy by Interval');
grid on;

subplot(3,1,2);
plot(tenney, entropies, 'rs-', 'LineWidth', 2, 'MarkerSize', 10);
xlabel('Tenney Height');
ylabel('Entanglement Entropy S');
title(sprintf('Entropy vs Tenney Height (r=%.4f)', corr_coeff));
grid on;
for k = 1:length(ratios)
    text(tenney(k)+0.02, entropies(k), names{k}, 'FontSize', 8);
end

subplot(3,1,3);
% Scan coupling strength for a few intervals
g_range = linspace(0.01, 3.0, 100);
test_idx = [1, 5, 8, 13]; % Unison, M3, P5, Octave
hold on;
for idx = test_idx
    w2 = ratios(idx);
    delta_val = w2 - w1;
    S_g = zeros(size(g_range));
    for gi = 1:length(g_range)
        gg = g_range(gi);
        Omega_R = sqrt(delta_val^2 + 4*gg^2);
        c10_im_val = (delta_val / Omega_R) * sin(Omega_R * t / 2);
        c01_im_val = -(2*gg / Omega_R) * sin(Omega_R * t / 2);
        p10_val = cos(Omega_R * t / 2)^2 + c10_im_val^2;
        p01_val = c01_im_val^2;
        S_val = 0;
        if p01_val > 1e-12, S_val = S_val - p01_val * log2(p01_val); end
        if p10_val > 1e-12, S_val = S_val - p10_val * log2(p10_val); end
        S_g(gi) = S_val;
    end
    plot(g_range, S_g, 'LineWidth', 2, 'DisplayName', names{idx});
end
hold off;
xlabel('Coupling strength g');
ylabel('Entanglement Entropy S');
title('Entropy vs Coupling for Selected Intervals');
legend('show');
grid on;

saveas(gcf, 'entanglement_octave.png');
fprintf('\nPlot saved to entanglement_octave.png\n');
