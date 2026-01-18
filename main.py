import streamlit as st
from supabase import create_client, Client

# Conexão com o Banco de Dados (Segredos do GitHub)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="FinanceApp 2026", layout="centered")

# --- FUNÇÕES DE BANCO ---
def salvar_dados(desc, valor, tipo, status, conta):
    supabase.table("transacoes").insert({
        "descricao": desc, "valor": valor, "tipo": tipo, "status": status, "conta": conta
    }).execute()

def buscar_dados():
    res = supabase.table("transacoes").select("*").execute()
    return res.data

# --- INTERFACE ---
aba1, aba2 = st.tabs(["💬 Chat de Registro", "📅 Visão Mensal"])

with aba1:
    # Lógica de cálculo dos totais vindo do banco
    dados = buscar_dados()
    df = pd.DataFrame(dados)
    
    if not df.empty:
        p_pagar = df[(df['tipo'] == 'Despesa') & (df['status'] == 'Pendente')]['valor'].sum()
        p_receber = df[(df['tipo'] == 'Receita') & (df['status'] == 'Pendente')]['valor'].sum()
    else:
        p_pagar = p_receber = 0

    col1, col2 = st.columns(2)
    col1.metric("🔴 Pagar este mês", f"R$ {p_pagar}")
    col2.metric("🟢 Receber este mês", f"R$ {p_receber}")

    with st.expander("Novo Registro", expanded=True):
        desc = st.text_input("O que foi feito?")
        vlr = st.number_input("Valor (R$)", min_value=0.0)
        tp = st.selectbox("Categoria", ["Despesa", "Receita", "Investimento"])
        stt = st.selectbox("Status", ["Pendente", "Concluído"])
        
        if st.button("Salvar no App"):
            salvar_dados(desc, vlr, tp, stt, "Conta Principal")
            st.success("Informação salva para ambos os usuários!")
            st.rerun()

with aba2:
    st.info("💡 **Lembrete:** Faltam R$ X para sua meta de investimento este mês.")
    if not df.empty:
        st.write("### Itens Pendentes")
        st.dataframe(df[df['status'] == 'Pendente'])
