"""
LAENGINE MCP Server

Exposes game development tools via the MCP protocol for LAOS orchestration.
Tools: generate_seed, get_teams, get_team_players, generate_schedule,
       simulate_next_round, get_standings
"""

import sys
import json
import os
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from laengine.brasfoot.data import gerar_times
from laengine.brasfoot.engine import gerar_tabela_jogos, simular_partida, calcular_tabela
from laengine.brasfoot.models import Team, Player, Match, Standings

try:
    import mcp.types as types
    from mcp.server import Server
    import mcp.server.stdio
    HAS_MCP = True
except ImportError:
    HAS_MCP = False


class LaengineServer:
    """LAENGINE MCP server implementation."""
    
    def __init__(self):
        self.game_state: dict[str, Any] = {
            "times": [],
            "partidas": [],
            "tabela": [],
        }
    
    def handle_tool(self, name: str, arguments: dict | None = None) -> str:
        """Handle a tool call and return JSON result."""
        handlers = {
            "generate_seed": self._generate_seed,
            "get_teams": self._get_teams,
            "get_team_players": self._get_team_players,
            "generate_schedule": self._generate_schedule,
            "simulate_next_round": self._simulate_next_round,
            "simulate_all_rounds": self._simulate_all_rounds,
            "get_standings": self._get_standings,
        }
        
        handler = handlers.get(name)
        if not handler:
            return json.dumps({"error": f"Unknown tool: {name}"})
        
        return handler(arguments or {})
    
    def _generate_seed(self, _args: dict) -> str:
        self.game_state["times"] = gerar_times()
        self.game_state["partidas"] = []
        self.game_state["tabela"] = []
        result = [{
            "id": t.id, "nome": t.nome, "cidade": t.cidade,
            "sigla": t.sigla, "overall": t.overall, "jogadores": len(t.jogadores)
        } for t in self.game_state["times"]]
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    def _get_teams(self, _args: dict) -> str:
        result = []
        for t in self.game_state["times"]:
            jogadores = [{
                "id": p.id, "nome": p.nome, "posicao": p.posicao,
                "overall": p.overall, "numero": p.numero
            } for p in t.jogadores]
            result.append({
                "id": t.id, "nome": t.nome, "sigla": t.sigla,
                "overall": t.overall, "jogadores": jogadores
            })
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    def _get_team_players(self, args: dict) -> str:
        team_id = args.get("team_id")
        team = next((t for t in self.game_state["times"] if t.id == team_id), None)
        if not team:
            return json.dumps({"error": "Time não encontrado"}, ensure_ascii=False)
        return json.dumps([{
            "id": p.id, "nome": p.nome, "posicao": p.posicao, "overall": p.overall,
            "ataque": p.ataque, "defesa": p.defesa, "meio": p.meio,
            "stamina": p.stamina, "idade": p.idade, "numero": p.numero
        } for p in team.jogadores], indent=2, ensure_ascii=False)
    
    def _generate_schedule(self, _args: dict) -> str:
        if not self.game_state["times"]:
            self.game_state["times"] = gerar_times()
        self.game_state["partidas"] = gerar_tabela_jogos(self.game_state["times"])
        result = [{
            "id": m.id, "rodada": m.rodada, "time_casa": m.time_casa_nome,
            "time_fora": m.time_fora_nome
        } for m in self.game_state["partidas"]]
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    def _simulate_next_round(self, _args: dict) -> str:
        if not self.game_state["partidas"]:
            return json.dumps({"error": "Gere a tabela primeiro"}, ensure_ascii=False)
        
        times_dict = {t.id: t for t in self.game_state["times"]}
        pendentes = [m for m in self.game_state["partidas"] if m.status == "pending"]
        if not pendentes:
            return json.dumps({"error": "Campeonato já terminou!"}, ensure_ascii=False)
        
        proxima_rodada = min(m.rodada for m in pendentes)
        rodada_jogos = [m for m in pendentes if m.rodada == proxima_rodada]
        
        for jogo in rodada_jogos:
            time_casa = times_dict.get(jogo.time_casa_id)
            time_fora = times_dict.get(jogo.time_fora_id)
            if time_casa and time_fora:
                simular_partida(jogo, time_casa, time_fora)
        
        self.game_state["tabela"] = calcular_tabela(self.game_state["times"], self.game_state["partidas"])
        
        result = []
        for jogo in rodada_jogos:
            result.append({
                "rodada": jogo.rodada,
                "time_casa": jogo.time_casa_nome,
                "time_fora": jogo.time_fora_nome,
                "gols_casa": jogo.gols_casa,
                "gols_fora": jogo.gols_fora,
                "eventos": [{"minuto": e.minuto, "descricao": e.descricao} for e in jogo.events]
            })
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    def _simulate_all_rounds(self, _args: dict) -> str:
        """Simulate all remaining rounds at once."""
        if not self.game_state["partidas"]:
            return json.dumps({"error": "Gere a tabela primeiro"}, ensure_ascii=False)
        
        results = []
        times_dict = {t.id: t for t in self.game_state["times"]}
        
        for match in self.game_state["partidas"]:
            if match.status == "pending":
                time_casa = times_dict.get(match.time_casa_id)
                time_fora = times_dict.get(match.time_fora_id)
                if time_casa and time_fora:
                    simular_partida(match, time_casa, time_fora)
        
        self.game_state["tabela"] = calcular_tabela(self.game_state["times"], self.game_state["partidas"])
        
        for m in self.game_state["partidas"]:
            results.append({
                "rodada": m.rodada,
                "time_casa": m.time_casa_nome,
                "time_fora": m.time_fora_nome,
                "gols_casa": m.gols_casa,
                "gols_fora": m.gols_fora,
            })
        
        return json.dumps({"partidas": results}, indent=2, ensure_ascii=False)
    
    def _get_standings(self, _args: dict) -> str:
        if not self.game_state["tabela"] and self.game_state["times"]:
            self.game_state["tabela"] = calcular_tabela(self.game_state["times"], self.game_state["partidas"])
        result = [{
            "pos": i+1, "time": s.nome, "sigla": s.sigla, "pts": s.pts, "j": s.j,
            "v": s.v, "e": s.e, "d": s.d, "gp": s.gp, "gc": s.gc, "sg": s.sg,
            "aproveitamento": round(s.pts / (s.j * 3) * 100, 1) if s.j > 0 else 0
        } for i, s in enumerate(self.game_state["tabela"])]
        return json.dumps(result, indent=2, ensure_ascii=False)


