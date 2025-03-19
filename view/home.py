import streamlit as st
from model.banco_dados import ProcessoDB, get_db, SessionLocal
from model.usuario import Usuario
from view.adicionar_processo import adicionarProcessos
from view.admin import painelAdmin
from datetime import datetime 

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

def atualizar_processo(nome, campo, valor):
    """Atualiza um campo específico do processo no banco de dados."""
    session = SessionLocal()
    processo = session.query(ProcessoDB).filter_by(nome=nome).first()

    if processo:
        setattr(processo, campo, valor)

        # Registrar data de alteração conforme o campo
        if campo == "saneado":
            processo.data_saneamento = datetime.now()
            processo.saneado = valor
        elif campo == "sei":
            processo.data_sei = datetime.now()
            processo.sei = valor
        elif campo == "enviado":
            processo.data_enviado = datetime.now()
            processo.enviado = valor

        session.commit()
    
    session.close()


def verificarProcessos():
    """ Aba para listar e acessar processos existentes """
    st.subheader("Lista de Processos")

    session = SessionLocal()
    processos = session.query(ProcessoDB).filter_by(enviado=False).order_by(ProcessoDB.valor.desc()).limit(15).all()
    session.close()

    if not processos:
        st.info("Nenhum processo cadastrado.")
    else:
        for processo in processos:
            if processo.saneado:
                saneado = 'NÃO'
            else:
                saneado = 'SIM'

            with st.expander(f"📄 Processo: **{processo.nome}** - Valor: R$ {processo.valor} - Situação: Saneado: {saneado} - Processo: {processo.sei} - Não enviado!"):
                col1, col2, col3 = st.columns(3)

                # Opção de saneamento (booleano)
                with col1:
                    if st.button(f"{'✅ Saneado' if processo.saneado else '❌ Não Saneado'}", key=f"saneado_{processo.nome}"):
                        atualizar_processo(processo.nome, "saneado", not processo.saneado)
                        st.rerun()

                # Campo para editar/remover SEI
                with col2:
                    sei_input = st.text_input("Número SEI:", value=processo.sei or "", key=f"sei_{processo.nome}")
                    if st.button("Salvar SEI", key=f"salvar_sei_{processo.nome}"):
                        atualizar_processo(processo.nome, "sei", sei_input)
                        st.success("SEI atualizado com sucesso!")
                        st.rerun()

                # Opção de envio (booleano)
                with col3:
                    if st.button(f"{'📩 Enviado' if processo.enviado else '📤 Não Enviado'}", key=f"enviado_{processo.nome}"):
                        atualizar_processo(processo.nome, "enviado", not processo.enviado)
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