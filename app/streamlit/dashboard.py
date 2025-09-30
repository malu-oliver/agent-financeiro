import streamlit as st
import httpx
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import hashlib
import os

# Configuração da página
st.set_page_config(
    page_title="Agente Financeiro Inteligente",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título da aplicação
st.title("🤖 Agente Financeiro Inteligente Autônomo")
st.markdown("---")

# Configuração da API URL
def get_api_url():
    """Obtém a URL da API das secrets ou usa padrão"""
    try:
        # Tenta obter das secrets do Streamlit
        if hasattr(st, 'secrets') and 'API_URL' in st.secrets:
            return st.secrets['API_URL']
    except:
        pass
    
    # Fallback para variável de ambiente ou padrão
    return os.getenv('API_URL', 'http://localhost:8000')

API_URL = get_api_url()

# Sidebar para informações do usuário
with st.sidebar:
    st.header("📊 Seu Perfil Financeiro")
    
    with st.form("user_profile"):
        st.subheader("Identificação")
        nome = st.text_input("Nome completo*", key="nome")
        email = st.text_input("E-mail (para salvar seu histórico)", key="email")
        idade = st.number_input("Idade*", min_value=18, max_value=100, value=30, key="idade")
        renda_mensal = st.number_input("Renda Mensal (R$)*", min_value=0.0, value=2500.0, format="%.2f", key="renda")
        
        st.subheader("Autoavaliação")
        auto_classificacao = st.selectbox(
            "Como você se classifica?",
            ["", "Conservador", "Moderado", "Agressivo", "Não sei"],
            key="auto_classificacao"
        )
        
        valor_investir = st.number_input(
            "Valor disponível para investir (R$)", 
            min_value=0.0, value=0.0, format="%.2f",
            key="valor_investir"
        )
        
        st.subheader("Contexto Adicional")
        referencias = st.text_area(
            "Alguma referência ou situação específica?",
            placeholder="Ex: Tenho dívidas, sou estudante, planejo comprar imóvel...",
            key="referencias"
        )
        
        submitted_profile = st.form_submit_button("Salvar Perfil")

# Função para gerar hash do usuário
def generate_user_hash(email, nome):
    """Gera hash único para usuário"""
    if email:
        unique_string = f"{email.lower()}_{nome.lower()}"
    else:
        unique_string = f"anonymous_{nome.lower()}_{datetime.now().timestamp()}"
    return hashlib.sha256(unique_string.encode()).hexdigest()

# Abas principais
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Análise Personalizada", "📈 Simulador", "📊 Meu Histórico", "🤖 Agente IA"])

with tab1:
    st.header("Análise Financeira Personalizada")
    
    with st.form("financial_analysis"):
        objetivo_financeiro = st.text_area(
            "Qual seu objetivo financeiro principal?*",
            placeholder="Ex: Quero guardar R$ 50.000 para entrada de um apartamento em 3 anos...",
            height=100,
            key="objetivo"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            prazo_objetivo = st.selectbox(
                "Prazo do objetivo",
                ["Curto prazo (até 1 ano)", "Médio prazo (1-5 anos)", "Longo prazo (acima de 5 anos)"],
                key="prazo"
            )
        with col2:
            prioridade = st.select_slider(
                "Prioridade",
                options=["Baixa", "Média", "Alta", "Máxima"],
                key="prioridade"
            )
        
        submitted_analysis = st.form_submit_button("Analisar com IA")
        
        if submitted_analysis and objetivo_financeiro and nome:
            # Preparar dados para API
            user_data = {
                "nome": nome,
                "idade": idade,
                "renda": renda_mensal,
                "objetivo_financeiro": objetivo_financeiro,
                "email": email if email else None,
                "valor_investir": valor_investir,
                "auto_classificacao": auto_classificacao,
                "referencias": referencias
            }
            
            # Chamada para API
            try:
                api_url = f"{API_URL}/api/v1/gerar-conteudo"
                
                with st.spinner("🤖 Agente IA analisando seu perfil..."):
                    response = httpx.post(api_url, json=user_data, timeout=60)
                    
                    if response.status_code != 201:
                        st.error(f"Erro na API: {response.status_code} - {response.text}")
                    else:
                        result = response.json()
                        
                        # Exibir resultados
                        st.success("Análise concluída!")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(
                                "Perfil Identificado", 
                                result.get('perfil_investidor', 'N/A').capitalize()
                            )
                        with col2:
                            consistency = result.get('metadata', {}).get('consistencia_perfil', 0)
                            st.metric("Consistência", f"{consistency*100:.0f}%")
                        with col3:
                            interactions = result.get('metadata', {}).get('interacoes_anteriores', 0)
                            st.metric("Interações", interactions)
                        
                        # Conteúdo educativo
                        st.subheader("📚 Recomendações Personalizadas")
                        st.write(result.get("conteudo_educativo", "Nenhum conteúdo gerado."))
                        
                        # Sugestões do agente
                        st.subheader("🚀 Próximas Ações Sugeridas")
                        suggestions = result.get('agente_ia', {}).get('sugestoes_inteligentes', [])
                        if suggestions:
                            for i, suggestion in enumerate(suggestions[:3], 1):
                                st.write(f"{i}. {suggestion}")
                        else:
                            st.info("Nenhuma sugestão disponível.")
                        
                        # Gráfico de perfil
                        st.subheader("📊 Distribuição do Seu Perfil")
                        percentages = result.get('percentuais_perfil', {})
                        if percentages:
                            fig = go.Figure(data=[go.Pie(
                                labels=[k.capitalize() for k in percentages.keys()],
                                values=list(percentages.values()),
                                hole=.3,
                                marker_colors=['#2E8B57', '#FFA500', '#DC143C']
                            )])
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Dados de perfil não disponíveis.")
                
            except httpx.RequestError as e:
                st.error(f"Erro de conexão com a API: {e}")
                st.info(f"Verifique se a API está rodando em: {API_URL}")
            except Exception as e:
                st.error(f"Erro inesperado: {str(e)}")

with tab2:
    st.header("📈 Simulador de Investimentos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Dados do Investimento")
        valor_inicial = st.number_input("Valor inicial (R$)", min_value=0.0, value=1000.0, key="valor_inicial")
        aporte_mensal = st.number_input("Aporte mensal (R$)", min_value=0.0, value=200.0, key="aporte_mensal")
        tempo_anos = st.slider("Tempo (anos)", 1, 30, 5, key="tempo_anos")
        perfil_simulacao = st.selectbox("Perfil de risco", ["conservador", "moderado", "agressivo"], key="perfil_simulacao")
        
        use_selic = st.checkbox("Usar taxa Selic como base", value=True, key="use_selic")
        taxa_personalizada = None
        if not use_selic:
            taxa_personalizada = st.slider("Taxa anual personalizada (%)", 1.0, 30.0, 10.0, key="taxa_personalizada")
    
    with col2:
        if st.button("Simular Investimento", type="primary", key="simular"):
            simulation_data = {
                "valor_inicial": valor_inicial,
                "aporte_mensal": aporte_mensal,
                "tempo_anos": tempo_anos,
                "perfil_risco": perfil_simulacao,
                "taxa_anual": taxa_personalizada if not use_selic else None
            }
            
            try:
                api_url = f"{API_URL}/api/v1/simular-investimento"
                
                with st.spinner("Calculando projeção..."):
                    response = httpx.post(api_url, json=simulation_data, timeout=30)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Exibir resultados
                        st.subheader("📊 Resultado da Simulação")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Valor Final", f"R$ {result.get('valor_final', 0):,.2f}")
                        with col2:
                            st.metric("Total Investido", f"R$ {result.get('total_investido', 0):,.2f}")
                        with col3:
                            st.metric("Ganhos com Juros", f"R$ {result.get('ganhos_juros', 0):,.2f}")
                        
                        st.metric("Retorno Total", f"{result.get('retorno_percentual', 0)}%")
                        st.metric("Taxa Anual Utilizada", f"{result.get('taxa_anual', 0)}%")
                        
                        # Gráfico de projeção
                        st.subheader("📈 Projeção Anual")
                        projecao = result.get('projecao_anual', [])
                        if projecao:
                            df = pd.DataFrame(projecao)
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(x=df['ano'], y=df['valor_acumulado'], 
                                                   name='Valor Acumulado', line=dict(color='#2E8B57')))
                            fig.add_trace(go.Scatter(x=df['ano'], y=df['total_investido'], 
                                                   name='Total Investido', line=dict(color='#FFA500')))
                            fig.update_layout(title="Evolução do Investimento")
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Dados de projeção não disponíveis.")
                    else:
                        st.error(f"Erro na simulação: {response.status_code} - {response.text}")
                
            except Exception as e:
                st.error(f"Erro na simulação: {str(e)}")
                st.info(f"Verifique se a API está rodando em: {API_URL}")

with tab3:
    st.header("📊 Meu Histórico e Evolução")
    
    if email:
        try:
            user_hash = generate_user_hash(email, nome)
            history_url = f"{API_URL}/api/v1/usuario/{user_hash}/historico"
            
            with st.spinner("Carregando seu histórico..."):
                response = httpx.get(history_url, timeout=30)
                if response.status_code == 200:
                    historico = response.json()
                    
                    st.subheader("📈 Sua Evolução de Perfil")
                    if 'evolucao' in historico:
                        evolucao = historico['evolucao']
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Perfil Atual", evolucao.get('evolution', 'N/A').capitalize())
                        with col2:
                            st.metric("Consistência", f"{evolucao.get('consistency', 0)*100:.0f}%")
                        with col3:
                            trend = evolucao.get('trend', 'N/A')
                            trend_emoji = "📈" if trend == "evolving" else "📊" if trend == "stable" else "🔍"
                            st.metric("Tendência", f"{trend_emoji} {trend}")
                    
                    st.subheader("📋 Histórico de Interações")
                    if 'interacoes' in historico and historico['interacoes']:
                        for interacao in historico['interacoes'][:5]:  # Últimas 5
                            with st.expander(f"Interação de {interacao.get('data', 'Data desconhecida')}"):
                                st.write(f"**Objetivo:** {interacao.get('objetivo', 'N/A')}")
                                st.write(f"**Perfil:** {interacao.get('perfil', 'N/A')}")
                    else:
                        st.info("Nenhuma interação anterior encontrada.")
                else:
                    st.info("Nenhum histórico encontrado para seu e-mail.")
                    
        except Exception as e:
            st.error(f"Erro ao carregar histórico: {str(e)}")
            st.info(f"Verifique se a API está rodando em: {API_URL}")
    else:
        st.info("👤 Informe seu e-mail na sidebar para visualizar seu histórico.")

with tab4:
    st.header("🤖 Status do Agente IA")
    
    try:
        status_url = f"{API_URL}/api/v1/agente-ia/status"
        
        response = httpx.get(status_url, timeout=10)
        if response.status_code == 200:
            status_data = response.json()
            
            st.subheader("🔧 Capacidades do Agente")
            capacidades = status_data.get('capacidades', {})
            for cap, ativa in capacidades.items():
                status = "✅ Ativa" if ativa else "❌ Inativa"
                st.write(f"- {cap.replace('_', ' ').title()}: {status}")
            
            st.subheader("📊 Estatísticas do Sistema")
            stats = status_data.get('estatisticas', {})
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Usuários Ativos", stats.get('usuarios_rastreados', 0))
                st.metric("Interações Totais", stats.get('interacoes_totais', 0))
            with col2:
                st.metric("Média por Usuário", f"{stats.get('media_interacoes_usuario', 0):.1f}")
                st.metric("Keywords Aprendidas", stats.get('keywords_aprendidas', 0))
        else:
            st.error(f"Erro ao obter status: {response.status_code}")
                
    except Exception as e:
        st.error(f"Erro ao carregar status: {str(e)}")
        st.info(f"Verifique se a API está rodando em: {API_URL}")

# Informações de configuração na sidebar
with st.sidebar:
    st.markdown("---")
    st.subheader("🔧 Configuração")
    
    if st.checkbox("Mostrar informações de debug"):
        st.write(f"**API URL:** {API_URL}")
        st.write(f"**Secrets carregadas:** {hasattr(st, 'secrets') and bool(st.secrets)}")
        
        # Testar conexão com API
        if st.button("Testar Conexão API"):
            try:
                response = httpx.get(f"{API_URL}/health", timeout=5)
                if response.status_code == 200:
                    st.success("✅ API conectada com sucesso!")
                else:
                    st.error(f"❌ API retornou status {response.status_code}")
            except Exception as e:
                st.error(f"❌ Erro de conexão: {e}")

# Rodapé
st.markdown("---")
st.markdown(
    "**🤖 Agente Financeiro Inteligente** - Aprendendo continuamente para oferecer "
    "as melhores recomendações financeiras personalizadas."
)