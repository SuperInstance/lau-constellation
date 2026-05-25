# Makefile for Quantum Spin-Music Experiments (CUDA)
#
# Build all:
#   make
#
# Build individual:
#   make berry_phase
#   make spin_statistics
#   make entanglement
#
# Clean:
#   make clean
#
# CPU-only (no GPU):
#   make CPU=1

NVCC     := nvcc
CXX      := g++
NVCCFLAGS := -O2 -arch=sm_60
CXXFLAGS  := -O2 -lm

ifdef CPU
# CPU-only build
TARGETS = berry_phase_cpu spin_statistics_cpu entanglement_cpu
else
TARGETS = berry_phase spin_statistics entanglement
endif

.PHONY: all clean run

all: $(TARGETS)

# ── GPU builds ──────────────────────────────────────────────────────────────

berry_phase: berry_phase.cu
	$(NVCC) $(NVCCFLAGS) -o $@ $< -lm

spin_statistics: spin_statistics.cu
	$(NVCC) $(NVCCFLAGS) -o $@ $< -lm

entanglement: entanglement.cu
	$(NVCC) $(NVCCFLAGS) -o $@ $< -lm

# ── CPU fallback builds ────────────────────────────────────────────────────

berry_phase_cpu: berry_phase.cu
	$(CXX) -DCPU_ONLY $(CXXFLAGS) -x c++ -o $@ $<

spin_statistics_cpu: spin_statistics.cu
	$(CXX) -DCPU_ONLY $(CXXFLAGS) -x c++ -o $@ $<

entanglement_cpu: entanglement.cu
	$(CXX) -DCPU_ONLY $(CXXFLAGS) -x c++ -o $@ $<

# ── Run all ─────────────────────────────────────────────────────────────────

run: all
	@echo ""
	@echo "════════════════════════════════════════════════════════════"
	@echo "  Experiment 1: Berry Phase = Pythagorean Comma"
	@echo "════════════════════════════════════════════════════════════"
	@./berry_phase || ./berry_phase_cpu
	@echo ""
	@echo "════════════════════════════════════════════════════════════"
	@echo "  Experiment 2: Spin Statistics Consonance"
	@echo "════════════════════════════════════════════════════════════"
	@./spin_statistics || ./spin_statistics_cpu
	@echo ""
	@echo "════════════════════════════════════════════════════════════"
	@echo "  Experiment 3: Entanglement = Consonance"
	@echo "════════════════════════════════════════════════════════════"
	@./entanglement || ./entanglement_cpu

clean:
	rm -f berry_phase spin_statistics entanglement
	rm -f berry_phase_cpu spin_statistics_cpu entanglement_cpu
