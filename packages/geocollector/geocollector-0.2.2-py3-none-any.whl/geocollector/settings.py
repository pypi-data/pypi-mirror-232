from dataclasses import dataclass
import pandas as pd


@dataclass
class NCBIsettings:
    """
    This class is meant to hold settings that exist throughout the lifetime of the program
    """
    API_KEY: str
    INPUT_FILE: str
    DATA_FRAME: pd.DataFrame = None
    
    def __post_init__(self) -> None:
        self._create_df()
    
    def _create_df(self) -> None:
        self.DATA_FRAME = pd.read_csv(self.INPUT_FILE, comment="#")
