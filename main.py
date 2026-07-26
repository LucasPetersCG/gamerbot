import discord
import os
import asyncio
import json
from discord.ext import commands, tasks
from dotenv import load_dotenv

# Importando Serviços
from services.ai_service import AIService
from services.steam_service import get_steam_news
from services.tibia_service import get_tibia_news
from services.rss_service import get_rpg_news 
from services.export_service import log_message, build_export_zip

# --- CONFIGURAÇÃO ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Arquivos
CONFIG_FILE = "data/channel_subscriptions.json"
SEEN_NEWS_FILE = "data/seen_news.json"

ai_service = AIService()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Remover o comando help padrão para usar o nosso personalizado
bot.remove_command('help')

# --- GERENCIAMENTO DE DADOS ---
def load_json(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except:
            return {} if "subscriptions" in filepath else []
    return {} if "subscriptions" in filepath else []

def save_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

# Carrega configurações
subscriptions = load_json(CONFIG_FILE)
seen_news_ids = set(load_json(SEEN_NEWS_FILE))

# --- FUNÇÕES DE CONFIGURAÇÃO (ADD/REMOVE) ---
def add_subscription(channel_id, service_tag):
    str_id = str(channel_id)
    
    if str_id not in subscriptions:
        subscriptions[str_id] = []
    
    if service_tag == "all":
        subscriptions[str_id] = ["Steam", "Tibia", "RPG"]
    elif service_tag not in subscriptions[str_id]:
        subscriptions[str_id].append(service_tag)
    
    save_json(CONFIG_FILE, subscriptions)

def remove_subscription(channel_id, service_tag):
    str_id = str(channel_id)
    
    if str_id not in subscriptions:
        return False

    if service_tag == "all":
        del subscriptions[str_id]
    elif service_tag in subscriptions[str_id]:
        subscriptions[str_id].remove(service_tag)
        if not subscriptions[str_id]:
            del subscriptions[str_id]
            
    save_json(CONFIG_FILE, subscriptions)
    return True

# --- PROCESSAMENTO E ENVIO ---
async def process_and_broadcast(news_items, force_target_channel=None, ignore_history=False):
    global seen_news_ids
    new_ids_found = False

    if not news_items:
        return

    for item in news_items:
        news_id = item['id']
        source = item['source'] 

        # 1. FILTRO DE DUPLICIDADE
        if not ignore_history and news_id in seen_news_ids:
            continue
        
        print(f"⚡ Processando: {item['title']} ({source})")

        # 2. IA - RESUMO
        summary = await ai_service.summarize(item['title'], item['content'], source)

        # 3. ÍCONES
        icon_map = {"Steam": "🎮", "Tibia": "🐉", "RPG": "🎲"}
        icon = icon_map.get(source, "📰")

        embed_text = (
            f"**{icon} {source} News**\n"
            f"**{item['title']}**\n\n"
            f"{summary}\n\n"
            f"🔗 [Ler original]({item['link']})"
        )

        # 4. LÓGICA DE ROTEAMENTO
        if force_target_channel:
            try:
                await force_target_channel.send(embed_text)
                await asyncio.sleep(1)
            except Exception as e:
                print(f"Erro no envio manual: {e}")
        else:
            for channel_id, subs in list(subscriptions.items()):
                if source in subs: 
                    channel = bot.get_channel(int(channel_id))
                    if channel:
                        try:
                            await channel.send(embed_text)
                            await asyncio.sleep(1.5) 
                        except Exception as e:
                            print(f"Erro ao enviar para {channel_id}: {e}")

        # 5. ATUALIZAR MEMÓRIA
        seen_news_ids.add(news_id)
        new_ids_found = True

    if new_ids_found:
        save_json(SEEN_NEWS_FILE, list(seen_news_ids))

# --- TAREFA AGENDADA (30 min) ---
@tasks.loop(minutes=30)
async def fetch_news_cycle():
    await bot.wait_until_ready()
    print("🔄 [AUTO] Iniciando ciclo de busca...")

    try:
        steam_news = await get_steam_news()
        await process_and_broadcast(steam_news)
    except Exception as e:
        print(f"Erro crítico no ciclo Steam: {e}")
    
    await asyncio.sleep(5) 
    
    try:
        tibia_news = await get_tibia_news(days=1)
        await process_and_broadcast(tibia_news)
    except Exception as e:
        print(f"Erro crítico no ciclo Tibia: {e}")

    await asyncio.sleep(5)

    try:
        rpg_news = await asyncio.to_thread(get_rpg_news)
        await process_and_broadcast(rpg_news)
    except Exception as e:
        print(f"Erro crítico no ciclo RPG: {e}")

    print("✅ [AUTO] Ciclo finalizado.")

# --- COMANDOS DE UX (AJUDA E BOAS VINDAS) ---

@bot.command(name="help")
async def help_command(ctx):
    """Exibe o menu de ajuda personalizado."""
    embed = discord.Embed(
        title="🤖 GamerBot - Central de Ajuda",
        description="Receba notícias traduzidas de Tibia, Steam e RPGs em geral!",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="⚙️ Configuração (Admins)",
        value=(
            "`!setup_all_news` - Recebe TODAS as notícias neste canal.\n"
            "`!setup_tibia_news` - Apenas notícias de Tibia.\n"
            "`!setup_steam_news` - Apenas notícias da Steam.\n"
            "`!setup_rpg_news` - Apenas notícias de RPGs de Mesa/Indie."
        ),
        inline=False
    )

    embed.add_field(
        name="🗑️ Remover Assinaturas",
        value=(
            "`!remove_all` - Para de receber tudo neste canal.\n"
            "`!remove_tibia`, `!remove_steam`, `!remove_rpg` - Remove específico."
        ),
        inline=False
    )

    embed.add_field(
        name="🔍 Comandos Manuais (Teste)",
        value=(
            "`!last_tibia [dias]` - Busca notícias recentes de Tibia.\n"
            "`!last_steam` - Busca última notícia da Steam.\n"
            "`!last_rpg` - Busca últimas do feed RPG.\n"
            "`!force_check` (Admin) - Força ciclo completo de atualização."
        ),
        inline=False
    )
    
    embed.set_footer(text="Desenvolvido por LucasPetersCG")
    await ctx.send(embed=embed)

@bot.event
async def on_guild_join(guild):
    """Executado quando o bot entra em um novo servidor."""
    print(f"Entrei no servidor: {guild.name}")
    
    # Tenta achar o canal de sistema ou o primeiro canal de texto disponível
    channel = guild.system_channel
    if channel is None:
        for c in guild.text_channels:
            if c.permissions_for(guild.me).send_messages:
                channel = c
                break
    
    if channel:
        embed = discord.Embed(
            title="👋 Olá! Eu sou o GamerBot!",
            description=(
                "Obrigado por me adicionar! Eu trago notícias de Games traduzidas com IA.\n\n"
                "**Para começar:**\n"
                "1. Vá até o canal de notícias.\n"
                "2. Digite `!setup_all_news` (ou escolha uma categoria específica).\n\n"
                "Para ver todos os comandos, digite `!help`."
            ),
            color=discord.Color.purple()
        )
        await channel.send(embed=embed)

# --- LOGGING DE MENSAGENS (EXPORT) ---
@bot.event
async def on_message(message):
    """
    Registra cada mensagem recebida para export posterior (!export_chats).
    IMPORTANTE: como sobrescrevemos on_message, precisamos chamar
    bot.process_commands(message) no final, senão os comandos com "!" param de funcionar.
    """
    # Não loga as próprias mensagens do bot
    if message.author.id != bot.user.id:
        try:
            log_message(message)
        except Exception as e:
            print(f"⚠️ Erro ao logar mensagem para export: {e}")

    await bot.process_commands(message)

# --- COMANDOS DE CONFIGURAÇÃO (SETUP) ---
@bot.command(name="setup_all_news")
@commands.has_permissions(administrator=True)
async def setup_all(ctx):
    add_subscription(ctx.channel.id, "all")
    await ctx.send(f"✅ {ctx.channel.mention} receberá **TODAS** as notícias.")

@bot.command(name="setup_steam_news")
@commands.has_permissions(administrator=True)
async def setup_steam(ctx):
    add_subscription(ctx.channel.id, "Steam")
    await ctx.send(f"✅ {ctx.channel.mention} receberá notícias da **Steam**.")

@bot.command(name="setup_tibia_news")
@commands.has_permissions(administrator=True)
async def setup_tibia(ctx):
    add_subscription(ctx.channel.id, "Tibia")
    await ctx.send(f"✅ {ctx.channel.mention} receberá notícias de **Tibia**.")

@bot.command(name="setup_rpg_news")
@commands.has_permissions(administrator=True)
async def setup_rpg(ctx):
    add_subscription(ctx.channel.id, "RPG")
    await ctx.send(f"✅ {ctx.channel.mention} receberá notícias de **RPG/D&D**.")

# --- COMANDOS DE REMOÇÃO (UNSUBSCRIBE) ---
@bot.command(name="remove_all")
@commands.has_permissions(administrator=True)
async def remove_all(ctx):
    if remove_subscription(ctx.channel.id, "all"):
        await ctx.send(f"🗑️ {ctx.channel.mention} removido de **TODAS** as listas de notícias.")
    else:
        await ctx.send("Este canal não tinha nenhuma assinatura ativa.")

@bot.command(name="remove_steam")
@commands.has_permissions(administrator=True)
async def remove_steam(ctx):
    if remove_subscription(ctx.channel.id, "Steam"):
        await ctx.send(f"🗑️ Notícias da **Steam** removidas deste canal.")
    else:
        await ctx.send("Este canal não estava assinado para Steam.")

@bot.command(name="remove_tibia")
@commands.has_permissions(administrator=True)
async def remove_tibia(ctx):
    if remove_subscription(ctx.channel.id, "Tibia"):
        await ctx.send(f"🗑️ Notícias de **Tibia** removidas deste canal.")
    else:
        await ctx.send("Este canal não estava assinado para Tibia.")

@bot.command(name="remove_rpg")
@commands.has_permissions(administrator=True)
async def remove_rpg(ctx):
    if remove_subscription(ctx.channel.id, "RPG"):
        await ctx.send(f"🗑️ Notícias de **RPG** removidas deste canal.")
    else:
        await ctx.send("Este canal não estava assinado para RPG.")

# --- COMANDOS MANUAIS ---
@bot.command(name="force_check")
@commands.has_permissions(administrator=True)
async def force_check(ctx):
    await ctx.send("🕵️ Forçando ciclo de busca (Isso pode demorar um pouco)...")
    
    s_news = await get_steam_news()
    await process_and_broadcast(s_news)
    
    t_news = await get_tibia_news(days=1)
    await process_and_broadcast(t_news)
    
    r_news = await asyncio.to_thread(get_rpg_news)
    await process_and_broadcast(r_news)
    
    await ctx.send("✅ Busca manual concluída!")

@bot.command(name="export_chats", aliases=["sync_export_now"])
@commands.has_permissions(administrator=True)
async def export_chats(ctx):
    """Gera um .zip com o histórico de mensagens logadas e envia no canal atual."""
    await ctx.send("📦 Gerando export do histórico de mensagens...")

    zip_path = build_export_zip()

    try:
        await ctx.send(file=discord.File(zip_path))
    except discord.HTTPException:
        await ctx.send(
            "❌ O arquivo é grande demais para o Discord aceitar. "
            "Busque o arquivo diretamente no servidor em `~/kodland-bot/data/discord_export/`."
        )
    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)

