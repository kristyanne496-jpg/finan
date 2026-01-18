import streamlit as st
import pandas as pd
from datetime import datetime

# Configurações Iniciais da Página (Aparência de App)
st.set_page_config(page_title="FinanceApp 2026", layout="centered")

# --- ESTILO CSS PARA APARÊNCIA DE APP ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    [data-testid="stHeader"] { visibility: hidden; }
    .main-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0px 4px 12px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- MOCKUP DE BANCO DE DADOS (Persistência) ---
# Em um ambiente real, aqui conectaríamos ao Supabase ou Firebase via GitHub Secrets
if 'movimentacoes' not in st.session_state:
    st.session_state.movimentacoes = pd.DataFrame(columns=['Data', 'Descricao', 'Valor', 'Conta', 'Tipo', 'Status'])

# --- INTERFACE DE NAVEGAÇÃO ---
aba1, aba2 = st.tabs(["💬 Registro Chat", "📅 Visão Mensal"])

# --- ABA 1: REGISTRO (CHAT) ---
with aba1:
    st.subheader("Registro Rápido")
    
    # Widgets de Resumo no Cabeçalho
    col1, col2 = st.columns(2)
    pendente_pagar = st.session_state.movimentacoes[(st.session_state.movimentacoes['Tipo'] == 'Despesa') & (st.session_state.movimentacoes['Status'] == 'Pendente')]['Valor'].sum()
    pendente_receber = st.session_state.movimentacoes[(st.session_state.movimentacoes['Tipo'] == 'Receita') & (st.session_state.movimentacoes['Status'] == 'Pendente')]['Valor'].sum()
    
    col1.metric("🔴 A Pagar", f"R$ {pendente_pagar:.2f}")
    col2.metric("🟢 A Receber", f"R$ {pendente_receber:.2f}")

    # Interface de "Chat"
    with st.container():
        input_chat = st.text_input("O que aconteceu hoje?", placeholder="Ex: Almoço 45 Nubank ou Salário 5000 Santander")
        col_btn1, col_btn2 = st.columns(2)
        tipo = col_btn1.selectbox("Tipo", ["Despesa", "Receita", "Investimento"])
        status = col_btn2.selectbox("Status", ["Pendente", "Concluído"])
        
        if st.button("Registrar Movimentação", use_container_width=True):
            nova_linha = {
                'Data': datetime.now().strftime("%d/%m/%Y"),
                'Descricao': input_chat,
                'Valor': 0.0, # Aqui entraria a lógica de extração de número do texto
                'Conta': "Padrão",
                'Tipo': tipo,
                'Status': status
            }
            # Simulação de salvamento permanente
            st.success("Registrado com sucesso!")

# --- ABA 2: VISÃO MENSAL & LEMBRETES ---
with aba2:
    st.subheader("📅 Controle Mensal")
    
    # Lembrete Exclusivo de Investimentos
    st.info("**💡 Lembrete de Investimento:** Não esqueça de realizar o aporte mensal planejado para atingir sua meta de 2026!")
    
    st.write("### Itens Pendentes")
    df_pendente = st.session_state.movimentacoes[st.session_state.movimentacoes['Status'] == 'Pendente']
    if df_pendente.empty:
        st.write("Tudo em dia por aqui! ✅")
    else:
        st.table(df_pendente)
