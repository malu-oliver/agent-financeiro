import os
import google.generativeai as genai
import re
from app.core.config.settings import settings

class IAGenerator:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        genai.configure(api_key=self.api_key)

    async def check_connection(self) -> bool:
        """Verifica a conexão com a API da IA (Google Gemini)."""
        return bool(self.api_key)

    async def generate_content(self, profile: str, user_data: dict, objective: str, conversation_context: str = "") -> str:
        """Gera conteúdo educativo personalizado usando o Google Gemini AI."""
        if not await self.check_connection():
            return "A conexão com o serviço de IA não pôde ser estabelecida. Verifique a configuração da chave de API (GEMINI_API_KEY)."

        prompt = self._build_prompt(profile, user_data, objective, conversation_context)

        try:
            model = genai.GenerativeModel("models/gemini-2.5-flash")
            response = model.generate_content(prompt)
            
            conteudo_bruto = response.text.strip()
            paragrafos = self._format_to_three_paragraphs(conteudo_bruto)
            return "\n\n".join(paragrafos)

        except Exception as e:
            print(f"Erro ao gerar conteúdo com Gemini: {e}")
            return f"Ocorreu um erro ao gerar o conteúdo financeiro: {str(e)}. Por favor, tente novamente mais tarde."

    def _build_prompt(self, profile: str, user_data: dict, objective: str, conversation_context: str = "") -> str:
        """Constrói o prompt para a IA com base nos dados do usuário e perfil."""
        name = user_data.get("nome", "usuário")
        age = user_data.get("idade", "não informada")
        income = user_data.get("renda_mensal", "não informada")

        # Build conversation context section
        context_section = ""
        if conversation_context:
            context_section = f"HISTÓRICO DE CONVERSAS ANTERIORES:\n{conversation_context}\n"

        prompt = f"""Atue como um educador financeiro especialista. Crie um conteúdo educativo personalizado para:

DADOS PESSOAIS:
- Nome: {name}
- Idade: {age} anos
- Renda mensal: R$ {income:.2f}
- Perfil classificado: {profile}
- Objetivo específico: {objective}

{context_section}

INSTRUÇÕES:
- Escreva EXATAMENTE 3 parágrafos educativos
- Cada parágrafo deve ter entre 4 a 6 frases
- Adapte o conteúdo ao perfil {profile}
- Use linguagem acessível e educativa
- Inclua conceitos financeiros relevantes para o perfil
- Mantenha um tom motivador e didático
- SEPARE cada parágrafo com uma linha em branco

ESTRUTURA:
1º PARÁGRAFO: Explicar conceitos fundamentais adequados ao perfil {profile}
2º PARÁGRAFO: Orientações práticas específicas para o objetivo mencionado
3º PARÁGRAFO: Dicas de educação financeira e próximos passos recomendados

NÃO use formatação Markdown, bullets points ou listas. Apenas texto corrido em 3 parágrafos separados por linha em branco.
"""
        return prompt

    def _format_to_three_paragraphs(self, text: str) -> list[str]:
        """Processa o texto bruto da IA para garantir exatamente 3 parágrafos."""
        paragrafos = re.split(r'\n\s*\n', text)
        paragrafos = [p.strip() for p in paragrafos if p.strip()]

        if len(paragrafos) < 3:
            if len(paragrafos) == 1:
                frases = re.split(r'(?<=[.!?])\s+', paragrafos[0])
                if len(frases) >= 3:
                    terco = len(frases) // 3
                    paragrafos = [
                        ". ".join(frases[:terco]) + ("." if frases[:terco] and not frases[:terco][-1].endswith(('.', '!', '?')) else ''),
                        ". ".join(frases[terco:2*terco]) + ("." if frases[terco:2*terco] and not frases[terco:2*terco][-1].endswith(('.', '!', '?')) else ''),
                        ". ".join(frases[2*terco:]) + ("." if frases[2*terco:] and not frases[2*terco:][-1].endswith(('.', '!', '?')) else '')
                    ]
                else:
                    paragrafos = paragrafos + ["", ""]
            elif len(paragrafos) == 2:
                paragrafos.append("")
        elif len(paragrafos) > 3:
            paragrafos = paragrafos[:3]
        
        # Garantir que todos os parágrafos tenham conteúdo, se possível
        for i in range(3):
            if i >= len(paragrafos) or not paragrafos[i]:
                paragrafos.insert(i, "[Conteúdo adicional não gerado ou vazio]")
                paragrafos = paragrafos[:3] # Garante que não exceda 3 após inserção

        return paragrafos

