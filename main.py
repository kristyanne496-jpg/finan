import streamlit as st
from supabase import create_client

# Tenta capturar as chaves ignorando espaços ou erros de digitação
try:
    # O .get ajuda a evitar o erro KeyError travando o app
    url = st.secrets.get("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY")

    if not url or not key:
        st.error("⚠️ As chaves não foram encontradas nos Secrets do Streamlit.")
        st.info("Acesse Settings > Secrets e verifique se os nomes estão em MAIÚSCULO.")
        st.stop()

    # Cria o cliente do banco de dados
    supabase = create_client(url.strip(), key.strip())
    
except Exception as e:
    st.error(f"❌ Erro crítico: {e}")
    st.stop()

# --- CONTINUAÇÃO DO SEU APP ---
st.title("💰 FinanceApp 2026")
# ... resto do código das abas
