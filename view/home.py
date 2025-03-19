import streamlit as st
from model.banco_dados import ProcessoDB, get_db

# Página Home após login
def configurarConta():
    """ Aba para alterar senha do usuário logado """
    st.subheader("Alterar Senha")

    conta = st.session_state.get("usuario", "")
    senha_atual = st.text_input("Senha Atual", type="password")
    nova_senha = st.text_input("Nova Senha", type="password")
    confirmar_senha = st.text_input("Confirme a Nova Senha", type="password")

    if st.button("Alterar Senha"):
        if not senha_atual or not nova_senha or not confirmar_senha:
            st.warning("Preencha todos os campos.")
        elif nova_senha != confirmar_senha:
            st.error("As senhas não coincidem.")
        else:
            session = get_db()
            usuario = session.query(Usuario).filter_by(conta=conta).first()
            session.close()

            if usuario and usuario.validar_senha(senha_atual):
                usuario.mudarSenha(nova_senha)
                st.success("Senha alterada com sucesso!")
            else:
                st.error("Senha atual incorreta.")

def verificarProcessos():
    """ Aba para listar e acessar processos existentes """
    st.subheader("Lista de Processos")

    session = get_db()
    processos = session.query(ProcessoDB).all()
    session.close()

    if not processos:
        st.info("Nenhum processo cadastrado.")
    else:
        for processo in processos:
            if st.button(f"🔍 {processo.nome}"):
                st.session_state["processo_selecionado"] = processo.nome
                st.session_state["pagina"] = "controleProcesso"
                st.experimental_rerun()

def home():
    """ Página principal com abas de configuração e visualização de processos """
    st.title(f"Bem-vindo, {st.session_state.get('usuario', '')}!")

    aba = st.sidebar.radio("Menu", ["Configurar Conta", "Verificar Processos"])

    if aba == "Configurar Conta":
        configurarConta()
    elif aba == "Verificar Processos":
        verificarProcessos()

    if st.sidebar.button("Sair"):
        del st.session_state["usuario"]
        st.experimental_rerun()