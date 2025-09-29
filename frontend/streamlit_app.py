import streamlit as st
import requests
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json
import os
#os.environ["STREAMLIT_SECRETS_FILE"] = ".streamlit/secrets.toml"

# Configuração da página
st.set_page_config(
    page_title="Sistema Inteligente de Educação Financeira",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título da aplicação
st.title("💰 Sistema Inteligente de Educação Financeira")
st.markdown("---")

# Função para carregar configurações
def load_config():
    """Carrega configurações do secrets.toml ou variáveis de ambiente"""
    try:
        # Tenta carregar do secrets.toml
        api_url = st.secrets.get("API_URL", "http://localhost:8000")
    except (FileNotFoundError, AttributeError):
        # Fallback para variáveis de ambiente ou valor padrão
        api_url = os.getenv("API_URL", "http://localhost:8000")
    
    return api_url

# Sidebar com informações
with st.sidebar:
    st.header("Configurações")
    
    # Carrega configuração
    DEFAULT_API_URL = load_config()
    api_url = st.text_input("URL da API", value=DEFAULT_API_URL)
    
    st.markdown("---")
    st.info("""
    **Funcionalidades:**
    - 🧠 Memória de conversação
    - 📊 Análise comparativa
    - 💰 Simulação de investimentos
    - 📈 Gráficos interativos
    - 🔍 Regex inteligente
    """)

# Função para fazer requisições à API com tratamento de erro
def make_api_request(url, json_data, timeout=60):
    """Faz requisição à API com tratamento robusto de erros"""
    try:
        response = requests.post(url, json=json_data, timeout=timeout)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, f"Erro de conexão: {e}"
    except json.JSONDecodeError as e:
        return None, f"Erro ao decodificar resposta: {e}"
    except Exception as e:
        return None, f"Erro inesperado: {e}"

# Abas principais
tab1, tab2, tab3, tab4 = st.tabs(["📊 Análise Principal", "💰 Simulação", "📈 Comparativos", "🧠 Histórico"])

with tab1:
    st.header("Análise Financeira Personalizada")
    
    with st.form("main_analysis_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome completo*", placeholder="Seu nome")
            idade = st.number_input("Idade*", min_value=18, max_value=100, value=30)
            renda_mensal = st.number_input("Renda Mensal (R$)*", min_value=0.0, value=5000.0, format="%.2f")
            valor_investir = st.number_input("Valor Disponível para Investir (R$)", 
                                           min_value=0.0, value=10000.0, format="%.2f")
        
        with col2:
            tempo_investimento = st.number_input("Tempo para Investimento (anos)", 
                                               min_value=1, max_value=50, value=5)
            auto_classificacao = st.selectbox("Como você se classifica?",
                                            ["", "conservador", "moderado", "agressivo", "indefinido"])
            referencia_texto = st.text_area("Texto de Referência (opcional)",
                                          placeholder="Cole aqui algum texto que queira usar como referência...",
                                          height=100)
        
        objetivo_financeiro = st.text_area("Objetivo Financeiro*",
                                         placeholder="Ex: Quero guardar dinheiro para comprar um apartamento em 5 anos e ter uma reserva de emergência...",
                                         height=80)
        
        submitted = st.form_submit_button("🚀 Gerar Análise Completa")
        
        if submitted:
            if not nome or not objetivo_financeiro:
                st.error("Por favor, preencha pelo menos nome e objetivo financeiro.")
            else:
                user_data = {
                    "nome": nome,
                    "idade": idade,
                    "renda_mensal": renda_mensal,
                    "objetivo_financeiro": objetivo_financeiro,
                    "valor_disponivel_investir": valor_investir if valor_investir > 0 else None,
                    "auto_classificacao": auto_classificacao if auto_classificacao else None,
                    "referencia_texto": referencia_texto if referencia_texto else None,
                    "tempo_investimento": tempo_investimento if tempo_investimento > 0 else None
                }
                
                with st.spinner("Analisando seu perfil e gerando conteúdo personalizado..."):
                    result, error = make_api_request(f"{api_url}/api/gerar-conteudo", user_data, timeout=120)
                
                if error:
                    st.error(f"Erro na análise: {error}")
                    st.info("""
                    **Solução de problemas:**
                    1. Verifique se a API está rodando em {api_url}
                    2. Execute: `uvicorn app.main:app --reload` na pasta app/
                    3. Verifique a conexão com a internet
                    """)
                else:
                    st.success("Análise concluída com sucesso!")
                    
                    # Exibir resultados
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Perfil Identificado", result['perfil_investidor'].upper())
                    
                    with col2:
                        if result.get('simulacao_investimento'):
                            st.metric("Projeção (Perfil)", 
                                    f"R$ {result['simulacao_investimento']['perfil']['valor_final']:,.2f}")
                    
                    with col3:
                        if result.get('analise_comparativa'):
                            st.metric("Usuários Similares", 
                                    result['analise_comparativa']['total_peers'])
                    
                    # Gráfico de perfil
                    st.subheader("📊 Distribuição do Perfil")
                    profile_data = result['percentuais_perfil']
                    
                    if profile_data:
                        fig = go.Figure(data=[go.Pie(
                            labels=[k.upper() for k in profile_data.keys()], 
                            values=list(profile_data.values()),
                            hole=.3
                        )])
                        fig.update_layout(title_text="Distribuição do Perfil de Investidor")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Conteúdo educativo
                    st.subheader("🎓 Conteúdo Educativo Personalizado")
                    st.write(result['conteudo_educativo'])
                    
                    # Simulação de investimento
                    if result.get('simulacao_investimento'):
                        st.subheader("💰 Projeção de Investimentos")
                        sim_data = result['simulacao_investimento']
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Cenário Perfil", f"R$ {sim_data['perfil']['valor_final']:,.2f}")
                        with col2:
                            st.metric("Cenário Otimista", f"R$ {sim_data['otimista']['valor_final']:,.2f}")
                        with col3:
                            st.metric("Cenário Pessimista", f"R$ {sim_data['pessimista']['valor_final']:,.2f}")
                        
                        # Gráfico de projeção se disponível
                        if sim_data.get('projecao_mensal'):
                            proj_data = sim_data['projecao_mensal']
                            if proj_data:
                                df = pd.DataFrame(proj_data)
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(x=df['ano'], y=df['valor_acumulado'],
                                                       mode='lines+markers', name='Valor Acumulado'))
                                fig.update_layout(title="Projeção de Valor Acumulado ao Longo do Tempo",
                                                xaxis_title="Anos", yaxis_title="Valor (R$)")
                                st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Simulação Detalhada de Investimentos")
    st.info("Em desenvolvimento - Use a aba principal para simulações básicas")
    
    with st.form("investment_form"):
        st.subheader("Parâmetros da Simulação")
        col1, col2 = st.columns(2)
        
        with col1:
            valor_inicial = st.number_input("Valor Inicial (R$)", min_value=0.0, value=1000.0)
            aporte_mensal = st.number_input("Aporte Mensal (R$)", min_value=0.0, value=500.0)
        
        with col2:
            tempo_anos = st.number_input("Tempo (anos)", min_value=1, max_value=50, value=10)
            taxa_anual = st.number_input("Taxa Anual (%)", min_value=0.0, max_value=100.0, value=12.0)
        
        simular = st.form_submit_button("📈 Simular Investimento")
        
        if simular:
            if valor_inicial < 0 or aporte_mensal < 0 or tempo_anos <= 0 or taxa_anual < 0:
                st.error("Por favor, insira valores válidos para a simulação.")
            else:
                simulation_request = {
                    "valor_inicial": valor_inicial,
                    "aporte_mensal": aporte_mensal,
                    "tempo_anos": tempo_anos,
                    "taxa_anual": taxa_anual
                }
                with st.spinner("Calculando simulação de investimento..."):
                    result, error = make_api_request(f"{api_url}/api/simular-investimento", simulation_request)
                
                if error:
                    st.error(f"Erro na simulação: {error}")
                else:
                    st.success("Simulação concluída com sucesso!")
                    st.subheader("Resultados da Simulação")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Valor Final", f"R$ {result['valor_final']:,.2f}")
                    with col2:
                        st.metric("Total Investido", f"R$ {result['total_investido']:,.2f}")
                    with col3:
                        st.metric("Juros Acumulados", f"R$ {result['juros_acumulados']:,.2f}")
                    
                    if result.get("projecao_mensal"):
                        st.subheader("📈 Projeção Mensal Detalhada")
                        proj_df = pd.DataFrame(result["projecao_mensal"])
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=proj_df["ano"], y=proj_df["valor_acumulado"],
                                               mode='lines+markers', name='Valor Acumulado'))
                        fig.update_layout(title="Projeção de Valor Acumulado ao Longo do Tempo",
                                        xaxis_title="Anos", yaxis_title="Valor (R$)")
                        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Análise Comparativa com Outros Usuários")
    st.info("Os dados comparativos aparecerão automaticamente na análise principal")

with tab4:
    st.header("Histórico e Memória de Conversação")
    st.info("Funcionalidade em desenvolvimento")

# Rodapé
st.markdown("---")
st.markdown("*Sistema Inteligente de Educação Financeira - v4.0*")

# Informações de debug (apenas em desenvolvimento)
if st.sidebar.checkbox("Mostrar informações de debug"):
    st.sidebar.subheader("Debug Info")
    st.sidebar.write(f"API URL: {api_url}")
    st.sidebar.write(f"Secrets carregados: {'sim' if hasattr(st, 'secrets') else 'não'}")