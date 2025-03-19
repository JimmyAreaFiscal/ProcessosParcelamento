import streamlit as st
from model.usuario import Usuario  # Importa a classe Usuario do código anterior

# Página de login
def login():
    st.title("Login")

    conta = st.text_input("Usuário", key="login_usuario")
    senha = st.text_input("Senha", type="password", key="login_senha")

    if st.button("Entrar"):
        if conta and senha:
            try:
                usuario = Usuario(conta, senha)
                if usuario.validarSenha(senha):
                    st.session_state["usuario"] = conta  # Guarda a sessão
                    st.success("Login bem-sucedido!")
                    st.rerun()  # Redireciona para a home
                else:
                    st.error("Conta ou senha incorretos.")
            except:
                st.error("Erro ao tentar logar. Verifique os dados.")
        else:
            st.warning("Preencha todos os campos.")

# Página de criação de conta
def criar_conta():
    st.title("Criar Conta")

    conta = st.text_input("Usuário", key="criar_usuario")
    senha = st.text_input("Senha", type="password", key="criar_senha")
    senha_confirma = st.text_input("Confirme a Senha", type="password", key="criar_senha_confirma")

    if st.button("Criar Conta"):
        if not conta or not senha or not senha_confirma:
            st.warning("Preencha todos os campos.")
        elif senha != senha_confirma:
            st.error("As senhas não coincidem.")
        else:
            try:
                usuario = Usuario(conta, senha)
                usuario.criarConta()
                st.success("Conta criada com sucesso! Volte para a tela de login.")
                if st.button("Voltar ao Login"):
                    st.session_state["pagina"] = "login"
                    st.rerun()
            except ValueError:
                st.error("Usuário já existe. Escolha outro nome de usuário.")
            except:
                st.error("Erro ao criar conta. Tente novamente.")