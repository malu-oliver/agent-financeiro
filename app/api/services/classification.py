import re
from typing import Dict, Optional
from app.core.utils.text_processing import clean_text, normalizar_texto

class ProfileClassifier:
    def __init__(self):
        self.regex_patterns = self._load_regex_patterns()
    
    def _load_regex_patterns(self) -> Dict:
        return {
            "conservador": [
                r"seguran[çc]a", r"estabil(?:e|izado|idade)?", r"reserva(s)?",
                r"aposentad(?:o|a|oria)", r"baixo(?:s)? risco(?:s)?", r"prote[cç][aã]o",
                r"garantia(s)?", r"seguro(s)?", r"poupan(?:ça|ca)", r"renda fixa",
                r"\btesouro\b", r"\bcdbs?\b", r"conservador(?:a|es)?"
            ],
            "moderado": [
                r"equil[ií]br(?:io|ar|ado)?", r"diversifica(?:r|[ãa]o|dor)?",
                r"m[eé]dio(?:s)? prazo", r"balancead(?:o|a|as)?", r"misto",
                r"modera(?:do|r)?", r"entre.*(risco|retorno)", r"prudente",
                r"cauteloso", r"diversificar carteira"
            ],
            "agressivo": [
                r"crescimento", r"alto(?:s)? retorno(?:s)?", r"alto(?:s)? risco(?:s)?",
                r"longo(?:s)? prazo(s)?", r"\ba[cç][oõ]es?\b", r"renda variavel",
                r"lucro", r"maximi[sz]ar", r"multiplicar", r"alavancagem",
                r"day trade|trading", r"criptomoedas?|crypto", r"agressivo(s)?"
            ]
        }
    
    def classify_profile(self, objective: str, auto_classificacao: Optional[str] = None, referencia_texto: Optional[str] = None, historico: list = None) -> Dict[str, float]:
        """Classifica perfil com base no objetivo e histórico"""
        texto = normalizar_texto(objective)
        if referencia_texto:
            texto += " " + normalizar_texto(referencia_texto)
        
        scores = {perfil: 0 for perfil in self.regex_patterns}
        
        # Análise por regex
        for perfil, padroes in self.regex_patterns.items():
            for padrao in padroes:
                if re.search(padrao, texto):
                    scores[perfil] += 2  # Peso maior para regex
        
        # Considerar auto-classificação do usuário
        if auto_classificacao and auto_classificacao in scores:
            scores[auto_classificacao] += 3 # Peso ainda maior para auto-classificação

        # Análise de histórico se disponível
        if historico:
            for conversa in historico[-3:]:  # Últimas 3 conversas
                perfil_anterior = conversa.get('profile', '')
                if perfil_anterior and perfil_anterior in scores:
                    scores[perfil_anterior] += 1
        
        total = sum(scores.values())
        if total == 0:
            # Se não houver score, retorna uma distribuição igual
            return {"conservador": 33.3, "moderado": 33.3, "agressivo": 33.3}
        
        # Normaliza os scores para percentuais
        return {k: (v/total)*100 for k, v in scores.items()}