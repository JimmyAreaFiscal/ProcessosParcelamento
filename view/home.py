import streamlit as st
from model.banco_dados import ProcessoDB, get_db
from model.usuario import Usuario
from view.adicionar_processo import adicionarProcessos
from view.admin import painelAdmin

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

            if usuario and usuario.validarSenha(senha_atual):
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
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📄 **{processo.nome}** - R$ {processo.valor}")
            with col2:
                if st.button(f"🔍 Detalhes", key=processo.nome):
                    st.session_state["processo_selecionado"] = processo.nome
                    st.session_state["pagina"] = "controleProcesso"
                    st.rerun()

def home():
    """ Página principal com abas de configuração e visualização de processos """
    st.title(f"Bem-vindo, {st.session_state.get('usuario', '')}!")

    aba = st.sidebar.radio("Menu", ["Configurar Conta", "Verificar Processos", "Adicionar Processos", "Painel de Administração"])

    if aba == "Configurar Conta":
        configurarConta()
    elif aba == "Verificar Processos":
        verificarProcessos()
    elif aba == "Adicionar Processos":
        adicionarProcessos()
    elif aba == "Painel de Administração":
        painelAdmin()

    if st.sidebar.button("Sair"):
        del st.session_state["usuario"]
        st.rerun()