# 🤖 ZUP Educação Financeira AI - Agente Inteligente

Um **Agente de IA completo** para educação financeira que combina autonomia, aprendizado contínuo, percepção ambiental e capacidade de planejamento. O sistema não apenas gera conteúdo educacional, mas **aprende**, **adapta** e **evolui** com cada interação do usuário.

## 🧠 Características de Agente de IA

### ✅ **AUTONOMIA**
- **Decisões Independentes**: O agente decide automaticamente a estratégia de conteúdo (educativo, transicional, interativo, especializado)
- **Triggers Autônomos**: Reage automaticamente a padrões de baixo engajamento, mudança de perfil e repetição de conteúdo
- **Adaptação Dinâmica**: Ajusta complexidade e foco sem intervenção humana

### ✅ **APRENDIZADO CONTÍNUO**
- **Melhoria com Experiência**: Cada interação melhora as próximas respostas
- **Eficácia de Keywords**: Ajusta automaticamente a efetividade das palavras-chave baseado no sucesso
- **Evolução de Usuários**: Progride o nível de aprendizado (iniciante → intermediário → avançado)
- **Memória Persistente**: Mantém contexto histórico de cada usuário

### ✅ **PERCEPÇÃO AMBIENTAL**
- **Análise de Evolução**: Detecta mudanças no perfil do usuário ao longo do tempo
- **Monitoramento Global**: Identifica padrões de uso em toda a base de usuários
- **Detecção de Tendências**: Reconhece se usuário está estável, evoluindo ou explorando

### ✅ **CAPACIDADE DE PLANEJAMENTO**
- **Planos de Longo Prazo**: Cria estratégias educacionais estruturadas
- **Progressão Adaptativa**: Planos inicial (3 passos) → intermediário (4 passos) → avançado (5 passos)
- **Sugestões Proativas**: Oferece próximos passos educacionais automaticamente

## 🎯 Funcionalidades Principais

- **Classificação Inteligente**: Perfil de investidor com aprendizado contínuo (conservador, moderado, agressivo)
- **Geração Autônoma**: Conteúdo educacional adaptativo usando Google Gemini AI
- **Comportamento Proativo**: Sugestões automáticas baseadas no contexto do usuário
- **Persistência Inteligente**: MongoDB Atlas com histórico completo de interações
- **API de Agente**: Endpoints específicos para funcionalidades de IA autônoma
- **Health Check Dinâmico**: Monitoramento em tempo real do status do agente

## 🏗️ Arquitetura do Agente de IA

```
app/
├── api/
│   ├── models/
│   │   └── schemas.py          # Modelos Pydantic para validação
│   ├── routes/
│   │   └── api_routes.py       # Endpoints da API + Agente IA
│   ├── services/
│   │   ├── database.py         # Conexão MongoDB + Persistência
│   │   ├── ia_classification.py # 🧠 Classificação com Aprendizado
│   │   └── ia_generator.py     # 🤖 Gerador Autônomo de Conteúdo
│   └── api_main.py            # FastAPI + Health Check Dinâmico
├── config/
│   └── settings.py            # Configurações ambiente
├── data/
│   └── profile_keywords.json  # Keywords para classificação adaptativa
└── streamlit/
    └── dashboard.py                 # Interface opcional (Streamlit)
```

### 🔧 Componentes do Agente IA

#### **IAGenerator** (`ia_generator.py`)
- `_autonomous_content_strategy()` - Decisões autônomas de estratégia
- `_learn_from_interaction()` - Aprendizado contínuo
- `_environmental_perception()` - Percepção de padrões globais
- `_planning_system()` - Planejamento de longo prazo
- `get_autonomous_suggestions()` - Comportamento proativo

#### **ProfileClassifier** (`ia_classification.py`)
- `classify_profile()` - Classificação com aprendizado
- `analyze_user_evolution()` - Análise de evolução temporal
- `_learn_from_classification()` - Melhoria de precisão
- `_intelligent_default_classification()` - Classificação autônoma

## 🚀 Como Executar

### Pré-requisitos

- Python 3.12+
- Conta no Google AI Studio (para Gemini API)
- Conta no MongoDB Atlas
- Git

