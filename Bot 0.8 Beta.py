import os
from threading import Thread
from flask import Flask
import datetime
import json
import random
import discord
from discord.ui import View, Select, Button
import copy
from discord.ext import commands

app = Flask('')

@app.route('/')
def home():
    return "O bot está online!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# === ADICIONE AQUI: GERENCIAMENTO DE DADOS E GACHA POOL ===
DATA_FILE = "jogadores_data.json"

def carregar_dados():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_dados(dados):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

JOGADORES = carregar_dados()

def obter_perfil(user_id):
    user_id_str = str(user_id)
    if user_id_str not in JOGADORES:
        JOGADORES[user_id_str] = {
            "moedas": 100,
            "inventario": ["Tohka Yatogami", "Ken Kaneki", "FIREFLY / SAM"]
        }
        salvar_dados(JOGADORES)
    return JOGADORES[user_id_str]
LIMITE_PITY = 50

def processar_gacha(user_id):
    perfil = obter_perfil(user_id)
    
    if "pity" not in perfil:
        perfil["pity"] = 0
        
    perfil["pity"] += 1
    pity_atual = perfil["pity"]
    
    if pity_atual >= LIMITE_PITY:
        perfil["pity"] = 0
        salvar_dados(JOGADORES)
        raridade_sorteada = "5_estrelas"
        personagem = choice(GACHA_POOL[raridade_sorteada])
        return personagem, raridade_sorteada, "Pity Ativado!"
    
    raridade_sorteada = sortear_raridade_normal() 
    
    if raridade_sorteada == "5_estrelas":
        perfil["pity"] = 0
        
    salvar_dados(JOGADORES)
    personagem = choice(GACHA_POOL[raridade_sorteada])
    return personagem, raridade_sorteada, f"Pity: {perfil['pity']}/{LIMITE_PITY}"

import random

def sortear_personagem():
    # Agrupa os personagens do dicionário principal PERSONAGENS por raridade
    pool_por_raridade = {
        "5_estrelas": [],
        "4_estrelas": [],
        "3_estrelas": []
    }
    
    # Mapeia as tuas raridades para o sistema de estrelas do Embed
    mapa_raridade = {
        "Lendaria": "5_estrelas",
        "Epica": "4_estrelas",
        "Rara": "4_estrelas",
        "Comum": "3_estrelas"
    }
    
    for nome, dados in PERSONAGENS.items():
        raridade_nome = dados.get("raridade", "Comum")
        categoria = mapa_raridade.get(raridade_nome, "3_estrelas")
        emoji = dados.get("emoji", "🎭")
        
        pool_por_raridade[categoria].append({
            "nome": nome,
            "emoji": emoji
        })
            
    raridades = ["3_estrelas", "4_estrelas", "5_estrelas"]
    pesos = [60, 35, 5]  # Percentagens (60% Comum, 35% Raro/Épico, 5% Lendário)
    
    raridades_validas = [r for r in raridades if pool_por_raridade[r]]
    pesos_validos = [pesos[raridades.index(r)] for r in raridades_validas]
    
    if not raridades_validas:
        return None, None
        
    raridade_sorteada = random.choices(raridades_validas, weights=pesos_validos, k=1)[0]
    personagem_sorteado = random.choice(pool_por_raridade[raridade_sorteada])
    
    return personagem_sorteado, raridade_sorteada


PERSONAGENS = {
    "Tohka Yatogami": {
        "anime": "Date A Live",
        "classe": "Saber",
        "raridade": "Rara",
        "emoji": "👑",
        "hp": 110,
        "mana": 40,
        "imagem_padrao": "https://cdn.imgchest.com/files/5e6e71b85a53.gif",
        "ataque_normal": {
            "nome": "Corte Espada Astral",
            "dano": 16,
            "descricao": "Tohka desfere um golpe veloz com sua espada espiritual.",
            "gif": "https://cdn.imgchest.com/files/63bd7b6baf58.gif"
        },
        "especial": {
            "nome": "⚔️ Sandalphon (Corte Final)",
            "dano": 32,
            "custo_mana": 20,
            "descricao": "Invoca o trono e desfere um golpe devastador.",
            "gif": "https://cdn.imgchest.com/files/17ed046e4e42.gif"
        },
        "defesa_normal": {
            "nome": "Barreira Astral",
            "reducao_dano": 0.5,
            "descricao": "Tohka ergue uma barreira de mana.",
            "imagem": "https://cdn.imgchest.com/files/a044451a35a3.gif"
    }},
    "Ken Kaneki": {
        "anime": "Tokyo Ghoul",
        "classe": "Berserker",
        "raridade": "Rara",
        "emoji": "☕",
        "hp": 95,
        "mana": 50,
        "imagem_padrao": "https://cdn.imgchest.com/files/832312a9603b.gif",
        "ataque_normal": {
            "nome": "Investida de Ghoul",
            "dano": 18,
            "descricao": "Kaneki avança rapidamente com as garras.",
            "gif": "https://cdn.imgchest.com/files/74638a34bf9e.gif"
        },
        "especial": {
            "nome": "🐙 Liberação de Kagune",
            "dano": 28,
            "custo_mana": 25,
            "descricao": "Libera seus tentáculos kagune com força total.",
            "gif": "https://cdn.imgchest.com/files/e3b092a368d9.gif"
        },
        "defesa_normal": {
            "nome": "Reflexo Ghoul",
            "reducao_dano": 0.5,
            "descricao": "Usa sua agilidade para amortecer o golpe.",
            "imagem": "https://cdn.imgchest.com/files/19d84e56d333.gif"
        }
    },
    "FIREFLY / SAM": {
        "anime": "Honkai: Star Rail",
         "classe": "Rider",
         "raridade": "Lendaria",
         "emoji": "🔥",
        "forma": "normal",  
        "hp": 120,
        "hp_max": 120,
        "mana": 45,
        "imagem_padrao": "https://cdn.imgchest.com/files/ae04c3cc283d.gif",
        "ataque_normal": {
            "nome": "Ordem Estelar (Ataque)",
            "dano": 15,
            "descricao": "Firefly desfere um golpe ágil com a lâmina de energia.",
            "gif": "https://cdn.imgchest.com/files/fd6fe2ef8713.gif"
        },
        "especial": {
            "nome": "Incandescência Completa (Transformação)",
            "dano": 25,
            "custo_mana": 20,
            "efeito": "transformar_sam",
            "descricao": "Firefly liberta o seu verdadeiro poder, vestindo a armadura SAM!",
            "gif": "https://cdn.imgchest.com/files/a65144462508.gif"
        },
        "defesa_normal": {
            "nome": "Evasão Tática",
            "reducao_dano": 0.5, 
            "descricao": "Firefly recua rapidamente da investida inimiga.",
            "imagem": "https://cdn.imgchest.com/files/f41d858423eb.gif"
        },
        # Modos SAM
        "ataque_sam": {
            "nome": "Bombardeio Férreo (Ataque SAM)",
            "dano": 35,
            "descricao": "SAM despenca dos céus envolto em chamas verdes esmagadoras.",
            "gif": "https://cdn.imgchest.com/files/a07562dec10a.gif"
        },
        "especial_sam": {
            "nome": "Sobrecarga de Retorno (Destransformação)",
            "dano": 40,
            "custo_mana": 25,
            "efeito": "transformar_normal",
            "descricao": "SAM descarrega um feixe massivo de chamas antes de voltar à base.",
            "gif": "https://cdn.imgchest.com/files/5125e6e1b780.gif"
        },
        "defesa_sam": {
            "nome": "Campo de Força / Barreira Kael",
            "reducao_dano": 0.7, 
            "descricao": "SAM projeta um escudo de energia térmica frontal.",
            "imagem": "https://cdn.imgchest.com/files/57e44b73bbbe.gif"
        }
},
   "Sasuke Uchiha": {
   "classe": "Archer",
   "raridade": "Rara",
   "emoji": "⚡",
        "anime": "Naruto",
        "hp": 100,
        "mana": 50,
        "imagem_padrao": "https://cdn.imgchest.com/files/daec3a69715a.gif",
        "ataque_normal": {
            "nome": "Estilo Fogo: Jutsu Bola de Fogo",
            "dano": 18,
            "descricao": "Sasuke lança uma esfera de fogo devastadora contra o oponente.",
            "gif": "https://cdn.imgchest.com/files/ed473b565a65.gif"
        },
        "especial": {
            "nome": " Chidori (Mil Pássaros)",
            "dano": 32,
            "custo_mana": 25,
            "descricao": "Concentra chakra de raio na mão e avança em alta velocidade.",
            "gif": "https://cdn.imgchest.com/files/0943da111e8e.gif"
        },
        "defesa_normal": {
            "nome": "Previsão do Sharingan",
            "reducao_dano": 0.5,
            "descricao": "Usa o Sharingan para prever os movimentos e esquivar do impacto.",
            "imagem": "https://cdn.imgchest.com/files/e82c844b2168.gif"
        },
},
    "White Queen": {
        "anime": "Date A Bullet",
        "classe": "Caster",
        "raridade": "Epica",
        "emoji": "♟️",
        "hp": 140,
        "mana": 50,
        "imagem_padrao": "https://cdn.imgchest.com/files/a09a20995cf4.gif",
        "ataque_normal": {
            "nome": "Corte de Lugh 🗡️",
            "dano": 17,
            "descricao": "White Queen desfere um golpe veloz e gélido com a sua espada.",
            "gif": "https://cdn.imgchest.com/files/c421a3755412.gif"
        },
        "especial": {
            "nome": "👑 Xeque-Mate (Decreto Absoluto)",
            "dano": 38,
            "custo_mana": 20,
            "descricao": "Invoca o poder do tabuleiro para aplicar um golpe devastador que esmaga o inimigo.",
            "gif": "https://cdn.imgchest.com/files/0d255a84ea3a.gif"
        },
        "defesa_normal": {
            "nome": "Barreira do Tabuleiro",
            "reducao_dano": 0.5,
            "descricao": "White Queen se protege com o poder de suas peças.",
            "imagem": "https://cdn.imgchest.com/files/b628f2923d42.gif"
        },
        "mecanica_unica": "xeque_mate"
    },
    "Kirara": {
        "anime": "Jujutsu Kaisen",
        "classe": "Estrategista",
        "raridade": "Epica",
        "emoji": "⭐",
        "hp": 120,
        "mana": 50,
        "imagem_padrao": "https://cdn.imgchest.com/files/88b405a50359.gif",
        "ataque_normal": {
            "nome": "Chuva de Moedas",
            "dano": 20,
            "descricao": "Kirara atira moedas como balas contra o oponente.",
            "gif": "https://cdn.imgchest.com/files/93aa2b06313e.mp4"
        },
        "especial": {
            "nome": "Repulsão Estelar",
            "dano": 45,
            "custo_mana": 20,
            "descricao": "Repeli tudo em cima do oponente.",
            "gif": "https://cdn.imgchest.com/files/0f672887d950.mp43"
        },
        "defesa_normal": {
            "nome": "Alinhamento das 5 Estrelas",
            "reducao_dano": 0.6,
            "descricao": "Junta as 5 estrelas para criar uma defesa absoluta.",
            "imagem": "https://cdn.imgchest.com/files/3e0ad0d472cc.gif"
        }
    },
    "Maomao": {
        "anime": "The Apothecary Diaries",
        "classe": "Caster",
        "raridade": "Lendaria",
        "emoji": "🧪",
        "hp": 130,
        "mana": 60,
        "imagem_padrao": "https://cdn.imgchest.com/files/fb9f99ad5dda.gif",
        "ataque_normal": {
            "nome": "Ofensa Ácida",
            "dano": 15,
            "descricao": "Maomao ofende o oponente com duras verdades, causando pouco dano direto, mas reduzindo a defesa dele.",
            "gif": "https://cdn.imgchest.com/files/f858bd5d68fa.mp4"
        },
        "especial": {
            "nome": "Envenenamento",
            "dano": 35,
            "custo_mana": 25,
            "descricao": "Usa venenos potentes: causa dano a si mesma, mas anula totalmente a defesa do inimigo por 1 a 2 rounds.",
            "gif": "https://cdn.imgchest.com/files/45606d6bbd42.gif"
        },
        "defesa_normal": {
            "nome": "Experimento Medicinal",
            "reducao_dano": 0.7,
            "descricao": "Testa venenos em si mesma: 50% de chance de mitigar 70% do dano (com auto-envenenamento), 30% de falha e 20% de imunidade total por 2 turnos.",
            "gif_sucesso": "https://cdn.imgchest.com/files/a56c92b9b3de.gif",
            "gif_falha": "https://cdn.imgchest.com/files/601987286d86.mp4"
        },
        "mecanica_unica": "envenenamento_maomao"
    }
}

