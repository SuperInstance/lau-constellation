#!/usr/bin/env python3
"""Web demo for constraint-toolkit.

Run: python3 demo.py
Open: http://localhost:8080

Zero external dependencies — uses only Python stdlib.
"""

from __future__ import annotations

import io
import json
import math
import struct
import sys
import tempfile
import wave
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, parse_qs

# Add parent to path so we can import constraint_toolkit without installing
sys.path.insert(0, str(Path(__file__).parent))

from constraint_toolkit.dials import (
    DIAL_RANGES,
    MOST_PLEASING_POINT,
    DialPosition,
    compute_dial_distance,
)
from constraint_toolkit.classifier import DialClassifier
from constraint_toolkit.analyzer import analyze_wav

# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------

INDEX_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Constraint Toolkit — Dials Not Laws</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0d1117;--surface:#161b22;--border:#30363d;
  --text:#e6edf3;--text-dim:#8b949e;
  --accent:#58a6ff;--accent2:#7ee787;--accent3:#d2a8ff;
  --danger:#f85149;--warn:#d29922;
  --radius:8px;
}
html{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;font-size:15px;color:var(--text);background:var(--bg)}
body{display:flex;min-height:100vh}
a{color:var(--accent);text-decoration:none}

/* Sidebar */
.sidebar{width:220px;min-height:100vh;background:var(--surface);border-right:1px solid var(--border);display:flex;flex-direction:column;padding:16px 0;flex-shrink:0}
.sidebar h2{font-size:14px;text-transform:uppercase;letter-spacing:1px;color:var(--text-dim);padding:8px 20px 12px;border-bottom:1px solid var(--border);margin-bottom:8px}
.nav-item{display:flex;align-items:center;gap:10px;padding:10px 20px;color:var(--text-dim);cursor:pointer;transition:all .15s;border-left:3px solid transparent}
.nav-item:hover{background:rgba(88,166,255,.08);color:var(--text)}
.nav-item.active{color:var(--accent);border-left-color:var(--accent);background:rgba(88,166,255,.06)}
.nav-item .icon{font-size:18px;width:24px;text-align:center}

/* Main */
.main{flex:1;display:flex;flex-direction:column;overflow:hidden}
.content{flex:1;overflow-y:auto;padding:24px 32px;max-width:1200px}

/* Sections */
.section{display:none}
.section.active{display:block}
.section h1{font-size:24px;margin-bottom:4px}
.section p.desc{color:var(--text-dim);margin-bottom:20px}

/* Cards */
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:20px;margin-bottom:16px}
.card h3{font-size:16px;margin-bottom:12px;color:var(--accent)}

