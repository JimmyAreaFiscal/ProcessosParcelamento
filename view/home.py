import streamlit as st
from model.banco_dados import ProcessoDB, get_db, SessionLocal
from model.usuario import Usuario
from view.adicionar_processo import adicionarProcessos
from view.admin import painelAdmin
from datetime import datetime 
from sqlalchemy.sql import extract

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
    """Atualiza um campo específico do processo no banco de dados e registra o usuário que fez a alteração."""
    session = SessionLocal()
    processo = session.query(ProcessoDB).filter_by(nome=nome).first()

    if processo:
        usuario_logado = st.session_state.get("usuario", "Desconhecido")  # Captura o usuário logado

        setattr(processo, campo, valor)
        processo.usuario_ultima_alteracao = usuario_logado  # Salva o nome do usuário que alterou

        # Registrar data de alteração conforme o campo
        if campo == "saneado":
            processo.data_saneamento = datetime.now()
        elif campo == "sei":
            processo.data_sei = datetime.now()
        elif campo == "enviado":
            processo.data_enviado = datetime.now()

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

            with st.expander(f"📄 Processo: **{processo.nome}**         Situação: Saneado: {saneado}"):
                
                col1, col2 = st.columns(2)

                with col1:
                    st.text(f"Valor: R$ {processo.valor}")
                    st.text(f"Situação: Saneado: {saneado}")
                    st.text(f"Processo: {processo.sei}")
                    if st.button(f"🔍 Detalhes", key=processo.nome):
                        st.session_state["processo_selecionado"] = processo.nome
                        st.session_state["pagina"] = "controleProcesso"
                        st.rerun()
                

                # Opção de saneamento (booleano)
                with col2:
                    if st.button(f"Marcar como {'✅ Saneado' if processo.saneado else '❌ Não Saneado'}", key=f"saneado_{processo.nome}"):
                        atualizar_processo(processo.nome, "saneado", not processo.saneado)
                        st.rerun()

                    sei_input = st.text_input("Número SEI:", value=processo.sei or "", key=f"sei_{processo.nome}")
                    if st.button("Salvar SEI", key=f"salvar_sei_{processo.nome}"):
                        atualizar_processo(processo.nome, "sei", sei_input)
                        st.success("SEI atualizado com sucesso!")
                        st.rerun()

                    if st.button(f"{'📩 Enviado' if processo.enviado else '📤 Não Enviado'}", key=f"enviado_{processo.nome}"):
                        atualizar_processo(processo.nome, "enviado", not processo.enviado)
                        st.rerun()

                



def obter_estatisticas():
    """Consulta o banco e retorna estatísticas dos processos."""
    session = SessionLocal()
    total_nao_saneados = session.query(ProcessoDB).filter_by(saneado=False).count()
    total_sem_sei = session.query(ProcessoDB).filter((ProcessoDB.sei == None) | (ProcessoDB.sei == "")).count()
    total_nao_enviados = session.query(ProcessoDB).filter_by(enviado=False).count()
    
    # Filtrar processos enviados no mês atual usando extract()
    mes_atual = datetime.now().month
    ano_atual = datetime.now().year
    total_enviados_mes = session.query(ProcessoDB).filter(
        ProcessoDB.enviado == True,
        ProcessoDB.data_enviado != None,
        extract('month', ProcessoDB.data_enviado) == mes_atual,
        extract('year', ProcessoDB.data_enviado) == ano_atual
    ).count()

    session.close()

    return total_nao_saneados, total_sem_sei, total_nao_enviados, total_enviados_mes

def home():
    """ Página principal com abas e estatísticas no sidebar """
    st.title(f"Bem-vindo, {st.session_state.get('usuario', '')}! 👋")

    # Obter estatísticas
    total_nao_saneados, total_sem_sei, total_nao_enviados, total_enviados_mes = obter_estatisticas()

    # Exibir estatísticas no sidebar
    with st.sidebar:
        st.header("📊 Estatísticas dos Processos")
        st.write(f"❌ **Não Saneados:** {total_nao_saneados}")
        st.write(f"📂 **Sem SEI:** {total_sem_sei}")
        st.write(f"📤 **Não Enviados:** {total_nao_enviados}")
        st.write(f"📩 **Enviados neste mês:** {total_enviados_mes}")

    # Criando abas estilizadas
    aba1, aba2, aba3, aba4 = st.tabs(["📋 Verificar Processos", "➕ Adicionar Processos", "⚙️ Configurar Conta", "🛠️ Painel de Administração"])

    with aba1:
        verificarProcessos()

    with aba2:
        adicionarProcessos()

    with aba3:
        configurarConta()

    with aba4:
        painelAdmin()

    # Botão de saída no final da página
    if st.button("🚪 Sair"):
        del st.session_state["usuario"]
        st.rerun()
