from typing import Dict, List, Tuple
import unicodedata
import re
from collections import Counter

def clean_text(text: str) -> str:
    """
    Normalização avançada com regex + preservação de aprendizado
    """
    text = str(text).lower()

    # Normalização: Usando NFD para melhor remoção de acentos
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

    # STOPWORDS: Remove palavras irrelevantes para melhor precisão
    STOPWORDS = {'de', 'para', 'com', 'em', 'o', 'a', 'os', 'as', 'um',
                 'uma', 'e', 'da', 'do', 'das', 'dos', 'na', 'no', 'nas', 'nos'}

    # Remove caracteres especiais mas preserva espaços para STOPWORDS
    text = re.sub(r"[^\w\s]", "", text)

    # Remove STOPWORDS mantendo palavras importantes
    palavras = [palavra for palavra in text.split()
                if palavra not in STOPWORDS and len(palavra) > 2]

    return ' '.join(palavras)


class ProfileClassifier:
    def __init__(self):
        # APRENDIZADO CONTÍNUO: Armazena padrões de classificação
        self.classification_history = {}  # Histórico local por usuário
        self.pattern_effectiveness = {}  # Aprende efetividade dos padrões regex
        self.regex_patterns = self._initialize_regex_patterns()

    def _initialize_regex_patterns(self) -> Dict[str, List[str]]:
        """
        PADRÕES REGEX INTELIGENTES - Combina precisão linguística com capacidade de evolução
        """
        return {
            'conservador': [
                r'seguran[çc]a',
                r'estabil(?:e|izado|idade)',
                r'reserva(?:s)?(?:\s+financeira)?',
                r'aposentad(?:o|a|oria)',
                r'baixo(?:s)?\s+risco(?:s)?',
                r'garantia(?:s)?',
                r'proteg(?:er|ido|ao)',
                r'poupan[çc]a',
                r'conserv(?:ar|ador|ativa)',
                r'sem\s+risco',
                r'seguro(?:s)?',
                r'renda\s+fixa',
                r'tesouro',
                r'cdb(?:s)?',
                r'debentur(?:e|as)?',
                r'prote[cç][aã]o'
            ],
            'moderado': [
                r'equil[ií]brio?(?:ar|ado)?',
                r'diversifica(?:r|[çã]ao|do)',
                r'm[eé]dio(?:s)?\s+prazo',
                r'balancead(?:o|a|as)?',
                r'misto(?:s)?',
                r'moderado(?:s)?',
                r'gradual(?:mente)?',
                r'paulatinam(?:ente)?',
                r'prudente',
                r'cauteloso',
                r'diversificar\s+carteira',
                r'alocac(?:ã|a)o\s+estrat[eé]gica',
                r'entre.*(risco|retorno)',
                r'meio\s+termo'
            ],
            'agressivo': [
                r'crescimento',
                r'alto(?:s)?\s+retorno(?:s)?',
                r'alto(?:s)?\s+risco(?:s)?',
                r'longo(?:s)?\s+prazo(?:s)?',
                r'maximi[sz]ar',
                r'multiplicar',
                r'agressiv(?:o|a|amente)',
                r'expans(?:ao|ivo)',
                r'arriscar',
                r'lucr(?:o|ar)\s+(?:alto|maximo)',
                r'rapid(?:o|amente)',
                r'a[cç][oõ]es?',
                r'renda\s+variavel',
                r'especula(?:r|ção|coes)',
                r'alavancagem|alavancar',
                r'day\s+trade|swing\s+trade|trading',
                r'criptomoedas?|crypto(?:s)?',
                r'arrojad(?:o|a|os|as)?'
            ]
        }

    def classify_profile(self, objective: str, user_id: str = None) -> Dict[str, float]:
        """
        MELHORIA HÍBRIDA: Classifica perfil usando apenas regex patterns
        """
        cleaned_objective = clean_text(objective)
        scores = {profile: 0.0 for profile in ['conservador', 'moderado', 'agressivo']}

        # Classificação com regex patterns + confiança
        regex_confidence = self._classify_with_regex(cleaned_objective, scores)

        # PERCEPÇÃO AMBIENTAL: Ajuste baseado em padrões históricos do usuário
        if user_id and user_id in self.classification_history:
            user_history = self.classification_history[user_id]

            # Extrai perfis do histórico
            profiles_only = []
            confidences = []
            for record in user_history:
                if isinstance(record, dict):
                    profiles_only.append(record['profile'])
                    confidences.append(record.get('confidence', 1.0))
                else:
                    profiles_only.append(record)  # Registro legacy
                    confidences.append(1.0)  # Confiança padrão

            # Se o usuário teve consistência em um perfil, dá peso extra
            if profiles_only:
                most_common_profile = max(set(profiles_only), key=profiles_only.count)
                if most_common_profile and most_common_profile in scores:
                    scores[most_common_profile] += 0.5  # Bônus de consistência

        total_score = sum(scores.values())
        if total_score == 0:
            # AUTONOMIA: Retorna classificação inteligente baseada em padrões globais
            percentages = self._intelligent_default_classification(cleaned_objective)
            confidence = 0.3  # Baixa confiança para classificação por fallback
        else:
            # Calcula a porcentagem de cada perfil
            percentages = {
                profile: (score / total_score) * 100
                for profile, score in scores.items()
            }
            # Confiança baseada nos regex patterns
            confidence = min(regex_confidence, 1.0)

        # NOVA FUNCIONALIDADE: Adiciona informação de confiança
        result = {
            **percentages,
            '_confidence': round(confidence, 2),
            '_matches': {
                'regex_matches': regex_confidence > 0,
                'total_matches': sum(scores.values())
            }
        }

        # APRENDIZADO: Registra esta classificação para futuro aprendizado
        self._learn_from_classification(user_id, percentages, cleaned_objective, confidence)

        return result

    def _classify_with_regex(self, cleaned_text: str, scores: Dict[str, float]) -> float:
        """
        Classificação precisa usando regex patterns
        """
        total_matches = 0
        pattern_matches = {profile: 0 for profile in scores.keys()}

        for profile, patterns in self.regex_patterns.items():
            for pattern in patterns:
                try:
                    matches = len(re.findall(pattern, cleaned_text, re.IGNORECASE))
                    if matches > 0:
                        # APRENDIZADO: Aplica efetividade aprendida para padrões regex
                        effectiveness = self.pattern_effectiveness.get(pattern, 1.0)
                        weighted_matches = matches * effectiveness
                        scores[profile] += weighted_matches
                        pattern_matches[profile] += matches
                        total_matches += matches
                except re.error:
                    # Ignora padrões regex inválidos
                    continue

        # Calcula confiança baseada na quantidade e qualidade dos matches
        confidence = min(total_matches / 3.0, 1.0) if total_matches > 0 else 0.0

        # APRENDIZADO: Registra padrões utilizados para futura otimização
        self._learn_pattern_effectiveness(pattern_matches, cleaned_text)

        return confidence

    def _learn_pattern_effectiveness(self, pattern_matches: Dict[str, int], objective: str):
        """
        APRENDIZADO CONTÍNUO: Aprende efetividade dos padrões regex
        """
        # Identifica o perfil dominante baseado nos matches
        if not any(pattern_matches.values()):
            return

        dominant_profile = max(pattern_matches, key=pattern_matches.get)

        # Atualiza efetividade dos padrões baseado no sucesso
        for profile, patterns in self.regex_patterns.items():
            for pattern in patterns:
                try:
                    if re.search(pattern, objective, re.IGNORECASE):
                        if pattern not in self.pattern_effectiveness:
                            self.pattern_effectiveness[pattern] = 1.0

                        # Se o perfil do padrão coincide com o dominante, aumenta efetividade
                        if profile == dominant_profile:
                            self.pattern_effectiveness[pattern] = min(
                                2.0, self.pattern_effectiveness[pattern] + 0.05)
                        else:
                            # Diminui efetividade se não coincide
                            self.pattern_effectiveness[pattern] = max(
                                0.7, self.pattern_effectiveness[pattern] - 0.02)
                except re.error:
                    continue

    def _intelligent_default_classification(self, cleaned_objective: str) -> Dict[str, float]:
        """AUTONOMIA: Classificação inteligente quando não há padrões diretos."""
        # Análise semântica básica baseada em padrões aprendidos
        objective_length = len(cleaned_objective.split())

        # PERCEPÇÃO: Objetivos mais longos tendem a ser mais detalhados (moderado)
        if objective_length > 20:
            return {"conservador": 25.0, "moderado": 55.0, "agressivo": 20.0}
        # Objetivos curtos podem indicar urgência (agressivo)
        elif objective_length < 8:
            return {"conservador": 20.0, "moderado": 30.0, "agressivo": 50.0}

        # Detecção de contexto por padrões linguísticos
        risk_indicators = ["rapido", "urgente", "muito", "maximo", "alto"]
        safety_indicators = ["seguro", "tranquilo", "estavel", "sem", "proteger"]

        risk_score = sum(1 for indicator in risk_indicators if indicator in cleaned_objective)
        safety_score = sum(1 for indicator in safety_indicators if indicator in cleaned_objective)

        if safety_score > risk_score:
            return {"conservador": 60.0, "moderado": 30.0, "agressivo": 10.0}
        elif risk_score > safety_score:
            return {"conservador": 15.0, "moderado": 35.0, "agressivo": 50.0}

        return {"conservador": 33.3, "moderado": 33.3, "agressivo": 33.3}

    def _learn_from_classification(self, user_id: str, profile: Dict[str, float], objective: str, confidence: float):
        """
        APRENDIZADO CONTÍNUO: Aprende com cada classificação para melhorar futuras respostas
        """
        if not user_id:
            return

        if user_id not in self.classification_history:
            self.classification_history[user_id] = []

        # Identifica o perfil dominante
        dominant_profile = max(profile, key=profile.get)

        # Carrega perfil anterior do histórico local
        previous_profile = None
        if self.classification_history[user_id]:
            last_record = self.classification_history[user_id][-1]
            previous_profile = last_record['profile'] if isinstance(last_record, dict) else last_record

        # Nova lógica de aprendizado
        efficacy_adjustment = 0.05  # Recompensa padrão
        if previous_profile and previous_profile != dominant_profile:
            efficacy_adjustment = -0.1  # Penaliza se perfil mudou (indica erro)

        matched_keywords = []
        for pattern in self.regex_patterns[dominant_profile]:
            if re.search(pattern, objective, re.IGNORECASE):
                matched_keywords.append(pattern)

        for keyword in matched_keywords:
            # Atualiza eficácia no dicionário
            self.pattern_effectiveness[keyword] = self.pattern_effectiveness.get(keyword, 1.0) + efficacy_adjustment
            if self.pattern_effectiveness[keyword] < 0:  # Limite mínimo
                self.pattern_effectiveness[keyword] = 0

        # Registra classificação com confiança
        classification_record = {
            'profile': dominant_profile,
            'confidence': confidence,
            'timestamp': len(self.classification_history[user_id])
        }

        self.classification_history[user_id].append(classification_record)

        # Mantém apenas os últimos 15 registros por usuário
        if len(self.classification_history[user_id]) > 15:
            self.classification_history[user_id] = self.classification_history[user_id][-15:]

    def analyze_user_evolution(self, user_id: str) -> Dict[str, any]:
        """
        PERCEPÇÃO AMBIENTAL MELHORADA: Analisa evolução com dados de confiança
        """
        if user_id not in self.classification_history:
            return {"evolution": "no_data", "consistency": 0, "trend": "unknown", "avg_confidence": 0.0, "trend_score": 0.0, "history_length": 0, "recent_changes": 0, "data_quality": 0.0, "confidence_trend": "stable"}

        history = self.classification_history[user_id]

        # Compatibilidade com registros antigos (strings) e novos (dicionários)
        profiles = []
        confidences = []

        for record in history:
            if isinstance(record, dict):
                profiles.append(record['profile'])
                confidences.append(record.get('confidence', 1.0))
            else:
                profiles.append(record)  # Registro legacy
                confidences.append(1.0)  # Confiança padrão para registros antigos

        # Calcula consistência
        profile_counts = Counter(profiles)
        if profiles:
            most_common_profile = profile_counts.most_common(1)[0]
            consistency = most_common_profile[1] / len(profiles)
        else:
            most_common_profile = ("no_data", 0)
            consistency = 0

        # Calcula confiança média
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Detecta tendência de mudança
        recent_profiles = profiles[-5:] if len(profiles) >= 5 else profiles
        if len(set(recent_profiles)) == 1:
            trend = "stable"
        elif len(recent_profiles) >= 3:
            recent_changes = len(set(recent_profiles))
            if recent_changes >= 3:
                trend = "exploring"  # Mudando muito
            elif recent_profiles[-1] != recent_profiles[0]:
                trend = "evolving"   # Mudança gradual
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        # Cálculo de trend_score numérico
        profile_map = {'conservador': 1, 'moderado': 2, 'agressivo': 3}
        numeric_profiles = [profile_map.get(p, 0) for p in profiles]
        if len(numeric_profiles) >= 2:
            half = len(numeric_profiles) // 2
            old_profiles = numeric_profiles[:half]
            recent_profiles_num = numeric_profiles[half:]
            trend_score = (sum(recent_profiles_num) / len(recent_profiles_num)) - (sum(old_profiles) / len(old_profiles)) if old_profiles else 0
        else:
            trend_score = 0

        # Análise de qualidade dos dados
        high_confidence_classifications = sum(1 for c in confidences if c >= 0.7)
        data_quality = high_confidence_classifications / len(confidences) if confidences else 0.0

        return {
            "evolution": most_common_profile[0],
            "consistency": round(consistency, 2),
            "trend": trend,
            "trend_score": round(trend_score, 2),
            "history_length": len(profiles),
            "recent_changes": len(set(recent_profiles)) if len(recent_profiles) > 1 else 0,
            "avg_confidence": round(avg_confidence, 2),
            "data_quality": round(data_quality, 2),
            "confidence_trend": "improving" if len(confidences) > 1 and confidences[-1] > confidences[0] else "stable"
        }

    def get_system_stats(self) -> Dict[str, any]:
        """
        Estatísticas do sistema de aprendizado
        """
        total_users = len(self.classification_history)
        total_classifications = sum(len(history) for history in self.classification_history.values())

        # Estatísticas de efetividade dos padrões
        avg_pattern_effectiveness = sum(self.pattern_effectiveness.values()) / len(self.pattern_effectiveness) if self.pattern_effectiveness else 1.0

        # Análise de qualidade dos dados
        all_confidences = []
        for history in self.classification_history.values():
            for record in history:
                if isinstance(record, dict):
                    all_confidences.append(record.get('confidence', 1.0))
                else:
                    all_confidences.append(1.0)

        avg_system_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0

        return {
            "learning_status": {
                "total_users": total_users,
                "total_classifications": total_classifications,
                "avg_classifications_per_user": round(total_classifications / total_users, 1) if total_users > 0 else 0
            },
            "effectiveness": {
                "patterns_learned": len(self.pattern_effectiveness),
                "avg_pattern_effectiveness": round(avg_pattern_effectiveness, 2)
            },
            "quality": {
                "avg_confidence": round(avg_system_confidence, 2),
                "high_confidence_percentage": round(sum(1 for c in all_confidences if c >= 0.7) / len(all_confidences) * 100, 1) if all_confidences else 0.0
            },
            "agent_characteristics": {
                "autonomy": "active" if total_classifications > 0 else "inactive",
                "learning": "active" if self.pattern_effectiveness else "inactive",
                "perception": "active" if total_users > 0 else "inactive",
                "adaptation": "active" if any(len(history) > 3 for history in self.classification_history.values()) else "inactive"
            }
        }