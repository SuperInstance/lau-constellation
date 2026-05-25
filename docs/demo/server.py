#!/usr/bin/env python3
"""
constraint-synth Live — A dial synthesizer demo.
Launch: python3 server.py
Opens: http://localhost:8080
"""

import http.server
import json
import math
import struct
import threading
import webbrowser
import io
import wave
import numpy as np
from urllib.parse import urlparse, parse_qs

PORT = 8080

# ── Tradition Presets ────────────────────────────────────────────────────────
TRADITIONS = {
    "Carnatic":  {"iv": 2.77, "ih": 3.63, "is": 2.8,  "color": "#FF6B6B"},
    "Gagaku":    {"iv": 2.38, "ih": 1.70, "is": 3.5,  "color": "#4ECDC4"},
    "Jazz":      {"iv": 3.10, "ih": 2.80, "is": 2.2,  "color": "#F7DC6F"},
    "Flamenco":  {"iv": 2.50, "ih": 3.20, "is": 3.0,  "color": "#E74C3C"},
    "Griot":     {"iv": 3.80, "ih": 2.10, "is": 1.8,  "color": "#F39C12"},
    "Raga":      {"iv": 2.90, "ih": 3.80, "is": 3.2,  "color": "#9B59B6"},
    "Maqam":     {"iv": 2.60, "ih": 2.50, "is": 2.6,  "color": "#3498DB"},
    "Gospel":    {"iv": 3.50, "ih": 3.00, "is": 1.5,  "color": "#E91E63"},
    "Highlife":  {"iv": 4.00, "ih": 2.30, "is": 2.0,  "color": "#27AE60"},
    "Pipa":      {"iv": 2.20, "ih": 2.00, "is": 3.8,  "color": "#8E44AD"},
}

UNEXPLORED = {"iv": 2.52, "ih": 1.89, "is": 2.75}

SAMPLE_RATE = 44100
DURATION = 2.0  # seconds


def lattice_oscillator(iv, ih, is_spec, sr=SAMPLE_RATE, dur=DURATION):
    """Generate audio from a lattice oscillator at the given dial position."""
    t = np.linspace(0, dur, int(sr * dur), dtype=np.float64)

    # Base frequencies derived from dial positions
    f1 = 110.0 * (1 + iv * 0.3)     # ~110-275 Hz
    f2 = 165.0 * (1 + ih * 0.25)    # ~165-371 Hz
    f3 = 220.0 * (1 + is_spec * 0.2) # ~220-440 Hz

    # Spectral richness from is_spec
    n_harmonics = max(2, int(is_spec * 2))

    signal = np.zeros_like(t)

    # Primary oscillator — additive harmonics
    for k in range(1, n_harmonics + 1):
        amp = 1.0 / (k ** (1 + ih * 0.15))
        phase_offset = k * iv * 0.3
        signal += amp * np.sin(2 * np.pi * f1 * k * t + phase_offset)

    # Secondary modulated tone
    mod = np.sin(2 * np.pi * f2 * t) * (0.3 + 0.2 * np.sin(2 * np.pi * iv * t))
    signal += mod

    # Spectral shimmer
    shimmer = 0.15 * np.sin(2 * np.pi * f3 * t + np.sin(2 * np.pi * ih * 0.5 * t) * is_spec)
    signal += shimmer

    # Amplitude envelope (attack-decay-sustain-release)
    n = len(t)
    attack = int(0.05 * sr)
    release = int(0.3 * sr)
    sustain_end = n - release

    envelope = np.ones(n)
    # Attack ramp
    envelope[:attack] = np.linspace(0, 1, attack)
    # Release ramp
    if sustain_end > attack:
        envelope[sustain_end:] = np.linspace(1, 0, release)

    signal *= envelope

    # Normalize
    peak = np.max(np.abs(signal))
    if peak > 0:
        signal = signal / peak * 0.85

    return signal.astype(np.float32)


def make_wav(audio):
    """Convert float32 numpy array to WAV bytes."""
    buf = io.BytesIO()
    # Convert float32 to int16
    audio_int16 = (audio * 32767).astype(np.int16)
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_int16.tobytes())
    return buf.getvalue()


