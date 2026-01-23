from groq import AsyncGroq
import os

# Definição das "Personas" da IA baseadas na fonte
PROMPTS = {
    "Steam": "Atue como um jornalista de games tech e hype. Use gírias moderadas (update, nerf, buff).",
    "Tibia": "Atue como um jogador veterano de Tibia (Old School). Use termos como 'Hunt', 'Update', 'CIP'.",
    "RPG": "Atue como um Mestre de D&D (Dungeon Master) sábio e empolgado. Use termos de RPG de mesa."
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
            system_persona = PROMPTS.get(source_type, "Atue como um assistente gamer.")

            prompt = (
                f"{system_persona} "
                f"Traduza e resuma a seguinte notícia para PT-BR. "
                f"Seja direto, evite introduções longas como 'Aqui está o resumo'. "
                f"Use formatação Markdown (negrito) para destacar pontos chave.\n\n"
                f"TÍTULO ORIGINAL: {title}\n"
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