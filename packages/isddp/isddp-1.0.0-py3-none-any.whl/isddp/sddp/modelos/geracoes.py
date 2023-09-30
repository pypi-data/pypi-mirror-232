# Imports de módulos externos
from cfinterface.components.line import Line
from cfinterface.components.integerfield import IntegerField
from cfinterface.components.literalfield import LiteralField
from cfinterface.components.floatfield import FloatField
from cfinterface.components.datetimefield import DatetimeField
from datetime import datetime

from isddp.sddp.modelos.blocos.tabelacsv import TabelaCSV


from typing import IO, List, Dict
import pandas as pd  # type: ignore


class GeracaoTotal(TabelaCSV):
    """
    Bloco com as informações dos cortes da evaporação linear.
    """
    BEGIN_PATTERN = ""
    IDENTIFIER = "Etapa,Total Hidro"
    SUBMERCADO = "Geracao"
    END_PATTERN = ""



    LINE_MODEL = Line(
        [
            LiteralField(size=80),
           #DatetimeField(size=7, format="%Y/%m"),
            FloatField(size=80, decimal_digits=2),
            FloatField(size=80, decimal_digits=2),
            FloatField(size=80, decimal_digits=2),
            FloatField(size=80, decimal_digits=2),
            FloatField(size=80, decimal_digits=2),
            FloatField(size=80, decimal_digits=2),
        ],
        delimiter=",",
    )


    COLUMN_NAMES = [
        "submercado",
        "periodo",
        "total_hidreletrica",
        "total_termica",
        "total_renovavel",
        "total_bateria",
        "total_injetado",
        "deficit",
    ]
    

    def read(self, file: IO, *args, **kwargs):        
        le = 0
        dados: Dict[str, List] = {c: [] for c in self.__class__.COLUMN_NAMES} 

        for linha in file.readlines():
            #print(linha)

            if self.SUBMERCADO in linha:
                SUBMERCADO = linha.strip()[15:50]

            if len(linha) < 3:
                le = 0 
            if le == 1:
                dados_linha = self.__class__.LINE_MODEL.read(linha)
                for i, c in enumerate(self.__class__.COLUMN_NAMES):
                    if(i==0): 
                        dados[c].append(SUBMERCADO)
                    else: 
                        dados[c].append(dados_linha[i-1])
            if self.IDENTIFIER in linha:
                le = 1



        self.data = self._monta_df(dados)  