# ── HTML Page ────────────────────────────────────────────────────────────────

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>constraint-synth Live</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }

  @font-face {
    font-family: 'System';
    src: local('SF Pro Display'), local('Segoe UI'), local('Helvetica Neue'), local('sans-serif');
  }

  body {
    background: #0a0a0f;
    color: #e0e0e0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    min-height: 100vh;
    overflow-x: hidden;
  }

  .app {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
  }

  h1 {
    text-align: center;
    font-size: 2.2rem;
    font-weight: 300;
    letter-spacing: 0.15em;
    margin-bottom: 0.3rem;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .subtitle {
    text-align: center;
    color: #555;
    font-size: 0.85rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    margin-bottom: 2.5rem;
  }

  .main-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
  }

  @media (max-width: 800px) {
    .main-grid { grid-template-columns: 1fr; }
  }

  .panel {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 1.5rem;
    backdrop-filter: blur(10px);
  }

  .panel-title {
    font-size: 0.75rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #667eea;
    margin-bottom: 1.2rem;
  }

  /* ── Dials ───────────────────────────────────── */
  .dial-group {
    margin-bottom: 1.5rem;
  }

  .dial-label {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 0.5rem;
  }

  .dial-label span:first-child {
    font-size: 0.9rem;
    color: #bbb;
  }

  .dial-label .dial-value {
    font-family: 'SF Mono', 'Fira Code', monospace;
    font-size: 1.1rem;
    color: #fff;
    text-shadow: 0 0 10px rgba(102,126,234,0.5);
  }

  input[type="range"] {
    -webkit-appearance: none;
    width: 100%;
    height: 6px;
    border-radius: 3px;
    background: rgba(255,255,255,0.08);
    outline: none;
    transition: background 0.2s;
  }

  input[type="range"]:hover {
    background: rgba(255,255,255,0.12);
  }

  input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #8b9cf7, #667eea);
    box-shadow: 0 0 12px rgba(102,126,234,0.6), 0 0 24px rgba(102,126,234,0.2);
    cursor: pointer;
    transition: transform 0.15s, box-shadow 0.15s;
  }

  input[type="range"]::-webkit-slider-thumb:hover {
    transform: scale(1.15);
    box-shadow: 0 0 18px rgba(102,126,234,0.8), 0 0 36px rgba(102,126,234,0.3);
  }

  input[type="range"]::-moz-range-thumb {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    border: none;
    background: radial-gradient(circle at 35% 35%, #8b9cf7, #667eea);
    box-shadow: 0 0 12px rgba(102,126,234,0.6);
    cursor: pointer;
  }

  /* ── Buttons ─────────────────────────────────── */
  .btn-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 1rem;
  }

  .preset-btn {
    padding: 0.45rem 0.85rem;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    background: rgba(255,255,255,0.04);
    color: #ccc;
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
    overflow: hidden;
  }

  .preset-btn::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--btn-color, #667eea);
    opacity: 0;
    transition: opacity 0.2s;
  }

  .preset-btn:hover {
    background: rgba(255,255,255,0.08);
    border-color: rgba(255,255,255,0.2);
    color: #fff;
  }

  .preset-btn:hover::before { opacity: 1; }

  .preset-btn.active {
    border-color: var(--btn-color, #667eea);
    color: #fff;
    background: rgba(102,126,234,0.12);
  }

  .preset-btn.active::before { opacity: 1; }

  .action-btn {
    padding: 0.55rem 1.2rem;
    border: 1px solid;
    border-radius: 10px;
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.25s;
  }

  .btn-random {
    border-color: rgba(102,126,234,0.4);
    background: rgba(102,126,234,0.08);
    color: #8b9cf7;
  }

  .btn-random:hover {
    background: rgba(102,126,234,0.18);
    box-shadow: 0 0 20px rgba(102,126,234,0.2);
  }

  .btn-unexplored {
    border-color: rgba(118,75,162,0.4);
    background: rgba(118,75,162,0.08);
    color: #b983ff;
  }

  .btn-unexplored:hover {
    background: rgba(118,75,162,0.18);
    box-shadow: 0 0 20px rgba(118,75,162,0.2);
  }

  /* ── Cluster Map ─────────────────────────────── */
  .cluster-container {
    position: relative;
    width: 100%;
    aspect-ratio: 1;
    max-height: 340px;
  }

  #clusterMap {
    width: 100%;
    height: 100%;
  }

  .tradition-dot {
    transition: r 0.3s, opacity 0.3s;
  }

  .tradition-label {
    font-size: 9px;
    fill: #888;
    pointer-events: none;
    transition: fill 0.3s;
  }

  .tradition-label.highlight {
    fill: #fff;
    font-weight: 600;
  }

  #currentDot {
    transition: cx 0.4s ease, cy 0.4s ease;
  }

  .nearest-tradition {
    text-align: center;
    margin-top: 0.8rem;
    font-size: 0.9rem;
    min-height: 1.4em;
    color: #aaa;
  }

  .nearest-tradition strong {
    color: #fff;
  }

  /* ── Waveform ────────────────────────────────── */
  .waveform-container {
    width: 100%;
    height: 160px;
    position: relative;
    border-radius: 12px;
    overflow: hidden;
    background: rgba(0,0,0,0.3);
  }

  #waveformCanvas {
    width: 100%;
    height: 100%;
  }

  /* ── Status Bar ──────────────────────────────── */
  .status-bar {
    margin-top: 2rem;
    display: flex;
    justify-content: center;
    gap: 2rem;
    font-size: 0.75rem;
    color: #444;
    letter-spacing: 0.1em;
  }

  .status-bar .dot {
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    margin-right: 0.4rem;
    vertical-align: middle;
  }

  .dot-green { background: #27AE60; box-shadow: 0 0 6px #27AE60; }
  .dot-yellow { background: #F39C12; box-shadow: 0 0 6px #F39C12; }

  /* ── Glow pulse for current position ─────────── */
  @keyframes pulse-glow {
    0%, 100% { opacity: 0.6; }
    50% { opacity: 1; }
  }

  .pulse-ring {
    animation: pulse-glow 2s ease-in-out infinite;
  }

  /* ── Loading overlay ─────────────────────────── */
  .loading-overlay {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: #0a0a0f;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    transition: opacity 0.5s;
  }

  .loading-overlay.hidden {
    opacity: 0;
    pointer-events: none;
  }

  .loading-text {
    font-size: 1.2rem;
    color: #667eea;
    letter-spacing: 0.3em;
    animation: pulse-glow 1.5s ease-in-out infinite;
  }
</style>
</head>
<body>

<div class="loading-overlay" id="loadingOverlay">
  <div class="loading-text">INITIALIZING SYNTH</div>
</div>

<div class="app">
  <h1>constraint-synth</h1>
  <div class="subtitle">Lattice Oscillator Parameter Space</div>

  <div class="main-grid">
    <!-- Left: Dials -->
    <div>
      <div class="panel">
        <div class="panel-title">Dials</div>

        <div class="dial-group">
          <div class="dial-label">
            <span>I_vert — Vertical Complexity</span>
            <span class="dial-value" id="iv-val">2.50</span>
          </div>
          <input type="range" id="iv" min="0" max="5" step="0.01" value="2.50">
        </div>

        <div class="dial-group">
          <div class="dial-label">
            <span>I_horiz — Horizontal Texture</span>
            <span class="dial-value" id="ih-val">2.50</span>
          </div>
          <input type="range" id="ih" min="0" max="5" step="0.01" value="2.50">
        </div>

        <div class="dial-group">
          <div class="dial-label">
            <span>I_spectral — Spectral Richness</span>
            <span class="dial-value" id="is-val">2.50</span>
          </div>
          <input type="range" id="is" min="0" max="5" step="0.01" value="2.50">
        </div>

        <div class="btn-row">
          <button class="action-btn btn-random" id="btnRandom">⟳ Random</button>
          <button class="action-btn btn-unexplored" id="btnUnexplored">◎ Unexplored</button>
        </div>
      </div>

      <div class="panel" style="margin-top: 1.5rem;">
        <div class="panel-title">Tradition Presets</div>
        <div class="btn-row" id="presets"></div>
      </div>

      <div class="panel" style="margin-top: 1.5rem;">
        <div class="panel-title">Waveform</div>
        <div class="waveform-container">
          <canvas id="waveformCanvas"></canvas>
        </div>
      </div>
    </div>

    <!-- Right: Cluster Map -->
    <div>
      <div class="panel">
        <div class="panel-title">Tradition Cluster Map</div>
        <div class="cluster-container">
          <svg id="clusterMap" viewBox="0 0 500 500">
            <!-- Grid -->
            <defs>
              <radialGradient id="bgGrad" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="rgba(102,126,234,0.05)" />
                <stop offset="100%" stop-color="transparent" />
              </radialGradient>
              <filter id="glow">
                <feGaussianBlur stdDeviation="3" result="blur"/>
                <feMerge>
                  <feMergeNode in="blur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
            </defs>
            <rect width="500" height="500" fill="url(#bgGrad)" rx="8"/>

            <!-- Grid lines -->
            <g stroke="rgba(255,255,255,0.04)" stroke-width="1">
              <line x1="100" y1="0" x2="100" y2="500"/>
              <line x1="200" y1="0" x2="200" y2="500"/>
              <line x1="300" y1="0" x2="300" y2="500"/>
              <line x1="400" y1="0" x2="400" y2="500"/>
              <line x1="0" y1="100" x2="500" y2="100"/>
              <line x1="0" y1="200" x2="500" y2="200"/>
              <line x1="0" y1="300" x2="500" y2="300"/>
              <line x1="0" y1="400" x2="500" y2="400"/>
            </g>

            <!-- Axis labels -->
            <text x="250" y="490" fill="#444" font-size="10" text-anchor="middle">I_horiz →</text>
            <text x="12" y="250" fill="#444" font-size="10" text-anchor="start" transform="rotate(-90,12,250)">I_vert →</text>

            <!-- Tradition dots and labels will be injected -->
            <g id="traditionDots"></g>

            <!-- Current position -->
            <circle id="currentDot" cx="250" cy="250" r="7" fill="#fff" filter="url(#glow)"/>
            <circle id="currentRing" cx="250" cy="250" r="16" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="1" class="pulse-ring"/>

            <!-- Crosshair lines from current pos -->
            <line id="crossH" x1="0" y1="250" x2="500" y2="250" stroke="rgba(255,255,255,0.08)" stroke-width="1" stroke-dasharray="4,4"/>
            <line id="crossV" x1="250" y1="0" x2="250" y2="500" stroke="rgba(255,255,255,0.08)" stroke-width="1" stroke-dasharray="4,4"/>
          </svg>
        </div>
        <div class="nearest-tradition" id="nearestTradition">
          Move the dials to explore the parameter space
        </div>
      </div>

      <!-- Third axis indicator -->
      <div class="panel" style="margin-top: 1.5rem;">
        <div class="panel-title">I_spectral Depth</div>
        <div style="display:flex;align-items:center;gap:1rem;">
          <div style="flex:1;height:12px;border-radius:6px;background:linear-gradient(90deg,#1a1a2e,#667eea,#764ba2,#e91e63);position:relative;">
            <div id="spectralMarker" style="position:absolute;top:-4px;width:20px;height:20px;border-radius:50%;background:#fff;box-shadow:0 0 10px rgba(102,126,234,0.6);transform:translateX(-50%);transition:left 0.3s ease;left:50%;"></div>
          </div>
          <span class="dial-value" id="spectralDepthVal">2.50</span>
        </div>
      </div>
    </div>
  </div>

  <div class="status-bar">
    <span><span class="dot dot-green"></span>SERVER</span>
    <span id="audioStatus"><span class="dot dot-yellow"></span>WAITING</span>
    <span id="coordsDisplay">( 2.50, 2.50, 2.50 )</span>
  </div>
</div>

<script>
// ── Tradition data ──────────────────────────────────────────────────────────
const TRADITIONS = {
  "Carnatic":  { iv: 2.77, ih: 3.63, is: 2.8, color: "#FF6B6B" },
  "Gagaku":    { iv: 2.38, ih: 1.70, is: 3.5, color: "#4ECDC4" },
  "Jazz":      { iv: 3.10, ih: 2.80, is: 2.2, color: "#F7DC6F" },
  "Flamenco":  { iv: 2.50, ih: 3.20, is: 3.0, color: "#E74C3C" },
  "Griot":     { iv: 3.80, ih: 2.10, is: 1.8, color: "#F39C12" },
  "Gospel":    { iv: 3.50, ih: 3.00, is: 1.5, color: "#E91E63" },
  "Raga":      { iv: 2.90, ih: 3.80, is: 3.2, color: "#9B59B6" },
  "Maqam":     { iv: 2.60, ih: 2.50, is: 2.6, color: "#3498DB" },
  "Highlife":  { iv: 4.00, ih: 2.30, is: 2.0, color: "#27AE60" },
  "Pipa":      { iv: 2.20, ih: 2.00, is: 3.8, color: "#8E44AD" },
};

const UNEXPLORED = { iv: 2.52, ih: 1.89, is: 2.75 };

// ── Audio ───────────────────────────────────────────────────────────────────
let audioCtx = null;
let currentSource = null;
let currentBuffer = null;
let waveformData = null;

function initAudio() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
}

async function playAudio(wavBytes) {
  initAudio();
  if (audioCtx.state === 'suspended') await audioCtx.resume();

  try {
    const audioBuffer = await audioCtx.decodeAudioData(wavBytes.slice(0));
    waveformData = audioBuffer.getChannelData(0);

    // Stop previous
    if (currentSource) {
      try { currentSource.stop(); } catch(e) {}
    }

    currentSource = audioCtx.createBufferSource();
    currentSource.buffer = audioBuffer;
    currentSource.connect(audioCtx.destination);
    currentSource.start(0);
    currentBuffer = audioBuffer;

    document.getElementById('audioStatus').innerHTML =
      '<span class="dot dot-green"></span>PLAYING';
    drawWaveform();

    currentSource.onended = () => {
      document.getElementById('audioStatus').innerHTML =
        '<span class="dot dot-yellow"></span>IDLE';
    };
  } catch(e) {
    console.error('Audio decode error:', e);
  }
}

// ── Waveform Drawing ────────────────────────────────────────────────────────
const wfCanvas = document.getElementById('waveformCanvas');
const wfCtx = wfCanvas.getContext('2d');

function resizeCanvas() {
  const rect = wfCanvas.parentElement.getBoundingClientRect();
  wfCanvas.width = rect.width * window.devicePixelRatio;
  wfCanvas.height = rect.height * window.devicePixelRatio;
  wfCtx.scale(window.devicePixelRatio, window.devicePixelRatio);
  drawWaveform();
}

function drawWaveform() {
  const w = wfCanvas.width / window.devicePixelRatio;
  const h = wfCanvas.height / window.devicePixelRatio;
  wfCtx.clearRect(0, 0, w, h);

  if (!waveformData) return;

  const step = Math.ceil(waveformData.length / w);
  const mid = h / 2;

  // Draw center line
  wfCtx.strokeStyle = 'rgba(102,126,234,0.15)';
  wfCtx.lineWidth = 1;
  wfCtx.beginPath();
  wfCtx.moveTo(0, mid);
  wfCtx.lineTo(w, mid);
  wfCtx.stroke();

  // Draw waveform
  const gradient = wfCtx.createLinearGradient(0, 0, w, 0);
  gradient.addColorStop(0, '#667eea');
  gradient.addColorStop(0.5, '#764ba2');
  gradient.addColorStop(1, '#e91e63');

  wfCtx.strokeStyle = gradient;
  wfCtx.lineWidth = 1.5;
  wfCtx.beginPath();

  for (let x = 0; x < w; x++) {
    const idx = x * step;
    let min = 1, max = -1;
    for (let j = 0; j < step && idx + j < waveformData.length; j++) {
      const val = waveformData[idx + j];
      if (val < min) min = val;
      if (val > max) max = val;
    }
    const yMin = mid + min * mid * 0.9;
    const yMax = mid + max * mid * 0.9;

    if (x === 0) {
      wfCtx.moveTo(x, yMax);
    } else {
      wfCtx.lineTo(x, yMax);
    }
  }
  wfCtx.stroke();

  // Mirror
  wfCtx.globalAlpha = 0.3;
  wfCtx.beginPath();
  for (let x = 0; x < w; x++) {
    const idx = x * step;
    let min = 1;
    for (let j = 0; j < step && idx + j < waveformData.length; j++) {
      const val = waveformData[idx + j];
      if (val < min) min = val;
    }
    const y = mid + min * mid * 0.9;
    if (x === 0) wfCtx.moveTo(x, y);
    else wfCtx.lineTo(x, y);
  }
  wfCtx.stroke();
  wfCtx.globalAlpha = 1;
}

window.addEventListener('resize', resizeCanvas);
setTimeout(resizeCanvas, 100);

// ── Cluster Map ─────────────────────────────────────────────────────────────
function dialToSVG(iv, ih) {
  // Map 0-5 to 40-460
  const x = 40 + (ih / 5) * 420;
  const y = 460 - (iv / 5) * 420;
  return { x, y };
}

function buildClusterDots() {
  const g = document.getElementById('traditionDots');
  g.innerHTML = '';

  // Connection lines between nearby traditions
  const tradEntries = Object.entries(TRADITIONS);
  for (let i = 0; i < tradEntries.length; i++) {
    for (let j = i + 1; j < tradEntries.length; j++) {
      const a = tradEntries[i][1], b = tradEntries[j][1];
      const dist = Math.sqrt((a.iv-b.iv)**2 + (a.ih-b.ih)**2);
      if (dist < 1.5) {
        const p1 = dialToSVG(a.iv, a.ih);
        const p2 = dialToSVG(b.iv, b.ih);
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", p1.x);
        line.setAttribute("y1", p1.y);
        line.setAttribute("x2", p2.x);
        line.setAttribute("y2", p2.y);
        line.setAttribute("stroke", "rgba(255,255,255,0.04)");
        line.setAttribute("stroke-width", "1");
        g.appendChild(line);
      }
    }
  }

  for (const [name, data] of tradEntries) {
    const pos = dialToSVG(data.iv, data.ih);

    // Glow
    const glow = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    glow.setAttribute("cx", pos.x);
    glow.setAttribute("cy", pos.y);
    glow.setAttribute("r", "12");
    glow.setAttribute("fill", data.color);
    glow.setAttribute("opacity", "0.15");
    g.appendChild(glow);

    // Dot
    const dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    dot.setAttribute("cx", pos.x);
    dot.setAttribute("cy", pos.y);
    dot.setAttribute("r", "5");
    dot.setAttribute("fill", data.color);
    dot.setAttribute("class", "tradition-dot");
    dot.setAttribute("id", "dot-" + name);
    dot.setAttribute("opacity", "0.7");
    g.appendChild(dot);

    // Label
    const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
    label.setAttribute("x", pos.x);
    label.setAttribute("y", pos.y - 12);
    label.setAttribute("text-anchor", "middle");
    label.setAttribute("class", "tradition-label");
    label.setAttribute("id", "label-" + name);
    label.textContent = name;
    g.appendChild(label);
  }
}

function updateClusterMap(iv, ih) {
  const pos = dialToSVG(iv, ih);
  document.getElementById('currentDot').setAttribute('cx', pos.x);
  document.getElementById('currentDot').setAttribute('cy', pos.y);
  document.getElementById('currentRing').setAttribute('cx', pos.x);
  document.getElementById('currentRing').setAttribute('cy', pos.y);
  document.getElementById('crossH').setAttribute('y1', pos.y);
  document.getElementById('crossH').setAttribute('y2', pos.y);
  document.getElementById('crossV').setAttribute('x1', pos.x);
  document.getElementById('crossV').setAttribute('x2', pos.x);

  // Find nearest tradition
  let minDist = Infinity;
  let nearest = "";
  for (const [name, data] of Object.entries(TRADITIONS)) {
    const dist = Math.sqrt((data.iv-iv)**2 + (data.ih-ih)**2 + (data.is-currentIS)**2);

    // Highlight proximity
    const dot = document.getElementById("dot-" + name);
    const label = document.getElementById("label-" + name);
    const nearness = Math.max(0, 1 - dist / 2.5);
    dot.setAttribute("r", 5 + nearness * 4);
    dot.setAttribute("opacity", 0.5 + nearness * 0.5);
    if (nearness > 0.4) {
      label.classList.add("highlight");
    } else {
      label.classList.remove("highlight");
    }

    if (dist < minDist) {
      minDist = dist;
      nearest = name;
    }
  }

  const el = document.getElementById('nearestTradition');
  if (minDist < 1.0) {
    el.innerHTML = 'Near <strong style="color:' + TRADITIONS[nearest].color + '">' + nearest + '</strong> (d=' + minDist.toFixed(2) + ')';
  } else {
    el.innerHTML = 'Exploring unclaimed space (nearest: ' + nearest + ', d=' + minDist.toFixed(2) + ')';
  }
}

buildClusterDots();

// ── Preset Buttons ──────────────────────────────────────────────────────────
const presetsDiv = document.getElementById('presets');
let activePreset = null;

for (const [name, data] of Object.entries(TRADITIONS)) {
  const btn = document.createElement('button');
  btn.className = 'preset-btn';
  btn.textContent = name;
  btn.style.setProperty('--btn-color', data.color);
  btn.addEventListener('click', () => {
    setDials(data.iv, data.ih, data.is);
    setActivePreset(name);
    requestAudio();
  });
  presetsDiv.appendChild(btn);
}

function setActivePreset(name) {
  document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
  if (name) {
    const btns = document.querySelectorAll('.preset-btn');
    btns.forEach(b => { if (b.textContent === name) b.classList.add('active'); });
  }
  activePreset = name;
}

// ── Action Buttons ──────────────────────────────────────────────────────────
document.getElementById('btnRandom').addEventListener('click', () => {
  const iv = Math.random() * 5;
  const ih = Math.random() * 5;
  const is = Math.random() * 5;
  setDials(iv, ih, is);
  setActivePreset(null);
  requestAudio();
});

document.getElementById('btnUnexplored').addEventListener('click', () => {
  setDials(UNEXPLORED.iv, UNEXPLORED.ih, UNEXPLORED.is);
  setActivePreset(null);
  requestAudio();
});

// ── Dial Logic ──────────────────────────────────────────────────────────────
const sliderIV = document.getElementById('iv');
const sliderIH = document.getElementById('ih');
const sliderIS = document.getElementById('is');
let currentIS = 2.5;

function setDials(iv, ih, is) {
  sliderIV.value = iv;
  sliderIH.value = ih;
  sliderIS.value = is;
  updateDisplays();
}

function updateDisplays() {
  const iv = parseFloat(sliderIV.value);
  const ih = parseFloat(sliderIH.value);
  const is = parseFloat(sliderIS.value);
  currentIS = is;

  document.getElementById('iv-val').textContent = iv.toFixed(2);
  document.getElementById('ih-val').textContent = ih.toFixed(2);
  document.getElementById('is-val').textContent = is.toFixed(2);
  document.getElementById('spectralDepthVal').textContent = is.toFixed(2);
  document.getElementById('spectralMarker').style.left = (is / 5 * 100) + '%';
  document.getElementById('coordsDisplay').textContent =
    '( ' + iv.toFixed(2) + ', ' + ih.toFixed(2) + ', ' + is.toFixed(2) + ' )';

  updateClusterMap(iv, ih);
}

updateDisplays();

// ── Server Communication ────────────────────────────────────────────────────
let audioRequestTimeout = null;

function requestAudio() {
  clearTimeout(audioRequestTimeout);
  audioRequestTimeout = setTimeout(() => {
    const iv = parseFloat(sliderIV.value);
    const ih = parseFloat(sliderIH.value);
    const is = parseFloat(sliderIS.value);

    fetch('/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ iv, ih, is })
    })
    .then(r => r.arrayBuffer())
    .then(data => playAudio(data))
    .catch(e => console.error('Fetch error:', e));
  }, 80);
}

