#from isddp.sddp.modelos.blocos.versaomodelo import VersaoModelo
from isddp.sddp.modelos.geracoes import GeracaoTotal

from isddp.sddp.modelos.arquivoscsv.arquivocsv import ArquivoCSV
from typing import Optional
import pandas as pd  # type: ignore


class Geracoes(ArquivoCSV):
    """
    Arquivo com os cortes da evaporação linear do NEWAVE.
    """

    BLOCKS = [GeracaoTotal]



    @property
    def tabela(self) -> Optional[pd.DataFrame]:
        b = self.data.get_blocks_of_type(GeracaoTotal)
        if isinstance(b, GeracaoTotal):
            return b.data
        return None
    
