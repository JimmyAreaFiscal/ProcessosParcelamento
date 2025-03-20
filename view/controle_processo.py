import streamlit as st
import pandas as pd
from io import BytesIO
from model.banco_dados import SessionLocal
from model.processo import ProcessoDB
from datetime import datetime

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

def exportar_processos():
    """Exporta todos os processos do banco de dados para um arquivo Excel."""
    session = SessionLocal()
    processos = session.query(ProcessoDB).all()
    session.close()

    if not processos:
        st.warning("Nenhum processo encontrado para exportação.")
        return None

    # Criar um DataFrame com os dados dos processos
    data = [{
        "Nome": p.nome,
        "Valor": p.valor,
        "Saneado": "Sim" if p.saneado else "Não",
        "SEI": p.sei or "N/A",
        "Enviado": "Sim" if p.enviado else "Não",
        "Data Inclusão": p.data_inclusao.strftime('%d/%m/%Y') if p.data_inclusao else "N/A",
        "Data Saneamento": p.data_saneamento.strftime('%d/%m/%Y') if p.data_saneamento else "N/A",
        "Data SEI": p.data_sei.strftime('%d/%m/%Y') if p.data_sei else "N/A",
        "Data Enviado": p.data_enviado.strftime('%d/%m/%Y') if p.data_enviado else "N/A",
        "Última Alteração por": p.usuario_ultima_alteracao or "N/A"
    } for p in processos]

    df = pd.DataFrame(data)

    # Criar um buffer de memória para salvar o arquivo Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Processos")
        writer.close()

    return output.getvalue()

def verificarProcessos():
    """ Aba para listar e acessar processos existentes e permitir exportação para Excel """
    st.subheader("Lista de Processos")

    session = SessionLocal()
    processos = session.query(ProcessoDB).filter_by(enviado=False).order_by(ProcessoDB.valor.desc()).limit(15).all()
    session.close()

    if not processos:
        st.info("Nenhum processo cadastrado.")
    else:
        for processo in processos:
            ultimo_usuario = processo.usuario_ultima_alteracao or "N/A"
            saneado = "SIM" if processo.saneado else "NÃO"

            with st.expander(f"📄 Processo: **{processo.nome}**"):
                col1, col2, col3 = st.columns(3)

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

                # Opção de saneamento (booleano)
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

                

    # Botão para exportar todos os processos para Excel
    st.subheader("📥 Exportar Processos")
    excel_data = exportar_processos()
    if excel_data:
        st.download_button(
            label="📊 Baixar Processos em Excel",
            data=excel_data,
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

    # Exibir datas associadas ao processo
    st.write(f"📅 **Data de Inclusão:** {processo.data_inclusao.strftime('%d/%m/%Y %H:%M:%S') if processo.data_inclusao else 'N/A'}")
    st.write(f"📅 **Data de Alteração de Saneamento:** {processo.data_saneamento.strftime('%d/%m/%Y %H:%M:%S') if processo.data_saneamento else 'N/A'}")
    st.write(f"📅 **Data de Alteração de SEI:** {processo.data_sei.strftime('%d/%m/%Y %H:%M:%S') if processo.data_sei else 'N/A'}")
    st.write(f"📅 **Data de Alteração de Enviado:** {processo.data_enviado.strftime('%d/%m/%Y %H:%M:%S') if processo.data_enviado else 'N/A'}")

    if st.button("Voltar para Home"):
        st.session_state["pagina"] = "home"
        st.rerun()