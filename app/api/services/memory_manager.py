from typing import Dict, List, Any, Optional
from datetime import datetime
from app.api.services import mongodb_crud
from app.core.config.settings import settings

class MemoryManager:
    def __init__(self):
        self.max_history = settings.max_conversation_history

    async def get_user_memory(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Recupera a memória do usuário"""
        try:
            memory = await mongodb_crud.find_document("user_memory", {"user_id": user_id})
            return memory
        except Exception as e:
            print(f"Erro ao buscar memória: {e}")
            return None

    async def update_user_memory(self, user_id: str, interaction: Dict[str, Any]):
        """Atualiza a memória do usuário com nova interação"""
        try:
            existing_memory = await self.get_user_memory(user_id)
            
            new_interaction = {
                "timestamp": datetime.now(),
                "request": interaction.get("request"),
                "response": interaction.get("response"),
                "profile": interaction.get("profile"),
                "objective": interaction.get("objective")
            }

            if existing_memory:
                # Atualiza memória existente
                history = existing_memory.get("conversation_history", [])
                history.append(new_interaction)
                
                # Mantém apenas o histórico mais recente
                if len(history) > self.max_history:
                    history = history[-self.max_history:]
                
                await mongodb_crud.update_document(
                    "user_memory", 
                    {"user_id": user_id},
                    {
                        "conversation_history": history,
                        "last_interaction": datetime.now(),
                        "preferences": self._extract_preferences(history),
                        "dominant_profile": new_interaction.get("profile")
                    }
                )
            else:
                # Cria nova memória
                memory_data = {
                    "user_id": user_id,
                    "conversation_history": [new_interaction],
                    "last_interaction": datetime.now(),
                    "preferences": {},
                    "dominant_profile": new_interaction.get("profile"),
                    "created_at": datetime.now()
                }
                await mongodb_crud.create_document("user_memory", memory_data)
        except Exception as e:
            print(f"Erro ao atualizar memória: {e}")

    async def get_conversation_context(self, user_id: str) -> str:
        """Gera contexto para IA baseado no histórico"""
        try:
            memory = await self.get_user_memory(user_id)
            if not memory or not memory.get("conversation_history"):
                return ""

            history = memory["conversation_history"][-3:]  # Últimas 3 interações
            context = "Histórico recente da conversa:\n"
            
            if memory.get("dominant_profile"):
                dominant_profile = memory.get('dominant_profile')
                context += f"Perfil dominante do usuário: {dominant_profile}\n\n"

            for i, interaction in enumerate(history):
                context += f"Interação {i+1}:\n"
                context += f"Objetivo: {interaction.get('objective', 'N/A')}\n"
                context += f"Perfil: {interaction.get('profile', 'N/A')}\n\n"
            
            return context
        except Exception as e:
            print(f"Erro ao gerar contexto: {e}")
            return ""

    def _extract_preferences(self, history: List[Dict]) -> Dict[str, Any]:
        """Extrai preferências do usuário do histórico"""
        try:
            if not history:
                return {}

            profiles = [interaction.get('profile') for interaction in history if interaction.get('profile')]
            objectives = [interaction.get('objective') for interaction in history if interaction.get('objective')]
            
            return {
                "preferred_profile": max(set(profiles), key=profiles.count) if profiles else None,
                "common_objectives": list(set(objectives))[:3],
                "interaction_count": len(history)
            }
        except:
            return {}