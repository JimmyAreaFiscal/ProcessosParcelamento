from view.home import home, configurarConta
from view.login import login, criar_conta, redefinir_senha
from model.banco_dados import SessionLocal, UsuarioDB
import streamlit as st 
from view.controle_processo import controleProcesso

def main():
    if not st.experimental_user.is_logged_in:
        if st.button("Log in"):
            st.login() 

    else:
        session = SessionLocal()
        usuario = session.query(UsuarioDB).filter_by(conta=st.experimental_user.email).first()
        session.close()
        
        if usuario.role == "aguardando_aprovacao":
            st.warning("Sua conta está aguardando aprovação.")

        elif st.session_state.get("pagina") == "controleProcesso":
            controleProcesso()
        
        else:
            home()

        if st.button("Sair"):
            st.logout()

    

if __name__ == "__main__":
    main()