// Debounced slider events
let sliderTimeout = null;
function onSliderChange() {
  updateDisplays();
  setActivePreset(null);

  clearTimeout(sliderTimeout);
  sliderTimeout = setTimeout(requestAudio, 120);
}

sliderIV.addEventListener('input', onSliderChange);
sliderIH.addEventListener('input', onSliderChange);
sliderIS.addEventListener('input', onSliderChange);

// ── Init ────────────────────────────────────────────────────────────────────
// Remove loading overlay
setTimeout(() => {
  document.getElementById('loadingOverlay').classList.add('hidden');
}, 600);

// Generate initial sound
setTimeout(requestAudio, 800);
</script>
</body>
</html>
"""


# ── HTTP Server ──────────────────────────────────────────────────────────────

class SynthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/generate':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)

            try:
                params = json.loads(body)
                iv = float(params.get('iv', 2.5))
                ih = float(params.get('ih', 2.5))
                is_spec = float(params.get('is', 2.5))
            except (json.JSONDecodeError, ValueError):
                self.send_error(400, 'Invalid parameters')
                return

            # Clamp
            iv = max(0, min(5, iv))
            ih = max(0, min(5, ih))
            is_spec = max(0, min(5, is_spec))

            # Generate audio in a thread to not block
            audio = lattice_oscillator(iv, ih, is_spec)
            wav_bytes = make_wav(audio)

            self.send_response(200)
            self.send_header('Content-Type', 'audio/wav')
            self.send_header('Content-Length', str(len(wav_bytes)))
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(wav_bytes)
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        # Suppress default request logging
        pass


def main():
    server = http.server.HTTPServer(('0.0.0.0', PORT), SynthHandler)
    print(f'constraint-synth Live running at http://localhost:{PORT}')
    print('Press Ctrl+C to stop')

    # Open browser
    webbrowser.open(f'http://localhost:{PORT}')

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down...')
        server.server_close()


if __name__ == '__main__':
    main()
