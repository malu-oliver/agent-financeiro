<<<<<<< HEAD
# agent-financeiro
=======
# 💰 ZUP Educação Financeira AI

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

Configure as variáveis de ambiente no arquivo `.env` (já presente na raiz do projeto):

**Variáveis obrigatórias que precisam ser configuradas:**
- `GEMINI_API_KEY`: Sua chave da API do Google Gemini AI
- `MONGO_CONNECTION_STRING`: String de conexão do MongoDB Atlas
- `SECRET_KEY`: Chave secreta para segurança da aplicação

**O arquivo `.env` já contém todas as configurações necessárias. Apenas certifique-se de que as chaves da API estão corretas.**

### 4. Execução

```bash
# Executar a API na porta 8000
uvicorn app.api.api_main:app --host 127.0.0.1 --port 8000 --reload

# Ou usando Python diretamente
python -m uvicorn app.api.api_main:app --host 127.0.0.1 --port 8000 --reload
```

>>>>>>> e9046ba (Primeiro commit)
