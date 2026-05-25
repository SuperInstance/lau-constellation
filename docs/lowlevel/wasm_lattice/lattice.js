/**
 * lattice.js — WASM Lattice Oscillator: AudioWorklet + Tradition Presets + Recording
 *
 * Enhanced with:
 *   - Smooth parameter transitions (no clicks)
 *   - Tradition preset system (10 world music traditions)
 *   - WAV recording (30s capture)
 *   - AnalyserNode integration for spectrum + waveform
 *   - Real-time consonance & pleasantness scores
 *   - Buffer queue for seamless playback
 */

// ============================================================================
// Tradition Preset Data (mirrors lattice.c TRADITIONS[])
// ============================================================================
const TRADITIONS = [
    { name: "Pythagorean",     color: "#00ff88", pos: [0.2, 0.3],  vertical: 0.4, horizontal: 0.2, spectral: 0.5 },
    { name: "Just Intonation", color: "#44ff44", pos: [0.25, 0.25], vertical: 0.3, horizontal: 0.15, spectral: 0.4 },
    { name: "Meantone",        color: "#88ff00", pos: [0.35, 0.2],  vertical: 0.5, horizontal: 0.25, spectral: 0.45 },
    { name: "Arabic Maqam",    color: "#ffaa00", pos: [0.65, 0.5],  vertical: 0.6, horizontal: 0.4, spectral: 0.55 },
    { name: "Indian Raga",     color: "#ff6600", pos: [0.7, 0.6],   vertical: 0.7, horizontal: 0.5, spectral: 0.6 },
    { name: "Gamelan",         color: "#ff0044", pos: [0.85, 0.7],  vertical: 0.8, horizontal: 0.6, spectral: 0.7 },
    { name: "Japanese",        color: "#ff44aa", pos: [0.8, 0.35],  vertical: 0.35, horizontal: 0.1, spectral: 0.35 },
    { name: "Blues",           color: "#4488ff", pos: [0.5, 0.7],   vertical: 0.5, horizontal: 0.35, spectral: 0.6 },
    { name: "Spectral",        color: "#8844ff", pos: [0.15, 0.75], vertical: 0.9, horizontal: 0.8, spectral: 0.3 },
    { name: "Techno",          color: "#00ccff", pos: [0.5, 0.15],  vertical: 0.95, horizontal: 0.0, spectral: 0.2 },
];

