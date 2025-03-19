import streamlit as st
from model.banco_dados import SessionLocal, ProcessoDB

def controleProcesso():
    """ Página para exibir detalhes do processo selecionado """
    if "processo_selecionado" not in st.session_state:
        st.warning("Nenhum processo selecionado.")
        return

    nome_processo = st.session_state["processo_selecionado"]

    session = SessionLocal()
    processo = session.query(ProcessoDB).filter_by(nome=nome_processo).first()
    session.close()

    if not processo:
        st.error("O processo não foi encontrado.")
        return

    st.title(f"Detalhes do Processo: {processo.nome}")

    st.write(f"**Valor:** {processo.valor}")
    st.write(f"**Saneado:** {'Sim' if processo.saneado else 'Não'}")
    st.write(f"**SEI:** {processo.sei}")
    st.write(f"**Enviado:** {'Sim' if processo.enviado else 'Não'}")

    # Exibir datas associadas ao processo
    st.write(f"📅 **Data de Inclusão:** {processo.data_inclusao.strftime('%d/%m/%Y %H:%M:%S') if processo.data_inclusao else 'N/A'}")
    st.write(f"📅 **Data de Alteração de Saneamento:** {processo.data_saneamento.strftime('%d/%m/%Y %H:%M:%S') if processo.data_saneamento else 'N/A'}")
    st.write(f"📅 **Data de Alteração de SEI:** {processo.data_sei.strftime('%d/%m/%Y %H:%M:%S') if processo.data_sei else 'N/A'}")
    st.write(f"📅 **Data de Alteração de Enviado:** {processo.data_enviado.strftime('%d/%m/%Y %H:%M:%S') if processo.data_enviado else 'N/A'}")

    if st.button("Voltar para Home"):
        st.session_state["pagina"] = "home"
        st.rerun()