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


class BlocoConvergencia(TabelaCSV):
    """
    Bloco com as informações dos cortes da evaporação linear.
    """
    BEGIN_PATTERN = ""
    IDENTIFIER = "Iter,        Zinf,        Zsup,"
    END_PATTERN = ""

    IDENTIFICADOR_CPUTIME_POLITICA_OPERATIVA = "Cputime Politica"
    IDENTIFICADOR_CPUTIME_SIMULACAO_OPERATIVA = " Cputime Simulacao"
    IDENTIFICADOR_CUSTO_MEDIO = "Custo Medio"
    IDENTIFICADOR_TOTAL_CPU_TIME = "Total CPU time"
    Cputime_Politica_Operativa = 0
    Cputime_Simulacao_Operativa = 0
    Custo_Medio = 0
    Total_CPU_Time = 0

    LINE_MODEL = Line(
        [
            FloatField(size=80, decimal_digits=2),
            FloatField(size=80, decimal_digits=2),
            FloatField(size=80, decimal_digits=2),
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
        "iter",
        "zinf",
        "zsup",
        "Gap",
        "Tol",
        "CPUBck",
        "CPUFwr",
        "NCutO",
        "NCutF",
    ]
    
    def pegaSegundoElemento(self, linha):
         return linha.strip().split(',')[1]

    def read(self, file: IO, *args, **kwargs):        
        le = 0
        dados: Dict[str, List] = {c: [] for c in self.__class__.COLUMN_NAMES} 

        for linha in file.readlines():
            #print(linha)

            if(self.IDENTIFICADOR_CPUTIME_POLITICA_OPERATIVA in linha):
                 self.Cputime_Politica_Operativa = float(self.pegaSegundoElemento(linha))
            if(self.IDENTIFICADOR_CPUTIME_SIMULACAO_OPERATIVA in linha):
                 self.Cputime_Simulacao_Operativa = float(self.pegaSegundoElemento(linha))
            if(self.IDENTIFICADOR_CUSTO_MEDIO in linha):
                 self.Custo_Medio = float(self.pegaSegundoElemento(linha))
            if(self.IDENTIFICADOR_TOTAL_CPU_TIME in linha):
                 self.Total_CPU_Time = float(self.pegaSegundoElemento(linha).strip(' s'))

            if len(linha) < 3:
                le = 0 
            if le == 1:
                dados_linha = self.__class__.LINE_MODEL.read(linha)
                for i, c in enumerate(self.__class__.COLUMN_NAMES):
                        dados[c].append(dados_linha[i])
            if self.IDENTIFIER in linha:
                le = 1
        self.data = pd.DataFrame(dados)  