/* Forms */
.upload-zone{border:2px dashed var(--border);border-radius:var(--radius);padding:40px;text-align:center;cursor:pointer;transition:border-color .2s}
.upload-zone:hover,.upload-zone.dragover{border-color:var(--accent)}
.upload-zone p{color:var(--text-dim);margin-top:8px}
.btn{display:inline-flex;align-items:center;gap:6px;padding:8px 16px;border:none;border-radius:var(--radius);cursor:pointer;font-size:14px;font-weight:500;transition:all .15s}
.btn-primary{background:var(--accent);color:#fff}
.btn-primary:hover{opacity:.85}
.btn-secondary{background:var(--border);color:var(--text)}
.btn-secondary:hover{background:#3d444d}

/* Dial display */
.dial-row{display:flex;gap:16px;margin:16px 0;flex-wrap:wrap}
.dial{width:100px;height:100px;border-radius:50%;border:3px solid var(--border);display:flex;align-items:center;justify-content:center;flex-direction:column;position:relative;background:var(--bg)}
.dial .value{font-size:22px;font-weight:700}
.dial .label{font-size:11px;color:var(--text-dim);margin-top:2px}
.dial.h{border-color:#f97583}.dial.r{border-color:#79c0ff}.dial.s{border-color:#56d364}

/* SVG container */
.viz-container{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px;margin-bottom:16px;overflow:auto}
.viz-container svg{width:100%;max-width:700px;display:block;margin:auto}

/* Tradition grid */
.tradition-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px}
.tradition-card{background:var(--bg);border:1px solid var(--border);border-radius:var(--radius);padding:14px;cursor:pointer;transition:border-color .2s}
.tradition-card:hover{border-color:var(--accent)}
.tradition-card .name{font-weight:600;margin-bottom:6px}
.tradition-card .dials{font-size:12px;color:var(--text-dim);line-height:1.6}
.tradition-card .desc{font-size:12px;color:var(--text-dim);margin-top:6px}

/* Results table */
.results-table{width:100%;border-collapse:collapse}
.results-table th,.results-table td{text-align:left;padding:8px 12px;border-bottom:1px solid var(--border);font-size:13px}
.results-table th{color:var(--text-dim);font-weight:600}

/* Compare */
.compare-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.compare-panel{background:var(--bg);border:1px solid var(--border);border-radius:var(--radius);padding:16px}

/* Toast */
.toast{position:fixed;bottom:20px;right:20px;background:var(--surface);border:1px solid var(--accent);border-radius:var(--radius);padding:12px 20px;color:var(--text);z-index:999;opacity:0;transition:opacity .3s;pointer-events:none}
.toast.show{opacity:1}

/* Slider row */
.slider-row{display:flex;align-items:center;gap:12px;margin:8px 0}
.slider-row label{width:140px;font-size:13px;color:var(--text-dim)}
.slider-row input[type=range]{flex:1}
.slider-row .val{width:40px;text-align:right;font-weight:600}

/* Responsive */
@media(max-width:768px){
  body{flex-direction:column}
  .sidebar{width:100%;min-height:auto;flex-direction:row;overflow-x:auto;padding:0}
  .sidebar h2{display:none}
  .nav-item{padding:12px 16px;border-left:none;border-bottom:3px solid transparent;white-space:nowrap}
  .nav-item.active{border-bottom-color:var(--accent);border-left-color:transparent}
  .content{padding:16px}
  .compare-grid{grid-template-columns:1fr}
}

/* Compose section */
.compose-controls{display:flex;gap:12px;flex-wrap:wrap;align-items:end}
</style>
</head>
<body>

<div class="sidebar">
  <h2>Toolkit</h2>
  <div class="nav-item active" data-section="analyze"><span class="icon">🔬</span> Analyze</div>
  <div class="nav-item" data-section="compose"><span class="icon">🎵</span> Compose</div>
  <div class="nav-item" data-section="explore"><span class="icon">🗺️</span> Explore</div>
  <div class="nav-item" data-section="compare"><span class="icon">⚖️</span> Compare</div>
</div>

<div class="main">
<div class="content">

<!-- ANALYZE -->
<div class="section active" id="sec-analyze">
  <h1>Analyze Audio</h1>
  <p class="desc">Upload a WAV file to map it into dial space and predict its genre.</p>
  <div class="card">
    <div class="upload-zone" id="dropZone">
      <div style="font-size:40px">📁</div>
      <p>Drop a WAV file here or click to browse</p>
      <input type="file" id="fileInput" accept=".wav" style="display:none">
    </div>
    <div style="margin-top:12px;text-align:center">
      <button class="btn btn-primary" id="analyzeBtn" disabled>Analyze</button>
    </div>
  </div>
  <div id="analysisResults" style="display:none">
    <div class="card">
      <h3>Dial Position</h3>
      <div class="dial-row">
        <div class="dial h"><div class="value" id="dialH">—</div><div class="label">Harmonic</div></div>
        <div class="dial r"><div class="value" id="dialR">—</div><div class="label">Rhythmic</div></div>
        <div class="dial s"><div class="value" id="dialS">—</div><div class="label">Spectral</div></div>
      </div>
    </div>
    <div class="card">
      <h3>Prediction</h3>
      <p id="genrePrediction" style="font-size:18px;margin-bottom:12px"></p>
      <table class="results-table" id="distanceTable"><thead><tr><th>Tradition</th><th>Distance</th></tr></thead><tbody></tbody></table>
    </div>
    <div class="card">
      <h3>Spectral Features</h3>
      <table class="results-table" id="featuresTable"><tbody></tbody></table>
    </div>
  </div>
</div>

<!-- COMPOSE -->
<div class="section" id="sec-compose">
  <h1>Compose</h1>
  <p class="desc">Generate music at any point in dial space. Adjust the sliders or click the visualization.</p>
  <div class="card">
    <h3>Target Dials</h3>
    <div class="slider-row"><label>Harmonic Tension</label><input type="range" id="compH" min="0" max="5" step="0.1" value="2.5"><span class="val" id="compHVal">2.5</span></div>
    <div class="slider-row"><label>Rhythmic Complexity</label><input type="range" id="compR" min="0" max="5" step="0.1" value="3.0"><span class="val" id="compRVal">3.0</span></div>
    <div class="slider-row"><label>Spectral Density</label><input type="range" id="compS" min="0" max="5" step="0.1" value="3.0"><span class="val" id="compSVal">3.0</span></div>
    <div class="compose-controls" style="margin-top:12px">
      <div class="slider-row"><label>BPM</label><input type="range" id="compBPM" min="60" max="200" step="5" value="120"><span class="val" id="compBPMVal">120</span></div>
      <div class="slider-row"><label>Bars</label><input type="range" id="compBars" min="2" max="16" step="1" value="4"><span class="val" id="compBarsVal">4</span></div>
      <button class="btn btn-primary" id="composeBtn">Compose &amp; Play</button>
    </div>
  </div>
  <div id="composePlayer" style="display:none" class="card">
    <h3>Playback</h3>
    <audio id="composeAudio" controls style="width:100%"></audio>
  </div>
  <div class="viz-container">
    <h3 style="margin-bottom:8px;font-size:14px;color:var(--text-dim)">Click to set target position</h3>
    <div id="composeViz"></div>
  </div>
</div>

<!-- EXPLORE -->
<div class="section" id="sec-explore">
  <h1>Explore Dial Space</h1>
  <p class="desc">10 musical traditions mapped as regions. Each occupies a characteristic zone.</p>
  <div class="viz-container">
    <div id="exploreViz"></div>
  </div>
  <div class="card">
    <h3>Tradition Profiles</h3>
    <div class="tradition-grid" id="traditionGrid"></div>
  </div>
  <div class="card">
    <h3>Key Findings</h3>
    <table class="results-table">
      <tr><td>V<sub>K</sub> / H<sub>onset</sub> correlation</td><td><strong>r = −0.935</strong></td></tr>
      <tr><td>Tradition recognition rate</td><td><strong>98%</strong></td></tr>
      <tr><td>Unexplored dial space</td><td><strong>82%</strong></td></tr>
      <tr><td>Most pleasing point</td><td><strong>(2.61, 2.33, 4.0) — Gagaku</strong></td></tr>
      <tr><td>Conservation ratio</td><td><strong>~1.003</strong></td></tr>
    </table>
  </div>
</div>

<!-- COMPARE -->
<div class="section" id="sec-compare">
  <h1>Compare</h1>
  <p class="desc">Upload two WAV files to compare their dial positions and tension profiles.</p>
  <div class="compare-grid">
    <div class="compare-panel">
      <h3 style="font-size:14px;margin-bottom:8px">Piece A</h3>
      <div class="upload-zone" id="dropA" style="padding:20px"><p>Drop WAV here</p><input type="file" id="fileA" accept=".wav" style="display:none"></div>
      <div id="resultA" style="margin-top:12px"></div>
    </div>
    <div class="compare-panel">
      <h3 style="font-size:14px;margin-bottom:8px">Piece B</h3>
      <div class="upload-zone" id="dropB" style="padding:20px"><p>Drop WAV here</p><input type="file" id="fileB" accept=".wav" style="display:none"></div>
      <div id="resultB" style="margin-top:12px"></div>
    </div>
  </div>
  <div class="card" id="compareResults" style="display:none;margin-top:16px">
    <h3>Comparison</h3>
    <p id="compareSummary"></p>
    <table class="results-table" style="margin-top:12px"><tbody id="compareTable"></tbody></table>
  </div>
</div>

</div>
</div>

<div class="toast" id="toast"></div>

<script>
// ---- Navigation ----
const navItems = document.querySelectorAll('.nav-item');
const sections = document.querySelectorAll('.section');
navItems.forEach(item => {
  item.addEventListener('click', () => {
    navItems.forEach(n => n.classList.remove('active'));
    sections.forEach(s => s.classList.remove('active'));
    item.classList.add('active');
    document.getElementById('sec-' + item.dataset.section).classList.add('active');
  });
});

// ---- Toast ----
function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}

// ---- Tradition data (will be fetched) ----
let TRADITIONS = {};
fetch('/traditions').then(r => r.json()).then(d => { TRADITIONS = d; renderTraditions(); renderExploreViz(); renderComposeViz(); });

// ---- SVG helpers ----
const COLORS = {Jazz:'#f97583',Classical:'#79c0ff',Gamelan:'#d2a8ff',Gagaku:'#56d364',Hindustani:'#ffa657',
  'African Polyrhythm':'#ff7b72',EDM:'#58a6ff',Blues:'#e3b341','Hip-hop':'#bc8cff',Latin:'#3fb950'};

function dialToSVG(h, r, s, cx, cy, scaleX, scaleY) {
  // Isometric projection: x = (r - h) * cos30, y = -(h + r) * sin30 - s
  const cos30 = 0.866, sin30 = 0.5;
  const x = cx + (r - h) * cos30 * scaleX;
  const y = cy - (-(h + r) * sin30 + s) * scaleY;
  return {x, y};
}

function makeDialSVG(width, height, traditions, marker, onClick) {
  const cx = width / 2, cy = height * 0.6;
  const scaleX = width / 7, scaleY = height / 8;
  let svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" style="font-family:sans-serif">`;

  // Grid lines
  for (let i = 0; i <= 5; i++) {
    for (let j = 0; j <= 5; j++) {
      const p = dialToSVG(i, j, 0, cx, cy, scaleX, scaleY);
      const p2 = dialToSVG(i, j, 5, cx, cy, scaleX, scaleY);
      svg += `<line x1="${p.x}" y1="${p.y}" x2="${p2.x}" y2="${p2.y}" stroke="#21262d" stroke-width="0.5"/>`;
    }
  }
  // Base plane
  const corners = [
    dialToSVG(0,0,0,cx,cy,scaleX,scaleY),
    dialToSVG(5,0,0,cx,cy,scaleX,scaleY),
    dialToSVG(5,5,0,cx,cy,scaleX,scaleY),
    dialToSVG(0,5,0,cx,cy,scaleX,scaleY)
  ];
  svg += `<polygon points="${corners.map(c=>c.x+','+c.y).join(' ')}" fill="rgba(88,166,255,0.03)" stroke="#30363d"/>`;

  // Axis labels
  const hEnd = dialToSVG(5, 0, 0, cx, cy, scaleX, scaleY);
  const rEnd = dialToSVG(0, 5, 0, cx, cy, scaleX, scaleY);
  const sEnd = dialToSVG(0, 0, 5, cx, cy, scaleX, scaleY);
  svg += `<text x="${hEnd.x-20}" y="${hEnd.y+16}" fill="#f97583" font-size="11">H (Harmonic)</text>`;
  svg += `<text x="${rEnd.x+4}" y="${rEnd.y+16}" fill="#79c0ff" font-size="11">R (Rhythmic)</text>`;
  svg += `<text x="${sEnd.x+4}" y="${sEnd.y}" fill="#56d364" font-size="11">S (Spectral)</text>`;

  // Tradition ellipses
  for (const [name, t] of Object.entries(traditions)) {
    const [ch, cr, cs] = t.center;
    const [sh, sr, ss] = t.spread;
    const center = dialToSVG(ch, cr, cs, cx, cy, scaleX, scaleY);
    const col = COLORS[name] || '#8b949e';
    svg += `<ellipse cx="${center.x}" cy="${center.y}" rx="${sr*scaleX*0.7}" ry="${ss*scaleY*0.7}" fill="${col}22" stroke="${col}" stroke-width="1.5" opacity="0.7"/>`;
    svg += `<circle cx="${center.x}" cy="${center.y}" r="3" fill="${col}"/>`;
    svg += `<text x="${center.x}" y="${center.y - ss*scaleY*0.7 - 6}" fill="${col}" font-size="10" text-anchor="middle">${name}</text>`;
  }

  // Most pleasing point star
  const mp = dialToSVG(2.61, 2.33, 4.0, cx, cy, scaleX, scaleY);
  svg += `<polygon points="${star(mp.x, mp.y, 6, 3)}" fill="#ffd700" stroke="#fff" stroke-width="0.5"/>`;
  svg += `<text x="${mp.x+10}" y="${mp.y-4}" fill="#ffd700" font-size="9">★ Most Pleasing</text>`;

  // Custom marker
  if (marker) {
    const m = dialToSVG(marker.h, marker.r, marker.s, cx, cy, scaleX, scaleY);
    svg += `<circle cx="${m.x}" cy="${m.y}" r="5" fill="#fff" stroke="var(--accent)" stroke-width="2"/>`;
  }

  // Invisible click overlay
  if (onClick) {
    svg += `<rect x="0" y="0" width="${width}" height="${height}" fill="transparent" onclick="handleVizClick(event)"/>`;
  }

  svg += `</svg>`;
  return svg;
}

function star(cx, cy, r1, r2) {
  let pts = [];
  for (let i = 0; i < 5; i++) {
    const a1 = (i * 72 - 90) * Math.PI / 180;
    const a2 = ((i * 72 + 36) - 90) * Math.PI / 180;
    pts.push(`${cx + r1*Math.cos(a1)},${cy + r1*Math.sin(a1)}`);
    pts.push(`${cx + r2*Math.cos(a2)},${cy + r2*Math.sin(a2)}`);
  }
  return pts.join(' ');
}

// ---- Explore viz ----
function renderExploreViz() {
  document.getElementById('exploreViz').innerHTML = makeDialSVG(700, 500, TRADITIONS, null, false);
}

function renderTraditions() {
  const grid = document.getElementById('traditionGrid');
  grid.innerHTML = '';
  for (const [name, t] of Object.entries(TRADITIONS)) {
    const [h,r,s] = t.center;
    const col = COLORS[name] || '#8b949e';
    grid.innerHTML += `<div class="tradition-card" style="border-left:3px solid ${col}">
      <div class="name" style="color:${col}">${name}</div>
      <div class="dials">H: ${h} · R: ${r} · S: ${s}</div>
      <div class="desc">${t.description}</div>
    </div>`;
  }
}

// ---- Compose viz ----
function renderComposeViz() {
  const h = parseFloat(document.getElementById('compH').value);
  const r = parseFloat(document.getElementById('compR').value);
  const s = parseFloat(document.getElementById('compS').value);
  document.getElementById('composeViz').innerHTML = makeDialSVG(700, 500, TRADITIONS, {h,r,s}, true);
}

// Slider bindings
['compH','compR','compS','compBPM','compBars'].forEach(id => {
  const el = document.getElementById(id);
  const valEl = document.getElementById(id + 'Val');
  el.addEventListener('input', () => {
    valEl.textContent = el.value;
    if (['compH','compR','compS'].includes(id)) renderComposeViz();
  });
});

// Click on viz to set position
window.handleVizClick = function(e) {
  const svg = e.target.closest('svg');
  if (!svg) return;
  const rect = svg.getBoundingClientRect();
  const width = 700, height = 500;
  const px = (e.clientX - rect.left) / rect.width * width;
  const py = (e.clientY - rect.top) / rect.height * height;
  const cx = width / 2, cy = height * 0.6;
  const scaleX = width / 7, scaleY = height / 8;
  // Inverse isometric (approximate): solve for h,r,s given x,y
  // We'll just adjust r and h based on x, keep s from slider
  const s = parseFloat(document.getElementById('compS').value);
  const cos30 = 0.866, sin30 = 0.5;
  // x = cx + (r-h)*cos30*sX → r-h = (x-cx)/(cos30*sX)
  // y = cy - (-(h+r)*sin30 + s)*sY → h+r = ((cy-y)/sY - s)/sin30... simplify
  const dR_H = (px - cx) / (cos30 * scaleX);
  const sumHR = -((py - cy) / scaleY + s) / sin30;
  const r_val = (dR_H + sumHR) / 2;
  const h_val = (sumHR - dR_H) / 2;
  const clamped = (v) => Math.max(0, Math.min(5, Math.round(v*10)/10));
  document.getElementById('compH').value = clamped(h_val);
  document.getElementById('compR').value = clamped(r_val);
  document.getElementById('compHVal').textContent = clamped(h_val);
  document.getElementById('compRVal').textContent = clamped(r_val);
  renderComposeViz();
};

// ---- Compose ----
document.getElementById('composeBtn').addEventListener('click', async () => {
  const h = document.getElementById('compH').value;
  const r = document.getElementById('compR').value;
  const s = document.getElementById('compS').value;
  const bpm = document.getElementById('compBPM').value;
  const bars = document.getElementById('compBars').value;
  showToast('Composing...');
  try {
    const resp = await fetch(`/compose?h=${h}&r=${r}&s=${s}&bpm=${bpm}&bars=${bars}`);
    if (!resp.ok) throw new Error('Compose failed');
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    document.getElementById('composeAudio').src = url;
    document.getElementById('composePlayer').style.display = 'block';
    document.getElementById('composeAudio').play();
    showToast('Composition ready!');
  } catch(e) { showToast('Error: ' + e.message); }
});

// ---- Analyze ----
let selectedFile = null;
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');

dropZone.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragover'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
dropZone.addEventListener('drop', e => {
  e.preventDefault(); dropZone.classList.remove('dragover');
  if (e.dataTransfer.files.length) { selectedFile = e.dataTransfer.files[0]; dropZone.querySelector('p').textContent = selectedFile.name; document.getElementById('analyzeBtn').disabled = false; }
});
fileInput.addEventListener('change', () => {
  if (fileInput.files.length) { selectedFile = fileInput.files[0]; dropZone.querySelector('p').textContent = selectedFile.name; document.getElementById('analyzeBtn').disabled = false; }
});

document.getElementById('analyzeBtn').addEventListener('click', async () => {
  if (!selectedFile) return;
  showToast('Analyzing...');
  const form = new FormData();
  form.append('file', selectedFile);
  try {
    const resp = await fetch('/analyze', {method:'POST', body: form});
    if (!resp.ok) throw new Error('Analysis failed');
    const data = await resp.json();
    const dp = data.dial_position;
    document.getElementById('dialH').textContent = dp.harmonic_tension.toFixed(2);
    document.getElementById('dialR').textContent = dp.rhythmic_complexity.toFixed(2);
    document.getElementById('dialS').textContent = dp.spectral_density.toFixed(2);
    document.getElementById('genrePrediction').innerHTML = `Predicted: <strong style="color:var(--accent)">${data.prediction.genre}</strong> (${(data.prediction.confidence*100).toFixed(1)}%)`;
    const tbody = document.querySelector('#distanceTable tbody');
    tbody.innerHTML = '';
    for (const [name, dist] of Object.entries(data.distances).sort((a,b) => a[1]-b[1])) {
      tbody.innerHTML += `<tr><td>${name}</td><td>${dist.toFixed(3)}</td></tr>`;
    }
    const ftbody = document.querySelector('#featuresTable tbody');
    ftbody.innerHTML = '';
    for (const [k,v] of Object.entries(data.spectral_features)) {
      ftbody.innerHTML += `<tr><td>${k}</td><td>${typeof v === 'number' ? v.toFixed(4) : v}</td></tr>`;
    }
    document.getElementById('analysisResults').style.display = 'block';
    showToast('Analysis complete!');
  } catch(e) { showToast('Error: ' + e.message); }
});

// ---- Compare ----
let fileA = null, fileB = null, resultA = null, resultB = null;
function setupCompare(dropId, inputId, side) {
  const dz = document.getElementById(dropId);
  const fi = document.getElementById(inputId);
  dz.addEventListener('click', () => fi.click());
  dz.addEventListener('dragover', e => { e.preventDefault(); dz.classList.add('dragover'); });
  dz.addEventListener('dragleave', () => dz.classList.remove('dragover'));
  dz.addEventListener('drop', async e => {
    e.preventDefault(); dz.classList.remove('dragover');
    const f = e.dataTransfer.files[0]; if (!f) return;
    dz.querySelector('p').textContent = f.name;
    if (side === 'A') fileA = f; else fileB = f;
    await doCompareUpload(side, f);
  });
  fi.addEventListener('change', async () => {
    const f = fi.files[0]; if (!f) return;
    dz.querySelector('p').textContent = f.name;
    if (side === 'A') fileA = f; else fileB = f;
    await doCompareUpload(side, f);
  });
}
async function doCompareUpload(side, f) {
  const form = new FormData(); form.append('file', f);
  try {
    const resp = await fetch('/analyze', {method:'POST', body:form});
    if (!resp.ok) throw new Error('Failed');
    const data = await resp.json();
    const dp = data.dial_position;
    const el = document.getElementById('result' + side);
    el.innerHTML = `<div style="font-size:13px">H: ${dp.harmonic_tension.toFixed(2)} · R: ${dp.rhythmic_complexity.toFixed(2)} · S: ${dp.spectral_density.toFixed(2)}<br>Predicted: <strong>${data.prediction.genre}</strong></div>`;
    if (side === 'A') resultA = data; else resultB = data;
    if (resultA && resultB) showComparison();
  } catch(e) { showToast('Error: ' + e.message); }
}
function showComparison() {
  const dpA = resultA.dial_position, dpB = resultB.dial_position;
  const dist = Math.sqrt((dpA.harmonic_tension-dpB.harmonic_tension)**2 + (dpA.rhythmic_complexity-dpB.rhythmic_complexity)**2 + (dpA.spectral_density-dpB.spectral_density)**2);
  document.getElementById('compareSummary').innerHTML = `Dial distance: <strong>${dist.toFixed(3)}</strong> · Same genre prediction: <strong>${resultA.prediction.genre === resultB.prediction.genre ? 'Yes' : 'No'}</strong>`;
  const tbody = document.getElementById('compareTable');
  tbody.innerHTML = `
    <tr><td></td><th>Piece A</th><th>Piece B</th></tr>
    <tr><td>Harmonic</td><td>${dpA.harmonic_tension.toFixed(3)}</td><td>${dpB.harmonic_tension.toFixed(3)}</td></tr>
    <tr><td>Rhythmic</td><td>${dpA.rhythmic_complexity.toFixed(3)}</td><td>${dpB.rhythmic_complexity.toFixed(3)}</td></tr>
    <tr><td>Spectral</td><td>${dpA.spectral_density.toFixed(3)}</td><td>${dpB.spectral_density.toFixed(3)}</td></tr>
    <tr><td>Genre</td><td>${resultA.prediction.genre}</td><td>${resultB.prediction.genre}</td></tr>
    <tr><td>Confidence</td><td>${(resultA.prediction.confidence*100).toFixed(1)}%</td><td>${(resultB.prediction.confidence*100).toFixed(1)}%</td></tr>
  `;
  document.getElementById('compareResults').style.display = 'block';
}
setupCompare('dropA', 'fileA', 'A');
setupCompare('dropB', 'fileB', 'B');
</script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# WAV synthesis helper (for compose endpoint)
# ---------------------------------------------------------------------------

def _generate_wav_from_dials(h: float, r: float, s: float, bpm: int = 120, bars: int = 4) -> bytes:
    """Synthesize a simple WAV from dial parameters."""
    sr = 44100
    duration = bars * 4 * 60 / bpm  # 4 beats per bar
    n_samples = int(sr * duration)
    t = [i / sr for i in range(n_samples)]

    # Base frequencies scaled by dials
    # Harmonic tension → more complex harmonics (add overtones)
    # Rhythmic complexity → more rhythmic variation
    # Spectral density → richer frequency content

    samples = [0.0] * n_samples

    # Fundamental
    base_freq = 220.0  # A3
    for i in range(n_samples):
        ti = t[i]

        # Rhythmic envelope — more complex rhythm = faster amplitude modulation
        rhythm_freq = 1.0 + r * 1.5  # 1–8.5 Hz
        envelope = 0.5 + 0.5 * math.sin(2 * math.pi * rhythm_freq * ti)
        # Add syncopation for higher rhythmic complexity
        if r > 2.5:
            sync_freq = rhythm_freq * 1.5
            envelope *= 0.5 + 0.5 * math.sin(2 * math.pi * sync_freq * ti + math.pi / 3)

        # Harmonic series — more overtones for higher harmonic tension
        n_harmonics = max(1, int(h * 2))  # 1–10 harmonics
        val = 0.0
        for k in range(1, n_harmonics + 1):
            amp = 1.0 / k  # Harmonics diminish
            # Slight detuning for tension
            detune = 1.0 + 0.002 * h * (k - 1)
            val += amp * math.sin(2 * math.pi * base_freq * k * detune * ti)

        # Spectral density → add noise component
        noise_amp = s * 0.02
        # Simple pseudo-noise using multiple sines at inharmonic frequencies
        noise = 0.0
        for p in range(max(1, int(s))):
            freq = base_freq * (2.718 + p * 0.73)  # Inharmonic
            noise += math.sin(2 * math.pi * freq * ti) / (p + 1)

        samples[i] = envelope * val * 0.3 + noise_amp * noise * 0.2

    # Normalize
    peak = max(abs(s) for s in samples) or 1.0
    samples = [int(s / peak * 32000) for s in samples]

    # Write WAV
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(struct.pack(f'<{len(samples)}h', *samples))
    return buf.getvalue()


# ---------------------------------------------------------------------------
# HTTP Handler
# ---------------------------------------------------------------------------

classifier = DialClassifier(k=5)


class DemoHandler(BaseHTTPRequestHandler):
    """Minimal HTTP handler for the web demo."""

    def _send(self, code: int, content_type: str, body: bytes) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, data: dict, code: int = 200) -> None:
        body = json.dumps(data, indent=2).encode()
        self._send(code, "application/json", body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self._send(200, "text/html; charset=utf-8", INDEX_HTML.encode())
        elif path == "/traditions":
            traditions_out = {}
            for name, info in DIAL_RANGES.items():
                traditions_out[name] = {
                    "center": info["center"].tolist(),
                    "spread": info["spread"].tolist(),
                    "description": info["description"],
                }
            self._send_json(traditions_out)
        elif path == "/compose":
            qs = parse_qs(parsed.query)
            h = float(qs.get("h", ["2.5"])[0])
            r = float(qs.get("r", ["3.0"])[0])
            s = float(qs.get("s", ["3.0"])[0])
            bpm = int(qs.get("bpm", ["120"])[0])
            bars = int(qs.get("bars", ["4"])[0])
            wav_data = _generate_wav_from_dials(h, r, s, bpm, bars)
            self._send(200, "audio/wav", wav_data)
        elif path == "/dial-space-svg":
            # Generate SVG string
            svg = _make_svg()
            self._send(200, "image/svg+xml", svg.encode())
        else:
            self._send(404, "text/plain", b"Not found")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/analyze":
            content_type = self.headers.get("Content-Type", "")
            if "multipart/form-data" not in content_type:
                self._send_json({"error": "Expected multipart/form-data"}, 400)
                return

            # Parse multipart manually (simple approach)
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)

            # Extract WAV data from multipart
            wav_data = _extract_file_from_multipart(body, content_type)
            if not wav_data:
                self._send_json({"error": "No WAV file found in upload"}, 400)
                return

            # Write to temp file and analyze
            try:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                    tf.write(wav_data)
                    tf_path = tf.name

                result = analyze_wav(tf_path)
                prediction = classifier.predict(result.dial_position)

                response = {
                    "dial_position": {
                        "harmonic_tension": result.dial_position.harmonic_tension,
                        "rhythmic_complexity": result.dial_position.rhythmic_complexity,
                        "spectral_density": result.dial_position.spectral_density,
                    },
                    "prediction": {
                        "genre": prediction.genre,
                        "confidence": prediction.confidence,
                    },
                    "distances": prediction.distances,
                    "spectral_features": result.spectral_features,
                    "duration": result.duration,
                    "onset_count": result.onset_count,
                }
                self._send_json(response)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            finally:
                Path(tf_path).unlink(missing_ok=True)
        else:
            self._send(404, "text/plain", b"Not found")

    def log_message(self, format: str, *args: Any) -> None:
        print(f"[demo] {args[0]}")