// ============================================================================
// AudioWorklet Processor
// ============================================================================
const PROCESSOR_CODE = `
class LatticeProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this.bufferSize = 256;
        this.outputBuffer = new Float32Array(this.bufferSize);
        this.ready = false;
        this.instance = null;

        // Smooth parameter interpolation
        this.targetDials = [0.5, 0.3, 0.5];
        this.currentDials = [0.5, 0.3, 0.5];
        this.smoothing = 0.005; // interpolation speed

        // Pending messages queue
        this.pendingMessages = [];

        this.port.onmessage = (e) => {
            const d = e.data;
            if (d.type === 'init') {
                this._init(d);
            } else if (!this.ready) {
                this.pendingMessages.push(d);
            } else {
                this._handleMessage(d);
            }
        };
    }

    async _init(data) {
        try {
            const module = await WebAssembly.compile(data.wasmBytes);
            this.instance = await WebAssembly.instantiate(module, {
                env: {
                    memory: new WebAssembly.Memory({ initial: 256 }),
                    expf: Math.exp,
                    sinf: Math.sin,
                    cosf: Math.cos,
                    log2f: Math.log2,
                    fabsf: Math.abs,
                    sqrtf: Math.sqrt,
                    malloc: (size) => this._malloc(size),
                    free: (ptr) => this._free(ptr),
                }
            });
            this.ready = true;

            this.instance.exports.lattice_init(
                data.voices || 4,
                data.partials || 16
            );

            this.port.postMessage({ type: 'ready' });

            // Process pending messages
            for (const msg of this.pendingMessages) {
                this._handleMessage(msg);
            }
            this.pendingMessages = [];
        } catch (err) {
            this.port.postMessage({ type: 'error', message: err.message });
        }
    }

    _malloc(size) {
        if (!this._heap) {
            this._heapOffset = 65536; // Start after initial pages
            const mem = this.instance.exports.memory;
            mem.grow(100); // Allocate extra pages
            this._heap = mem;
        }
        const ptr = this._heapOffset;
        this._heapOffset += size + 15 & ~15; // 16-byte aligned
        return ptr;
    }

    _free(ptr) { /* No-op for our simple allocator */ }

    _handleMessage(d) {
        if (d.type === 'dial') {
            this.targetDials[d.dial] = d.value;
        }
        if (d.type === 'noteOn') {
            this.instance.exports.lattice_note_on(d.frequency);
        }
        if (d.type === 'noteOff') {
            this.instance.exports.lattice_note_off(d.frequency);
        }
        if (d.type === 'tradition') {
            this.instance.exports.lattice_set_tradition(d.id);
        }
        if (d.type === 'reverb') {
            this.instance.exports.lattice_set_reverb(d.mix);
        }
        if (d.type === 'masterVol') {
            this.instance.exports.lattice_set_master_vol(d.vol);
        }
        if (d.type === 'startRecording') {
            const maxSamples = d.seconds * 44100;
            this.instance.exports.lattice_alloc_wav_buffer(maxSamples);
            this.instance.exports.lattice_start_recording(d.seconds);
        }
        if (d.type === 'stopRecording') {
            this.instance.exports.lattice_stop_recording();
            const numSamples = this.instance.exports.lattice_get_recording_samples();
            this.port.postMessage({ type: 'recordingDone', samples: numSamples });
        }
    }

    process(inputs, outputs) {
        if (!this.ready) return true;

        const output = outputs[0];

        // Smooth dial interpolation (prevent clicks)
        for (let i = 0; i < 3; i++) {
            this.currentDials[i] += (this.targetDials[i] - this.currentDials[i]) * this.smoothing;
            this.instance.exports.lattice_set_dial(i, this.currentDials[i]);
        }

        // Allocate temp buffer in WASM memory
        const mem = this.instance.exports.memory.buffer;
        const ptr = this._malloc(this.bufferSize * 4);

        this.instance.exports.lattice_process(ptr, this.bufferSize);

        const wasmBuf = new Float32Array(mem, ptr, this.bufferSize);
        for (let ch = 0; ch < output.length; ch++) {
            output[ch].set(wasmBuf);
        }

        // Send metering data (throttled)
        if (typeof this._meterCounter === 'undefined') this._meterCounter = 0;
        this._meterCounter++;
        if (this._meterCounter % 64 === 0) {
            const consonance = this.instance.exports.lattice_get_consonance();
            const pleasantness = this.instance.exports.lattice_get_pleasantness();
            const peak = this.instance.exports.lattice_get_peak();
            const tradition = this.instance.exports.lattice_get_tradition();
            const samples = this.instance.exports.lattice_get_recording_samples();
            this.port.postMessage({
                type: 'meter',
                consonance, pleasantness, peak, tradition, recordingSamples: samples,
                dials: [...this.currentDials]
            });
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
    constructor(voices = 4, partials = 16, sampleRate = 44100) {
        this.voices = voices;
        this.partials = partials;
        this.sampleRate = sampleRate;
        this.audioCtx = null;
        this.workletNode = null;
        this.analyser = null;
        this.gainNode = null;
        this.ready = false;
        this.onReady = null;
        this.onMeter = null;

        this.dials = { vertical: 0.5, horizontal: 0.3, spectral: 0.5 };
        this.meterData = { consonance: 0, pleasantness: 0, peak: 0, tradition: -1, dials: [0.5, 0.3, 0.5] };
        this.recording = false;
    }

    async init() {
        this.audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: this.sampleRate });

        const wasmResponse = await fetch('lattice.wasm');
        const wasmBytes = await wasmResponse.arrayBuffer();

        const blob = new Blob([PROCESSOR_CODE], { type: 'application/javascript' });
        const workletUrl = URL.createObjectURL(blob);
        await this.audioCtx.audioWorklet.addModule(workletUrl);

        this.workletNode = new AudioWorkletNode(this.audioCtx, 'lattice-processor', {
            outputChannelCount: [2]
        });

        // Create gain node for volume control
        this.gainNode = this.audioCtx.createGain();
        this.gainNode.gain.value = 1.0;

        // Create analyser for waveform + spectrum display
        this.analyser = this.audioCtx.createAnalyser();
        this.analyser.fftSize = 2048;
        this.analyser.smoothingTimeConstant = 0.85;

        // Chain: worklet → gain → analyser → destination
        this.workletNode.connect(this.gainNode);
        this.gainNode.connect(this.analyser);
        this.analyser.connect(this.audioCtx.destination);

        // Handle metering messages
        this.workletNode.port.onmessage = (e) => {
            if (e.data.type === 'ready') {
                this.ready = true;
                if (this.onReady) this.onReady();
            }
            if (e.data.type === 'meter') {
                this.meterData = e.data;
                if (this.onMeter) this.onMeter(e.data);
            }
            if (e.data.type === 'recordingDone') {
                this.recording = false;
                if (this.onRecordingDone) this.onRecordingDone(e.data.samples);
            }
            if (e.data.type === 'error') {
                console.error('AudioWorklet error:', e.data.message);
            }
        };

        return new Promise((resolve, reject) => {
            const origOnReady = this.onReady;
            this.onReady = () => {
                if (origOnReady) origOnReady();
                resolve();
            };
            this.workletNode.port.postMessage({
                type: 'init', wasmBytes,
                voices: this.voices, partials: this.partials
            });
        });
    }

    setDial(name, value) {
        value = Math.max(0, Math.min(1, value));
        this.dials[name] = value;
        const dialMap = { vertical: 0, horizontal: 1, spectral: 2 };
        if (this.workletNode && dialMap[name] !== undefined) {
            this.workletNode.port.postMessage({ type: 'dial', dial: dialMap[name], value });
        }
    }

    noteOn(frequency) {
        if (this.workletNode) {
            this.workletNode.port.postMessage({ type: 'noteOn', frequency });
        }
    }

    noteOff(frequency) {
        if (this.workletNode) {
            this.workletNode.port.postMessage({ type: 'noteOff', frequency });
        }
    }

    setTradition(id) {
        if (this.workletNode) {
            this.workletNode.port.postMessage({ type: 'tradition', id });
        }
    }

    setReverb(mix) {
        if (this.workletNode) {
            this.workletNode.port.postMessage({ type: 'reverb', mix });
        }
    }

    setVolume(vol) {
        if (this.gainNode) {
            this.gainNode.gain.setTargetAtTime(vol, this.audioCtx.currentTime, 0.01);
        }
    }

    startRecording(seconds = 30) {
        if (!this.workletNode || this.recording) return;
        this.recording = true;
        this.workletNode.port.postMessage({ type: 'startRecording', seconds });
    }

    stopRecording() {
        if (!this.workletNode || !this.recording) return;
        this.workletNode.port.postMessage({ type: 'stopRecording' });
    }

    getWaveformData() {
        if (!this.analyser) return null;
        const data = new Uint8Array(this.analyser.frequencyBinCount);
        this.analyser.getByteTimeDomainData(data);
        return data;
    }

    getSpectrumData() {
        if (!this.analyser) return null;
        const data = new Uint8Array(this.analyser.frequencyBinCount);
        this.analyser.getByteFrequencyData(data);
        return data;
    }

    async resume() {
        if (this.audioCtx && this.audioCtx.state === 'suspended') {
            await this.audioCtx.resume();
        }
    }
}

// ============================================================================
// Export
// ============================================================================
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { LatticeOscillator, TRADITIONS };
}
if (typeof window !== 'undefined') {
    window.LatticeOscillator = LatticeOscillator;
    window.TRADITIONS = TRADITIONS;
}
