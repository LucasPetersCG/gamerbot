import feedparser
import urllib.request
import ssl

def get_rpg_news():
    # URL NOVA (A antiga estava offline)
    url = "https://tribality.com/feed" 
    news_list = []

    print(f"🎲 [DEBUG RPG] Iniciando busca em: {url}")

    try:
        # Contexto SSL permissivo para Docker
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        # User-Agent para não ser bloqueado como bot
        req = urllib.request.Request(
            url, 
            data=None, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )

        with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
            raw_data = response.read()
            d = feedparser.parse(raw_data)
            
            if not d.entries:
                print("🎲 [DEBUG RPG] RSS baixado mas sem entradas.")
            
            for entry in d.entries[:3]:
                # Tenta pegar ID, Link ou GUID
                unique_id = getattr(entry, 'id', getattr(entry, 'link', None))
                
                # Limpa HTML da descrição se for muito longo
                summary = getattr(entry, 'description', '') or getattr(entry, 'summary', '')
                if len(summary) > 2000: 
                    summary = summary[:2000] + "..."

                news_list.append({
                    'id': unique_id,
                    'title': entry.title,
                    'link': entry.link,
                    'content': summary,
                    'source': 'RPG'
                })

    except Exception as e:
        print(f"🎲 [DEBUG RPG] Erro: {e}")

    return news_list