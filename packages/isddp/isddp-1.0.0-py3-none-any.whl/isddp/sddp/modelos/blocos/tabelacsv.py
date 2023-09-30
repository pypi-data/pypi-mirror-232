from cfinterface.components.block import Block
from cfinterface.components.line import Line
from cfinterface.components.floatfield import FloatField
from cfinterface.components.integerfield import IntegerField

from copy import deepcopy
from typing import IO, List, Dict
import pandas as pd  # type: ignore


class TabelaCSV(Block):
    """
    Bloco para ler uma tabela com separadores CSV fornecidos
    a partir de um modelo de linha, para arquivos de saída do NEWAVE.
    """
    IDENTIFIER = "Estg,Ser.,Bloc"
    BEGIN_PATTERN = ""
    #LINE_MODEL = Line([])
    LINE_MODEL = Line(
        [
            IntegerField(size=80),
            IntegerField(size=80),
            IntegerField(size=80),
        ],
        delimiter=",",
    )
    #COLUMN_NAMES: List[str] = []
    COLUMN_NAMES = [
        "Estagio",
        "Serie",
        "Bloco",
    ]
    END_PATTERN = ""

    #def _monta_df(self, dados: dict) -> pd.DataFrame:
    #    return 

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, TabelaCSV):
            return False
        else:
            if not all(
                [type(self.data) is pd.DataFrame, type(o.data) is pd.DataFrame]
            ):
                return False
            else:
                return self.data.equals(o.data)

    def read(self, file: IO, *args, **kwargs):        
        le = 0
        self.line_model = deepcopy(self.__class__.LINE_MODEL)
        self.column_names = deepcopy(self.__class__.COLUMN_NAMES)
        for linha in file.readlines():

            if(self.IDENTIFIER in linha):
                 
                 for i, elemento in enumerate(linha.strip().split(',')):
                      if(i>=3):
                           self.line_model.fields.append(FloatField(size=80, decimal_digits=2))
                           #self.column_names.append(str(elemento.replace(" ", "")))
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