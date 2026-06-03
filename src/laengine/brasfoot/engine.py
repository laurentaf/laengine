"""Match simulation engine for Brasfoot."""

import random
from typing import List, Dict
from .models import Team, Player, Match, MatchEvent, Standings


def gerar_tabela_jogos(times: List[Team]) -> List[Match]:
    """Generate round-robin schedule (turno + returno)."""
    match_id = 0
    jogos = []
    n = len(times)
    rodadas = n - 1
    metade = n // 2
    
    for volta in range(2):
        for rodada in range(rodadas):
            for i in range(metade):
                match_id += 1
                casa = (rodada + i) % (n - 1)
                fora = (n - 1 - i + rodada) % (n - 1)
                if i == 0:
                    fora = n - 1
                
                if volta == 0:
                    jogo = Match(match_id, rodada + 1, times[casa].id, times[fora].id,
                                times[casa].nome, times[fora].nome)
                else:
                    jogo = Match(match_id, rodada + 1 + rodadas, times[fora].id, times[casa].id,
                                times[fora].nome, times[casa].nome)
                jogos.append(jogo)
    
    return jogos


def simular_partida(match: Match, time_casa: Team, time_fora: Team) -> Match:
    """Simulate a full match with text commentary events."""
    match.status = "playing"
    match.events = []
    
    # Team strength from top 11 players
    casa_11 = sorted(time_casa.jogadores, key=lambda p: p.overall, reverse=True)[:11]
    fora_11 = sorted(time_fora.jogadores, key=lambda p: p.overall, reverse=True)[:11]
    
    casa_forca = sum(p.overall for p in casa_11) / 11
    fora_forca = sum(p.overall for p in fora_11) / 11
    casa_forca += 3  # home advantage
    
    gols_casa = 0
    gols_fora = 0
    
    # 90 minutes of simulation
    for minuto in range(1, 91):
        prob_evento = 0.12 + (casa_forca + fora_forca) / 2000
        
        if random.random() < prob_evento:
            # Attacking team based on strength
            if random.random() < casa_forca / (casa_forca + fora_forca):
                time_atk = time_casa
                time_def = time_fora
                atacando_casa = True
            else:
                time_atk = time_fora
                time_def = time_casa
                atacando_casa = False
            
            # Pick random attacker and defender
            atacantes = [p for p in time_atk.jogadores if p.posicao in ["ATA", "MEI", "LAT"]]
            defensores = [p for p in time_def.jogadores if p.posicao in ["ZAG", "LAT", "MEI"]]
            if not atacantes:
                atacantes = time_atk.jogadores
            if not defensores:
                defensores = time_def.jogadores
            
            atacante = random.choice(atacantes)
            defensor = random.choice(defensores)
            
            decisao = random.random()
            
            if decisao < 0.12:  # GOAL
                prob_gol = atacante.ataque / (atacante.ataque + defensor.defesa + 20)
                if random.random() < prob_gol:
                    if atacando_casa:
                        gols_casa += 1
                        desc = f"⚽ Aos {minuto}' - QUE GOL! {atacante.nome} recebe na área, gira e chuta no ângulo! GOL DO {time_casa.nome.upper()}!"
                    else:
                        gols_fora += 1
                        desc = f"⚽ Aos {minuto}' - GOLAÇO! {atacante.nome} domina no peito e bate colocado! GOL DO {time_fora.nome.upper()}!"
                    match.events.append(MatchEvent(minuto, "GOL", desc, time_atk.id, atacante.nome))
            
            elif decisao < 0.30:  # SHOT
                desc = f"⏱ Aos {minuto}' - {atacante.nome} arrisca de fora da área! A bola passa perto do travessão."
                match.events.append(MatchEvent(minuto, "CHUTE", desc, time_atk.id, atacante.nome))
            
            elif decisao < 0.45:  # FOUL
                desc = f"🟨 Aos {minuto}' - Falta dura! {defensor.nome} chega atrasado em {atacante.nome}."
                match.events.append(MatchEvent(minuto, "FALTA", desc, time_def.id, defensor.nome))
            
            elif decisao < 0.55:  # OFFSIDE
                desc = f"🚩 Aos {minuto}' - {atacante.nome} estava impedido! Lance anulado."
                match.events.append(MatchEvent(minuto, "IMPEDIMENTO", desc, time_atk.id, atacante.nome))
            
            elif decisao < 0.70:  # CORNER
                desc = f"⏱ Aos {minuto}' - Escanteio para {time_atk.nome}. {atacante.nome} cobra fechado, mas a zaga afasta."
                match.events.append(MatchEvent(minuto, "ESCANTEIO", desc, time_atk.id, atacante.nome))
            
            elif decisao < 0.82:  # SAVE
                goleiros = [p for p in time_def.jogadores if p.posicao == "GOL"]
                if goleiros:
                    desc = f"🧤 Aos {minuto}' - {goleiros[0].nome} faz uma defesa espetacular! Evita o gol com a ponta dos dedos!"
                    match.events.append(MatchEvent(minuto, "DEFESA", desc, time_def.id, goleiros[0].nome))
            
            elif decisao < 0.94:  # CROSS / MISS
                desc = f"⏱ Aos {minuto}' - {atacante.nome} cruza da esquerda, mas ninguém consegue desviar."
                match.events.append(MatchEvent(minuto, "JOGADA", desc, time_atk.id, atacante.nome))
            
            elif decisao < 0.98 and random.random() < 0.3:  # YELLOW CARD
                desc = f"🟨 Cartão amarelo! {defensor.nome} para o contra-ataque com falta tática."
                match.events.append(MatchEvent(minuto, "CARTAO", desc, time_def.id, defensor.nome))
    
    # Stoppage time drama
    if gols_casa + gols_fora < 3 and random.random() < 0.25:
        minuto = 90 + random.randint(1, 6)
        if random.random() < 0.5:
            gols_casa += 1
            desc = f"⚽ Aos {minuto}' - GOOOOOOL! Nos acréscimos! A torcida vai à loucura! GOL DO {time_casa.nome}!".upper()
        else:
            gols_fora += 1
            desc = f"⚽ Aos {minuto}' - GOOOOOOL! {time_fora.nome} vira nos acréscimos! É de matar o coração!".upper()
        match.events.append(MatchEvent(minuto, "GOL", desc, time_casa.id if gols_casa > gols_fora else time_fora.id))
    
    match.gols_casa = gols_casa
    match.gols_fora = gols_fora
    match.status = "finished"
    
    match.events.append(MatchEvent(90, "FIM",
        f"🏁 FIM DE JOGO! {time_casa.nome} {gols_casa} x {gols_fora} {time_fora.nome}", 0))
    
    return match


def calcular_tabela(times: List[Team], partidas: List[Match]) -> List[Standings]:
    """Calculate league standings from match results."""
    tabela: Dict[int, Standings] = {}
    
    for t in times:
        tabela[t.id] = Standings(t.id, t.nome, t.sigla)
    
    for partida in partidas:
        if partida.status != "finished":
            continue
        
        casa = tabela[partida.time_casa_id]
        fora = tabela[partida.time_fora_id]
        
        casa.j += 1
        fora.j += 1
        casa.gp += partida.gols_casa
        casa.gc += partida.gols_fora
        fora.gp += partida.gols_fora
        fora.gc += partida.gols_casa
        
        if partida.gols_casa > partida.gols_fora:
            casa.v += 1
            casa.pts += 3
            fora.d += 1
        elif partida.gols_casa < partida.gols_fora:
            fora.v += 1
            fora.pts += 3
            casa.d += 1
        else:
            casa.e += 1
            fora.e += 1
            casa.pts += 1
            fora.pts += 1
        
        casa.sg = casa.gp - casa.gc
        fora.sg = fora.gp - fora.gc
    
    return sorted(tabela.values(), key=lambda s: (s.pts, s.v, s.sg, s.gp), reverse=True)
