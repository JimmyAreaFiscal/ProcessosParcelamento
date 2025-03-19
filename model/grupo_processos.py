from model.processo import Processo
import pandas as pd 

class GrupoProcessos:

    def __init__(self):
        self._processos = [] 

    def inserirProcesso(self, processo: Processo):
        self._processos.append(processo)

    def retornarSituacao(self):
        lista_processos = {
                           'NúmeroProcessos': [],
                           'ValoresProcessos': [],
                           'Saneado': [],
                           'SEI': [],
                           'EnviadoParaDívida':[]
                           }
        
        for processo in self._processos:
            lista_processos['NúmeroProcessos'].append(processo.retornarNome())
            lista_processos['ValoresProcessos'].append(processo.retornarValor())
            lista_processos['Saneado'].append(processo.retornarSaneado())
            lista_processos['SEI'].append(processo.retornarSei())
            lista_processos['EnviadoParaDívida'].append(processo.retornarEnviado())

        df = pd.DataFrame(lista_processos)

        df.sort_values(by='ValoresProcessos', inplace=True, ascending=False)
        return df 
