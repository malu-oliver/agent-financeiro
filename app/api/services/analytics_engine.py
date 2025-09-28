from typing import List, Dict, Any
from datetime import datetime
from app.api.services import mongodb_crud
import statistics

class AnalyticsEngine:
    async def compare_with_peers(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compara usuário com outros usuários similares"""
        try:
            similar_users = await self._find_similar_users(user_data)
            
            if not similar_users:
                return {
                    "message": "Dados insuficientes para comparação no momento",
                    "total_peers": 0
                }
            
            analysis = {
                "total_peers": len(similar_users),
                "age_group_comparison": await self._analyze_age_group(similar_users, user_data['idade']),
                "income_comparison": await self._analyze_income(similar_users, user_data['renda_mensal']),
                "profile_distribution": await self._analyze_profiles(similar_users),
                "common_objectives": await self._analyze_objectives(similar_users)
            }
            
            return analysis
        except Exception as e:
            print(f"Erro na análise comparativa: {e}")
            return {"erro": "Análise comparativa temporariamente indisponível"}

    async def _find_similar_users(self, user_data: Dict, max_diff_age: int = 5, max_diff_income: float = 0.3) -> List[Dict]:
        """Encontra usuários com idade e renda similares"""
        try:
            all_users = await mongodb_crud.find_all_documents("usuarios")
            
            similar_users = []
            for user in all_users:
                if user.get('_id'):  # Evita comparar com o próprio usuário atual
                    age_diff = abs(user.get('idade', 0) - user_data['idade'])
                    income_diff = abs(user.get('renda_mensal', 0) - user_data['renda_mensal']) / max(user_data['renda_mensal'], 1)
                    
                    if age_diff <= max_diff_age and income_diff <= max_diff_income:
                        similar_users.append(user)
            
            return similar_users
        except:
            return []

    async def _analyze_age_group(self, users: List[Dict], user_age: int) -> Dict:
        """Analisa distribuição por faixa etária"""
        try:
            ages = [user.get('idade', 0) for user in users if user.get('idade')]
            
            if not ages:
                return {"faixa_etaria": self._get_age_group(user_age), "comparacao": "sem dados"}
            
            return {
                "media_idade": round(statistics.mean(ages), 1),
                "mediana_idade": statistics.median(ages),
                "faixa_etaria": self._get_age_group(user_age),
                "comparacao": "acima" if user_age > statistics.mean(ages) else "abaixo" if user_age < statistics.mean(ages) else "na media"
            }
        except:
            return {"faixa_etaria": self._get_age_group(user_age), "comparacao": "erro"}

    async def _analyze_income(self, users: List[Dict], user_income: float) -> Dict:
        """Analisa distribuição de renda"""
        try:
            incomes = [user.get('renda_mensal', 0) for user in users if user.get('renda_mensal')]
            
            if not incomes:
                return {"comparacao": "sem dados"}
            
            avg_income = statistics.mean(incomes)
            return {
                "media_renda": round(avg_income, 2),
                "comparacao": "acima" if user_income > avg_income else "abaixo" if user_income < avg_income else "na media",
                "quartil": self._get_income_quartile(user_income, incomes)
            }
        except:
            return {"comparacao": "erro"}

    async def _analyze_profiles(self, users: List[Dict]) -> Dict:
        """Analisa distribuição de perfis"""
        try:
            # Busca perfis no histórico
            profiles = []
            for user in users:
                historico = await mongodb_crud.find_document("historico", {"user_id": str(user.get('_id'))})
                if historico and historico.get('perfil_classificado'):
                    profiles.append(historico.get('perfil_classificado'))
            
            profile_count = {}
            for profile in profiles:
                profile_count[profile] = profile_count.get(profile, 0) + 1
            
            return profile_count
        except:
            return {}

    async def _analyze_objectives(self, users: List[Dict]) -> List[str]:
        """Analisa objetivos comuns"""
        try:
            objectives = []
            for user in users:
                if user.get('objetivo_financeiro'):
                    objectives.append(user.get('objetivo_financeiro')[:100])  # Limita tamanho
            
            return list(set(objectives))[:5]  # Retorna até 5 objetivos únicos
        except:
            return []

    def _get_age_group(self, age: int) -> str:
        if age <= 25: return "18-25"
        elif age <= 35: return "26-35"
        elif age <= 45: return "36-45"
        elif age <= 55: return "46-55"
        else: return "56+"

    def _get_income_quartile(self, income: float, incomes: List[float]) -> int:
        if not incomes:
            return 1
        try:
            sorted_incomes = sorted(incomes)
            n = len(sorted_incomes)
            for i, inc in enumerate(sorted_incomes):
                if income <= inc:
                    return min(4, (i * 4) // n + 1)
            return 4
        except:
            return 1