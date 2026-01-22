import discord
import os
import aiohttp
import asyncio
from discord.ext import commands, tasks
from dotenv import load_dotenv

# --- CONFIGURAÇÃO ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('NEWS_CHANNEL_ID'))

# Configuração dos Jogos por Gênero (AppIDs da Steam)
# Você pode adicionar mais IDs aqui procurando no steamdb.info
GAME_CONFIG = {
    "RPG": [
        1086940, # Baldur's Gate 3
        1091500, # Cyberpunk 2077
        292030,  # The Witcher 3
    ],
    "MMORPG": [
        39210,   # Final Fantasy XIV
        582660,  # Black Desert
        306130,  # Elder Scrolls Online
    ]
}

# --- MEMÓRIA DO BOT ---
# Usaremos um SET (conjunto) para guardar IDs de notícias já enviadas.
# Sets são muito mais rápidos que listas para verificar "se já existe".
seen_news_ids = set()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# --- FUNÇÃO AUXILIAR ---
async def process_game_news(session, channel, game_id, genre):
    """Busca notícia de um jogo específico e posta se for nova."""
    url = f"http://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid={game_id}&count=1&maxlength=300&format=json"
    
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                news_items = data.get('appnews', {}).get('newsitems', [])
                
                if news_items:
                    latest = news_items[0]
                    news_id = latest['gid']
                    
                    # VERIFICAÇÃO DE DUPLICIDADE
                    if news_id not in seen_news_ids:
                        title = latest['title']
                        link = latest['url']
                        game_name = f"Jogo ID {game_id}" # Melhoraremos isso depois
                        
                        # Monta a mensagem bonita
                        msg = (f"**Nova Notícia de {genre}!** 🎮\n"
                               f"**{title}**\n"
                               f"{link}")
                        
                        await channel.send(msg)
                        
                        # Adiciona à memória para não repetir
                        seen_news_ids.add(news_id)
                        print(f"Postado: {title} (ID: {news_id})")
    except Exception as e:
        print(f"Erro ao processar jogo {game_id}: {e}")

# --- TAREFA PRINCIPAL ---
@tasks.loop(seconds=30) # Aumentei para 30 min para não estourar limite da API
async def fetch_genre_news():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)
    
    if not channel:
        print("Canal não encontrado!")
        return

    print("Iniciando varredura de notícias...")
    
    # Abre uma única sessão para todas as requisições (muito mais eficiente)
    async with aiohttp.ClientSession() as session:
        # Loop pelos gêneros
        for genre, game_ids in GAME_CONFIG.items():
            # Loop pelos jogos dentro do gênero
            for game_id in game_ids:
                await process_game_news(session, channel, game_id, genre)
                # Pausa pequena para não ser bloqueado pela Steam
                await asyncio.sleep(1) 

@bot.event
async def on_ready():
    print(f'Logado como {bot.user}')
    if not fetch_genre_news.is_running():
        fetch_genre_news.start()

if __name__ == '__main__':
    bot.run(TOKEN)