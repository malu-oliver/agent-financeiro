import os
import google.generativeai as genai
import re
from app.config.settings import settings
import random
from collections import Counter
import logging

# Configura logging para depuração
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IAGenerator:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                logger.info("✅ Google Gemini API configurada com sucesso!")
            except Exception as e:
                logger.error(f"❌ Erro ao configurar Gemini API: {e}")
        else:
            logger.warning("⚠️ GEMINI_API_KEY não configurada - usando modo fallback")
        
        # Sistema de autonomia - decisões baseadas em contexto
        self.user_contexts = {}  # Cache de contextos por usuário
        self.interaction_count = {}  # Contador de interações
        self.autonomous_triggers = {
            "low_engagement": 3,
            "profile_drift": 0.3,
            "content_repetition": 2
        }

    async def check_connection(self) -> bool:
        """Verifica a conexão com a API da IA (Google Gemini)."""
        if not self.api_key:
            logger.warning("⚠️ Nenhuma chave de API fornecida.")
            return False
        try:
            models = genai.list_models()
            available_models = [m.name for m in models]
            logger.info(f"✅ Conexão com Gemini API bem-sucedida. Modelos disponíveis: {available_models}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao verificar conexão Gemini: {e}")
            return False

    async def generate_content(self, profile: str, user_data: dict, objective: str, user_id: str = None) -> str:
        """Gera conteúdo educativo personalizado usando o Google Gemini AI com comportamento autônomo."""
        logger.info(f"Gerando conteúdo para user_id={user_id}, perfil={profile}, objetivo={objective}")
        if not self.api_key:
            logger.warning("Usando modo fallback devido à ausência de GEMINI_API_KEY.")
            return await self._generate_fallback_content(profile, user_data, objective)
        
        if not await self.check_connection():
            logger.warning("Usando modo fallback devido a falha na conexão com Gemini API.")
            return await self._generate_fallback_content(profile, user_data, objective)

        content_strategy = await self._autonomous_content_strategy(user_id, profile, user_data, objective)
        prompt = self._build_prompt(profile, user_data, objective, content_strategy)

        try:
            model = genai.GenerativeModel("gemini-2.5-flash")  # Atualizado para modelo disponível
            response = model.generate_content(prompt)
            logger.info("✅ Conteúdo gerado com sucesso pela Gemini API.")

            if not response.text:
                logger.warning("Resposta da Gemini API vazia, usando modo fallback.")
                return await self._generate_fallback_content(profile, user_data, objective)

            conteudo_bruto = response.text.strip()
            paragrafos = self._format_to_three_paragraphs(conteudo_bruto)

            await self._learn_from_interaction(user_id, profile, content_strategy, len(conteudo_bruto))

            return "\n\n".join(paragrafos)

        except Exception as e:
            logger.error(f"❌ Erro ao gerar conteúdo com Gemini: {e}")
            return await self._generate_fallback_content(profile, user_data, objective)

    async def _generate_fallback_content(self, profile: str, user_data: dict, objective: str) -> str:
        """Gera conteúdo fallback conciso e personalizado usando todos os campos do schema."""
        name = user_data.get("nome", "investidor")
        age = user_data.get("idade", "")
        income = user_data.get("renda", "")
        invest_value = user_data.get("valor_investir", 0)
        self_classification = user_data.get("auto_classificacao", "não informado")
        references = user_data.get("referencias", "nenhuma referência fornecida")
        
        age_text = f", {age} anos" if age else ""
        income_text = f", renda de R$ {income:,.2f}/mês" if income else ""
        invest_text = f"R$ {invest_value:,.2f}" if invest_value else "seus recursos"
        self_class_text = f"Você se identifica como '{self_classification}', alinhado ao perfil {profile}." if self_classification != "não informado" else ""
        references_text = f"Sua referência a '{references}' sugere confiança em renda fixa." if "renda fixa" in references.lower() else ""

        # Análise do objetivo
        objective_lower = objective.lower()
        is_car_purchase = "carro" in objective_lower or "veículo" in objective_lower
        has_emergency_fund = "reserva" in objective_lower
        timeline = "1-3 anos" if is_car_purchase else "médio a longo prazo"

        if profile == "conservador":
            para1 = f"{name}{age_text}{income_text}, seu objetivo de {objective} combina com seu perfil conservador. {self_class_text} {references_text} Com {invest_text}, você pode comprar um carro em {timeline}. Sua reserva permite focar diretamente no objetivo."
            
            para2 = f"Invista {invest_text} em Tesouro Selic para segurança e acesso rápido. CDBs com 100% do CDI e cobertura do FGC são confiáveis. LCIs de 6-24 meses oferecem isenção fiscal."
            
            para3 = f"Abra uma conta numa corretora confiável. Acompanhe seus investimentos mensalmente. Estude renda fixa em vídeos gratuitos. Consulte um planejador para ajustar ao preço do carro."

        elif profile == "moderado":
            para1 = f"{name}{age_text}{income_text}, seu objetivo de {objective} alinha-se ao perfil moderado. {self_class_text} {references_text} Com {invest_text}, você pode comprar um carro em {timeline}. Sua reserva permite buscar retorno moderado."
            
            para2 = f"Aloque 60% de {invest_text} em Tesouro IPCA+ e CDBs para segurança. Use 40% em ETFs ou fundos imobiliários para crescimento. Escolha prazos de {timeline}."
            
            para3 = f"Pesquise corretoras e revise sua carteira trimestralmente. Estude diversificação em blogs gratuitos. Consulte um assessor para alinhar ao plano do carro. Você está no caminho certo."

        else:
            para1 = f"{name}{age_text}{income_text}, seu objetivo de {objective} combina com seu perfil agressivo. {self_class_text} {references_text} Com {invest_text}, você pode buscar altos retornos em {timeline}. Sua reserva permite riscos calculados."
            
            para2 = f"Invista 50% de {invest_text} em ações ou ETFs para crescimento. Aloque 20% em fundos imobiliários e 30% em Tesouro IPCA+. Considere 5% em criptomoedas com cautela."
            
            para3 = f"Monitore o mercado semanalmente. Estude renda variável em fóruns gratuitos. Consulte um especialista para ajustar ao plano do carro. Com dedicação, seu objetivo está ao alcance."

        return f"{para1}\n\n{para2}\n\n{para3}"

    def _build_prompt(self, profile: str, user_data: dict, objective: str, strategy: dict = None) -> str:
        """Constrói o prompt para a IA com base nos dados do usuário, perfil e estratégia autônoma."""
        name = user_data.get("nome", "usuário")
        age = user_data.get("idade", "não informada")
        income = user_data.get("renda", "não informada")
        invest_value = user_data.get("valor_investir", 0)
        self_classification = user_data.get("auto_classificacao", "não informado")
        references = user_data.get("referencias", "nenhuma referência fornecida")

        content_type = strategy.get("type", "educativo") if strategy else "educativo"
        focus_area = strategy.get("focus", "conceitos básicos") if strategy else "conceitos básicos"
        complexity = strategy.get("complexity", "intermediário") if strategy else "intermediário"

        # Análise do objetivo
        objective_lower = objective.lower()
        is_car_purchase = "carro" in objective_lower or "veículo" in objective_lower
        has_emergency_fund = "reserva" in objective_lower
        timeline = "curto a médio prazo (1-3 anos)" if is_car_purchase else "médio a longo prazo"

        prompt = f"""Você é um consultor financeiro especializado em educação financeira.

DADOS DO CLIENTE:
- Nome: {name}
- Idade: {age} anos
- Renda mensal: R$ {income:,.2f}
- Valor para investir: R$ {invest_value:,.2f}
- Perfil de investidor: {profile.upper()}
- Objetivo financeiro: "{objective}"
- Autoclassificação do cliente: {self_classification}
- Referências do cliente: {references}
- Possui reserva de emergência: {'Sim' if has_emergency_fund else 'Não'}
- Horizonte de tempo: {timeline}

CONTEXTO:
- Tipo de conteúdo: {content_type}
- Foco: {focus_area}
- Detalhamento: {complexity}

INSTRUÇÕES:
1. Escreva EXATAMENTE 3 parágrafos
2. Cada parágrafo com 3-4 frases curtas e claras
3. Use linguagem simples, educativa e motivadora
4. Personalize para o perfil {profile} e objetivo "{objective}"
5. Inclua recomendações práticas para o prazo e objetivo
6. Explique por que as recomendações são adequadas
7. Use autoclassificação e referências para confiança
8. Foque no objetivo se há reserva; senão, sugira reserva
9. Evite jargões e mantenha clareza
10. Não use marcadores ou formatação complexa

ESTRUTURA:
1º PARÁGRAFO: Perfil e objetivo, com autoclassificação e referências
2º PARÁGRAFO: Investimentos adequados ao objetivo e prazo
3º PARÁGRAFO: Plano de ação com foco em educação financeira

Comece diretamente com o primeiro parágrafo:"""

        logger.info(f"Prompt construído: {prompt[:200]}...")  # Log parcial do prompt
        return prompt

    def _format_to_three_paragraphs(self, text: str) -> list[str]:
        """Processa o texto bruto da IA para garantir exatamente 3 parágrafos."""
        text = re.sub(r'```[\s\S]*?```', '', text)
        paragrafos = re.split(r'\n\s*\n', text)
        paragrafos = [p.strip() for p in paragrafos if p.strip()]
        
        cleaned_paragrafos = []
        for p in paragrafos:
            cleaned_p = re.sub(r'^(\d+\.\s*|[-*•]\s*)', '', p)
            cleaned_paragrafos.append(cleaned_p)

        if len(cleaned_paragrafos) < 3:
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
                    cleaned_paragrafos = cleaned_paragrafos + ["", ""]
            elif len(cleaned_paragrafos) == 2:
                cleaned_paragrafos.append("")
        
        if len(cleaned_paragrafos) > 3:
            cleaned_paragrafos = cleaned_paragrafos[:3]
        elif len(cleaned_paragrafos) < 3:
            while len(cleaned_paragrafos) < 3:
                cleaned_paragrafos.append("")

        return cleaned_paragrafos

    async def _autonomous_content_strategy(self, user_id: str, profile: str, user_data: dict, objective: str) -> dict:
        """AUTONOMIA: Decide automaticamente a melhor estratégia de conteúdo baseada no contexto do usuário."""
        if not user_id:
            return {"type": "educativo", "focus": "fundamentos do perfil " + profile, "complexity": "intermediário"}

        context = self.user_contexts.get(user_id, {
            "previous_profiles": [],
            "content_types_used": [],
            "engagement_level": 0,
            "learning_progress": "iniciante",
            "interacoes_anteriores": 0
        })
        interacoes_anteriores = context.get('interacoes_anteriores', 0)
        self.autonomous_triggers['profile_drift'] = 0.3 + (0.1 * interacoes_anteriores / 10)

        strategies = ['educativo', 'interativo', 'especializado', 'transicional']
        if interacoes_anteriores > 5:
            content_type = random.choice(strategies) if random.random() > 0.7 else 'transicional'
        else:
            content_type = 'educativo'

        if context["previous_profiles"] and context["previous_profiles"][-1] != profile:
            return {
                "type": "transicional",
                "focus": f"transição do perfil {context['previous_profiles'][-1]} para {profile}",
                "complexity": "avançado"
            }

        interaction_count = self.interaction_count.get(user_id, 0)
        if interaction_count >= self.autonomous_triggers["low_engagement"]:
            return {
                "type": "avançado",
                "focus": "estratégias específicas e otimização de carteira",
                "complexity": "detalhado"
            }

        if context["learning_progress"] == "avançado":
            return {
                "type": "especializado",
                "focus": "técnicas avançadas e cenários complexos",
                "complexity": "especialista"
            }

        focus_areas = {
            "conservador": f"preservação de capital para {objective}",
            "moderado": f"equilíbrio entre risco e retorno para {objective}",
            "agressivo": f"crescimento acelerado para {objective}"
        }

        return {
            "type": content_type,
            "focus": focus_areas.get(profile, f"fundamentos financeiros para {objective}"),
            "complexity": "intermediário"
        }

    async def _environmental_perception(self, user_id: str) -> str:
        """PERCEPÇÃO AMBIENTAL: Avalia consistência do usuário com base no histórico local."""
        context = self.user_contexts.get(user_id, {
            "previous_profiles": [],
            "engagement_level": 0,
            "learning_progress": "iniciante",
            "interacoes_anteriores": 0
        })
        profiles = context["previous_profiles"]
        
        if len(profiles) < 2:
            perception = 'insufficient_data'
        else:
            profile_counts = Counter(profiles)
            most_common_profile = profile_counts.most_common(1)[0]
            user_consistency = most_common_profile[1] / len(profiles)
            avg_global_consistency = 0.5  # Valor padrão
            perception = 'exploring' if user_consistency < avg_global_consistency - 0.2 else 'stable'
        
        context['perception'] = perception
        return perception

    async def _learn_from_interaction(self, user_id: str, profile: str, strategy: dict, content_length: int):
        """APRENDIZADO CONTÍNUO: Aprende com cada interação para melhorar futuras respostas."""
        if not user_id:
            return

        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = {
                "previous_profiles": [],
                "content_types_used": [],
                "engagement_level": 0,
                "learning_progress": "iniciante",
                "interacoes_anteriores": 0,
                "perception": "insufficient_data",
                "plans": [],
                "evolution": {"trend": "stable"}
            }

        context = self.user_contexts[user_id]
        if profile not in context["previous_profiles"][-3:]:
            context["previous_profiles"].append(profile)
            if len(context["previous_profiles"]) > 3:
                context["previous_profiles"] = context["previous_profiles"][-3:]

        content_type = strategy.get("type", "educativo")
        context["content_types_used"].append(content_type)

        engagement_score = min(content_length / 800, 1.0)
        context["engagement_level"] = (context["engagement_level"] + engagement_score) / 2

        if context["engagement_level"] > 0.7:
            context["learning_progress"] = "avançado"
        elif context["engagement_level"] > 0.4:
            context["learning_progress"] = "intermediário"

        context["interacoes_anteriores"] = context.get("interacoes_anteriores", 0) + 1
        self.interaction_count[user_id] = self.interaction_count.get(user_id, 0) + 1

    async def _planning_system(self, user_id: str, profile: str, learning_level: str) -> list:
        """PLANEJAMENTO: Cria planos adaptativos com priorização por perfil."""
        steps = {
            'iniciante': ['educação básica', 'orçamento pessoal', 'poupança'],
            'intermediário': ['diversificação', 'renda fixa', 'análise de risco', 'planejamento tributário'],
            'avançado': ['ações', 'fundos multimercado', 'criptomoedas', 'startups', 'revisão de portfólio']
        }.get(learning_level, ['educação básica'])
        
        if profile == 'agressivo':
            steps.insert(0, 'análise de risco avançada')
        elif profile == 'conservador':
            steps.append('construir reserva de emergência')
        
        context = self.user_contexts.get(user_id, {})
        context["plans"] = steps
        return steps

    async def get_autonomous_suggestions(self, user_id: str) -> dict:
        """SUGESTÕES AUTÔNOMAS: Retorna sugestões baseadas no aprendizado e evolução."""
        if not user_id:
            return {"suggestions": [], "autonomous_action": "none", "learning_progress": "iniciante", "interaction_count": 0}

        context = self.user_contexts.get(user_id, {
            "previous_profiles": [],
            "content_types_used": [],
            "engagement_level": 0,
            "learning_progress": "iniciante",
            "interacoes_anteriores": 0,
            "perception": "insufficient_data",
            "plans": [],
            "evolution": {"trend": "stable"}
        })
        interaction_count = self.interaction_count.get(user_id, 0)

        suggestions = []
        autonomous_action = "none"

        if interaction_count >= 3:
            suggestions.extend(["Análise de diversificação da carteira", "Revisão de metas de curto e longo prazo", "Otimização de alocação de ativos"])
            autonomous_action = "suggest_advanced_topics"

        if len(context.get("previous_profiles", [])) > 1:
            suggestions.append("Avaliação de adequação do novo perfil de risco")
            autonomous_action = "profile_evolution_detected"

        engagement = context.get("engagement_level", 0)
        if engagement > 0.7:
            suggestions.append("Exploração de estratégias avançadas e alternativas")
            autonomous_action = "high_engagement_detected"
        elif engagement < 0.3:
            suggestions.append("Reforço dos conceitos fundamentais de investimento")
            autonomous_action = "low_engagement_detected"

        if context["evolution"].get('trend') == 'evolving':
            suggestions.append('revisar objetivos anuais')

        return {
            "suggestions": suggestions,
            "autonomous_action": autonomous_action,
            "learning_progress": context.get("learning_progress", "iniciante"),
            "interaction_count": interaction_count
        }