@bot.command(name="last_tibia")
async def last_tibia(ctx, days: int = 1):
    if days > 30:
        await ctx.send("❌ Máximo de 30 dias.")
        return
    await ctx.send(f"🔎 Buscando Tibia News dos últimos {days} dias...")
    news = await get_tibia_news(days=days)
    if news:
        await process_and_broadcast(news, force_target_channel=ctx.channel, ignore_history=True)
        await ctx.send("✅ Tibia check finalizado.")
    else:
        await ctx.send("Nada encontrado.")

@bot.command(name="last_steam")
async def last_steam(ctx):
    await ctx.send("🔎 Buscando últimas notícias da Steam...")
    news = await get_steam_news()
    if news:
        await process_and_broadcast(news, force_target_channel=ctx.channel, ignore_history=True)
        await ctx.send("✅ Steam check finalizado.")
    else:
        await ctx.send("Nada encontrado.")

@bot.command(name="last_rpg")
async def last_rpg(ctx):
    await ctx.send("🔎 Buscando últimas notícias de RPG...")
    news = await asyncio.to_thread(get_rpg_news)
    if news:
        await process_and_broadcast(news, force_target_channel=ctx.channel, ignore_history=True)
        await ctx.send("✅ RPG check finalizado.")
    else:
        await ctx.send("Nada encontrado.")

@bot.event
async def on_ready():
    print(f'🤖 Bot logado como {bot.user}')
    if not fetch_news_cycle.is_running():
        fetch_news_cycle.start()

if __name__ == '__main__':
    bot.run(TOKEN)