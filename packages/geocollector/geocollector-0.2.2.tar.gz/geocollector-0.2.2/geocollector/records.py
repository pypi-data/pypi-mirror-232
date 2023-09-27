from dataclasses import dataclass


@dataclass
class Record:
    TITLE: str
    ORGANISM: str
    SOURCE: str
    PLATFORM_ID: str
    PLATFORM_NAME: str
    SRX_LINK: str
    CELL_TYPE: str
    GSE: str
    GSM: str
    SEARCH_ID: str
    SRX_ACCESSION: str = ""
    
    def __post_init__(self) -> None:
        self.ORGANISM = self.ORGANISM.lower()
        self.set_srx_accession()
    
    def set_srx_accession(self) -> None:
        self.SRX_ACCESSION = self.SRX_LINK.split("=")[-1]