### 1. Clonagem e Configuração

```bash
# Clone o repositório
git clone https://github.com/Bootcamp-Zup-AI-Camp-para-Minas/zup-educacao-financeira-ai.git
cd zup-educacao-financeira-ai

# Crie um ambiente virtual
python -m venv .venv

# Ative o ambiente virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

### 2. Instalação das Dependências

```bash
pip install -r requirements.txt
```

### 3. Configuração do Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Google Gemini AI (obrigatório para geração de conteúdo)
GEMINI_API_KEY=sua_chave_gemini_aqui

# MongoDB Atlas (obrigatório para persistência do agente)
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority&authSource=admin
DATABASE_NAME=educacao_financeira

# Configurações da aplicação
APP_NAME=ZUP Educação Financeira AI
SECRET_KEY=sua_chave_secreta_aqui
ENVIRONMENT=development
```

**⚠️ IMPORTANTE - Configuração MongoDB Atlas:**

1. **Database User**: Crie um Database User (não apenas Project Member):
   - MongoDB Atlas → Database Access → Add New Database User
   - Role: `readWriteAnyDatabase` ou específica para o database
   
2. **Network Access**: Libere seu IP ou use `0.0.0.0/0` para testes
   
3. **String de Conexão**: Copie do MongoDB Atlas → Connect → Drivers

