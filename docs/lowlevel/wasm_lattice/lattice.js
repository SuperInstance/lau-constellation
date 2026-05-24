/**
 * lattice.js — WASM Lattice Oscillator: AudioWorklet + Loader
 *
 * This file serves dual purpose:
 *   1. As an AudioWorklet processor (lattice-processor.js)
 *   2. As the WASM loader and API bridge
 *
 * Usage in main thread:
 *   const osc = new LatticeOscillator(voices, partials, sampleRate);
 *   osc.noteOn(440);
 *   osc.setDial('vertical', 0.7);
 *
 * Build: emcc lattice.c -O3 -s WASM=1 -s MODULARIZE=1 \
 *        -s EXPORT_NAME='createLatticeModule' \
 *        -s EXPORTED_FUNCTIONS="['_lattice_init','_lattice_process','_lattice_set_dial','_lattice_note_on','_lattice_note_off','_lattice_get_dial','_lattice_get_consonance','_malloc','_free']" \
 *        -o lattice_module.js
 */

// ============================================================================
// AudioWorklet Processor (runs in audio thread)
// ============================================================================

// This string is used to create a Blob URL for the AudioWorklet
const PROCESSOR_CODE = `
class LatticeProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this.bufferSize = 128;
        this.outputBuffer = new Float32Array(this.bufferSize);
        this.ready = false;
        this.module = null;
        this.instance = null;

        this.port.onmessage = async (e) => {
            if (e.data.type === 'init') {
                try {
                    // Load WASM module
                    const module = await WebAssembly.compile(e.data.wasmBytes);
                    this.instance = await WebAssembly.instantiate(module, {
                        env: {
                            memory: new WebAssembly.Memory({ initial: 256 }),
                            expf: Math.exp,
                            sinf: Math.sin,
                            cosf: Math.cos,
                            log2f: Math.log2,
                        }
                    });
                    this.ready = true;

                    // Initialize oscillator
                    this.instance.exports.lattice_init(
                        e.data.voices || 4,
                        e.data.partials || 8
                    );

                    this.port.postMessage({ type: 'ready' });
                } catch (err) {
                    this.port.postMessage({ type: 'error', message: err.message });
                }
            }

            if (e.data.type === 'dial') {
                if (this.ready) {
                    this.instance.exports.lattice_set_dial(e.data.dial, e.data.value);
                }
            }

            if (e.data.type === 'noteOn') {
                if (this.ready) {
                    this.instance.exports.lattice_note_on(e.data.frequency);
                }
            }

            if (e.data.type === 'noteOff') {
                if (this.ready) {
                    this.instance.exports.lattice_note_off(e.data.frequency);
                }
            }
        };
    }

    process(inputs, outputs, parameters) {
        if (!this.ready) return true;

        const output = outputs[0];
        const numChannels = output.length;

        // Allocate WASM memory for one buffer
        const ptr = this.instance.exports._malloc
            ? this.instance.exports._malloc(this.bufferSize * 4)
            : 0;

        if (ptr) {
            // Process audio in WASM
            this.instance.exports.lattice_process(ptr, this.bufferSize);

            // Copy from WASM memory to output
            const wasmBuffer = new Float32Array(
                this.instance.exports.memory.buffer, ptr, this.bufferSize
            );

            for (let ch = 0; ch < numChannels; ch++) {
                output[ch].set(wasmBuffer);
            }

            this.instance.exports._free(ptr);
        }

        return true;
    }
}

registerProcessor('lattice-processor', LatticeProcessor);
`;

// ============================================================================
// Main Thread API
// ============================================================================

class LatticeOscillator {
    constructor(voices = 4, partials = 8, sampleRate = 44100) {
        this.voices = voices;
        this.partials = partials;
        this.sampleRate = sampleRate;
        this.audioCtx = null;
        this.workletNode = null;
        this.ready = false;
        this.onReady = null;

        // Dial state
        this.dials = {
            vertical: 0.5,
            horizontal: 0.3,
            spectral: 0.5
        };
    }

    async init() {
        // Create audio context
        this.audioCtx = new (window.AudioContext || window.webkitAudioContext)({
            sampleRate: this.sampleRate
        });

        // Load WASM binary
        const wasmResponse = await fetch('lattice.wasm');
        const wasmBytes = await wasmResponse.arrayBuffer();

        // Create AudioWorklet from blob
        const blob = new Blob([PROCESSOR_CODE], { type: 'application/javascript' });
        const workletUrl = URL.createObjectURL(blob);

        await this.audioCtx.audioWorklet.addModule(workletUrl);

        // Create worklet node
        this.workletNode = new AudioWorkletNode(this.audioCtx, 'lattice-processor', {
            outputChannelCount: [2]
        });

        // Connect to output
        this.workletNode.connect(this.audioCtx.destination);

        // Wait for ready
        return new Promise((resolve, reject) => {
            this.workletNode.port.onmessage = (e) => {
                if (e.data.type === 'ready') {
                    this.ready = true;
                    if (this.onReady) this.onReady();
                    resolve();
                }
                if (e.data.type === 'error') {
                    reject(new Error(e.data.message));
                }
            };

            // Send init message with WASM bytes
            this.workletNode.port.postMessage({
                type: 'init',
                wasmBytes: wasmBytes,
                voices: this.voices,
                partials: this.partials
            });
        });
    }

    setDial(name, value) {
        value = Math.max(0, Math.min(1, value));
        this.dials[name] = value;

        const dialMap = { vertical: 0, horizontal: 1, spectral: 2 };
        if (this.workletNode && dialMap[name] !== undefined) {
            this.workletNode.port.postMessage({
                type: 'dial',
                dial: dialMap[name],
                value: value
            });
        }
    }

    noteOn(frequency) {
        if (this.workletNode) {
            this.workletNode.port.postMessage({
                type: 'noteOn',
                frequency: frequency
            });
        }
    }

    noteOff(frequency) {
        if (this.workletNode) {
            this.workletNode.port.postMessage({
                type: 'noteOff',
                frequency: frequency
            });
        }
    }

    // Resume audio context (required after user gesture)
    async resume() {
        if (this.audioCtx && this.audioCtx.state === 'suspended') {
            await this.audioCtx.resume();
        }
    }
}

// ============================================================================
// Export for module usage
// ============================================================================

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { LatticeOscillator };
}

// Global for browser <script> usage
if (typeof window !== 'undefined') {
    window.LatticeOscillator = LatticeOscillator;
}
