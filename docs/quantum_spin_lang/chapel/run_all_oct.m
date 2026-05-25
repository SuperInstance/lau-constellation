% Run all three experiments
addpath(pwd);

fprintf('========================================\n');
fprintf('  QUANTUM SPIN-MUSIC EXPERIMENTS\n');
fprintf('  Octave/MATLAB Implementation\n');
fprintf('========================================\n\n');

berry_phase_oct;
fprintf('\n');
spin_statistics_oct;
fprintf('\n');
entanglement_oct;

fprintf('\nAll experiments complete.\n');