def adicionar_exp(personagem_dados, qtd_exp):
    # Se já estiver no nível máximo (100), não acumula mais
    if personagem_dados.get("nivel", 1) >= 100:
        return False, 100
    
    personagem_dados["exp"] += qtd_exp
    subiu_nivel = False
    
    # Cada nível exige mais EXP (ex: nível atual * 100)
    exp_necessaria = personagem_dados["nivel"] * 100
    
    while personagem_dados["exp"] >= exp_necessaria and personagem_dados["nivel"] < 100:
        personagem_dados["exp"] -= exp_necessaria
        personagem_dados["nivel"] += 1
        subiu_nivel = True
        exp_necessaria = personagem_dados["nivel"] * 100
        
    # Trava no nível 100 se atingir o teto
    if personagem_dados["nivel"] >= 100:
        personagem_dados["nivel"] = 100
        personagem_dados["exp"] = 0
        
    return subiu_nivel, personagem_dados["nivel"]


import discord
from discord.ui import View, Select

class MenuPrincipal(View):
    def __init__(self):
        super().__init__(timeout=180) # O menu desativa após 3 minutos sem uso

    @discord.ui.select(
        placeholder="📜 Escolha uma opção do menu...",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="Fases de Farm",
                description="Veja as fases disponíveis para ganhar moedas",
                emoji="⚔️",
                value="fases"
            ),
            discord.SelectOption(
                label="Comandos de Perfil",
                description="Ver coleção, saldo e personagens",
                emoji="👤",
                value="perfil"
            ),
            discord.SelectOption(
                label="Sistema de Gacha",
                description="Instruções e como rodar o gacha",
                emoji="🎰",
                value="gacha"
            )
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: Select):
        opcao = select.values[0]

        if opcao == "fases":
            # Monta o texto das fases usando o teu dicionário FASE_MOEDAS
            texto = "⚔️ **FASE DE FARM DE MOEDAS** ⚔️\n\n"
            for id_fase, dados in FASE_MOEDAS.items():
                texto += f"**Fase {id_fase}:** {dados['nome']}\n"
                texto += f"👾 *Inimigo:* {dados['inimigo']} | 🪙 *Recompensa:* {dados['moedas']} moedas\n"
                texto += "-----------------------------------\n"
            
            await interaction.response.send_message(texto, ephemeral=True)

        elif opcao == "perfil":
            texto = (
                "👤 **COMANDOS DE PERFIL E COLEÇÃO**\n\n"
                "• `!colecao` — Veja os seus personagens obtidos.\n"
                "• `!personagens` — Lista completa de personagens do jogo.\n"
                "• `!ver [nome]` — Detalhes, status e raridade de um personagem."
            )
            await interaction.response.send_message(texto, ephemeral=True)

        elif opcao == "gacha":
            texto = (
                "🎰 **SISTEMA DE GACHA**\n\n"
                "• Use `!gacha` para sortear um personagem aleatório.\n"
                "• **Custo:** 50 moedas por tentativa.\n"
                "• Se tirar um personagem repetido, recebe **25 moedas** de reembolso!"
            )
            await interaction.response.send_message(texto, ephemeral=True)


class InstanciaPersonagem:
    def __init__(self, nome_p: str):
        self.nome_chave = nome_p
        self.dados = copy.deepcopy(PERSONAGENS[nome_p])
        self.nome = self.dados.get("nome", nome_p)
        self.anime = self.dados["anime"]
        self.classe = self.dados.get("classe", "Guerreiro")
        self.hp_max = self.dados["hp"]
        self.hp = self.dados["hp"]
        self.mana_max = self.dados["mana"] 
        self.mana = self.dados["mana"]
        self.defendendo = False
        self.forma = self.dados.get("forma", "normal")
        self.imagem_padrao = self.dados.get("imagem_padrao", "")

    def esta_vivo(self):
        return self.hp > 0

    def obter_ataque(self):
        if self.nome_chave == "FIREFLY / SAM" and self.forma == "sam":
            return self.dados["ataque_sam"]
        return self.dados["ataque_normal"]

    def obter_especial(self):
        if self.nome_chave == "FIREFLY / SAM" and self.forma == "sam":
            return self.dados["especial_sam"]
        return self.dados["especial"]

    def obter_defesa(self):
        if self.nome_chave == "FIREFLY / SAM" and self.forma == "sam":
            return self.dados["defesa_sam"]
        return self.dados["defesa_normal"]

class Lutador:
    def __init__(self, usuario: discord.Member, nomes_personagens: list):
        self.usuario = usuario
        self.nome_user = usuario.display_name
        self.time = []
        
        for nome in nomes_personagens:
            p_obj = Personagem(nome)
            self.time.append(p_obj)
            
        self.indice_ativo = 0

    @property
    def ativo(self):
        return self.time[self.indice_ativo]

    def tem_vivos(self):
        return any(p.esta_vivo() for p in self.time)

    def proximo_vivo_automatico(self):
        for i, p in enumerate(self.time):
            if p.esta_vivo():
                self.indice_ativo = i
                return True
        return False

