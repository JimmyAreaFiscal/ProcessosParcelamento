from view.home import home, configurarConta
from view.login import login, criar_conta
from model.banco_dados import SessionLocal, UsuarioDB
import streamlit as st 
from view.controle_processo import controleProcesso


def main():
    if "usuario" in st.session_state:
        session = SessionLocal()
        usuario = session.query(UsuarioDB).filter_by(conta=st.session_state["usuario"]).first()
        session.close()

        if usuario.role == "aguardando_aprovacao":
            st.warning("Sua conta está aguardando aprovação. Você pode apenas trocar sua senha.")
            configurarConta()
        elif st.session_state.get("pagina") == "controleProcesso":
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