from datetime import datetime
from model.banco_dados import SessionLocal, ProcessoDB, ProcessoHistoricoDB
import streamlit as st

def atualizar_processo(nome: str, campo: str, valor):
    """
    Atualiza um campo de um processo e registra a alteração com data e usuário.
    """
    session = SessionLocal()
    processo = session.query(ProcessoDB).filter_by(nome=nome).first()

    if processo:
        usuario_logado = st.session_state.get("usuario", "Desconhecido")
        setattr(processo, campo, valor)
        processo.usuario_ultima_alteracao = usuario_logado
        agora = datetime.now()

        if campo == "saneado":
            processo.data_saneamento = agora
        elif campo == "sei":
            processo.data_sei = agora
        elif campo == "enviado":
            processo.data_enviado = agora

        session.commit()
    session.close()

def exportar_processos():
    """
    Exporta todos os processos do banco como lista de dicionários.
    """
    session = SessionLocal()
    processos = session.query(ProcessoDB).all()
    session.close()

    return [
        {
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
        }
        for p in processos
    ]

def inserir_ou_atualizar_processo(processo_model):
    """
    Insere novo processo ou atualiza existente mantendo histórico.
    """
    session = SessionLocal()
    existente = session.query(ProcessoDB).filter_by(nome=processo_model.retornarNome()).first()

    if existente:
        historico = ProcessoHistoricoDB(
            id=str(existente.id) + "_hist" + str(int(session.query(ProcessoHistoricoDB).count()) + 1),
            nome=existente.nome,
            valor=existente.valor,
            saneado=existente.saneado,
            sei=existente.sei,
            enviado=existente.enviado
        )
        session.add(historico)

        existente.valor = processo_model.retornarValor()
        existente.saneado = processo_model.retornarSaneado()
        existente.sei = processo_model.retornarSei()
        existente.enviado = processo_model.retornarEnviado()
    else:
        novo = ProcessoDB(
            nome=processo_model.retornarNome(),
            valor=processo_model.retornarValor(),
            saneado=processo_model.retornarSaneado(),
            sei=processo_model.retornarSei(),
            enviado=processo_model.retornarEnviado()
        )
        session.add(novo)

    session.commit()
    session.close()