**Obtenha suas chaves:**
- **Gemini API**: [Google AI Studio](https://makersuite.google.com/app/apikey) 
- **MongoDB**: [MongoDB Atlas](https://cloud.mongodb.com/)

### 4. Execução

```bash
# Executar a API (com auto-reload para desenvolvimento)
uvicorn app.api.api_main:app --reload --host 127.0.0.1 --port 8000

# Ou executar sem auto-reload (para produção)
uvicorn app.api.api_main:app --host 127.0.0.1 --port 8000
```

**💡 Dica**: Use `--reload` durante o desenvolvimento. O servidor reinicia automaticamente quando você modificar arquivos Python!

## 📡 API Endpoints

### 🚀 **Endpoint Principal do Agente**

#### `POST /api/v1/gerar-conteudo`
Endpoint inteligente que **aprende e evolui** com cada uso.

**Request Body:**
```json
{
  "nome": "Ana Silva",
  "idade": 32,
  "renda_mensal": 8500.0,
  "objetivo_financeiro": "Quero diversificar meus investimentos para ter uma aposentadoria confortável, mas sem muito risco."
}
```

**Response com Características de Agente:**
```json
{
  "perfil_investidor": "conservador",
  "percentuais_perfil": {
    "conservador": 75.0,
    "moderado": 20.0,
    "agressivo": 5.0
  },
  "conteudo_educativo": "Conteúdo personalizado em 3 parágrafos...",
  "agente_ia": {
    "comportamento_autonomo": "high_engagement_detected",
    "sugestoes_inteligentes": [
      "diversificação",
      "análise de risco", 
      "planejamento tributário"
    ],
    "nivel_aprendizado": "avançado",
    "evolucao_usuario": {
      "consistency": 0.85,
      "trend": "stable"
    },
    "proximas_acoes": ["reserva de emergência", "investimentos básicos"]
  },
  "metadata": {
    "user_id": "60d5ecb74b24a1234567890",
    "interacoes_anteriores": 5,
    "consistencia_perfil": 0.85,
    "tendencia": "stable"
  }
}
```

### 🤖 **Endpoints Específicos do Agente IA**

#### `GET /api/v1/agente-ia/status`
Status e capacidades do sistema de agente IA.

#### `GET /api/v1/agente-ia/{user_id}/sugestoes`
Sugestões autônomas baseadas no aprendizado do usuário.

#### `GET /api/v1/agente-ia/{user_id}/evolucao`
Análise da evolução do perfil do usuário ao longo do tempo.

#### `POST /api/v1/agente-ia/{user_id}/feedback`
Sistema de feedback para aprendizado contínuo do agente.

### 👥 **Endpoints CRUD de Usuários**

#### `GET /api/v1/usuarios` - Lista usuários
#### `GET /api/v1/usuarios/{id}` - Busca usuário específico
#### `POST /api/v1/usuarios` - Cria novo usuário
#### `PUT /api/v1/usuarios/{id}` - Atualiza usuário
#### `DELETE /api/v1/usuarios/{id}` - Remove usuário

### 🔍 **Endpoints de Monitoramento**

#### `GET /health` - Health check dinâmico
Verifica status da API, MongoDB e serviço de IA em tempo real.

#### `GET /` - Informações da API
#### `GET /perfis-investidor` - Perfis disponíveis

## 🧠 Como o Agente de IA Funciona

### 🔄 **Fluxo Inteligente Completo**

1. **📥 Recepção**: API recebe dados do usuário
2. **🧠 Análise Autônoma**: Agente decide estratégia de conteúdo automaticamente
3. **🔍 Classificação Adaptativa**: Perfil determinado com aprendizado contínuo
4. **🤖 Geração Inteligente**: Google Gemini cria conteúdo baseado na estratégia autônoma
5. **📚 Aprendizado**: Sistema aprende com a interação para melhorar próximas respostas
6. **💾 Persistência**: Contexto salvo no MongoDB para evolução contínua
7. **🎯 Comportamento Proativo**: Oferece sugestões automáticas para próximos passos

### 🔧 **Capacidades Avançadas do Agente**

#### **Autonomia Comportamental**
- Decide automaticamente entre estratégias: educativo, transicional, interativo, especializado
- Ajusta complexidade baseado no progresso: iniciante → intermediário → avançado
- Reage a triggers: baixo engajamento, mudança de perfil, repetição de conteúdo

#### **Aprendizado Inteligente**
- **Eficácia de Keywords**: Ajusta peso das palavras-chave baseado no sucesso
- **Contexto do Usuário**: Mantém memória de interações, preferências e evolução
- **Padrões Globais**: Aprende com toda a base de usuários para melhorar classificações

#### **Percepção Temporal**
- **Evolução de Perfil**: Detecta mudanças ao longo do tempo (estável, evoluindo, explorando)
- **Consistência**: Calcula consistência do usuário em suas escolhas financeiras
- **Tendências**: Identifica padrões de comportamento para adaptação proativa

#### **Planejamento Estruturado**
- **Planos Adaptativos**: Cria roadmaps educacionais personalizados
- **Progressão Inteligente**: 3 passos (inicial) → 4 passos (intermediário) → 5 passos (avançado)
- **Sugestões Proativas**: Oferece próximos tópicos educacionais automaticamente

## 🛠️ Tecnologias e Arquitetura

### **Stack Principal**
- **FastAPI**: Framework web assíncrono de alta performance
- **Google Gemini AI**: Modelo de linguagem avançado para geração de conteúdo
- **MongoDB Atlas**: Banco NoSQL em nuvem para persistência inteligente
- **Motor**: Driver assíncrono para MongoDB (suporte completo a async/await)
- **Pydantic**: Validação de dados e configurações type-safe
- **Uvicorn**: Servidor ASGI para aplicações Python

### **Componentes de IA Avançada**
- **Sistema de Aprendizado**: Melhoria contínua baseada em feedback implícito
- **Cache Inteligente**: Contexto de usuário em memória para decisões rápidas
- **Triggers Autônomos**: Sistema reativo para mudanças de comportamento
- **Planejamento Temporal**: Criação de planos educacionais de longo prazo
- **Análise de Padrões**: Detecção de tendências em comportamento do usuário

### **Persistência Inteligente**
O MongoDB Atlas armazena automaticamente:
- `usuarios`: Dados pessoais e evolução do perfil
- `historico`: Todas as interações com contexto completo
- `perfis`: Classificações com metadados de aprendizado
- `feedback_agente`: Sistema de feedback para melhoria contínua

### **Monitoramento e Observabilidade**
- Health check dinâmico com status em tempo real
- Métricas de aprendizado e engajamento
- Rastreamento de evolução de usuários
- Dashboard de capacidades do agente

## 🔧 Configuração e Personalização

### **Personalização de Keywords Inteligente**

O agente usa aprendizado contínuo, mas você pode ajustar as keywords base em `app/data/profile_keywords.json`:

```json
{
  "conservador": [
    "segurança", "estabilidade", "reserva", "aposentadoria", 
    "baixo risco", "proteção", "poupança", "tesouro direto"
  ],
  "moderado": [
    "equilíbrio", "diversificação", "médio prazo", "balanceado",
    "fundos multimercado", "imóveis", "inflação"
  ],
  "agressivo": [
    "crescimento", "risco", "alta rentabilidade", "ações", 
    "bolsa de valores", "criptomoedas", "startups"
  ]
}
```

**⚠️ Nota**: O agente aprende automaticamente a eficácia dessas keywords e as ajusta com base no sucesso das classificações.

### **Configurações Avançadas do Agente**

#### **Triggers Autônomos** (em `IAGenerator`)
```python
self.autonomous_triggers = {
    "low_engagement": 3,      # Após 3 interações básicas
    "profile_drift": 0.3,     # 30% mudança no perfil
    "content_repetition": 2   # Mesmo tipo de conteúdo 2x
}
```

#### **Níveis de Aprendizado**
- **Iniciante**: 0-0.5 engajamento
- **Intermediário**: 0.5-0.8 engajamento  
- **Avançado**: >0.8 engajamento

### **Configuração do Banco de Dados Inteligente**

O sistema cria automaticamente as collections com índices otimizados:
- `usuarios`: Dados de usuários com índice por nome/idade
- `historico`: Histórico completo com índice por user_id e timestamp
- `perfis`: Classificações com metadados de aprendizado
- `feedback_agente`: Sistema de feedback para melhoria contínua

## 🧪 Testando o Agente de IA

### **Testes Rápidos**

Após iniciar o servidor, acesse:
- **📋 Documentação Swagger**: http://127.0.0.1:8000/docs
- **📖 Documentação ReDoc**: http://127.0.0.1:8000/redoc
- **💓 Health Check**: http://127.0.0.1:8000/health

### **Testando Características do Agente**

#### **1. Teste de Autonomia**
```bash
# Fazer múltiplas chamadas para o mesmo usuário
curl -X POST "http://127.0.0.1:8000/api/v1/gerar-conteudo" \
-H "Content-Type: application/json" \
-d '{
  "nome": "Maria",
  "idade": 30,
  "renda_mensal": 5000,
  "objetivo_financeiro": "Quero investir com segurança"
}'

# Observe como o "comportamento_autonomo" evolui nas respostas
```

#### **2. Teste de Aprendizado**
```bash
# Verificar evolução do usuário após múltiplas interações
curl "http://127.0.0.1:8000/api/v1/agente-ia/{user_id}/evolucao"

# Resposta mostra: consistency, trend, history_length
```

#### **3. Teste de Sugestões Proativas**
```bash
# Obter sugestões autônomas do agente
curl "http://127.0.0.1:8000/api/v1/agente-ia/{user_id}/sugestoes"

# Resposta inclui: autonomous_action, suggestions, learning_progress
```

#### **4. Teste de Status do Agente**
```bash
curl "http://127.0.0.1:8000/api/v1/agente-ia/status"

# Mostra capacidades ativas e estatísticas de aprendizado
```

### **Validação de Persistência**

```python
# Teste direto das capacidades do agente
python -c "
import asyncio
from app.api.services.ia_generator import IAGenerator

async def test():
    agent = IAGenerator()
    
    # Teste de autonomia
    strategy = await agent._autonomous_content_strategy('test_user', 'moderado', {}, 'investir')
    print(f'Estratégia autônoma: {strategy}')
    
    # Teste de sugestões proativas
    suggestions = await agent.get_autonomous_suggestions('test_user')
    print(f'Ação autônoma: {suggestions[\"autonomous_action\"]}')

asyncio.run(test())
"
```

## 🚀 Deploy e Produção

### **Comandos de Execução**

#### **Desenvolvimento (Recomendado)**
```bash
# Com auto-reload - ideal para desenvolvimento
uvicorn app.api.api_main:app --reload --host 127.0.0.1 --port 8000

# Alternativa usando Python diretamente
python -m uvicorn app.api.api_main:app --reload --host 127.0.0.1 --port 8000
```

#### **Produção**
```bash
# Sem reload - melhor performance para produção
uvicorn app.api.api_main:app --host 0.0.0.0 --port 8000 --workers 4

# Com configurações avançadas para produção
uvicorn app.api.api_main:app --host 0.0.0.0 --port 8000 --workers 4 --access-log --log-level info
```

### **Variáveis de Ambiente para Produção**

```env
# Produção
ENVIRONMENT=production
DEBUG=False

# MongoDB Atlas (URLs de produção)
MONGODB_URL=mongodb+srv://prod_user:strong_password@cluster-prod.mongodb.net/educacao_financeira_prod?retryWrites=true&w=majority&authSource=admin

# Chaves de API (produção)
GEMINI_API_KEY=sua_chave_producao_gemini

# Segurança
SECRET_KEY=chave_super_secreta_producao

# CORS (ajuste conforme seu domínio)
ALLOWED_ORIGINS=https://seu-dominio.com,https://www.seu-dominio.com
```

### **Monitoramento do Agente em Produção**

#### **Health Check Avançado**
- Monitor contínuo de conexão MongoDB
- Verificação automática da API Gemini
- Status das capacidades do agente em tempo real

#### **Métricas de Aprendizado**
- Taxa de evolução de usuários
- Eficácia das keywords adaptativas
- Padrões de engajamento detectados
- Performance de sugestões autônomas

#### **Logging Inteligente**
O agente registra automaticamente:
- Decisões autônomas tomadas
- Evolução de aprendizado por usuário
- Padrões globais detectados
- Triggers ativados e suas causas

## 📊 Características Técnicas do Agente

### **Validação Científica**
✅ **4/4 Características de Agente de IA Implementadas:**
- **Autonomia**: Decisões independentes sobre estratégias
- **Aprendizado Contínuo**: Melhoria com experiência
- **Percepção Ambiental**: Monitoramento de padrões
- **Capacidade de Planejamento**: Planos de longo prazo

### **Performance e Escalabilidade**
- **Async/Await**: Operações não-bloqueantes
- **Cache Inteligente**: Contexto em memória para decisões rápidas
- **Persistência Eficiente**: Índices otimizados no MongoDB
- **Triggers Reativos**: Resposta imediata a mudanças de comportamento

### **Segurança e Confiabilidade**
- **Validação Pydantic**: Type safety em todas as operações
- **Fallback Inteligente**: Modo simulação quando serviços estão indisponíveis
- **Health Check Dinâmico**: Monitoramento contínuo de componentes
- **Logs Estruturados**: Rastreabilidade completa das decisões do agente

## 🤝 Contribuição

Contribuições são bem-vindas! Este é um projeto de **Agente de IA avançado**.

### **Como Contribuir**
1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AgentImprovement`)
3. Commit suas mudanças (`git commit -m 'Add: Nova capacidade do agente'`)
4. Push para a branch (`git push origin feature/AgentImprovement`)  
5. Abra um Pull Request

### **Áreas de Melhoria**
- **Novos Triggers Autônomos**: Padrões comportamentais adicionais
- **Algoritmos de Aprendizado**: Melhoria das funções de aprendizado contínuo
- **Percepção Ambiental**: Detecção de novos padrões globais
- **Planejamento Avançado**: Estratégias educacionais mais sofisticadas
- **Métricas de Performance**: Novos indicadores de eficácia do agente

### **Diretrizes**
- Mantenha as 4 características do agente (autonomia, aprendizado, percepção, planejamento)
- Adicione testes para novas funcionalidades de IA
- Documente comportamentos autônomos adicionados
- Considere impacto na performance com grandes volumes de usuários

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

## 🏆 Créditos

**Desenvolvido por**: Bootcamp Zup AI Camp para Minas  
**Tecnologia**: Agente de IA com Autonomia, Aprendizado Contínuo, Percepção Ambiental e Capacidade de Planejamento  
**Status**: ✅ **Agente de IA Completo e Funcional** - 4/4 Características Implementadas

*Este é um verdadeiro Agente de IA, não apenas uma API com IA integrada. O sistema pensa, aprende, percebe e planeja autonomamente.* 🤖✨