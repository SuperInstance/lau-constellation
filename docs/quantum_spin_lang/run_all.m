% run_all.m — Run all quantum spin-music experiments (Octave/MATLAB)
%
% Executes all three experiments and generates plots.
% Usage: octave --no-gui run_all.m

fprintf('============================================\n');
fprintf('  Quantum Spin-Music Experiments (Octave)\n');
fprintf('============================================\n\n');

fprintf('--- Experiment 1: Berry Phase ---\n');
run('berry_phase.m');
fprintf('\n');

fprintf('--- Experiment 2: Spin Statistics ---\n');
run('spin_statistics.m');
fprintf('\n');

fprintf('--- Experiment 3: Entanglement ---\n');
run('entanglement.m');
fprintf('\n');

fprintf('============================================\n');
fprintf('  All experiments complete.\n');
fprintf('============================================\n');
