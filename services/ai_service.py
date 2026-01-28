from groq import AsyncGroq
import os

# Definição das "Personas" da IA baseadas na fonte
PROMPTS = {
    "Steam": "Atue como um jornalista de games. Entenda o contexto de notícias de jogos de videogame e os principais jargões e tipos de palavras que se usa no contexto daquele jogo e a melhor forma de traduzí-las para o português sem perder o contexto.",
    "Tibia": "Atue como um jornalista de game focado em Tibia. Entenda o contexto de notícias de jogos de videogame e os principais jargões e tipos de palavras que se usa no contexto daquele jogo e a melhor forma de traduzí-las para o português sem perder o contexto",
    "RPG": "Atue como um jornalista de games focado em jogos de RPG de mesa. Entenda o contexto de notícias de jogos de videogame e os principais jargões e tipos de palavras que se usa no contexto daquele jogo e a melhor forma de traduzí-las para o português sem perder o contexto"
}

class AIService:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.client = AsyncGroq(api_key=self.api_key)

    async def summarize(self, title, content, source_type):
        """
        Recebe título, conteúdo e o tipo da fonte (Steam, Tibia, RPG)
        para gerar um resumo personalizado.
        """
        try:
            # Limita conteúdo para não estourar tokens ou confundir a IA
            short_content = content[:2500]
            
            # Seleciona o prompt base, ou usa um genérico se não encontrar
            system_persona = PROMPTS.get(source_type, "Atue como um jornalista de jogos.")

            prompt = (
                f"{system_persona} "
                f"Traduza e resuma a seguinte notícia para PT-BR, incluindo o nome do jogo destacado antes do resumo. "
                f"Seja direto, evite introduções longas como 'Aqui está o resumo'. "
                f"Use formatação Markdown (negrito) para destacar pontos chave.\n\n"
                f"NOME DO JOGO - TÍTULO Traduzido: {title}\n"
                f"CONTEÚDO: {short_content}"
            )

            chat_completion = await self.client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.6, # 0.6 para ser criativo mas não alucinar
            )

            return chat_completion.choices[0].message.content

        except Exception as e:
            print(f"❌ Erro na IA ({source_type}): {e}")
            return f"Não foi possível gerar o resumo via IA.\n**Título Original:** {title}"