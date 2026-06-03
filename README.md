# LAENGINE

Game development capability for LAOS — match simulation, sports data, and interactive game UI.

## Capabilities

- **Match Simulation**: Brasfoot-style text commentary engine
- **Team/Player Generation**: Synthetic Brazilian teams with realistic attributes
- **League Management**: Round-robin scheduling, standings
- **MCP Tools**: All game operations exposed via MCP protocol

## Architecture

```
laengine/
├── src/laengine/
│   ├── brasfoot/        ← Brasfoot simulation engine
│   │   ├── models.py    (Team, Player, Match, MatchEvent, Standings)
│   │   ├── data.py      (synthetic team/player generation)
│   │   └── engine.py    (schedule, simulation, standings)
│   └── mcp/
│       └── server.py    ← MCP server exposing game tools
├── skills/
│   └── game-ui-skill.md ← Design patterns for game UIs
└── pyproject.toml
```

## Usage

### MCP server (for LAOS orchestration)
```bash
uv run python -m laengine.mcp.server
```

### As a Python library
```python
from laengine.brasfoot import gerar_times, simular_partida

times = gerar_times()
print(f"{len(times)} times gerados")
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `generate_seed` | Generate 10 Brazilian teams |
| `get_teams` | List all teams with players |
| `get_team_players` | Get players for a specific team |
| `generate_schedule` | Create round-robin schedule |
| `simulate_next_round` | Simulate next round |
| `simulate_all_rounds` | Simulate entire season |
| `get_standings` | Get current league table |
