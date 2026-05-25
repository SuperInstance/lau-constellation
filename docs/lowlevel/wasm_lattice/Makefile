# Makefile for WASM Lattice Oscillator
#
# Prerequisites:
#   - emscripten (emcc in PATH): https://emscripten.org/docs/getting_started/
#   - gcc (for native build)
#   - python3 (for serving)
#
# Targets:
#   make            — Build WASM
#   make wasm       — Build lattice.wasm with Emscripten
#   make native     — Build native binary for testing
#   make all        — Build WASM + native
#   make serve      — Build WASM + start HTTP server
#   make demo       — Build + serve + open browser
#   make clean      — Remove all build artifacts

EMCC  := emcc
CC    := gcc

# Source files
SRC       := lattice.c
WASM_OUT  := lattice.wasm
NATIVE_OUT := lattice_native

# ── Emscripten flags ──────────────────────────────────────────────
EXPORTED = '_lattice_init','_lattice_process','_lattice_set_dial','_lattice_note_on','_lattice_note_off','_lattice_get_dial','_lattice_get_consonance','_lattice_get_pleasantness','_lattice_set_tradition','_lattice_get_tradition','_lattice_get_peak','_lattice_set_reverb','_lattice_set_master_vol','_lattice_start_recording','_lattice_stop_recording','_lattice_get_recording_samples','_lattice_build_wav','_lattice_get_wav_data','_lattice_alloc_wav_buffer','_lattice_free_wav_buffer','_lattice_get_num_traditions','_lattice_get_tradition_info','_malloc','_free'

EMFLAGS = -Os -s WASM=1 -s STANDALONE_WASM -s EXPORTED_FUNCTIONS="[$(EXPORTED)]" -s EXPORTED_RUNTIME_METHODS="['ccall','cwrap']" --no-entry -Wall

# ── Native flags ──────────────────────────────────────────────────
NATIVE_FLAGS := -O3 -Wall -Wextra
NATIVE_LIBS  := -lm

# ── Server config ─────────────────────────────────────────────────
PORT := 8000

# ── Targets ───────────────────────────────────────────────────────

.PHONY: all wasm native clean serve demo open help

all: wasm native

## Build WASM with Emscripten
wasm: $(WASM_OUT)

$(WASM_OUT): $(SRC)
	$(EMCC) $(EMFLAGS) -o $@ $<
	@echo "✓ Built: $@ ($(shell stat -c%s $@ 2>/dev/null || echo '?') bytes)"

## Build native binary for testing
native: $(NATIVE_OUT)

$(NATIVE_OUT): $(SRC)
	$(CC) $(NATIVE_FLAGS) -DNATIVE_TEST -o $@ $< $(NATIVE_LIBS)
	@echo "✓ Built: $@ (native)"

## Test the native build
test: native
	@echo "Running native test..."
	@./$(NATIVE_OUT)

## Build WASM and start HTTP server
serve: wasm
	@echo ""
	@echo "  ┌─────────────────────────────────────────┐"
	@echo "  │  Lattice Oscillator                      │"
	@echo "  │  http://localhost:$(PORT)/index.html      │"
	@echo "  └─────────────────────────────────────────┘"
	@echo ""
	@python3 -m http.server $(PORT)

## Build, serve, and open browser
demo: serve
	@python3 -c "import webbrowser; webbrowser.open('http://localhost:$(PORT)/index.html')" &

## Clean all build artifacts
clean:
	rm -f $(WASM_OUT) $(NATIVE_OUT) lattice.js lattice_module.js \
	      *.wasm *.so *.o output.raw output.wav
	@echo "✓ Clean"

## Show help
help:
	@echo ""
	@echo "Lattice Oscillator — Build Targets"
	@echo "───────────────────────────────────"
	@echo "  make          Build WASM"
	@echo "  make wasm     Build lattice.wasm (requires emscripten)"
	@echo "  make native   Build native test binary (requires gcc)"
	@echo "  make test     Run native test"
	@echo "  make serve    Build WASM + start HTTP server on :$(PORT)"
	@echo "  make demo     Build + serve + open browser"
	@echo "  make clean    Remove build artifacts"
	@echo "  make help     Show this message"
	@echo ""
