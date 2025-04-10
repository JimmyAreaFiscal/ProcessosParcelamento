import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
from service.processo_service import atualizar_processo, exportar_processos
from model.banco_dados import SessionLocal, ProcessoDB, DecisoesJudiciais, EfeitosDecisoesJudiciais
from model.processo import Processo

def verificarProcessos():
    """ Aba para listar e acessar processos existentes e permitir exportação para Excel """
    st.subheader("Lista de Processos")

    session = SessionLocal()

    cnpjs_com_suspensao = (
        session.query(DecisoesJudiciais.cpf_contribuinte)
        .join(EfeitosDecisoesJudiciais, DecisoesJudiciais.efeitos_fk == EfeitosDecisoesJudiciais.id)
        .filter(EfeitosDecisoesJudiciais.descricao_efeitos == "Suspensão do Crédito Tributário")
        .distinct()
    )
    processos = (
        session.query(ProcessoDB)
        .filter(
            ProcessoDB.enviado == False,
            ~ProcessoDB.cnpj_empresa.in_(cnpjs_com_suspensao)
        )
        .order_by(ProcessoDB.valor.desc())
        .limit(15)
        .all()
)
    session.close()

    if not processos:
        st.info("Nenhum processo cadastrado.")
    else:
        for processo in processos:
            ultimo_usuario = processo.usuario_ultima_alteracao or "N/A"
            saneado = "SIM" if processo.saneado else "NÃO"

            with st.expander(f"📄 Processo: **{processo.nome}** - Nome da Empresa: {processo.nome_empresa}"):
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.subheader('Informações do Processo')
                    st.text(f"Saneado: {saneado}")
                    st.text(f'Processo: {processo.sei}')
                    st.text(f'Valor em Débito : R$ {processo.valor}')
                    st.text(f'Última alteração por: {ultimo_usuario}')
                    if st.button(f"🔍 Detalhes", key=processo.nome):
                        st.session_state["processo_selecionado"] = processo.nome
                        st.session_state["pagina"] = "controleProcesso"
                        st.rerun()

                with col2:
                    st.subheader('Alterar informações do Processo')
                    if st.button(f"Mudar para: {'✅ Saneado' if not processo.saneado else '❌ Não Saneado'}", key=f"saneado_{processo.nome}"):
                        atualizar_processo(processo.nome, "saneado", not processo.saneado)
                        st.rerun()

                    sei_input = st.text_input("Alterar número do SEI:", value=processo.sei or "", key=f"sei_{processo.nome}")
                    if st.button("Salvar", key=f"salvar_sei_{processo.nome}"):
                        atualizar_processo(processo.nome, "sei", sei_input)
                        st.success("SEI atualizado com sucesso!")
                        st.rerun()

                    if st.button(f"{'📩 Enviar' if not processo.enviado else '📤 Cancelar envio'}", key=f"enviado_{processo.nome}"):
                        atualizar_processo(processo.nome, "enviado", not processo.enviado)
                        st.rerun()


    st.subheader("📥 Exportar Processos")
    dados_export = exportar_processos()
    if dados_export:
        df = pd.DataFrame(dados_export)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Processos")
        st.download_button(
            label="📊 Baixar Processos em Excel",
            data=output.getvalue(),
            file_name="processos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

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

    st.write(f"📅 **Data de Inclusão:** {processo.data_inclusao.strftime('%d/%m/%Y %H:%M:%S') if processo.data_inclusao else 'N/A'}")
    st.write(f"📅 **Data de Alteração de Saneamento:** {processo.data_saneamento.strftime('%d/%m/%Y %H:%M:%S') if processo.data_saneamento else 'N/A'}")
    st.write(f"📅 **Data de Alteração de SEI:** {processo.data_sei.strftime('%d/%m/%Y %H:%M:%S') if processo.data_sei else 'N/A'}")
    st.write(f"📅 **Data de Alteração de Enviado:** {processo.data_enviado.strftime('%d/%m/%Y %H:%M:%S') if processo.data_enviado else 'N/A'}")

    if st.button("Voltar para Home", key="voltar_home"):
        st.session_state["pagina"] = "home"
        st.rerun()
