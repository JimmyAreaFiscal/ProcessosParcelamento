"""
Classe para realizar processamento dos processos de parcelamento.

"""
from sqlalchemy import Column, String, Float, Boolean
from model.banco_dados import ProcessoDB, ProcessoHistoricoDB, SessionLocal, Base, engine


class Processo:

    def __init__(self, nome: str, valor: float, saneado: bool, sei: str, enviado: bool):
        self._nome = nome 
        self._valor = valor 
        self._saneado = saneado 
        self._sei = sei 
        self._enviado = enviado 

    def alterarSaneado(self, saneado: bool):
        self._saneado = saneado 

    def alterarSei(self, num_sei: str):
        self._sei = num_sei

    def alterarEnvio(self, situacao: bool):
        self._enviado = situacao 

    def retornarNome(self):
        return self._nome
    
    def retornarValor(self):
        return self._valor
    
    def retornarSaneado(self):
        return self._saneado
    
    def retornarSei(self):
        return self._sei

    def retornarEnviado(self):
        return self._enviado
    
    def inserirEmBancoDeDados(self):
        session = SessionLocal()

        # Verificar se o processo já existe
        processo_existente = session.query(ProcessoDB).filter_by(nome=self._nome).first()

        if processo_existente:
            # Salvar os dados antigos na tabela de histórico
            historico = ProcessoHistoricoDB(
                id=str(processo_existente.id) + "_hist" + str(int(session.query(ProcessoHistoricoDB).count()) + 1),
                nome=processo_existente.nome,
                valor=processo_existente.valor,
                saneado=processo_existente.saneado,
                sei=processo_existente.sei,
                enviado=processo_existente.enviado,
            )
            session.add(historico)

            # Atualizar os dados na tabela de processos
            processo_existente.valor = self.retornarNome()
            processo_existente.saneado = self.retornarSaneado()
            processo_existente.sei = self.retornarSei()
            processo_existente.enviado = self.retornarEnviado()

        else:
            # Inserir um novo processo
            novo_processo = ProcessoDB(
                nome=self.retornarNome(),
                valor=self.retornarValor(),
                saneado=self.retornarSaneado(),
                sei=self.retornarSei(),
                enviado=self.retornarEnviado(),
            )
            session.add(novo_processo)

        session.commit()
        session.close()
