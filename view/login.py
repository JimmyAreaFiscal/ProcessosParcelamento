import streamlit as st
from model.usuario import Usuario  # Importa a classe Usuario do código anterior
from model.banco_dados import SessionLocal, UsuarioDB

# Página de login
def login():
    """Tela de login do sistema"""
    st.title("🔐 Login")

    conta = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        session = SessionLocal()
        usuario = session.query(UsuarioDB).filter_by(conta=conta).first()
        user = Usuario(conta=usuario.conta, senha=senha)

        if usuario and user.validarSenha(senha):
            if usuario.precisa_redefinir_senha:
                st.session_state["usuario_redefinir"] = conta  # Armazena o usuário para redefinir senha
                st.session_state["pagina"] = "redefinir_senha"
                st.rerun()
            else:
                st.session_state["usuario"] = conta
                st.session_state["pagina"] = "home"
                st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")

def redefinir_senha():
    """Página para redefinir senha após um reset pelo admin"""
    st.title("🔑 Redefinir Senha")

    conta = st.session_state.get("usuario_redefinir", "")
    if not conta:
        st.error("Erro ao carregar usuário.")
        return


    nova_senha = st.text_input("Nova Senha", type="password")
    confirmar_senha = st.text_input("Confirme a Nova Senha", type="password")
    
    user = Usuario(conta=conta, senha='')

    if st.button("Alterar Senha"):
        if not nova_senha or not confirmar_senha:
            st.warning("Preencha todos os campos.")
        elif nova_senha != confirmar_senha:
            st.error("As senhas não coincidem.")
        else:
            session = SessionLocal()
            usuario = session.query(UsuarioDB).filter_by(conta=conta).first()

            if usuario:
                user.mudarSenha(usuario, nova_senha)
                usuario.precisa_redefinir_senha = False  # Remove a necessidade de redefinição
                session.commit()
                session.close()
                st.success("Senha alterada com sucesso! Faça login novamente.")
                del st.session_state["usuario_redefinir"]
                st.session_state["pagina"] = "login"
                st.rerun()

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