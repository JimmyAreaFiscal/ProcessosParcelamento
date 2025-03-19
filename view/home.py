import streamlit as st

# Página Home após login
def home():
    st.title("Home")
    st.write(f"Bem-vindo, {st.session_state['usuario']}!")

    if st.button("Sair"):
        del st.session_state["usuario"]
        st.experimental_rerun()