def _extract_file_from_multipart(body: bytes, content_type: str) -> bytes | None:
    """Extract the first file payload from a multipart/form-data body."""
    boundary = content_type.split("boundary=")[-1].encode()
    if boundary not in body:
        return None
    parts = body.split(b"--" + boundary)
    for part in parts:
        if b"Content-Disposition" not in part:
            continue
        # Find the header/body separator
        sep = b"\r\n\r\n"
        idx = part.find(sep)
        if idx < 0:
            continue
        file_data = part[idx + len(sep):]
        # Strip trailing \r\n
        if file_data.endswith(b"\r\n"):
            file_data = file_data[:-2]
        if len(file_data) > 0:
            return file_data
    return None


def _make_svg() -> str:
    """Generate the dial space SVG for the /dial-space-svg endpoint."""
    width, height = 700, 500
    cx, cy = width / 2, height * 0.6
    scaleX, scaleY = width / 7, height / 8
    cos30, sin30 = 0.866, 0.5

    def proj(h, r, s):
        x = cx + (r - h) * cos30 * scaleX
        y = cy - (-(h + r) * sin30 + s) * scaleY
        return x, y

    svg_parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">']

    # Base plane
    corners = [proj(0,0,0), proj(5,0,0), proj(5,5,0), proj(0,5,0)]
    pts = " ".join(f"{x},{y}" for x, y in corners)
    svg_parts.append(f'<polygon points="{pts}" fill="rgba(88,166,255,0.03)" stroke="#30363d"/>')

    # Traditions
    colors = {"Jazz": "#f97583", "Classical": "#79c0ff", "Gamelan": "#d2a8ff", "Gagaku": "#56d364",
              "Hindustani": "#ffa657", "African Polyrhythm": "#ff7b72", "EDM": "#58a6ff",
              "Blues": "#e3b341", "Hip-hop": "#bc8cff", "Latin": "#3fb950"}

    for name, info in DIAL_RANGES.items():
        ch, cr, cs = info["center"]
        sh, sr_val, ss = info["spread"]
        x, y = proj(ch, cr, cs)
        col = colors.get(name, "#8b949e")
        rx = sr_val * scaleX * 0.7
        ry = ss * scaleY * 0.7
        svg_parts.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{col}22" stroke="{col}" stroke-width="1.5"/>')
        svg_parts.append(f'<circle cx="{x}" cy="{y}" r="3" fill="{col}"/>')
        svg_parts.append(f'<text x="{x}" y="{y - ry - 6}" fill="{col}" font-size="10" text-anchor="middle">{name}</text>')

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    server = HTTPServer(("0.0.0.0", port), DemoHandler)
    print(f"🎵 Constraint Toolkit demo running at http://localhost:{port}")
    print("   Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()


if __name__ == "__main__":
    main()
