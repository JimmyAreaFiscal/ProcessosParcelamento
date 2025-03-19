import streamlit as st
import pandas as pd
from model.banco_dados import SessionLocal, ProcessoDB, UsuarioDB
from datetime import datetime

def adicionarProcessos():
    """Página para importar processos via planilha (apenas para Auditores)."""
    # Verificar se o usuário tem permissão
    if "usuario" not in st.session_state:
        st.error("Você precisa estar logado para acessar esta página.")
        return

    session = SessionLocal()
    usuario = session.query(UsuarioDB).filter_by(conta=st.session_state["usuario"]).first()
    session.close()

    if not usuario or usuario.role != "Auditor":
        st.error("Acesso negado. Esta funcionalidade é exclusiva para Auditores.")
        return

    st.title("Adicionar Processos via Planilha 📂")

    st.write("Envie um arquivo **Excel ou CSV** contendo as colunas **nome** e **valor**.")

    # Upload do arquivo
    arquivo = st.file_uploader("Escolha um arquivo", type=["xlsx", "csv"])

    if arquivo:
        try:
            if arquivo.name.endswith(".xlsx"):
                df = pd.read_excel(arquivo)
            else:
                df = pd.read_csv(arquivo)

            # Verificar se as colunas corretas existem
            if not {"nome", "valor"}.issubset(df.columns):
                st.error("O arquivo deve conter as colunas 'nome' e 'valor'.")
                return

            session = SessionLocal()
            processos_adicionados = 0

            for _, row in df.iterrows():
                nome, valor = row["nome"], row["valor"]

                if not nome or not isinstance(valor, (int, float)):  # Validação
                    continue

                processo_existente = session.query(ProcessoDB).filter_by(nome=nome).first()

                if not processo_existente:
                    novo_processo = ProcessoDB(
                        nome=nome,
                        valor=valor,
                        saneado=False,
                        sei="",
                        enviado=False,
                        data_inclusao=datetime.utcnow()
                    )
                    session.add(novo_processo)
                    processos_adicionados += 1

            session.commit()
            session.close()

            st.success(f"Importação concluída! **{processos_adicionados} processos foram adicionados.**")
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {str(e)}")