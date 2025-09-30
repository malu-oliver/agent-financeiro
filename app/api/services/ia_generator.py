import os
import google.generativeai as genai
import re
from app.config.settings import settings


class IAGenerator:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                print("✅ Google Gemini API configurada com sucesso!")
            except Exception as e:
                print(f"❌ Erro ao configurar Gemini API: {e}")
        else:
            print("⚠️  GEMINI_API_KEY não configurada - usando modo fallback")
        
        # Sistema de autonomia - decisões baseadas em contexto
        self.user_contexts = {}  # Cache de contextos por usuário
        self.interaction_count = {}  # Contador de interações
        self.autonomous_triggers = {
            "low_engagement": 3,  # Após 3 interações básicas
            "profile_drift": 0.3,  # 30% mudança no perfil
            "content_repetition": 2  # Mesmo tipo de conteúdo 2x
        }

    async def check_connection(self) -> bool:
        """Verifica a conexão com a API da IA (Google Gemini)."""
        if not self.api_key:
            return False
        try:
            # Testa a conexão listando modelos disponíveis
            genai.list_models()
            return True
        except Exception as e:
            print(f"❌ Erro ao verificar conexão Gemini: {e}")
            return False

    async def generate_content(self, profile: str, user_data: dict, objective: str, user_id: str = None) -> str:
        """Gera conteúdo educativo personalizado usando o Google Gemini AI com comportamento autônomo."""
        
        # Verifica se a API está configurada e funcionando
        if not self.api_key:
            return await self._generate_fallback_content(profile, user_data, objective)
        
        if not await self.check_connection():
            return await self._generate_fallback_content(profile, user_data, objective)

        # AUTONOMIA: Decide automaticamente o tipo de conteúdo baseado no contexto
        content_strategy = await self._autonomous_content_strategy(user_id, profile, user_data, objective)

        prompt = self._build_prompt(
            profile, user_data, objective, content_strategy)

        try:
            # Usa um modelo mais recente e disponível
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)

            if not response.text:
                return await self._generate_fallback_content(profile, user_data, objective)

            conteudo_bruto = response.text.strip()
            paragrafos = self._format_to_three_paragraphs(conteudo_bruto)

            # APRENDIZADO: Armazena feedback implícito para melhorar próximas interações
            await self._learn_from_interaction(user_id, profile, content_strategy, len(conteudo_bruto))

            return "\n\n".join(paragrafos)

        except Exception as e:
            print(f"❌ Erro ao gerar conteúdo com Gemini: {e}")
            return await self._generate_fallback_content(profile, user_data, objective)

    async def _generate_fallback_content(self, profile: str, user_data: dict, objective: str) -> str:
        """Gera conteúdo fallback quando a API não está disponível"""
        name = user_data.get("nome", "investidor")
        age = user_data.get("idade", "")
        income = user_data.get("renda", "")
        
        age_text = f"com {age} anos" if age else ""
        income_text = f"e renda de R$ {income:,.2f}" if income else ""
        
        if profile == "conservador":
            return f"""Para você, {name} {age_text} {income_text}, que busca {objective}, como investidor conservador recomendo focar em segurança e estabilidade. A preservação do capital deve ser sua prioridade, com investimentos de baixo risco e alta liquidez.

Considere aplicar em Tesouro Direto, CDBs de bancos sólidos, LCIs e LCAs que oferecem isenção fiscal. Fundos de renda fixa e previdência privada conservadora também são opções adequadas. Mantenha uma reserva de emergência equivalente a 6 meses de despesas.

Monitore regularmente seus investimentos e ajuste conforme suas necessidades evoluam. Busque educação financeira contínua e consulte profissionais qualificados para decisões importantes. Lembre-se: consistência e paciência são fundamentais no perfil conservador."""
        
        elif profile == "moderado":
            return f"""Para você, {name} {age_text} {income_text}, que busca {objective}, como investidor moderado recomendo um equilíbrio entre segurança e crescimento. Sua estratégia pode combinar renda fixa com exposição controlada à renda variável.

Considere uma carteira com 60-70% em renda fixa (Tesouro IPCA+, CDBs, debêntures) e 30-40% em renda variável (fundos imobiliários, ações de empresas sólidas, ETFs). Fundos multimercado e ETFs internacionais podem diversificar seus riscos.

Revise sua alocação trimestralmente e rebalanceie quando necessário. Estabeleça metas claras e prazos realistas. A educação financeira é sua aliada para tomar decisões mais assertivas ao longo do tempo."""
        
        else:  # agressivo
            return f"""Para você, {name} {age_text} {income_text}, que busca {objective}, como investidor agressivo recomendo focar em crescimento patrimonial com tolerância a volatilidade. Sua carteira pode ter maior exposição a ativos de alto potencial.

Considere 40-50% em renda variável (ações growth, small caps, ETFs setoriais), 20-30% em fundos imobiliários e REITs, e o restante em renda fixa atrelada à inflação. Mercados internacionais e criptomoedas (com parcela pequena) podem oferecer diversificação.

Mantenha-se informado sobre tendências de mercado e esteja preparado para volatilidade. Diversifique entre setores e geografias. Lembre-se que alto retorno potencial vem com alto risco - invista apenas o que estiver disposto a arriscar."""

    def _build_prompt(self, profile: str, user_data: dict, objective: str, strategy: dict = None) -> str:
        """Constrói o prompt para a IA com base nos dados do usuário, perfil e estratégia autônoma."""
        name = user_data.get("nome", "usuário")
        age = user_data.get("idade", "não informada")
        income = user_data.get("renda", "não informada")
        invest_value = user_data.get("valor_investir", 0)

        # PLANEJAMENTO: Adapta prompt baseado na estratégia autônoma
        content_type = strategy.get("type", "educativo") if strategy else "educativo"
        focus_area = strategy.get("focus", "conceitos básicos") if strategy else "conceitos básicos"
        complexity = strategy.get("complexity", "intermediário") if strategy else "intermediário"

        prompt = f"""Você é um consultor financeiro especializado em educação financeira personalizada. 

DADOS DO CLIENTE:
- Nome: {name}
- Idade: {age} anos
- Renda mensal: R$ {income:,.2f}
- Valor para investir: R$ {invest_value:,.2f}
- Perfil de investidor: {profile.upper()}
- Objetivo financeiro: "{objective}"

CONTEXTO DA CONSULTA:
- Tipo de conteúdo: {content_type}
- Foco principal: {focus_area}
- Nível de detalhe: {complexity}

INSTRUÇÕES ESPECÍFICAS:
1. Escreva EXATAMENTE 3 parágrafos
2. Cada parágrafo deve ter 4-6 frases bem elaboradas
3. Use linguagem natural, educativa e motivadora
4. Personalize para o perfil {profile} e objetivo específico
5. Inclua exemplos práticos e recomendações concretas
6. Mantenha tom profissional mas acessível
7. Foque em educação financeira, não apenas recomendações

ESTRUTURA DOS PARÁGRAFOS:
1º PARÁGRAFO: Análise do perfil {profile} em relação ao objetivo "{objective}"
2º PARÁGRAFO: Estratégias específicas e produtos financeiros adequados
3º PARÁGRAFO: Plano de ação e próximos passos práticos

NÃO use marcadores, números ou formatação complexa. Apenas texto corrido natural dividido em 3 parágrafos separados por uma linha em branco.

Comece diretamente com o primeiro parágrafo:"""

        return prompt

    def _format_to_three_paragraphs(self, text: str) -> list[str]:
        """Processa o texto bruto da IA para garantir exatamente 3 parágrafos."""
        # Remove possíveis marcações de código
        text = re.sub(r'```[\s\S]*?```', '', text)
        
        # Divide por parágrafos
        paragrafos = re.split(r'\n\s*\n', text)
        paragrafos = [p.strip() for p in paragrafos if p.strip()]
        
        # Remove números e marcadores do início dos parágrafos
        cleaned_paragrafos = []
        for p in paragrafos:
            # Remove "1.", "2.", "3.", "-", "*" etc do início
            cleaned_p = re.sub(r'^(\d+\.\s*|[-*•]\s*)', '', p)
            cleaned_paragrafos.append(cleaned_p)

        if len(cleaned_paragrafos) < 3:
            # Se não tem parágrafos suficientes, divide o texto existente
            if len(cleaned_paragrafos) == 1:
                sentences = re.split(r'(?<=[.!?])\s+', cleaned_paragrafos[0])
                if len(sentences) >= 6:
                    third = len(sentences) // 3
                    cleaned_paragrafos = [
                        ' '.join(sentences[:third]),
                        ' '.join(sentences[third:2*third]),
                        ' '.join(sentences[2*third:])
                    ]
                else:
                    # Conteúdo fallback se não conseguir dividir
                    cleaned_paragrafos = cleaned_paragrafos + ["", ""]
            elif len(cleaned_paragrafos) == 2:
                cleaned_paragrafos.append("")
        
        # Garante exatamente 3 parágrafos
        if len(cleaned_paragrafos) > 3:
            cleaned_paragrafos = cleaned_paragrafos[:3]
        elif len(cleaned_paragrafos) < 3:
            while len(cleaned_paragrafos) < 3:
                cleaned_paragrafos.append("")

        return cleaned_paragrafos

    # ==================== CARACTERÍSTICAS DE AGENTE DE IA ====================

    async def _autonomous_content_strategy(self, user_id: str, profile: str, user_data: dict, objective: str) -> dict:
        """AUTONOMIA: Decide automaticamente a melhor estratégia de conteúdo baseada no contexto do usuário."""
        if not user_id:
            return {"type": "educativo", "focus": "fundamentos do perfil " + profile, "complexity": "intermediário"}

        # Carrega contexto do usuário
        context = self.user_contexts.get(user_id, {
            "previous_profiles": [],
            "content_types_used": [],
            "engagement_level": 0,
            "learning_progress": "iniciante"
        })

        # DECISÃO AUTÔNOMA 1: Detectar mudança de perfil
        if context["previous_profiles"] and context["previous_profiles"][-1] != profile:
            return {
                "type": "transicional",
                "focus": f"transição do perfil {context['previous_profiles'][-1]} para {profile}",
                "complexity": "avançado"
            }

        # DECISÃO AUTÔNOMA 2: Baseado no nível de engajamento
        interaction_count = self.interaction_count.get(user_id, 0)
        if interaction_count >= self.autonomous_triggers["low_engagement"]:
            return {
                "type": "avançado",
                "focus": "estratégias específicas e otimização de carteira",
                "complexity": "detalhado"
            }

        # DECISÃO AUTÔNOMA 3: Progressão do aprendizado
        if context["learning_progress"] == "avançado":
            return {
                "type": "especializado",
                "focus": "técnicas avançadas e cenários complexos",
                "complexity": "especialista"
            }

        # Estratégia padrão baseada no perfil
        focus_areas = {
            "conservador": "preservação de capital e segurança",
            "moderado": "equilíbrio entre risco e retorno", 
            "agressivo": "crescimento acelerado e oportunidades"
        }

        return {
            "type": "educativo",
            "focus": focus_areas.get(profile, "fundamentos financeiros"),
            "complexity": "intermediário"
        }

    async def _learn_from_interaction(self, user_id: str, profile: str, strategy: dict, content_length: int):
        """APRENDIZADO CONTÍNUO: Aprende com cada interação para melhorar futuras respostas."""
        if not user_id:
            return

        # Atualiza contexto do usuário
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = {
                "previous_profiles": [],
                "content_types_used": [],
                "engagement_level": 0,
                "learning_progress": "iniciante",
                "preferences": {}
            }

        context = self.user_contexts[user_id]

        # Aprende sobre perfis do usuário
        if profile not in context["previous_profiles"][-3:]:
            context["previous_profiles"].append(profile)
            if len(context["previous_profiles"]) > 3:
                context["previous_profiles"] = context["previous_profiles"][-3:]

        # Aprende sobre tipos de conteúdo
        content_type = strategy.get("type", "educativo")
        context["content_types_used"].append(content_type)

        # Calcula nível de engajamento baseado na qualidade da resposta
        engagement_score = min(content_length / 800, 1.0)  # Normaliza para 0-1
        context["engagement_level"] = (
            context["engagement_level"] + engagement_score) / 2

        # Evolui o nível de aprendizado
        if context["engagement_level"] > 0.7:
            context["learning_progress"] = "avançado"
        elif context["engagement_level"] > 0.4:
            context["learning_progress"] = "intermediário"

        # Atualiza contador de interações
        self.interaction_count[user_id] = self.interaction_count.get(
            user_id, 0) + 1

    async def get_autonomous_suggestions(self, user_id: str) -> dict:
        """MÉTODO PÚBLICO: Retorna sugestões autônomas para o usuário baseadas no aprendizado."""
        if not user_id:
            return {"suggestions": [], "autonomous_action": "none", "learning_progress": "iniciante", "interaction_count": 0}

        context = self.user_contexts.get(user_id, {})
        interaction_count = self.interaction_count.get(user_id, 0)

        suggestions = []
        autonomous_action = "none"

        # Sugestão autônoma baseada no progresso
        if interaction_count >= 3:
            suggestions.extend(["Análise de diversificação da carteira", "Revisão de metas de curto e longo prazo", "Otimização de alocação de ativos"])
            autonomous_action = "suggest_advanced_topics"

        # Sugestão baseada na mudança de perfil
        if len(context.get("previous_profiles", [])) > 1:
            suggestions.append("Avaliação de adequação do novo perfil de risco")
            autonomous_action = "profile_evolution_detected"

        # Sugestão baseada no nível de engajamento
        engagement = context.get("engagement_level", 0)
        if engagement > 0.7:
            suggestions.append("Exploração de estratégias avançadas e alternativas")
            autonomous_action = "high_engagement_detected"
        elif engagement < 0.3:
            suggestions.append("Reforço dos conceitos fundamentais de investimento")
            autonomous_action = "low_engagement_detected"

        return {
            "suggestions": suggestions,
            "autonomous_action": autonomous_action,
            "learning_progress": context.get("learning_progress", "iniciante"),
            "interaction_count": interaction_count
        }