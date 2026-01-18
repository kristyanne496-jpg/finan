import streamlit as st
import pandas as pd
from supabase import create_client, Client
import re
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FinanceApp 2026", layout="centered")

# --- CONEXÃO COM BANCO DE DADOS (SUPABASE) ---
try:
    url = st.secrets.get("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY")
    if not url or not key:
        st.error("⚠️ Configure SUPABASE_URL e SUPABASE_KEY nos Secrets do Streamlit.")
        st.stop()
    supabase: Client = create_client(url.strip(), key.strip())
except Exception as e:
    st.error(f"Erro de Conexão: {e}")
    st.stop()

# --- ESTILO CSS PARA APARÊNCIA DE APP ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    [data-testid="stHeader"] { visibility: hidden; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #eeeeee; border-radius: 10px 10px 0 0; padding: 10px 20px; 
    }
    .stTabs [aria-selected="true"] { background-color: #ffffff !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE LÓGICA ---
def extrair_dados_chat(texto):
    """Extrai valor e descrição básica do texto do chat"""
    valores = re.findall(r'\d+(?:[.,]\d+)?', texto)
    valor = float(valores[0].replace(',', '.')) if valores else 0.0
    desc = re.sub(r'\d+(?:[.,]\d+)?', '', texto).strip()
    return desc, valor

def salvar_no_banco(desc, valor, tipo, status, conta):
    supabase.table("transacoes").insert({
        "descricao": desc, "valor": valor, "tipo": tipo, "status": status, "conta": conta,
        "data": datetime.now().strftime("%Y-%m-%d")
    }).execute()

def buscar_dados():
    res = supabase.table("transacoes").select("*").order("created_at", desc=True).execute()
    return pd.DataFrame(res.data)

# --- INTERFACE DO APLICATIVO ---
st.title("💰 FinanceApp 2026")

aba1, aba2 = st.tabs(["💬 Chat de Registro", "📅 Visão Mensal"])

# --- ABA 1: CHAT DE REGISTRO ---
with aba1:
    # Busca dados atuais para os indicadores
    df_dados = buscar_dados()
    
    if not df_dados.empty:
        # Garante que a coluna valor é numérica
        df_dados['valor'] = pd.to_numeric(df_dados['valor'])
        pagar = df_dados[(df_dados['tipo'] == 'Despesa') & (df_dados['status'] == 'Pendente')]['valor'].sum()
        receber = df_dados[(df_dados['tipo'] == 'Receita') & (df_dados['status'] == 'Pendente')]['valor'].sum()
    else:
        pagar = receber = 0.0

    # Cards de Resumo
    c1, c2 = st.columns(2)
    c1.metric("🔴 A Pagar (Mês)", f"R$ {pagar:,.2f}")
    c2.metric("🟢 A Receber (Mês)", f"R$ {receber:,.2f}")

    st.divider()

    # Interface do Chat
    st.write("### O que aconteceu agora?")
    entrada = st.text_input("Ex: Mercado 150 Nubank", placeholder="Digite a descrição e o valor...")
    
    col_t, col_s, col_b = st.columns([1, 1, 1])
    tipo_sel = col_t.selectbox("Tipo", ["Despesa", "Receita", "Investimento"])
    status_sel = col_s.selectbox("Status", ["Pendente", "Concluído"])
    banco_sel = col_b.selectbox("Banco", ["Nubank", "Santander", "Inter", "Dinheiro"])

    if st.button("🚀 Registrar no Banco", use_container_width=True):
        if entrada:
            desc_limpa, valor_extraido = extrair_dados_chat(entrada)
            salvar_no_banco(desc_limpa, valor_extraido, tipo_sel, status_sel, banco_sel)
            st.success(f"Registrado: {desc_limpa} - R$ {valor_extraido}")
            st.rerun()
        else:
            st.warning("Digite algo no chat antes de salvar.")

# --- ABA 2: VISÃO MENSAL ---
with aba2:
    st.subheader("📋 Controle de Pendências")
    
    # Lembrete de Investimento (Fixado)
    st.warning("🚀 **Lembrete de Investimento:** Não esqueça de garantir o aporte deste mês para o seu futuro!")

    if not df_dados.empty:
        # Filtra apenas o que falta pagar ou receber
        pendentes = df_dados[df_dados['status'] == 'Pendente']
        
        if not pendentes.empty:
            st.write("#### Itens que ainda faltam:")
            # Formatação para exibição
            display_df = pendentes[['data', 'descricao', 'valor', 'tipo', 'conta']]
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.success("✅ Tudo pago e recebido por enquanto!")
            
        st.divider()
        with st.expander("Ver histórico completo"):
            st.table(df_dados)
    else:
        st.info("Nenhum dado encontrado no banco de dados.")
