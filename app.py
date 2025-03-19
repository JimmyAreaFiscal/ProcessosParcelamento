from view.home import home
from view.login import login, criar_conta
import streamlit as st 
from view.controle_processo import controleProcesso

def main():
    if "usuario" in st.session_state:
        if st.session_state.get("pagina") == "controleProcesso":
            controleProcesso()
        else:
            home()
    else:
        pagina = st.session_state.get("pagina", "login")

        if pagina == "login":
            login()
            if st.button("Criar Conta"):
                st.session_state["pagina"] = "criar_conta"
                st.rerun()
        elif pagina == "criar_conta":
            criar_conta()
            if st.button("Voltar ao Login"):
                st.session_state["pagina"] = "login"
                st.rerun()

if __name__ == "__main__":
    main()