class TrocarSelect(discord.ui.Select):
    def __init__(self, batalha_view, lutador):
        self.batalha_view = batalha_view
        self.lutador = lutador
        
        options = []
        for idx, p in enumerate(lutador.time):
            if p.esta_vivo() and idx != lutador.indice_ativo:
                extra = " (SAM)" if p.nome_chave == "FIREFLY / SAM" and p.forma == "sam" else ""
                options.append(discord.SelectOption(
                    label=f"{p.nome}{extra}",
                    description=f"HP: {p.hp}/{p.hp_max} | Mana: {p.mana}",
                    value=str(idx)
                ))
        
        super().__init__(placeholder="Escolha quem vai entrar em campo...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.lutador.usuario:
            return await interaction.response.send_message("Não é o seu turno!", ephemeral=True)
        
        novo_idx = int(self.values[0])
        self.lutador.indice_ativo = novo_idx
        personagem_novo = self.lutador.ativo
        
        await interaction.response.defer()
        log = f"🔄 **{self.lutador.nome_user}** substituiu o personagem e enviou **{personagem_novo.nome}** para o combate!"
        await self.batalha_view.proximo_turno(interaction, log, imagem_url=personagem_novo.imagem_padrao)

class TrocarView(discord.ui.View):
    def __init__(self, batalha_view, lutador):
        super().__init__(timeout=30)
        self.add_item(TrocarSelect(batalha_view, lutador))

class BatalhaView(discord.ui.View):
    def __init__(self, p1: Lutador, p2: Lutador):
        super().__init__(timeout=180)
        self.p1 = p1
        self.p2 = p2
        self.turno_atual = p1

    def oponente(self, lutador):
        return self.p2 if lutador == self.p1 else self.p1

    def atualizar_embed(self, log="A batalha 3v3 começou!", imagem_url=None):
        embed = discord.Embed(
            title=f"⚔️ Batalha 3v3: {self.p1.nome_user} vs {self.p2.nome_user}",
            color=discord.Color.purple()
        )
        
        # Status P1
        status_p1 = ""
        for idx, p in enumerate(self.p1.time):
            marcador = "▶ " if idx == self.p1.indice_ativo else "   "
            status = f"❤️ {p.hp}/{p.hp_max}" if p.esta_vivo() else "💀 Derrotado"
            extra = " [SAM]" if p.nome_chave == "FIREFLY / SAM" and p.forma == "sam" else ""
            status_p1 += f"{marcador}**{p.nome}{extra}**: {status}\n"

        # Status P2
        status_p2 = ""
        for idx, p in enumerate(self.p2.time):
            marcador = "▶ " if idx == self.p2.indice_ativo else "   "
            status = f"❤️ {p.hp}/{p.hp_max}" if p.esta_vivo() else "💀 Derrotado"
            extra = " [SAM]" if p.nome_chave == "FIREFLY / SAM" and p.forma == "sam" else ""
            status_p2 += f"{marcador}**{p.nome}{extra}**: {status}\n"

        embed.add_field(name=f"🛡️ Time de {self.p1.nome_user}", value=status_p1, inline=True)
        embed.add_field(name=f"⚔️ Time de {self.p2.nome_user}", value=status_p2, inline=True)
        embed.add_field(name="📜 Ação Recente", value=log, inline=False)
        embed.set_footer(text=f"Turno de: {self.turno_atual.nome_user} (Ativo: {self.turno_atual.ativo.nome})")

        # Exibe a imagem/GIF da ação realizada se for fornecida
        if imagem_url and imagem_url.startswith("http"):
            embed.set_image(url=imagem_url)

        return embed

    async def validar(self, interaction):
        if interaction.user != self.turno_atual.usuario:
            await interaction.response.send_message("Não é a sua vez!", ephemeral=True)
            return False
        return True

    async def proximo_turno(self, interaction, log, imagem_url=None):
        alvo = self.oponente(self.turno_atual)
        
        if not alvo.ativo.esta_vivo():
            if not alvo.tem_vivos():
                embed = self.atualizar_embed(log=f"🏆 **{self.turno_atual.nome_user}** venceu a batalha!", imagem_url=imagem_url)
                self.stop()
                await interaction.message.edit(embed=embed, view=None)
                return
            else:
                alvo.proximo_vivo_automatico()
                log += f"\n⚠️ O personagem anterior caiu! **{alvo.ativo.nome}** entrou em campo por {alvo.nome_user}!"

        self.turno_atual = alvo
        self.turno_atual.ativo.defendendo = False
        await interaction.message.edit(embed=self.atualizar_embed(log=log, imagem_url=imagem_url), view=self)

    @discord.ui.button(label="Atacar", style=discord.ButtonStyle.danger)
    async def atacar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.validar(interaction): return
        await interaction.response.defer()
        
        atacante = self.turno_atual.ativo
        defensor = self.oponente(self.turno_atual).ativo
        acao = atacante.obter_ataque()
        dano_base = acao["dano"]
        
        if defensor.defendendo:
            reducao = defensor.obter_defesa()["reducao_dano"]
            dano = max(1, int(dano_base * (1 - reducao)))
        else:
            dano = dano_base + random.randint(-2, 2)
            
        defensor.hp = max(0, defensor.hp - dano)
        gif_acao = acao.get("gif", "")
        
        await self.proximo_turno(interaction, f"⚔️ **{atacante.nome}** usou *{acao['nome']}* em **{defensor.nome}**, causando {dano} de dano!", imagem_url=gif_acao)

    @discord.ui.button(label="Habilidade", style=discord.ButtonStyle.success)
    async def habilidade(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.validar(interaction): return
        
        atacante = self.turno_atual.ativo
        acao = atacante.obter_especial()
        custo = acao["custo_mana"]

        if atacante.mana < custo:
            await interaction.response.send_message(f"Mana insuficiente! Custo necessário: {custo}.", ephemeral=True)
            return

        await interaction.response.defer()
        defensor = self.oponente(self.turno_atual).ativo

        atacante.mana -= custo
        dano = acao["dano"] + random.randint(-3, 3)
        defensor.hp = max(0, defensor.hp - dano)
        
        efeito_texto = ""
        if "efeito" in acao:
            if acao["efeito"] == "transformar_sam":
                atacante.forma = "sam"
                efeito_texto = " 🔥 **Firefly vestiu a armadura SAM!**"
            elif acao["efeito"] == "transformar_normal":
                atacante.forma = "normal"
                efeito_texto = " ✨ **SAM desativou a armadura, retornando à forma base!**"

        gif_acao = acao.get("gif", "")
        await self.proximo_turno(interaction, f"💥 **{atacante.nome}** usou **{acao['nome']}** e causou {dano} de dano!{efeito_texto}", imagem_url=gif_acao)

    @discord.ui.button(label="Defender", style=discord.ButtonStyle.primary)
    async def defender(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.validar(interaction): return
        await interaction.response.defer()
        
        self.turno_atual.ativo.defendendo = True
        defesa_info = self.turno_atual.ativo.obter_defesa()
        img_defesa = defesa_info.get("imagem", "")
        
        await self.proximo_turno(interaction, f"🛡️ **{self.turno_atual.ativo.nome}** usou *{defesa_info['nome']}* e entrou em postura defensiva!", imagem_url=img_defesa)

    @discord.ui.button(label="Trocar", style=discord.ButtonStyle.secondary, emoji="🔄")
    async def trocar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.validar(interaction): return
        
        lutador = self.turno_atual
        view_troca = TrocarView(self, lutador)
        
        if not view_troca.children[0].options:
            return await interaction.response.send_message("Você não tem outros personagens vivos para trocar!", ephemeral=True)
        
        await interaction.response.send_message("Escolha qual personagem do seu time vai entrar em campo:", view=view_troca, ephemeral=True)

    @discord.ui.button(label="Desistir", style=discord.ButtonStyle.secondary)
    async def desistir(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.p1.usuario and interaction.user != self.p2.usuario:
            return await interaction.response.send_message("Você não está participando deste duelo!", ephemeral=True)
        
        await interaction.response.defer()
        desistente = interaction.user
        vencedor = self.p2 if desistente == self.p1.usuario else self.p1
        perdedor_nome = self.p1.nome_user if desistente == self.p1.usuario else self.p2.nome_user
        
        embed = self.atualizar_embed(log=f"🏳️ **{perdedor_nome}** desistiu. **{vencedor.nome_user}** venceu por W.O.!")
        for child in self.children:
            child.disabled = True
        self.stop()
        
        await interaction.message.edit(embed=embed, view=self)
        
class SelecaoTimeP1(discord.ui.View):
    def __init__(self, ctx, oponente):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.oponente = oponente

        user_id = str(ctx.author.id)
        perfil = obter_perfil(user_id)
        inventario = perfil.get("inventario", [])

        options = []
        for nome in inventario:
            if nome in PERSONAGENS:
                dados = PERSONAGENS[nome]
                # Tenta procurar o emoji nas chaves corretas do dicionário
                emoji_pers = dados.get("emoji") or dados.get("emoji_pers") or "⚔️"
                options.append(
                    discord.SelectOption(
                        label=nome,
                        description=f"{dados.get('universo', 'Outro')} | {dados.get('classe', 'Guerreiro')}",
                        emoji=emoji_pers
                    )
                )
               
        # Caso o jogador tenha menos de 3 personagens, ajusta o limite para não dar erro
        max_escolhas = min(3, len(options)) if options else 1

        self.select_item = discord.ui.Select(
            placeholder="[P1] Escolha os 3 personagens do seu time...",
            min_values=max_escolhas,
            max_values=3 if len(options) >= 3 else max_escolhas,
            options=options if options else [discord.SelectOption(label="Sem personagens", value="vazio")]
        )
        self.select_item.callback = self.select_callback
        self.add_item(self.select_item)

    async def select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("❌ Esta seleção pertence ao criador do duelo!", ephemeral=True)

        p1_time = self.select_item.values
        
        view_p2 = SelecaoTimeP2(self.ctx, self.oponente, p1_time)
        embed = discord.Embed(
            title=f"⚔️ Duelo 3v3: {self.ctx.author.name} vs {self.oponente.name}",
            description=f"**{self.ctx.author.name}** já escolheu o time!\n\n{self.oponente.mention}, escolha os 3 personagens para o seu time no menu abaixo:",
            color=discord.Color.blue()
        )
        
        await interaction.response.edit_message(embed=embed, view=view_p2)
        self.stop()
        
class SelecaoTimeP2(discord.ui.View):
    def __init__(self, ctx, oponente, p1_time):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.oponente = oponente
        self.p1_time = p1_time

        options = [
            discord.SelectOption(label="Tohka Yatogami", description="Date A Live | Ataques pesados", emoji="👑"),
            discord.SelectOption(label="Ken Kaneki", description="Tokyo Ghoul | Velocidade e Kagune", emoji="☕"),
            discord.SelectOption(label="FIREFLY / SAM", description="Honkai: Star Rail | Transformação", emoji="🔥")
        ]

        # Criamos o select utilizando herança/instanciação correta
        self.select_item = discord.ui.Select(
            placeholder="[P2] Escolha os 3 personagens do seu time...",
            min_values=3,
            max_values=3,
            options=options
        )
        self.select_item.callback = self.select_callback
        self.add_item(self.select_item)

    async def select_callback(self, interaction: discord.Interaction):
        # 🔒 Validação segura comparando os IDs do usuário
        if interaction.user.id != self.oponente.id:
            return await interaction.response.send_message("❌ Esta seleção pertence ao oponente!", ephemeral=True)

        p2_time = self.select_item.values
        p1 = Lutador(self.ctx.author, self.p1_time)
        p2 = Lutador(self.oponente, p2_time)

        batalha_view = BatalhaView(p1, p2)
        embed = batalha_view.atualizar_embed(log="A batalha 3v3 começou!")
        
        await interaction.response.edit_message(embed=embed, view=batalha_view)
        self.stop()
        super().__init__(timeout=60)
        self.ctx = ctx
        self.oponente = oponente

        user_id = str(ctx.author.id)
        perfil = obter_perfil(user_id)
        inventario_jogador = perfil.get("inventario", [])

        options = []
        for nome_perso in inventario_jogador:
            if nome_perso in PERSONAGENS:
                dados = PERSONAGENS[nome_perso]
                anime = dados.get("anime", "Desconhecido")
                
                emoji_map = {
                    "Tohka Yatogami": "👑",
                    "Ken Kaneki": "☕",
                    "FIREFLY / SAM": "🔥",
                    "Sasuke Uchiha": "⚡",
                    "White Queen": "👑"
                }
                emoji = emoji_map.get(nome_perso, "⚔️")
                
                options.append(
                    discord.SelectOption(
                        label=nome_perso,
                        description=f"{anime} | Personagem de Batalha",
                        emoji=emoji
                    )
                )

        if not options:
            options.append(discord.SelectOption(label="Nenhum personagem disponível", description="Invoca personagens primeiro!"))

        self.select = discord.ui.Select(
            placeholder="[P1] Escolha os 3 personagens do seu time...",
            min_values=1,
            max_values=min(3, len(options)),
            options=options
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("Esta seleção pertence ao oponente!", ephemeral=True)
            return

        p1_time = self.select.values
        view_p2 = SelecaoTimeP2(self.ctx, self.oponente, p1_time)
        embed_p2 = discord.Embed(
            title=f"⚔️ Duelo: {self.ctx.author.name} vs {self.oponente.name}",
            description=f"{self.oponente.mention}, escolha os 3 personagens para o seu time no menu abaixo:",
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(content="", embed=embed_p2, view=view_p2)


class SelecaoTimeP2(discord.ui.View):
    def __init__(self, ctx, oponente, p1_time):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.oponente = oponente
        self.p1_time = p1_time

        user_id = str(oponente.id)
        perfil = obter_perfil(user_id)
        inventario_jogador = perfil.get("inventario", [])

        options = []
        for nome_perso in inventario_jogador:
            if nome_perso in PERSONAGENS:
                dados = PERSONAGENS[nome_perso]
                anime = dados.get("anime", "Desconhecido")
                
                emoji_map = {
                    "Tohka Yatogami": "👑",
                    "Ken Kaneki": "☕",
                    "FIREFLY / SAM": "🔥",
                    "Sasuke Uchiha": "⚡",
                    "White Queen": "👑"
                }
                emoji = emoji_map.get(nome_perso, "⚔️")
                
                options.append(
                    discord.SelectOption(
                        label=nome_perso,
                        description=f"{anime} | Personagem de Batalha",
                        emoji=emoji
                    )
                )

        if not options:
            options.append(discord.SelectOption(label="Nenhum personagem disponível", description="Invoca personagens primeiro!"))

        self.select = discord.ui.Select(
            placeholder="[P2] Escolha os 3 personagens do seu time...",
            min_values=1,
            max_values=min(3, len(options)),
            options=options
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: discord.Interaction):
        if interaction.user != self.oponente:
            await interaction.response.send_message("Esta seleção pertence ao oponente!", ephemeral=True)
            return

        p2_time = self.select.values
        
        p1 = Lutador(self.ctx.author, self.p1_time)
        p2 = Lutador(self.oponente, p2_time)
        
        batalha_view = BatalhaView(p1, p2)
        embed = batalha_view.atualizar_embed(log=f"A batalha 3v3 entre **{p1.nome_user}** e **{p2.nome_user}** começou!", imagem_url=p1.ativo.imagem_padrao)
        
        await interaction.response.edit_message(content="", embed=embed, view=batalha_view)

class SelecaoTimeP2(discord.ui.View):
    def __init__(self, ctx, oponente, p1_time):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.oponente = oponente
        self.p1_time = p1_time

        user_id = str(oponente.id)
        perfil = obter_perfil(user_id)
        inventario = perfil.get("inventario", [])

        options = []
        for nome in inventario:
            if nome in PERSONAGENS:
                dados = PERSONAGENS[nome]
                emoji_pers = dados.get("emoji") or dados.get("emoji_pers") or "⚔️"
                options.append(
                    discord.SelectOption(
                        label=nome,
                        description=f"{dados.get('universo', 'Outro')} | {dados.get('classe', 'Guerreiro')}",
                        emoji=emoji_pers
                    )
                )

        total_chars = len(options)
        max_escolhas = min(4, total_chars) if total_chars > 0 else 1

        self.select_item = discord.ui.Select(
            placeholder="[P2] Escolha os 4 personagens do seu time...",
            min_values=max_escolhas,
            max_values=4 if total_chars >= 4 else max_escolhas,
            options=options if options else [discord.SelectOption(label="Sem personagens", value="vazio")]
        )
        self.select_item.callback = self.select_callback
        self.add_item(self.select_item)

    async def select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.oponente.id:
            return await interaction.response.send_message("❌ Esta seleção pertence ao oponente convidado!", ephemeral=True)

        p2_time = self.select_item.values
        
class BatalhaView(discord.ui.View):
    def __init__(self, ctx, p1, p2, p1_time, p2_time, hp_p1, hp_p2, mana_p1, mana_p2):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.p1 = p1
        self.p2 = p2
        self.p1_time = p1_time
        self.p2_time = p2_time
        self.hp_p1 = hp_p1
        self.hp_p2 = hp_p2
        self.mana_p1 = mana_p1
        self.mana_p2 = mana_p2
        self.turno = p1  # Começa o P1
        
        self.indice_p1 = 0
        self.indice_p2 = 0

    @discord.ui.button(label="Ataque Normal", style=discord.ButtonStyle.primary, emoji="⚔️")
    async def ataque_normal(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.turno:
            return await interaction.response.send_message("❌ Não é o teu turno!", ephemeral=True)

        atacante = self.p1 if self.turno == self.p1 else self.p2
        time_atacante = self.p1_time if self.turno == self.p1 else self.p2_time
        indice_atual = self.indice_p1 if self.turno == self.p1 else self.indice_p2
        
        pers_nome = time_atacante[indice_atual]
        dados = PERSONAGENS.get(pers_nome, {})
        
        # Usa o gif de ataque se houver (ex: Kirara a atirar moedas)
        gif_ataque = dados.get("gif_ataque") or dados.get("gif") or "https://via.placeholder.com/400"
        dano = 25

        if self.turno == self.p1:
            self.hp_p2 = max(0, self.hp_p2 - dano)
            proximo_turno = self.p2
        else:
            self.hp_p1 = max(0, self.hp_p1 - dano)
            proximo_turno = self.p1

        self.turno = proximo_turno

        await self.atualizar_batalha(interaction, f"⚔️ {pers_nome} ({atacante.display_name}) usou o Ataque Principal e causou {dano} de dano!", gif_ataque)

    @discord.ui.button(label="Ataque Especial", style=discord.ButtonStyle.success, emoji="✨")
    async def ataque_especial(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.turno:
            return await interaction.response.send_message("❌ Não é o teu turno!", ephemeral=True)

        atacante = self.p1 if self.turno == self.p1 else self.p2
        time_atacante = self.p1_time if self.turno == self.p1 else self.p2_time
        indice_atual = self.indice_p1 if self.turno == self.p1 else self.indice_p2
        dicionario_mana = self.mana_p1 if self.turno == self.p1 else self.mana_p2

        pers_nome = time_atacante[indice_atual]
        dados = PERSONAGENS.get(pers_nome, {})
        
        custo_mana = dados.get("especial", {}).get("custo_mana", 20)
        mana_atual = dicionario_mana.get(pers_nome, 50)

        if mana_atual < custo_mana:
            return await interaction.response.send_message(f"❌ {pers_nome} não tem mana suficiente! ({mana_atual}/{custo_mana})", ephemeral=True)

        dicionario_mana[pers_nome] -= custo_mana
        dano = 50
        
        # Usa o gif especial (ex: Kirara a repelir tudo)
        gif_especial = dados.get("gif_especial") or dados.get("gif") or "https://via.placeholder.com/400"

        if self.turno == self.p1:
            self.hp_p2 = max(0, self.hp_p2 - dano)
            proximo_turno = self.p2
        else:
            self.hp_p1 = max(0, self.hp_p1 - dano)
            proximo_turno = self.p1

        self.turno = proximo_turno

        await self.atualizar_batalha(interaction, f"✨ {pers_nome} ({atacante.display_name}) usou o Ataque Especial repelindo o oponente!", gif_especial)

    @discord.ui.button(label="Defender", style=discord.ButtonStyle.secondary, emoji="🛡️")
    async def defender(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.turno:
            return await interaction.response.send_message("❌ Não é o teu turno!", ephemeral=True)

        atacante = self.p1 if self.turno == self.p1 else self.p2
        time_atacante = self.p1_time if self.turno == self.p1 else self.p2_time
        indice_atual = self.indice_p1 if self.turno == self.p1 else self.indice_p2
        pers_nome = time_atacante[indice_atual]

        efeito_extra = ""
        if "Kirara" in pers_nome:
            efeito_extra = "\n⭐ *Juntou as 5 estrelas para reforçar a defesa absoluta!*"

        dicionario_mana = self.mana_p1 if self.turno == self.p1 else self.mana_p2
        dicionario_mana[pers_nome] = min(100, dicionario_mana.get(pers_nome, 50) + 15)

        gif_defesa = PERSONAGENS.get(pers_nome, {}).get("gif") or "https://via.placeholder.com/400"

        if self.turno == self.p1:
            self.turno = self.p2
        else:
            self.turno = self.p1

        await self.atualizar_batalha(interaction, f"🛡️ {pers_nome} ({atacante.display_name}) assumiu posição defensiva!{efeito_extra}", gif_defesa)

    @discord.ui.button(label="Trocar Personagem", style=discord.ButtonStyle.danger, emoji="🔄")
    async def trocar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.turno:
            return await interaction.response.send_message("❌ Não é o teu turno!", ephemeral=True)

        if self.turno == self.p1:
            self.indice_p1 = (self.indice_p1 + 1) % len(self.p1_time)
            novo_pers = self.p1_time[self.indice_p1]
            self.turno = self.p2
        else:
            self.indice_p2 = (self.indice_p2 + 1) % len(self.p2_time)
            novo_pers = self.p2_time[self.indice_p2]
            self.turno = self.p1

        gif_troca = PERSONAGENS.get(novo_pers, {}).get("gif") or "https://via.placeholder.com/400"

        await self.atualizar_batalha(interaction, f"🔄 Troca efetuada! O novo combatente ativo é **{novo_pers}**.", gif_troca)

    async def atualizar_batalha(self, interaction: discord.Interaction, descricao: str, gif_url: str):
        if self.hp_p1 <= 0 or self.hp_p2 <= 0:
            vencedor = self.p1 if self.hp_p2 <= 0 else self.p2
            embed_fim = discord.Embed(
                title="🏆 FIM DO DUELO!",
                description=f"O Jogador **{vencedor.display_name}** venceu a batalha!",
                color=discord.Color.gold()
            )
            for item in self.children:
                item.disabled = True
            return await interaction.response.edit_message(embed=embed_fim, view=self)

        embed = discord.Embed(
            title="⚔️ DUELO EM ANDAMENTO",
            description=descricao,
            color=discord.Color.purple()
        )
        embed.set_image(url=gif_url)

        info_mana_p1 = "\n".join([f"• {p}: 💧 {self.mana_p1.get(p, 50)}" for p in self.p1_time])
        ativo_p1 = self.p1_time[self.indice_p1]

        embed.add_field(
            name=f"Equipa {self.p1.display_name} (Ativo: ⚔️ {ativo_p1})",
            value=f"❤️ HP Partilhado: **{self.hp_p1}**\n**Mana dos Combatentes:**\n{info_mana_p1}",
            inline=False
        )

        info_mana_p2 = "\n".join([f"• {p}: 💧 {self.mana_p2.get(p, 50)}" for p in self.p2_time])
        ativo_p2 = self.p2_time[self.indice_p2]

        embed.add_field(
            name=f"Equipa {self.p2.display_name} (Ativo: ⚔️ {ativo_p2})",
            value=f"❤️ HP Partilhado: **{self.hp_p2}**\n**Mana dos Combatentes:**\n{info_mana_p2}",
            inline=False
        )

        embed.set_footer(text=f"Turno atual de: {self.turno.display_name}")
        await interaction.response.edit_message(embed=embed, view=self)

async def iniciar_combate(ctx, p1, p2, p1_time, p2_time):

    hp_p1 = sum(PERSONAGENS[nome].get("hp", 100) for nome in p1_time if nome in PERSONAGENS)
    hp_p2 = sum(PERSONAGENS[nome].get("hp", 100) for nome in p2_time if nome in PERSONAGENS)

    mana_p1 = {nome: PERSONAGENS[nome].get("mana", 50) for nome in p1_time if nome in PERSONAGENS}
    mana_p2 = {nome: PERSONAGENS[nome].get("mana", 50) for nome in p2_time if nome in PERSONAGENS}

    view = BatalhaView(ctx, p1, p2, p1_time, p2_time, hp_p1, hp_p2, mana_p1, mana_p2)

    embed = discord.Embed(
        title="⚔️ INÍCIO DO DUELO!",
        description=f"A batalha começou! Turno inicial de **{p1.display_name}**.",
        color=discord.Color.red()
    )
    embed.add_field(
        name=f"Equipa de {p1.display_name}",
        value=f"❤️ HP Partilhado: **{hp_p1}**\n👥 Combatentes: {', '.join(p1_time)}",
        inline=False
    )
    embed.add_field(
        name=f"Equipa de {p2.display_name}",
        value=f"❤️ HP Partilhado: **{hp_p2}**\n👥 Combatentes: {', '.join(p2_time)}",
        inline=False
    )

    await ctx.send(embed=embed, view=view)


class SelecaoTimeP1(discord.ui.View):
    def __init__(self, ctx, oponente):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.oponente = oponente

        user_id = str(ctx.author.id)
        perfil = obter_perfil(user_id)
        inventario = perfil.get("inventario", [])

        options = []
        for nome in inventario:
            if nome in PERSONAGENS:
                dados = PERSONAGENS[nome]
                emoji_pers = dados.get("emoji") or dados.get("emoji_pers") or "⚔️"
                options.append(
                    discord.SelectOption(
                        label=nome,
                        description=f"{dados.get('universo', 'Outro')} | {dados.get('classe', 'Guerreiro')}",
                        emoji=emoji_pers
                    )
                )

        total_chars = len(options)
        max_escolhas = min(4, total_chars) if total_chars > 0 else 1

        self.select_item = discord.ui.Select(
            placeholder="[P1] Escolha os 4 personagens do seu time...",
            min_values=max_escolhas,
            max_values=4 if total_chars >= 4 else max_escolhas,
            options=options if options else [discord.SelectOption(label="Sem personagens", value="vazio")]
        )
        self.select_item.callback = self.select_callback
        self.add_item(self.select_item)

    async def select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("❌ Esta seleção pertence ao criador do duelo!", ephemeral=True)

        p1_time = self.select_item.values
        
        if "vazio" in p1_time:
            return await interaction.response.send_message("❌ Precisas de selecionar personagens válidos!", ephemeral=True)

        await interaction.response.send_message(
            f"✅ Time P1 confirmado! Agora é a vez de {self.oponente.mention} escolher.", 
            ephemeral=True
        )
        
        view_p2 = SelecaoTimeP2(self.ctx, self.oponente, p1_time)
        await self.ctx.send(f"⚔️ **[P2]** {self.oponente.mention}, escolhe os teus 4 combatentes:", view=view_p2)

# === SELEÇÃO DE EQUIPA (4 PERSONAGENS) ===
class SelecaoTimeSelect(Select):
    def __init__(self, ctx, oponente, turno_jogador, time_p1=None, time_p2=None):
        self.ctx = ctx
        self.oponente = oponente
        self.turno_jogador = turno_jogador
        self.time_p1 = time_p1 or []
        self.time_p2 = time_p2 or []

        jogador_alvo = ctx.author if turno_jogador == "p1" else oponente
        perfil = obter_perfil(str(jogador_alvo.id))
        inventario = perfil.get("inventario", [])

        time_atual = self.time_p1 if turno_jogador == "p1" else self.time_p2
        
        options = []
        for nome_perso in inventario:
            if nome_perso in time_atual:
                continue
                
            p_dados = PERSONAGENS.get(nome_perso, {})
            emoji = p_dados.get("emoji", "⚔️")
            options.append(discord.SelectOption(
                label=nome_perso, 
                description=f"HP: {p_dados.get('hp', 100)} | Mana: {p_dados.get('mana', 50)}", 
                emoji=emoji
            ))

        if not options:
            options.append(discord.SelectOption(label="Sem mais personagens", value="fim"))

        escolhidos_num = len(time_atual) + 1
        super().__init__(placeholder=f"Escolhe o combatente #{escolhidos_num} de 4...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        jogador_esperado = self.ctx.author if self.turno_jogador == "p1" else self.oponente
        
        if interaction.user != jogador_esperado:
            return await interaction.response.send_message("Este painel não é para ti!", ephemeral=True)

        escolha = self.values[0]
        if escolha == "fim":
            return await interaction.response.send_message("Não tens mais personagens disponíveis.", ephemeral=True)

        if self.turno_jogador == "p1":
            self.time_p1.append(escolha)
            
            if len(self.time_p1) < 4:
                view = View(timeout=60)
                view.add_item(SelecaoTimeSelect(self.ctx, self.oponente, "p1", time_p1=self.time_p1))
                embed = discord.Embed(
                    title="⚔️ Seleção de Equipa (P1)",
                    description=f"✅ **Equipa P1:** {', '.join(self.time_p1)}\n\n👉 Escolhe o próximo combatente (#{len(self.time_p1)+1}/4):",
                    color=discord.Color.blue()
                )
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                view = View(timeout=60)
                view.add_item(SelecaoTimeSelect(self.ctx, self.oponente, "p2", time_p1=self.time_p1, time_p2=[]))
                embed = discord.Embed(
                    title="⚔️ Seleção de Equipa (P2)",
                    description=f"✅ **P1 já escolheu a sua equipa!**\n\n👉 **{self.oponente.mention}**, escolhe o teu **1º combatente** para a equipa 4x4:",
                    color=discord.Color.gold()
                )
                await interaction.response.edit_message(embed=embed, view=view)
        else:
            self.time_p2.append(escolha)
            
            if len(self.time_p2) < 4:
                view = View(timeout=60)
                view.add_item(SelecaoTimeSelect(self.ctx, self.oponente, "p2", time_p1=self.time_p1, time_p2=self.time_p2))
                embed = discord.Embed(
                    title="⚔️ Seleção de Equipa (P2)",
                    description=f"✅ **Equipa P2:** {', '.join(self.time_p2)}\n\n👉 Escolhe o próximo combatente (#{len(self.time_p2)+1}/4):",
                    color=discord.Color.gold()
                )
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                view_batalha = Duelo4x4BatalhaView(self.ctx, self.oponente, self.time_p1, self.time_p2)
                embed = discord.Embed(
                    title="🔥 DUELO 4X4 INICIADO! 🔥",
                    description=(
                        f"👤 **Equipa P1 ({self.ctx.author.name}):** {', '.join(self.time_p1)}\n"
                        f"VS\n"
                        f"👤 **Equipa P2 ({self.oponente.name}):** {', '.join(self.time_p2)}\n\n"
                        f"-----------------------------------\n"
                        f"🎮 *O primeiro combatente de cada lado entrou em campo! Clica abaixo:*"
                    ),
                    color=discord.Color.purple()
                )
                await interaction.response.edit_message(embed=embed, view=view_batalha)


# === MENU PARA TROCAR DE PERSONAGEM EM COMBATE ===
class TrocarCombatenteSelect(Select):
    def __init__(self, batalha_view, jogador_id):
        self.batalha_view = batalha_view
        self.jogador_id = jogador_id
        
        is_p1 = (jogador_id == batalha_view.ctx.author.id)
        time = batalha_view.time_p1 if is_p1 else batalha_view.time_p2
        index_atual = batalha_view.index_p1 if is_p1 else batalha_view.index_p2
        
        options = []
        for i, nome_perso in enumerate(time):
            hp_perso = batalha_view.hp_equipa_1[i] if is_p1 else batalha_view.hp_equipa_2[i]
            if i != index_atual and hp_perso > 0:
                p_dados = PERSONAGENS.get(nome_perso, {})
                options.append(discord.SelectOption(
                    label=nome_perso, 
                    description=f"HP Atual: {hp_perso}", 
                    emoji=p_dados.get("emoji", "⚔️")
                ))
                
        if not options:
            options.append(discord.SelectOption(label="Nenhum personagem disponível para troca", value="nenhum"))
            
        super().__init__(placeholder="Escolhe o combatente para entrar em campo...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.jogador_id:
            return await interaction.response.send_message("Este menu não é para ti!", ephemeral=True)
            
        escolha = self.values[0]
        if escolha == "nenhum":
            return await interaction.response.send_message("Não tens outros combatentes vivos disponíveis para troca.", ephemeral=True)
            
        is_p1 = (interaction.user.id == self.batalha_view.ctx.author.id)
        time = self.batalha_view.time_p1 if is_p1 else self.batalha_view.time_p2
        
        novo_index = time.index(escolha)
        if is_p1:
            self.batalha_view.index_p1 = novo_index
            self.batalha_view.carregar_status_p1()
        else:
            self.batalha_view.index_p2 = novo_index
            self.batalha_view.carregar_status_p2()
            
        self.batalha_view.turno_atual = self.batalha_view.oponente.id if is_p1 else self.batalha_view.ctx.author.id
        nome_jogador = self.batalha_view.p1_name if is_p1 else self.batalha_view.p2_name
        
        acao = f"🔄 **{nome_jogador}** retirou o seu combatente e enviou **{escolha}** para o campo!"
        await self.batalha_view.atualizar_painel(interaction, acao)


# === COMBATE 4X4 COM MANA VISÍVEL, BOTÃO DE TROCA E GIFS ===
class Duelo4x4BatalhaView(View):
    def __init__(self, ctx, oponente, time_p1, time_p2):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.oponente = oponente
        self.p1_name = ctx.author.name
        self.p2_name = oponente.name
        
        self.time_p1 = time_p1
        self.time_p2 = time_p2
        
        self.index_p1 = 0
        self.index_p2 = 0
        
        self.hp_equipa_1 = [PERSONAGENS.get(p, {}).get("hp", 100) for p in time_p1]
        self.hp_max_equipa_1 = list(self.hp_equipa_1)
        self.mana_equipa_1 = [PERSONAGENS.get(p, {}).get("mana", 50) for p in time_p1]
        self.mana_max_equipa_1 = list(self.mana_equipa_1)
        
        self.hp_equipa_2 = [PERSONAGENS.get(p, {}).get("hp", 100) for p in time_p2]
        self.hp_max_equipa_2 = list(self.hp_equipa_2)
        self.mana_equipa_2 = [PERSONAGENS.get(p, {}).get("mana", 50) for p in time_p2]
        self.mana_max_equipa_2 = list(self.mana_equipa_2)
        
        self.carregar_status_p1()
        self.carregar_status_p2()
        
        self.turno_atual = ctx.author.id

    def carregar_status_p1(self):
        p1_dados = PERSONAGENS.get(self.time_p1[self.index_p1], {})
        self.hp_1 = self.hp_equipa_1[self.index_p1]
        self.hp_max_1 = self.hp_max_equipa_1[self.index_p1]
        self.mana_1 = self.mana_equipa_1[self.index_p1]
        self.mana_max_1 = self.mana_max_equipa_1[self.index_p1]
        
        self.nome_ataque_1 = p1_dados.get("ataque_normal", {}).get("nome", "Ataque")
        self.ataque_1 = p1_dados.get("ataque_normal", {}).get("dano", 15)
        self.nome_especial_1 = p1_dados.get("especial", {}).get("nome", "Especial")
        self.especial_1 = p1_dados.get("especial", {}).get("dano", 30)
        self.custo_mana_1 = p1_dados.get("especial", {}).get("custo_mana", 20)
        self.gif_1 = p1_dados.get("gif") or p1_dados.get("imagem")

    def carregar_status_p2(self):
        p2_dados = PERSONAGENS.get(self.time_p2[self.index_p2], {})
        self.hp_2 = self.hp_equipa_2[self.index_p2]
        self.hp_max_2 = self.hp_max_equipa_2[self.index_p2]
        self.mana_2 = self.mana_equipa_2[self.index_p2]
        self.mana_max_2 = self.mana_max_equipa_2[self.index_p2]
        
        self.nome_ataque_2 = p2_dados.get("ataque_normal", {}).get("nome", "Ataque")
        self.ataque_2 = p2_dados.get("ataque_normal", {}).get("dano", 15)
        self.nome_especial_2 = p2_dados.get("especial", {}).get("nome", "Especial")
        self.especial_2 = p2_dados.get("especial", {}).get("dano", 30)
        self.custo_mana_2 = p2_dados.get("especial", {}).get("custo_mana", 20)
        self.gif_2 = p2_dados.get("gif") or p2_dados.get("imagem")

    def guardar_status_atual(self):
        self.hp_equipa_1[self.index_p1] = self.hp_1
        self.mana_equipa_1[self.index_p1] = self.mana_1
        self.hp_equipa_2[self.index_p2] = self.hp_2
        self.mana_equipa_2[self.index_p2] = self.mana_2

    def verificar_proximo_vivo_p1(self):
        for i in range(len(self.time_p1)):
            if self.hp_equipa_1[i] > 0:
                self.index_p1 = i
                self.carregar_status_p1()
                return True
        return False

    def verificar_proximo_vivo_p2(self):
        for i in range(len(self.time_p2)):
            if self.hp_equipa_2[i] > 0:
                self.index_p2 = i
                self.carregar_status_p2()
                return True
        return False

    async def atualizar_painel(self, interaction, acao_texto):
        self.guardar_status_atual()

        if self.hp_1 <= 0:
            tem_mais = self.verificar_proximo_vivo_p1()
            if not tem_mais:
                return await self.concluir_duelo(interaction, vencedor=self.oponente)
            else:
                acao_texto += f"\n💀 O combatente de **{self.p1_name}** caiu! Entrou: **{self.time_p1[self.index_p1]}**"

        if self.hp_2 <= 0:
            tem_mais = self.verificar_proximo_vivo_p2()
            if not tem_mais:
                return await self.concluir_duelo(interaction, vencedor=self.ctx.author)
            else:
                acao_texto += f"\n💀 O combatente de **{self.p2_name}** caiu! Entrou: **{self.time_p2[self.index_p2]}**"

        vez_quem = self.ctx.author if self.turno_atual == self.ctx.author.id else self.oponente
        perso_p1_atual = self.time_p1[self.index_p1]
        perso_p2_atual = self.time_p2[self.index_p2]

        embed = discord.Embed(
            title="⚔️ Duelo 4x4 em Andamento",
            description=(
                f"👤 **{self.p1_name}** | Ativo: **{perso_p1_atual}**\n"
                f"❤️ HP: {self.hp_1}/{self.hp_max_1} | 💙 Mana: {self.mana_1}/{self.mana_max_1}\n\n"
                f"👤 **{self.p2_name}** | Ativo: **{perso_p2_atual}**\n"
                f"❤️ HP: {self.hp_2}/{self.hp_max_2} | 💙 Mana: {self.mana_2}/{self.mana_max_2}\n\n"
                f"-----------------------------------\n"
                f"📌 **Vez de:** {vez_quem.mention}\n"
                f"📝 *Última Ação:* {acao_texto}"
            ),
            color=discord.Color.blue()
        )
        
        gif_ativo = self.gif_1 if self.turno_atual == self.ctx.author.id else self.gif_2
        if gif_ativo:
            embed.set_image(url=gif_ativo)

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Atacar", style=discord.ButtonStyle.primary, emoji="⚔️")
    async def botao_atacar(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.turno_atual:
            return await interaction.response.send_message("Não é o teu turno!", ephemeral=True)

        if interaction.user == self.ctx.author:
            self.hp_2 -= self.ataque_1
            acao = f"{self.p1_name} usou **{self.nome_ataque_1}** e causou **{self.ataque_1} de dano**!"
            self.turno_atual = self.oponente.id
        else:
            self.hp_1 -= self.ataque_2
            acao = f"{self.p2_name} usou **{self.nome_ataque_2}** e causou **{self.ataque_2} de dano**!"
            self.turno_atual = self.ctx.author.id

        await self.atualizar_painel(interaction, acao)

    @discord.ui.button(label="Especial", style=discord.ButtonStyle.danger, emoji="👑")
    async def botao_especial(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.turno_atual:
            return await interaction.response.send_message("Não é o teu turno!", ephemeral=True)

        if interaction.user == self.ctx.author:
            if self.mana_1 < self.custo_mana_1:
                return await interaction.response.send_message("⚠️ Não tens mana suficiente para o especial!", ephemeral=True)
            self.mana_1 -= self.custo_mana_1
            self.hp_2 -= self.especial_1
            acao = f"{self.p1_name} usou o especial **{self.nome_especial_1}** causando **{self.especial_1} de dano**!"
            self.turno_atual = self.oponente.id
        else:
            if self.mana_2 < self.custo_mana_2:
                return await interaction.response.send_message("⚠️ Não tens mana suficiente para o especial!", ephemeral=True)
            self.mana_2 -= self.custo_mana_2
            self.hp_1 -= self.especial_2
            acao = f"{self.p2_name} usou o especial **{self.nome_especial_2}** causando **{self.especial_2} de dano**!"
            self.turno_atual = self.ctx.author.id

        await self.atualizar_painel(interaction, acao)

    @discord.ui.button(label="Defender", style=discord.ButtonStyle.secondary, emoji="🛡️")
    async def botao_defender(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.turno_atual:
            return await interaction.response.send_message("Não é o teu turno!", ephemeral=True)

        if interaction.user == self.ctx.author:
            self.mana_1 = min(self.mana_max_1, self.mana_1 + 15)
            acao = f"{self.p1_name} assumiu postura defensiva e recuperou **15 de mana**!"
            self.turno_atual = self.oponente.id
        else:
            self.mana_2 = min(self.mana_max_2, self.mana_2 + 15)
            acao = f"{self.p2_name} assumiu postura defensiva e recuperou **15 de mana**!"
            self.turno_atual = self.ctx.author.id

        await self.atualizar_painel(interaction, acao)

    @discord.ui.button(label="Trocar", style=discord.ButtonStyle.success, emoji="🔄")
    async def botao_trocar(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.turno_atual:
            return await interaction.response.send_message("Não é o teu turno!", ephemeral=True)

        view_troca = View(timeout=60)
        view_troca.add_item(TrocarCombatenteSelect(self, interaction.user.id))
        await interaction.response.send_message("🔄 Escolhe qual dos teus personagens queres colocar em campo:", view=view_troca, ephemeral=True)

    @discord.ui.button(label="Desistir", style=discord.ButtonStyle.secondary, emoji="🏳️")
    async def botao_desistir(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author and interaction.user != self.oponente:
            return await interaction.response.send_message("Não fazes parte deste duelo!", ephemeral=True)

        vencedor = self.oponente if interaction.user == self.ctx.author else self.ctx.author
        desistente = interaction.user
        
        for child in self.children:
            child.disabled = True

        embed = discord.Embed(
            title="🏳️ DESISTÊNCIA",
            description=f"O jogador **{desistente.name}** desistiu da luta!\n🏆 **Vitória atribuída a {vencedor.mention}!**",
            color=discord.Color.orange()
        )
        await interaction.response.edit_message(embed=embed, view=self)

    async def concluir_duelo(self, interaction, vencedor):
        for child in self.children:
            child.disabled = True
        
        embed = discord.Embed(
            title="🏁 FIM DO DUELO 4X4",
            description=f"🏆 **A equipa vencedora pertence a {vencedor.mention}!**",
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed, view=self)


# === COMANDO !DUELO 4X4 ===
@bot.command(name="duelo")
async def duelo(ctx, oponente: discord.Member):
    if oponente == ctx.author or oponente.bot:
        return await ctx.send("❌ Duelo inválido! Não podes desafiar a ti próprio nem a um bot.")

    perfil_p1 = obter_perfil(str(ctx.author.id))
    perfil_p2 = obter_perfil(str(oponente.id))

    if len(perfil_p1.get("inventario", [])) < 4:
        return await ctx.send("❌ Precisas de pelo menos **4 personagens** no teu inventário para um duelo 4x4!")
    if len(perfil_p2.get("inventario", [])) < 4:
        return await ctx.send(f"❌ {oponente.mention} precisa de ter pelo menos **4 personagens** no inventário!")

    view = View(timeout=60)
    view.add_item(SelecaoTimeSelect(ctx, oponente, "p1"))
    
    await ctx.send(
        f"⚔️ **{ctx.author.mention} desafiou {oponente.mention} para um Duelo 4x4!**\n"
        f"👉 **{ctx.author.name}**, usa o menu abaixo para escolher o teu **1º combatente**:",
        view=view
    )

@bot.command(name="gacha")
async def gacha(ctx):
    perfil = obter_perfil(ctx.author.id)
    custo = 50

    if perfil["moedas"] < custo:
        return await ctx.send(f"❌ Você não tem moedas suficientes! Custo: **{custo} moedas**. Você possui: **{perfil['moedas']}**.")

    perfil["moedas"] -= custo
    personagem, raridade = sortear_personagem()
    nome_perso = personagem["nome"]
    emoji_perso = personagem["emoji"]

    ja_possui = nome_perso in perfil["inventario"]
    if not ja_possui:
        perfil["inventario"].append(nome_perso)
        msg_footer = "Novo personagem adicionado à sua coleção!"
    else:
        perfil["moedas"] += 25
        msg_footer = "Você já possuía este personagem! Recebeu +25 moedas de reembolso."

    salvar_dados(JOGADORES)

    titulos = {
        "5_estrelas": "🌟🌟🌟🌟🌟 LENDÁRIO!",
        "4_estrelas": "✨✨✨✨ RARO!",
        "3_estrelas": "⭐ ⭐ ⭐ COMUM"
    }
    cores = {
        "5_estrelas": discord.Color.gold(),
        "4_estrelas": discord.Color.purple(),
        "3_estrelas": discord.Color.blue()
    }

    embed = discord.Embed(
        title=titulos[raridade],
        description=f"Você tirou: **{emoji_perso} {nome_perso}**!\n\n💰 Saldo atual: **{perfil['moedas']} moedas**",
        color=cores[raridade]
    )
    embed.set_footer(text=msg_footer)
    await ctx.send(embed=embed)

@bot.command(name="colecao")
async def colecao(ctx):
    user_id = str(ctx.author.id)
    perfil = obter_perfil(user_id)
    inventario = perfil.get("inventario", [])
    
    embed = discord.Embed(
        title=f"📦 Coleção de {ctx.author.display_name}",
        color=discord.Color.green()
    )
    embed.add_field(name="🪙 Moedas", value=f"**{perfil.get('moedas', 0)}**", inline=False)
    
    if not inventario:
        embed.description = "Ainda não tens nenhum personagem! Usa o comando de gacha para conseguir."
    else:
        texto_perso = ""
        
        # Compatibilidade: Se for lista (antigo) ou dicionário (novo)
        if isinstance(inventario, list):
            for nome in inventario:
                texto_perso += f"• **{nome}** — Nível 1 (XP: 0/100)\n"
        else:
            for nome, dados in inventario.items():
                if isinstance(dados, dict):
                    nivel = dados.get("nivel", 1)
                    exp = dados.get("exp", 0)
                    texto_perso += f"• **{nome}** — Nível {nivel} (XP: {exp}/{nivel * 100})\n"
                else:
                    texto_perso += f"• **{dados}** — Nível 1 (XP: 0/100)\n"
                    
        embed.add_field(name="Personagens:", value=texto_perso, inline=False)
        
    await ctx.send(embed=embed)

@bot.command(name="diario")
async def diario(ctx):
    perfil = obter_perfil(ctx.author.id)
    recompensa = 100
    perfil["moedas"] += recompensa
    salvar_dados(JOGADORES)
    await ctx.send(f"🎁 **{ctx.author.display_name}**, você resgatou sua recompensa diária de **{recompensa} moedas**! Saldo total: **{perfil['moedas']}**.")
@bot.command(name="dar_moedas")
@commands.has_permissions(administrator=True)
async def dar_moedas(ctx, membro: discord.Member, quantidade: int):
    perfil = obter_perfil(membro.id)
    perfil["moedas"] += quantidade
    salvar_dados(JOGADORES)
    await ctx.send(f"✅ Adicionadas **{quantidade} moedas** para {membro.mention}! Novo saldo: **{perfil['moedas']} moedas**.")

@dar_moedas.error
async def dar_moedas_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Apenas administradores podem usar este comando!")

@bot.command(name="dar_personagem")
@commands.has_permissions(administrator=True)
async def dar_personagem(ctx, membro: discord.Member, *, nome_personagem: str):
    if nome_personagem not in PERSONAGENS:
        return await ctx.send(f"❌ O personagem **{nome_personagem}** não existe no arquivo do bot. Verifique a grafia exata!")

    perfil = obter_perfil(membro.id)
    if nome_personagem in perfil["inventario"]:
        return await ctx.send(f"⚠️ {membro.mention} já possui o personagem **{nome_personagem}** na coleção.")

    perfil["inventario"].append(nome_personagem)
    salvar_dados(JOGADORES)
    await ctx.send(f"🎉 O personagem **{nome_personagem}** foi adicionado à coleção de {membro.mention} com sucesso!")

@dar_personagem.error
async def dar_personagem_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Apenas administradores podem usar este comando!")
        
@bot.command(name="pity")
async def ver_pity(ctx):
    user_id = str(ctx.author.id)
    perfil = obter_perfil(user_id)
    
    if "pity" not in perfil:
        perfil["pity"] = 0
        
    pity_atual = perfil["pity"]
    faltam = LIMITE_PITY - pity_atual
    
    await ctx.send(f"📊 **Seu Pity Atual:** {pity_atual}/{LIMITE_PITY}\n🎯 Faltam **{faltam}** tiragens para a raridade máxima garantida!")
    
@bot.command(name="personagens")
async def ver_personagens(ctx):
    mensagem = "📜 **PERSONAGENS DISPONÍVEIS NO JOGO** 📜\n\n"
    
    for nome, dados in PERSONAGENS.items():
        anime = dados.get("anime", "Desconhecido")
        hp = dados.get("hp", 100)
        mana = dados.get("mana", 50)
        
        # Puxa o emoji do personagem (ou usa 🎭 se não tiver) e a raridade (ou Comum por defeito)
        emoji = dados.get("emoji", "🎭")
        raridade = dados.get("raridade", "Comum")

        mensagem += f"{emoji} **{nome}** [{raridade}] ({anime})\n"
        mensagem += f"❤️ HP: {hp} | 🔷 Mana: {mana}\n"
        mensagem += f"------------------------\n"
        
    await ctx.send(mensagem)

@bot.command(name="ver")
async def ver_personagem(ctx, *, nome_personagem: str = None):
    if not nome_personagem:
        await ctx.send("❌ Por favor, digita o nome de um personagem. Exemplo: `!ver Tohka Yatogami`")
        return

    # Procura o personagem sem diferenciar maiúsculas/minúsculas
    personagem_encontrado = None
    nome_real = ""
    
    for nome, dados in PERSONAGENS.items():
        if nome.lower() == nome_personagem.lower():
            personagem_encontrado = dados
            nome_real = nome
            break

    if not personagem_encontrado:
        await ctx.send(f"❌ O personagem **{nome_personagem}** não foi encontrado no sistema.")
        return

    # Mapeamento de cores por raridade
    cores_raridade = {
        "Lendaria": discord.Color.gold(),
        "Epica": discord.Color.purple(),
        "Rara": discord.Color.blue(),
        "Comum": discord.Color.dark_grey()
    }

    # Puxa os dados dinâmicos do personagem
    raridade_perso = personagem_encontrado.get("raridade", "Comum")
    emoji_perso = personagem_encontrado.get("emoji", "🎭")
    cor_perso = cores_raridade.get(raridade_perso, discord.Color.blue())

    # Criar o Embed visual com cor e emoji dinâmicos
    embed = discord.Embed(
        title=f"{emoji_perso} {nome_real} [{raridade_perso}]",
        description=f"**Anime:** {personagem_encontrado.get('anime', 'Desconhecido')}",
        color=cor_perso
    )

    embed.add_field(name="❤️ HP", value=personagem_encontrado.get("hp", 100), inline=True)
    embed.add_field(name="🔷 Mana", value=personagem_encontrado.get("mana", 50), inline=True)

    # Adiciona os ataques ao card
    ataque = personagem_encontrado.get("ataque_normal", {})
    if ataque:
        embed.add_field(
            name=f"⚔️ {ataque.get('nome', 'Ataque Normal')}", 
            value=f"Dano: {ataque.get('dano', 0)}\n_{ataque.get('descricao', '')}_", 
            inline=False
        )

    especial = personagem_encontrado.get("especial", {})
    if especial:
        embed.add_field(
            name=f"💥 {especial.get('nome', 'Especial')}", 
            value=f"Dano: {especial.get('dano', 0)} | Custo: {especial.get('custo_mana', 0)} Mana\n_{especial.get('descricao', '')}_", 
            inline=False
        )

    # Define a imagem do personagem
    imagem_url = personagem_encontrado.get("imagem_padrao")
    if imagem_url:
        embed.set_image(url=imagem_url)

    await ctx.send(embed=embed)
import random

def adicionar_exp(personagem_dados, qtd_exp):
    if personagem_dados.get("nivel", 1) >= 100:
        return False, 100
    
    personagem_dados["exp"] += qtd_exp
    subiu_nivel = False
    
    exp_necessaria = personagem_dados["nivel"] * 100
    
    while personagem_dados["exp"] >= exp_necessaria and personagem_dados["nivel"] < 100:
        personagem_dados["exp"] -= exp_necessaria
        personagem_dados["nivel"] += 1
        subiu_nivel = True
        exp_necessaria = personagem_dados["nivel"] * 100
        
    if personagem_dados["nivel"] >= 100:
        personagem_dados["nivel"] = 100
        personagem_dados["exp"] = 0
        
    return subiu_nivel, personagem_dados["nivel"]

@bot.command(name="escolher")
async def escolher_personagem(ctx, *, nome_personagem: str):
    user_id = str(ctx.author.id)
    perfil = obter_perfil(user_id)
    
    # Verifica se o personagem existe no jogo
    if nome_personagem not in PERSONAGENS:
        await ctx.send(f"❌ O personagem **{nome_personagem}** não existe no jogo!")
        return
        
    # Verifica se o jogador já o tirou no Gacha (guardado no inventário)
    if nome_personagem not in perfil.get("inventario", []):
        await ctx.send(f"❌ Ainda não tens o personagem **{nome_personagem}** no teu inventário! Puxa primeiro no Gacha.")
        return
        
    perfil["personagem_selecionado"] = nome_personagem
    salvar_dados(JOGADORES)
    await ctx.send(f"✅ **{nome_personagem}** foi selecionado com sucesso para as batalhas de farm!")

# === CLASSE DOS BOTÕES DE COMBATE COM PERSONAGENS ===
class CombateView(discord.ui.View):
    def __init__(self, ctx, parte, etapa):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.parte = parte
        self.etapa = etapa

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("❌ Apenas o jogador que iniciou esta batalha pode escolher as ações!", ephemeral=True)
            return False
        return True

    async def processar_luta(self, interaction: discord.Interaction, acao: str):
        user_id = str(self.ctx.author.id)
        perfil = obter_perfil(user_id)

        # Buscar o personagem selecionado pelo jogador
        nome_perso = perfil.get("personagem_selecionado")
        if nome_perso and nome_perso in PERSONAGENS:
            dados_perso = PERSONAGENS[nome_perso]
            dano_base_normal = dados_perso["ataque_normal"]["dano"]
            dano_base_especial = dados_perso["especial"]["dano"]
            nome_ataque_especial = dados_perso["especial"]["nome"]
        else:
            # Valores padrão caso o jogador não tenha selecionado nenhum
            dano_base_normal = 15
            dano_base_especial = 30
            nome_ataque_especial = "Ataque Especial 💥"

        dano_inimigo = random.randint(10, 25)

        if acao == "atacar":
            dano_jogador = random.randint(dano_base_normal - 3, dano_base_normal + 5)
            acao_texto = f"Ataque Normal 🗡️ ({dano_base_normal} base)"
        elif acao == "especial":
            dano_jogador = random.randint(dano_base_especial - 5, dano_base_especial + 8)
            acao_texto = f"{nome_ataque_especial}"
        elif acao == "defender":
            dano_inimigo = max(1, dano_inimigo // 2)
            dano_jogador = random.randint(10, 20)
            acao_texto = "Defesa e Contra-Ataque 🛡️"

        vitoria = dano_jogador >= (dano_inimigo - 8)

        for item in self.children:
            item.disabled = True

        if not vitoria:
            embed_derrota = discord.Embed(
                title=f"💥 Derrota na Parte {self.parte}/5: {self.etapa['nome']}",
                description=f"Usaste **{acao_texto}**, mas o **{self.etapa['inimigo']}** superou a tua estratégia!",
                color=discord.Color.red()
            )
            embed_derrota.add_field(name="🗡️ Teu Dano", value=str(dano_jogador), inline=True)
            embed_derrota.add_field(name="🛡️ Dano Inimigo", value=str(dano_inimigo), inline=True)
            await interaction.response.edit_message(embed=embed_derrota, view=self)
            return

        moedas_ganhas = self.etapa["moedas"]
        perfil["moedas"] = perfil.get("moedas", 0) + moedas_ganhas
        
                # === ADICIONAR XP E SUBIR DE NÍVEL (ATÉ 100) ===
        nome_perso = perfil.get("personagem_selecionado")
        msg_nivel = ""
        
        if nome_perso:
            inventario = perfil.get("inventario", {})
            if nome_perso in inventario:
                dados_perso = inventario[nome_perso]
                
                # Compatibilidade se o inventário antigo for apenas texto
                if not isinstance(dados_perso, dict):
                    dados_perso = {"nivel": 1, "exp": 0}
                    inventario[nome_perso] = dados_perso
                
                # Adiciona 150 de XP por vitória na fase
                subiu, novo_nivel = adicionar_exp(dados_perso, 150)
                
                if subiu:
                    msg_nivel = f"\n🎉 **LEVEL UP!** O teu personagem **{nome_perso}** subiu para o **Nível {novo_nivel}**!"

                # Atualiza o progresso linear do farm
        if "progresso_farm" not in perfil:
            perfil["progresso_farm"] = "1"
            
        parte_atual_int = int(self.parte)
        if parte_atual_int == int(perfil["progresso_farm"]):
            perfil["progresso_farm"] = str(parte_atual_int + 1)
 
        if self.parte == "5":
            perfil["ultimo_farm"] = datetime.datetime.now().isoformat()
            
        salvar_dados(JOGADORES)

        embed = discord.Embed(
            title=f"🎉 Vitória com {acao_texto}! (Parte {self.parte}/5)",
            description=f"Derrotaste o **{self.etapa['inimigo']}** com sucesso usando **{nome_perso or 'Personagem Padrão'}**!",
            color=discord.Color.green()
        )
        embed.add_field(name="🗡️ Teu Dano", value=str(dano_jogador), inline=True)
        embed.add_field(name="🛡️ Dano Inimigo", value=str(dano_inimigo), inline=True)
        embed.add_field(name="🪙 Recompensa", value=f"+{moedas_ganhas} Moedas", inline=False)
        embed.add_field(name="💳 Saldo Total", value=f"{perfil['moedas']} Moedas", inline=True)

        if self.parte != "5":
            proxima = int(self.parte) + 1
            embed.set_footer(text=f"Usa !farm {proxima} para o próximo combate!")
        else:
            perfil["progresso_farm"] = "1"
            salvar_dados(JOGADORES)
            embed.set_footer(text="🏆 Parabéns! Concluíste todas as fases! O progresso voltou para a Parte 1 e o tempo de espera começou.")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Ataque Normal", style=discord.ButtonStyle.primary, emoji="🗡️")
    async def botao_atacar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.processar_luta(interaction, "atacar")

    @discord.ui.button(label="Defender", style=discord.ButtonStyle.secondary, emoji="🛡️")
    async def botao_defender(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.processar_luta(interaction, "defender")

    @discord.ui.button(label="Ataque Especial", style=discord.ButtonStyle.danger, emoji="👑")
    async def botao_especial(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.processar_luta(interaction, "especial")

import datetime
import random
import discord
from discord.ui import View, Button

# === DADOS DAS FASES ===
FASE_MOEDAS = {
    "1": {"nome": "Treino Inicial", "inimigo": "Ladrão Novato", "moedas": 20},
    "2": {"nome": "Confronto no Beco", "inimigo": "Ladrão de Ruas", "moedas": 40},
    "3": {"nome": "Assalto na Praça", "inimigo": "Criminoso Profissional", "moedas": 60},
    "4": {"nome": "Ataque ao Covil", "inimigo": "Chefe dos Bandidos", "moedas": 80},
    "5": {"nome": "Confronto Final", "inimigo": "Senhor do Crime", "moedas": 100}
}

FASE_XP = {
    "1": {"nome": "Floresta Calma", "inimigo": "Slime de Treino", "exp": 1},
    "2": {"nome": "Caverna Sombria", "inimigo": "Morcego Selvagem", "exp": 1},
    "3": {"nome": "Ruínas Antigas", "inimigo": "Esqueleto Guerreiro", "exp": 1},
    "4": {"nome": "Montanha Gélida", "inimigo": "Golem de Gelo", "exp": 1},
    "5": {"nome": "Templo do Dragão", "inimigo": "Mini-Dragão", "exp": 1}
}

# === CLASSE DE COMBATE INTERATIVO COM 5 PARTES ===
class FarmBatalhaView(View):
    def __init__(self, ctx, tipo, parte, perfil, personagem_nome):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.tipo = tipo
        self.parte = parte
        self.perfil = perfil
        self.personagem_nome = personagem_nome
        
        # Seleciona o dicionário correto (Moedas ou XP)
        dados_fase = FASE_MOEDAS if tipo == "moedas" else FASE_XP
        self.etapa_info = dados_fase[parte]
        self.nome_inimigo = self.etapa_info["inimigo"]
        
        # Puxa os dados base do personagem
        p_dados = PERSONAGENS.get(personagem_nome, {})
        self.hp = p_dados.get("hp", 100)
        self.hp_max = p_dados.get("hp", 100)
        self.mana = p_dados.get("mana", 50)
        self.mana_max = p_dados.get("mana", 50)
        
        self.nome_ataque = p_dados.get("ataque_normal", {}).get("nome", "Ataque Normal")
        self.dano_ataque = p_dados.get("ataque_normal", {}).get("dano", 16)
        
        self.nome_especial = p_dados.get("especial", {}).get("nome", "Ataque Especial")
        self.dano_especial = p_dados.get("especial", {}).get("dano", 32)
        self.custo_mana = p_dados.get("especial", {}).get("custo_mana", 20)
        
        # HP do inimigo escala de acordo com a parte (mais difícil à medida que avança)
        self.hp_inimigo = 50 + (int(parte) * 20)

    async def atualizar_painel(self, interaction, mensagem_acao):
        if self.hp <= 0:
            return await self.concluir_combate(interaction, "derrota")
        if self.hp_inimigo <= 0:
            return await self.concluir_combate(interaction, "vitoria")

        embed = discord.Embed(
            title=f"⚔️ Batalha: {self.etapa_info['nome']} (Parte {self.parte}/5)",
            description=(
                f"👤 **Lutador:** {self.personagem_nome} | ❤️ HP: {self.hp}/{self.hp_max} | 💙 Mana: {self.mana}/{self.mana_max}\n"
                f"👾 **Inimigo:** {self.nome_inimigo} | ❤️ HP Inimigo: {self.hp_inimigo}\n\n"
                f"-----------------------------------\n"
                f"📝 *Última Ação:* {mensagem_acao}"
            ),
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed, view=self)

    async def turno_inimigo(self):
        dano_inimigo = random.randint(8, 14 + int(self.parte))
        self.hp -= dano_inimigo
        return f"O {self.nome_inimigo} revidou e causou **{dano_inimigo} de dano**!"

    @discord.ui.button(label="Atacar", style=discord.ButtonStyle.primary, emoji="⚔️")
    async def botao_atacar(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("Esta batalha não é tua!", ephemeral=True)
        
        self.hp_inimigo -= self.dano_ataque
        acao = f"Usaste **{self.nome_ataque}** e causaste **{self.dano_ataque} de dano**."
        
        if self.hp_inimigo > 0:
            revide = await self.turno_inimigo()
            acao += f"\n{revide}"
            
        await self.atualizar_painel(interaction, acao)

    @discord.ui.button(label="Especial", style=discord.ButtonStyle.danger, emoji="👑")
    async def botao_especial(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("Esta batalha não é tua!", ephemeral=True)
            
        if self.mana < self.custo_mana:
            return await interaction.response.send_message(f"⚠️ Não tens mana suficiente! Precisas de {self.custo_mana} de mana.", ephemeral=True)
            
        self.mana -= self.custo_mana
        self.hp_inimigo -= self.dano_especial
        acao = f"Usaste o golpe especial **{self.nome_especial}** causando **{dano} de dano** maciço!" if 'dano' in locals() else f"Usaste o golpe especial **{self.nome_especial}** causando dano maciço!"
        
        if self.hp_inimigo > 0:
            revide = await self.turno_inimigo()
            acao += f"\n{revide}"
            
        await self.atualizar_painel(interaction, acao)

    @discord.ui.button(label="Defender", style=discord.ButtonStyle.secondary, emoji="🛡️")
    async def botao_defender(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("Esta batalha não é tua!", ephemeral=True)
            
        recupera_mana = 15
        self.mana = min(self.mana_max, self.mana + recupera_mana)
        dano_inimigo = max(3, random.randint(3, 7))
        self.hp -= dano_inimigo
        
        acao = f"Assumiste postura defensiva, recuperaste **{recupera_mana} de mana** e bloqueaste parte do ataque (sofrendo só {dano_inimigo} de dano)."
        
        await self.atualizar_painel(interaction, acao)

    async def concluir_combate(self, interaction, resultado):
        for child in self.children:
            child.disabled = True
            
        agora = datetime.datetime.now()
        chave_progresso = f"progresso_farm_{self.tipo}"
        chave_cooldown = f"ultimo_farm_{self.tipo}"
        
        if resultado == "vitoria":
            parte_atual = int(self.parte)
            
            if self.tipo == "moedas":
                recompensa = self.etapa_info["moedas"]
                self.perfil["moedas"] = self.perfil.get("moedas", 0) + recompensa
                texto_fim = f"🎉 **Vitória na Parte {self.parte}!** Ganhaste **{recompensa} moedas**."
            else:
                if "itens_exp" not in self.perfil:
                    self.perfil["itens_exp"] = 0
                self.perfil["itens_exp"] += 1
                texto_fim = f"🎉 **Treino Concluído (Parte {self.parte})!** Ganhaste **1x Poção de EXP**."

            # Atualiza o progresso para a próxima parte
            proxima_parte = str(parte_atual + 1)
            if parte_atual < 5:
                self.perfil[chave_progresso] = proxima_parte
                texto_fim += f"\n🔓 **Parte {proxima_parte} desbloqueada!**"
            else:
                # Se concluiu a parte 5, ativa o cooldown de 1 hora e reinicia o progresso para a parte 1
                self.perfil[chave_cooldown] = agora.isoformat()
                self.perfil[chave_progresso] = "1"
                texto_fim += f"\n🏆 **Parabéns! Concluíste todas as 5 partes de {self.tipo}!** Entraste em descanso de 1 hora."

            salvar_dados(JOGADORES)
        else:
            texto_fim = f"💀 **Derrota!** O teu personagem desmaiou na Parte {self.parte}. Tenta novamente."
            salvar_dados(JOGADORES)

        embed = discord.Embed(title="🏁 Fim da Batalha", description=texto_fim, color=discord.Color.green() if resultado == "vitoria" else discord.Color.red())
        await interaction.response.edit_message(embed=embed, view=self)


# === COMANDO !FARM COM ESCOLHA DE TIPO E PARTES ===
@bot.command(name="farm")
async def farm(ctx, tipo: str = None, parte: str = "1"):
    user_id = str(ctx.author.id)
    perfil = obter_perfil(user_id)
    
    personagem_nome = perfil.get("personagem_selecionado")
    if not personagem_nome:
        await ctx.send("⚠️ Ainda não selecionaste nenhum personagem! Usa `!escolher <nome>` primeiro.")
        return

    if tipo not in ["moedas", "xp"]:
        await ctx.send(
            "⚔️ **CENTRAL DE FARM (5 PARTES)** ⚔️\n"
            "Usa o comando indicando o tipo e a parte pretendida:\n"
            "• `!farm moedas <1-5>` — Batalha por moedas.\n"
            "• `!farm xp <1-5>` — Batalha de treino por itens de XP."
        )
        return

    chave_cooldown = f"ultimo_farm_{tipo}"
    chave_progresso = f"progresso_farm_{tipo}"
    agora = datetime.datetime.now()

    # Verifica o cooldown de 1 hora caso tenha terminado a parte 5 recentemente
    if chave_cooldown in perfil:
        ultimo_uso = datetime.datetime.fromisoformat(perfil[chave_cooldown])
        tempo_decorrido = (agora - ultimo_uso).total_seconds()
        
        if tempo_decorrido < 3600:
            tempo_restante = int(3600 - tempo_decorrido)
            minutos = tempo_restante // 60
            segundos = tempo_restante % 60
            await ctx.send(f"⏳ **Descanso necessário!** Concluíste o ciclo de **{tipo}** recentemente. Podes recomeçar daqui a **{minutos}m {segundos}s**.")
            return

    # Validação da progressão linear das 5 partes
    progresso_atual = perfil.get(chave_progresso, "1")
    if parte not in ["1", "2", "3", "4", "5"]:
        await ctx.send("❌ Parte inválida! Escolhe uma parte entre **1** e **5** (Exemplo: `!farm moedas 1`).")
        return

    if int(parte) > int(progresso_atual):
        await ctx.send(f"🔒 **Acesso bloqueado!** Ainda precisas de concluir a **Parte {progresso_atual}** antes de avançar para esta.")
        return

    # Prepara o painel de início do combate
    p_dados = PERSONAGENS.get(personagem_nome, {})
    hp_atual = p_dados.get("hp", 100)
    mana_atual = p_dados.get("mana", 50)
    
    dados_fase = FASE_MOEDAS if tipo == "moedas" else FASE_XP
    etapa = dados_fase[parte]

    embed = discord.Embed(
        title=f"⚔️ Batalha: {etapa['nome']} (Parte {parte}/5)",
        description=(
            f"👤 **Lutador:** {personagem_nome} | ❤️ HP: {hp_atual}/{hp_atual} | 💙 Mana: {mana_atual}/{mana_atual}\n"
            f"👾 **Inimigo Encontrado:** {etapa['inimigo']}\n\n"
            f"-----------------------------------\n"
            f"🎮 *O combate começou! Clica num botão abaixo:*"
        ),
        color=discord.Color.purple()
    )

    view = FarmBatalhaView(ctx, tipo, parte, perfil, personagem_nome)
    await ctx.send(embed=embed, view=view)


    # === COMANDO PARA REMOVER MOEDAS ===
@bot.command(name="tirarmoedas")
@commands.has_permissions(administrator=True)
async def tirar_moedas(ctx, membro: discord.Member, quantidade: int):
    user_id = str(membro.id)
    perfil = obter_perfil(user_id)
    
    saldo_atual = perfil.get("moedas", 0)
    
    # Garante que o saldo não fica negativo
    perfil["moedas"] = max(0, saldo_atual - quantidade)
    salvar_dados(JOGADORES)
    
    await ctx.send(f"✅ Removidas **{quantidade} moedas** de {membro.mention}. Saldo atual: **{perfil['moedas']} moedas**.")

@tirar_moedas.error
async def tirar_moedas_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Não tens permissões de administrador para usar este comando!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Uso correto: `!tirarmoedas @utilizador <quantidade>`")


# === COMANDO PARA REMOVER PERSONAGEM DO INVENTÁRIO ===
@bot.command(name="tirarpersonagem")
@commands.has_permissions(administrator=True)
async def tirar_personagem(ctx, membro: discord.Member, *, nome_personagem: str):
    user_id = str(membro.id)
    perfil = obter_perfil(user_id)
    
    inventario = perfil.get("inventario", [])
    
    if nome_personagem not in inventario:
        await ctx.send(f"❌ O utilizador {membro.mention} não possui o personagem **{nome_personagem}** no inventário.")
        return
        
    inventario.remove(nome_personagem)
    
    # Se o personagem removido era o que estava selecionado, limpa a seleção
    if perfil.get("personagem_selecionado") == nome_personagem:
        perfil["personagem_selecionado"] = None
        
    salvar_dados(JOGADORES)
    
    await ctx.send(f"✅ O personagem **{nome_personagem}** foi removido do inventário de {membro.mention}.")

@tirar_personagem.error
async def tirar_personagem_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Não tens permissões de administrador para usar este comando!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Uso correto: `!tirarpersonagem @utilizador <nome_do_personagem>`")

# === COMANDO DE AJUDA / COMO JOGAR ===
@bot.command(name="ajuda", aliases=["como-jogar", "tutorial"])
async def ajuda_jogo(ctx):
    embed = discord.Embed(
        title="📖 Guia Completo - Como Jogar",
        description="Bem-vindo ao sistema de combates e farm! Segue os passos abaixo para lutares com as tuas personagens:",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="👥 1. Selecionar a tua Personagem",
        value="Antes de entrares em combate, escolhe qual personagem do teu inventário vais usar com `!escolher <nome_da_personagem>` (exemplo: `!escolher White Queen`).",
        inline=False
    )
    embed.add_field(
        name="⚔️ 2. Sistema de Farm por Fases",
        value=(
            "• O farm é composto por **5 partes progressivas** (`!farm 1` até `!farm 5`).\n"
            "• Podes avançar continuamente pelas partes 1 a 4 sem tempo de espera.\n"
            "• **Atenção:** O cooldown de 1 hora só é ativado após concluíres com sucesso a **Parte 5**!"
        ),
        inline=False
    )
    embed.add_field(
        name="🛡️ 3. Em Batalha",
        value="Usa os botões para **Atacar**, **Defender** ou realizar o **Ataque Especial** (a White Queen possui a mecânica única de **Xeque-Mate** com o botão 👑!).",
        inline=False
    )
    embed.set_footer(text="Usa '!comandos' para veres a lista completa de comandos.")
    await ctx.send(embed=embed)


# === COMANDO DE LISTA DE COMANDOS ===
@bot.command(name="comandos", aliases=["cmds"])
async def listar_comandos(ctx):
    embed = discord.Embed(
        title="📜 Lista de Comandos",
        description="Consulta abaixo todos os comandos disponíveis no bot:",
        color=discord.Color.gold()
    )
    
    # Comandos para jogadores
    embed.add_field(
        name="👥 Comandos de Jogador",
        value=(
            "• `!ajuda` — Exibe o guia de como jogar.\n"
            "• `!comandos` — Mostra esta lista de comandos.\n"
            "• `!escolher <nome>` — Seleciona a personagem ativa para lutar.\n"
            "• `!farm <1-5>` — Inicia as batalhas de farm por partes."
        ),
        inline=False
    )
    
    # Comandos para administradores
    embed.add_field(
        name="🛡️ Comandos de Administrador",
        value=(
            "• `!tirarmoedas @membro <qtd>` — Retira moedas do saldo de um jogador.\n"
            "• `!tirarpersonagem @membro <nome>` — Remove uma personagem do inventário de um jogador."
        ),
        inline=False
    )
    
    embed.set_footer(text="Aproveita as tuas batalhas no servidor!")
    await ctx.send(embed=embed)
    
@bot.command(name="menu")
async def exibir_menu(ctx):
    embed = discord.Embed(
        title="🌸 Central de Ajuda & Navegação",
        description="Selecione uma das opções abaixo para explorar as fases e comandos do bot!",
        color=discord.Color.purple()
    )
    
    # Envia a mensagem com o menu interativo anexado
    view = MenuPrincipal()
    await ctx.send(embed=embed, view=view)

if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)
