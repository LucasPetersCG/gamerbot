import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

# 1. Carrega as variáveis do arquivo .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# 2. Configura as Intenções (Intents)
# O Discord exige que digamos explicitamente o que o bot pode ver
intents = discord.Intents.default()
intents.message_content = True # Permite ler mensagens

# 3. Define o prefixo e cria a instância do bot
bot = commands.Bot(command_prefix='!', intents=intents)

# 4. Evento: Quando o bot estiver pronto e conectado
@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user} (ID: {bot.user.id})')
    print('------')

# 5. Inicia o bot
if __name__ == '__main__':
    bot.run(TOKEN)