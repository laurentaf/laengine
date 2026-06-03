"""Data models for Brasfoot simulation."""

from dataclasses import dataclass, field, asdict
from typing import List, Optional
import json


@dataclass
class Player:
    """A football player."""
    id: int
    nome: str
    posicao: str  # GOL, ZAG, LAT, MEI, ATA
    overall: int
    ataque: int
    defesa: int
    meio: int
    stamina: int
    idade: int
    numero: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Team:
    """A football team with squad."""
    id: int
    nome: str
    cidade: str
    sigla: str
    jogadores: List[Player] = field(default_factory=list)
    overall: int = 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "cidade": self.cidade,
            "sigla": self.sigla,
            "overall": self.overall,
            "jogadores": [p.to_dict() for p in self.jogadores],
        }


@dataclass
class MatchEvent:
    """An event during a match (goal, foul, save, etc)."""
    minuto: int
    tipo: str  # GOL, CARTAO, CHUTE, FALTA, ESCANTEIO, DEFESA, IMPEDIMENTO, FIM
    descricao: str
    time_id: int
    jogador_nome: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Match:
    """A football match with events."""
    id: int
    rodada: int
    time_casa_id: int
    time_fora_id: int
    time_casa_nome: str = ""
    time_fora_nome: str = ""
    gols_casa: int = 0
    gols_fora: int = 0
    events: List[MatchEvent] = field(default_factory=list)
    status: str = "pending"  # pending, playing, finished

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "rodada": self.rodada,
            "time_casa_id": self.time_casa_id,
            "time_fora_id": self.time_fora_id,
            "time_casa_nome": self.time_casa_nome,
            "time_fora_nome": self.time_fora_nome,
            "gols_casa": self.gols_casa,
            "gols_fora": self.gols_fora,
            "eventos": [e.to_dict() for e in self.events],
            "status": self.status,
        }


@dataclass
class Standings:
    """League table entry."""
    time_id: int
    nome: str
    sigla: str
    pts: int = 0
    j: int = 0
    v: int = 0
    e: int = 0
    d: int = 0
    gp: int = 0
    gc: int = 0
    sg: int = 0

    def to_dict(self) -> dict:
        return asdict(self)
