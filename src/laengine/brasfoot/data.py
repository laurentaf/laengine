"""Synthetic data generation for Brazilian football teams."""

import random
from .models import Team, Player


TIMES_BRASILEIROS = [
    ("Flamengo", "Rio de Janeiro", "FLA"),
    ("Palmeiras", "São Paulo", "PAL"),
    ("Santos", "Santos", "SAN"),
    ("São Paulo", "São Paulo", "SAO"),
    ("Corinthians", "São Paulo", "COR"),
    ("Cruzeiro", "Belo Horizonte", "CRU"),
    ("Grêmio", "Porto Alegre", "GRE"),
    ("Internacional", "Porto Alegre", "INT"),
    ("Bahia", "Salvador", "BAH"),
    ("Fluminense", "Rio de Janeiro", "FLU"),
]

NOMES = [
    "João", "Pedro", "Lucas", "Gabriel", "Rafael", "Felipe", "Gustavo",
    "Diego", "Bruno", "Leonardo", "Matheus", "Marcos", "Paulo", "Carlos",
    "André", "Ricardo", "Eduardo", "Thiago", "Fernando", "Rodrigo",
    "Julio", "Vinicius", "Leandro", "Marcelo", "Alexandre", "Roberto",
    "William", "Daniel", "Cesar", "Luis", "Igor", "Henrique", "Jorge",
    "Adriano", "Márcio", "Sérgio", "Renato", "Edson", "Mauro", "Nelson",
    "Antonio", "Fabio", "Ronaldo", "Anderson", "Samuel", "Erick",
    "Wagner", "Hugo", "Caio", "Otavio",
]

SOBRENOMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Lima", "Pereira", "Costa",
    "Ferreira", "Rodrigues", "Almeida", "Nascimento", "Araujo", "Ribeiro",
    "Carvalho", "Gomes", "Martins", "Barbosa", "Rocha", "Dias", "Moreira",
    "Teixeira", "Cavalcanti", "Monteiro", "Cardoso", "Melo", "Castro",
    "Campos", "Vieira", "Azevedo", "Fernandes", "Barros", "Bezerra",
    "Muniz", "Xavier", "Neves", "Pires", "Mendes", "Correia", "Farias",
    "Brito", "Cruz", "Freitas", "Moura", "Lopes", "Vargas", "Nogueira",
    "Duarte", "Tavares", "Fonseca", "Miranda",
]

POSICOES = [
    ("GOL", 1, 2),
    ("ZAG", 3, 4),
    ("LAT", 5, 6),
    ("MEI", 7, 8),
    ("ATA", 9, 10),
    ("ZAG", 11, 12),
    ("MEI", 13, 14),
    ("LAT", 15, 16),
    ("ATA", 17, 18),
    ("MEI", 19, 20),
]


def _gerar_atributos(posicao: str) -> tuple:
    """Generate attributes for a given position."""
    base = random.randint(55, 92)
    variacao = random.randint(5, 25)
    
    if posicao == "GOL":
        return (base, base - variacao, base - variacao - 5, base - variacao - 10)
    elif posicao == "ZAG":
        return (base - variacao - 10, base, base - variacao, base - variacao - 15)
    elif posicao == "LAT":
        return (base - variacao - 5, base - variacao, base - variacao, base - variacao - 5)
    elif posicao == "MEI":
        return (base - variacao - 5, base - variacao - 10, base, base - variacao - 5)
    elif posicao == "ATA":
        return (base, base - variacao - 20, base - variacao - 5, base - variacao - 5)
    return (base, base, base, base)


def gerar_time(time_id: int, nome: str, cidade: str, sigla: str) -> Team:
    """Generate a team with synthetic players."""
    random.seed(f"laengine_team_{time_id}")
    jogadores = []
    player_id = time_id * 100
    
    for posicao, num_min, num_max in POSICOES:
        for i in range(num_max - num_min + 1):
            player_id += 1
            nome_completo = f"{random.choice(NOMES)} {random.choice(SOBRENOMES)}"
            ovr, atk, df, mei = _gerar_atributos(posicao)
            jogadores.append(Player(
                id=player_id,
                nome=nome_completo,
                posicao=posicao,
                overall=ovr,
                ataque=atk,
                defesa=df,
                meio=mei,
                stamina=random.randint(60, 95),
                idade=random.randint(19, 36),
                numero=num_min + i,
            ))
    
    # Calcular overall do time (média dos 11 melhores)
    sorted_jogadores = sorted(jogadores, key=lambda p: p.overall, reverse=True)
    overall_time = sum(p.overall for p in sorted_jogadores[:11]) // 11
    
    return Team(time_id, nome, cidade, sigla, jogadores, overall_time)


def gerar_times() -> list[Team]:
    """Generate all 10 Brazilian teams."""
    return [
        gerar_time(i + 1, nome, cidade, sigla)
        for i, (nome, cidade, sigla) in enumerate(TIMES_BRASILEIROS)
    ]
