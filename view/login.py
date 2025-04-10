import streamlit as st
from model.usuario import Usuario  # Importa a classe Usuario do código anterior
from model.banco_dados import SessionLocal
from model.usuario import UsuarioDB
import hashlib
import os 

# Página de login
def login():

    st.set_page_config(page_title='Sistema de Controle de Parcelamentos da Divisão de Parcelamentos', layout='centered')

    # Captura e-mail da sessão OAuth
    email_google = st.experimental_user.email if hasattr(st, "experimental_user") and st.experimental_user else None

    # Se for o admin definido no secrets, autentica via formulário
    admin_email = st.secrets["admin"]["usuario"]

    if email_google and email_google == admin_email:
        st.title("Login de Administrador")
        senha = st.text_input("Senha do Administrador", type="password")

        if st.button("Entrar como Admin"):
            session = SessionLocal()
            usuario = session.query(UsuarioDB).filter_by(conta=admin_email).first()
            session.close()

            if usuario:
                senha_hash = hashlib.pbkdf2_hmac('sha256', senha.encode(), usuario.salt, 100000)
                if senha_hash == usuario.senha_hash:
                    st.session_state["usuario"] = admin_email
                    st.session_state["pagina"] = "home"
                    st.success("Login de administrador realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("Senha incorreta.")
            else:
                st.error("Conta de administrador não encontrada.")

        return

    # Login padrão via Google OAuth
    if not email_google:
        st.info("Faça login com sua conta Google no topo direito da página.")
        return

    st.success(f"Autenticado como: {email_google}")

    session = SessionLocal()
    usuario = session.query(UsuarioDB).filter_by(conta=email_google).first()

    if not usuario:
        novo_usuario = UsuarioDB(conta=email_google, role="aguardando_aprovacao", precisa_redefinir_senha=False, salt=b"", senha_hash=b"")
        session.add(novo_usuario)
        session.commit()
        st.warning("Usuário autenticado, mas não cadastrado no sistema. Aguarde aprovação de um administrador.")
        session.close()
        return

    if usuario.precisa_redefinir_senha:
        st.session_state["usuario_redefinir"] = email_google
        st.session_state["pagina"] = "redefinir_senha"
        st.rerun()

    st.session_state["usuario"] = email_google
    st.session_state["pagina"] = "home"
    session.close()
    st.rerun()

