#from isddp.sddp.modelos.blocos.versaomodelo import VersaoModelo

from isddp.sddp.modelos.tabelaSDDP import BlocoTabelaSDDP
from isddp.sddp.modelos.tabelaSDDP import BlocoTabelaCadastro
from isddp.sddp.modelos.tabelaSDDP import BlocoTabelaPersonalizada
from isddp.sddp.modelos.arquivoscsv.arquivocsv import ArquivoCSV
from typing import Optional
import pandas as pd  # type: ignore

class PatamarPU(ArquivoCSV):
    """
    Arquivo com os cortes da evaporação linear do NEWAVE.
    """
    BLOCKS = [BlocoTabelaSDDP]
    @property
    def tabela(self) -> Optional[pd.DataFrame]:
        b = self.data.get_blocks_of_type(BlocoTabelaSDDP)
        if isinstance(b, BlocoTabelaSDDP):
            return b.data
        return None

class PatamarHorario(ArquivoCSV):
    """
    Arquivo com os cortes da evaporação linear do NEWAVE.
    """
    BLOCKS = [BlocoTabelaSDDP]
    @property
    def tabela(self) -> Optional[pd.DataFrame]:
        b = self.data.get_blocks_of_type(BlocoTabelaSDDP)
        if isinstance(b, BlocoTabelaSDDP):
            return b.data
        return None

class GeracaoTermicaPorUsina(ArquivoCSV):
    """
    Arquivo com os cortes da evaporação linear do NEWAVE.
    """
    BLOCKS = [BlocoTabelaSDDP]
    @property
    def tabela(self) -> Optional[pd.DataFrame]:
        b = self.data.get_blocks_of_type(BlocoTabelaSDDP)
        if isinstance(b, BlocoTabelaSDDP):
            return b.data
        return None

class GeracaoHidreletricaPorUsina(ArquivoCSV):
    """
    Arquivo com os cortes da evaporação linear do NEWAVE.
    """
    BLOCKS = [BlocoTabelaSDDP]
    @property
    def tabela(self) -> Optional[pd.DataFrame]:
        b = self.data.get_blocks_of_type(BlocoTabelaSDDP)
        if isinstance(b, BlocoTabelaSDDP):
            return b.data
        return None

class IntercambioSDDP(ArquivoCSV):
    """
    Arquivo com os cortes da evaporação linear do NEWAVE.
    """
    BLOCKS = [BlocoTabelaSDDP]
    @property
    def tabela(self) -> Optional[pd.DataFrame]:
        b = self.data.get_blocks_of_type(BlocoTabelaSDDP)
        if isinstance(b, BlocoTabelaSDDP):
            return b.data
        return None
    

class PequenaUsina(ArquivoCSV):
    """
    Arquivo com os cortes da evaporação linear do NEWAVE.
    """
    BLOCKS = [BlocoTabelaSDDP]
    @property
    def tabela(self) -> Optional[pd.DataFrame]:
        b = self.data.get_blocks_of_type(BlocoTabelaSDDP)
        if isinstance(b, BlocoTabelaSDDP):
            return b.data
        return None


class EARMSDDP(ArquivoCSV):
    """
    Arquivo earm65.csv
    """
    BLOCKS = [BlocoTabelaSDDP]
    @property
    def tabela(self) -> Optional[pd.DataFrame]:
        b = self.data.get_blocks_of_type(BlocoTabelaSDDP)
        if isinstance(b, BlocoTabelaSDDP):
            return b.data
        return None
    
class CMOSDDP(ArquivoCSV):
    """
    Arquivo cmgdem.csv
    """
    BLOCKS = [BlocoTabelaSDDP]
    @property
    def tabela(self) -> Optional[pd.DataFrame]:
        b = self.data.get_blocks_of_type(BlocoTabelaSDDP)
        if isinstance(b, BlocoTabelaSDDP):
            return b.data
        return None

class ENERVERSDDP(ArquivoCSV):
    """
    Arquivo enerver.csv
    """
    BLOCKS = [BlocoTabelaSDDP]
    @property
    def tabela(self) -> Optional[pd.DataFrame]:
        b = self.data.get_blocks_of_type(BlocoTabelaSDDP)
        if isinstance(b, BlocoTabelaSDDP):
            return b.data
        return None
    
class ENAFLUSDDP(ArquivoCSV):
    """
    Arquivo enaflu.csv
    """
    BLOCKS = [BlocoTabelaSDDP]
    @property
    def tabela(self) -> Optional[pd.DataFrame]:
        b = self.data.get_blocks_of_type(BlocoTabelaSDDP)
        if isinstance(b, BlocoTabelaSDDP):
            return b.data
        return None

class EcoHidreletrica(ArquivoCSV):
    """
    Arquivo de eco do cadastro das hidrelétrica athidr.csv
    """
    BLOCKS = [BlocoTabelaCadastro]
    @property
    def tabela(self) -> Optional[pd.DataFrame]:
        b = self.data.get_blocks_of_type(BlocoTabelaCadastro)
        if isinstance(b, BlocoTabelaCadastro):
            return b.data
        return None


class EcoTermica(ArquivoCSV):
    """
    Arquivo de eco do cadastro das hidrelétrica atterm.csv
    """
    BLOCKS = [BlocoTabelaCadastro]
    @property
    def tabela(self) -> Optional[pd.DataFrame]:
        b = self.data.get_blocks_of_type(BlocoTabelaCadastro)
        if isinstance(b, BlocoTabelaCadastro):
            return b.data
        return None


class LeituraPersonalizadaSDDP(ArquivoCSV):
    """
    Arquivo com os cortes da evaporação linear do NEWAVE.
    """
    BLOCKS = [BlocoTabelaPersonalizada]
    @property
    def tabela(self) -> Optional[pd.DataFrame]:
        b = self.data.get_blocks_of_type(BlocoTabelaPersonalizada)
        if isinstance(b, BlocoTabelaPersonalizada):
            return b.data
        return None