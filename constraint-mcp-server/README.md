# Constraint Theory MCP Server for Copilot for Eclipse

Exposes the constraint-theory ecosystem as MCP (Model Context Protocol) tools that GitHub Copilot can use natively inside Eclipse.

## Tools

| Tool | Description |
|------|-------------|
| `constraint_snap` | Snap a MIDI pitch to the nearest Eisenstein lattice point |
| `constraint_funnel` | Apply gravitational pull toward a target pitch |
| `constraint_diagnose` | 4-order Goodman diagnostic (position → direction → curvature → structure) |
| `constraint_generate` | Generate music in a given mode + terrain |
| `constraint_render` | Render notes to WAV audio (base64-encoded) |
| `constraint_terrain_list` | List all available musical terrains |

## Setup

### 1. Install the Python MCP server

```bash
cd constraint-mcp-server
pip install -e ".[cli]"
```

### 2. Install the Eclipse plugin

Copy `com.superinstance.constraint.copilot/` into your Eclipse dropins or install via the PDE.

Requires:
- Copilot for Eclipse installed
- `com.microsoft.copilot.eclipse.ui` plugin (provides `mcpRegistration` extension point)

### 3. Configure workspace path

Set the system property or environment variable so the plugin can find the Python packages:

```ini
# eclipse.ini
-Dconstraint.workspace=/path/to/your/workspace
```

Or set `CONSTRAINT_WORKSPACE` environment variable.

## Testing the MCP server standalone

```bash
# The server speaks JSON-RPC over stdio
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python3 -m constraint_mcp_server
```

## Architecture

```
Copilot Chat (Eclipse)
    ↓ tool calls
Copilot Plugin (com.microsoft.copilot.eclipse.ui)
    ↓ MCP stdio JSON-RPC
constraint-mcp-server (Python)
    ↓ imports
constraint-substrate  → lattice_snap, funnel, is_laman, consensus, holonomy
constraint-instrument → 7 modes, 17 terrains, Goodman diagnostic
constraint-synth      → audio rendering, 5 presets
```

## Connection Config

The `ConstraintMcpProvider` returns JSON like `mcp-config.json`:

```json
{
  "servers": {
    "constraint-ecosystem": {
      "command": "python3",
      "args": ["-m", "constraint_mcp_server"],
      "env": {
        "PYTHONPATH": "...",
        "CONSTRAINT_WORKSPACE": "..."
      },
      "type": "stdio"
    }
  }
}
```
