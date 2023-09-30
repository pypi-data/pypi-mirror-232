#from isddp.sddp.modelos.blocos.versaomodelo import VersaoModelo
from isddp.sddp.modelos.convergenciaSDDP import BlocoConvergencia

from isddp.sddp.modelos.arquivoscsv.arquivocsv import ArquivoCSV
from typing import Optional
import pandas as pd  # type: ignore


class Convergencia(ArquivoCSV):
    """
    Arquivo com os cortes da evaporação linear do NEWAVE.
    """

    BLOCKS = [BlocoConvergencia]



    @property
    def tabelaConvergencia(self) -> Optional[pd.DataFrame]:
        b = self.data.get_blocks_of_type(BlocoConvergencia)
        if isinstance(b, BlocoConvergencia):
            return b.data
        return None
    
    @property
    def valorCputimePoliticaOperativa(self) -> Optional[pd.DataFrame]:
        b = self.data.get_blocks_of_type(BlocoConvergencia)
        if isinstance(b, BlocoConvergencia):
            return b.Cputime_Politica_Operativa
        return None

    @property
    def valorCputimeSimulacaoOperativa(self) -> Optional[pd.DataFrame]:
        b = self.data.get_blocks_of_type(BlocoConvergencia)
        if isinstance(b, BlocoConvergencia):
            return b.Cputime_Simulacao_Operativa
        return None
    
    @property
    def valorCustoMedio(self) -> Optional[pd.DataFrame]:
        b = self.data.get_blocks_of_type(BlocoConvergencia)
        if isinstance(b, BlocoConvergencia):
            return b.Custo_Medio
        return None
    
    @property
    def valorTotalCPUTime(self) -> Optional[pd.DataFrame]:
        b = self.data.get_blocks_of_type(BlocoConvergencia)
        if isinstance(b, BlocoConvergencia):
            return b.Total_CPU_Time
        return None
