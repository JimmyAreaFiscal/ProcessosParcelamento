from view.home import home
from view.login import login, criar_conta
import streamlit as st 


# Estrutura principal
def main():
    if "usuario" in st.session_state:
        home()
    else:
        pagina = st.session_state.get("pagina", "login")

        if pagina == "login":
            login()
            if st.button("Criar Conta"):
                st.session_state["pagina"] = "criar_conta"
                st.experimental_rerun()
        elif pagina == "criar_conta":
            criar_conta()
            if st.button("Voltar ao Login"):
                st.session_state["pagina"] = "login"
                st.experimental_rerun()

if __name__ == "__main__":
    main()