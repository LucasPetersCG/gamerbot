import aiohttp

async def get_tibia_news(days=1):
    url = f"https://api.tibiadata.com/v4/news/archive/{days}"
    news_list = []

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Tratamento seguro da estrutura da API v4
                    news_wrapper = data.get('news', {})
                    if isinstance(news_wrapper, dict):
                        items = news_wrapper.get('news', [])
                    elif isinstance(news_wrapper, list):
                        items = news_wrapper
                    else:
                        items = []

                    for item in items:
                        if not isinstance(item, dict): continue

                        # --- CORREÇÃO AQUI ---
                        # Convertemos para minúsculo (.lower()) para garantir que 'news' bata com 'news'
                        raw_type = item.get('type', '').lower()
                        
                        if raw_type in ['news', 'ticker']:
                            news_list.append({
                                'id': str(item.get('id', item.get('url', 'no-id'))),
                                'title': item.get('news', 'Sem título'),
                                'link': item.get('url', ''),
                                'content': f"Categoria: {item.get('category')}. Tipo: {item.get('type')}. {item.get('news')}", 
                                'source': 'Tibia'
                            })
    except Exception as e:
        print(f"Erro ao buscar TibiaData: {e}")
    
    return news_list