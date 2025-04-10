"""
Classe para representar os dados de um processo de parcelamento.
"""

class Processo:

    def __init__(self, nome: str, valor: float, saneado: bool, sei: str, enviado: bool):
        self._nome = nome
        self._valor = valor
        self._saneado = saneado
        self._sei = sei
        self._enviado = enviado

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