# MCP server instance for async framework
if HAS_MCP:
    mcp_server = Server("laengine")
    engine = LaengineServer()
    
    @mcp_server.list_tools()
    async def handle_list_tools():
        return [
            types.Tool(
                name="health",
                description="Check server health status",
                inputSchema={"type": "object", "properties": {}, "required": []},
            ),
            types.Tool(
                name="generate_seed",
                description="Generate 10 Brazilian football teams with synthetic players",
                inputSchema={"type": "object", "properties": {}, "required": []},
            ),
            types.Tool(
                name="get_teams",
                description="Get all teams and their players",
                inputSchema={"type": "object", "properties": {}, "required": []},
            ),
            types.Tool(
                name="get_team_players",
                description="Get players for a specific team",
                inputSchema={"type": "object", "properties": {
                    "team_id": {"type": "integer", "description": "Team ID"}
                }, "required": ["team_id"]},
            ),
            types.Tool(
                name="generate_schedule",
                description="Generate round-robin schedule for all teams",
                inputSchema={"type": "object", "properties": {}, "required": []},
            ),
            types.Tool(
                name="simulate_next_round",
                description="Simulate the next pending round of matches",
                inputSchema={"type": "object", "properties": {}, "required": []},
            ),
            types.Tool(
                name="simulate_all_rounds",
                description="Simulate all remaining rounds at once",
                inputSchema={"type": "object", "properties": {}, "required": []},
            ),
            types.Tool(
                name="get_standings",
                description="Get current league standings",
                inputSchema={"type": "object", "properties": {}, "required": []},
            ),
        ]
    
    @mcp_server.call_tool()
    async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
        if name == "health":
            return [types.TextContent(type="text", text='{"status": "ok", "server": "laengine"}')]
        result = engine.handle_tool(name, arguments or {})
        return [types.TextContent(type="text", text=result)]
    
    async def run_mcp():
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await mcp_server.run(
                read_stream, write_stream,
                mcp_server.create_initialization_options(),
            )


def main():
    """Run the MCP server (stdio)."""
    import asyncio
    if HAS_MCP:
        asyncio.run(run_mcp())
    else:
        # CLI mode for testing
        import sys
        engine = LaengineServer()
        print("LAENGINE Test CLI")
        print("Commands: generate_seed, get_teams, get_team_players, generate_schedule, simulate_next_round, simulate_all_rounds, get_standings, quit")
        while True:
            try:
                cmd = input("\n> ").strip()
                if cmd == "quit":
                    break
                print(engine.handle_tool(cmd))
            except EOFError:
                break
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    main()
