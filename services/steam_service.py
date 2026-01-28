import aiohttp
import asyncio

# IDs dos Jogos Steam
GAME_CONFIG = {
    "RPG": [1086940, 1091500, 292030, 3240220],
    "MMORPG": [39210, 582660, 306130, 1547000],
    "NewSet1": [2694490, 582660, 3564740, 2344520, 2429640, 4124950, 1599340, 761890, 216150],
    "NewSet2": [1374490, 1343370, 2437170, 835570, 206480, 212500, 372000, 1172620, 730, 578080, 1172470, 2139460, 381210, 261550, 813780],
    "NewSet3": [2188170, 1174180, 2357570, 1057090, 261570, 367520, 1030300, 1245620, 2622380, 2141910, 435150, 1142710, 489830, 1063730, 1771300, 1763400, 2407250]
}

async def get_steam_news():
    news_list = []
    
    async with aiohttp.ClientSession() as session:
        # Loop correto desempacotando (Chave, Valor)
        for genre, ids_list in GAME_CONFIG.items():
            for app_id in ids_list:
                # Pegamos apenas a notícia mais recente (count=1)
                url = f"http://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid={app_id}&count=1&maxlength=500&format=json"
                
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            items = data.get('appnews', {}).get('newsitems', [])
                            
                            if items:
                                latest = items[0]
                                news_list.append({
                                    'id': str(latest['gid']), # Convertendo para string para padronizar
                                    'title': latest['title'],
                                    'link': latest['url'],
                                    'content': latest.get('contents', 'Sem conteúdo de texto.'),
                                    'source': 'Steam' # Importante para a IA saber quem é
                                })
                except Exception as e:
                    print(f"Erro ao buscar Steam ID {app_id}: {e}")
                
                # Pequena pausa para não floodar a API da Steam localmente se a lista for gigante
                await asyncio.sleep(1) 
                
    return news_list