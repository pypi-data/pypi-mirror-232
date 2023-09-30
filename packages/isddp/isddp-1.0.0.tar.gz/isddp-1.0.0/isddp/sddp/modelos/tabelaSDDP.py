# Imports de módulos externos
from cfinterface.components.line import Line
from cfinterface.components.integerfield import IntegerField
from cfinterface.components.literalfield import LiteralField
from isddp.sddp.modelos.blocos.tabelacsv import TabelaCSV

import pandas as pd  # type: ignore
from copy import deepcopy
from typing import IO, List, Dict


class BlocoTabelaSDDP(TabelaCSV):
    """
    Bloco com as informações dos cortes da evaporação linear.
    """
    BEGIN_PATTERN = ""
    IDENTIFIER = "Estg,Ser.,Bloc"
    END_PATTERN = ""

    LINE_MODEL = Line(
        [
            IntegerField(size=80),
            IntegerField(size=80),
            IntegerField(size=80),
        ],
        delimiter=",",
    )

    #COLUMN_NAMES = [
    #    "Estagio",
    #    "Serie",
    #    "Bloco",
    #]
    COLUMN_NAMES = [
        "periodo",
        "serie",
        "patamar",
    ]

class BlocoTabelaCadastro(TabelaCSV):
    """
    Leitura do eco de cadastro das hidrelétricas athidr.csv
    """
    BEGIN_PATTERN = ""
    IDENTIFIER = "Nome        ,Sistema     ,"
    END_PATTERN = ""

    LINE_MODEL = Line(
        [
            LiteralField(size=80),
            LiteralField(size=80),
        ],
        delimiter=",",
    )

    COLUMN_NAMES = [
        "Nome",
        "Sistema",
    ]
    
    def read(self, file: IO, *args, **kwargs):        
        le = 0
        self.line_model = deepcopy(self.LINE_MODEL)
        self.column_names = deepcopy(self.COLUMN_NAMES)
        dados: Dict[str, List] = {c: [] for c in self.column_names} 
        for linha in file.readlines():
            if(self.IDENTIFIER in linha):
                 for i, elemento in enumerate(linha.strip().split(',')):
                      if(i>=2):
                           self.line_model.fields.append(LiteralField(size=80))
                           self.column_names.append(str(elemento.replace(" ", "")))
                 dados: Dict[str, List] = {c: [] for c in self.column_names} 

            if len(linha) < 3:
                le = 0 
            if le == 1:
                dados_linha = self.line_model.read(linha)
                for i, c in enumerate(self.column_names):
                        dados[c].append(dados_linha[i])
            if self.IDENTIFIER in linha:
                le = 1

        #self.data = self._monta_df(dados) 
        self.data = pd.DataFrame(data=dados, columns=self.column_names)


class BlocoTabelaPersonalizada(TabelaCSV):
    """
    Bloco com as informações dos cortes da evaporação linear.
    """
    BEGIN_PATTERN = ""
    IDENTIFIER = "Stag,Seq.,Blck"
    END_PATTERN = ""

    LINE_MODEL = Line(
        [
            IntegerField(size=80),
            IntegerField(size=80),
            IntegerField(size=80),
        ],
        delimiter=",",
    )

    #COLUMN_NAMES = [
    #    "Estagio",
    #    "Serie",
    #    "Bloco",
    #]
    COLUMN_NAMES = [
        "estagio",
        "cenario",
        "patamar",
    ]