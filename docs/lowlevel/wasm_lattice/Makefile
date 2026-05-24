# Makefile for WASM Lattice Oscillator
#
# Prerequisites:
#   - emscripten (emcc in PATH): https://emscripten.org/docs/getting_started/
#   - A web browser (for serving, use: python3 -m http.server 8000)
#
# Targets:
#   make           — Build lattice.wasm
#   make all       — Build WASM + run benchmark
#   make serve     — Start local HTTP server for testing
#   make native    — Build native shared library for benchmarking
#   clean          — Remove build artifacts

EMCC = emcc
CC = gcc

# Emscripten flags
EMFLAGS = -O3 \
          -s WASM=1 \
          -s STANDALONE_WASM \
          -s EXPORTED_FUNCTIONS="['_lattice_init','_lattice_process','_lattice_set_dial','_lattice_note_on','_lattice_note_off','_lattice_get_dial','_lattice_get_consonance']" \
          -s EXPORTED_RUNTIME_METHODS="['ccall','cwrap']" \
          --no-entry \
          -Wall

# Native flags
NATIVE_FLAGS = -O3 -shared -fPIC -Wall -lm

# Source
SRC = lattice.c
WASM_OUT = lattice.wasm
NATIVE_OUT = lattice_native.so

# Default target
.PHONY: all wasm native clean serve

all: wasm native

wasm: $(WASM_OUT)

$(WASM_OUT): $(SRC)
	$(EMCC) $(EMFLAGS) -o $@ $<
	@echo "Built: $(WASM_OUT) ($(shell stat -f%z $(WASM_OUT) 2>/dev/null || stat -c%s $(WASM_OUT)) bytes)"

native: $(NATIVE_OUT)

$(NATIVE_OUT): $(SRC)
	$(CC) $(NATIVE_FLAGS) -o $@ $<
	@echo "Built: $(NATIVE_OUT)"

serve: wasm
	@echo "Serving at http://localhost:8000/"
	@echo "Open http://localhost:8000/index.html in your browser"
	python3 -m http.server 8000

clean:
	rm -f $(WASM_OUT) $(NATIVE_OUT) lattice.js lattice_module.js \
	      *.wasm *.so *.o output.raw output.wav
