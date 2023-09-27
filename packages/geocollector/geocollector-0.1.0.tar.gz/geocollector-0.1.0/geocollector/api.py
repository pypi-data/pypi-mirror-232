import re
import aiohttp
import asyncio
import pandas as pd
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from logging import Logger
from records import Record
from typing import Type
from types import TracebackType
import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
import time


class NCBI:
    eutils_session: aiohttp.ClientSession = None
    sra_session: aiohttp.ClientSession = None
    eutils_search_path: str = f"/entrez/eutils/esearch.fcgi?db=gds&term=[accession]&idtype=acc"
    eutils_fetch_path: str = f"/entrez/eutils/efetch.fcgi?db=gds&id=[ids]"
    
    def __init__(self, input_df: pd.DataFrame, logger: Logger, key: str = ""):
        self._ncbi_key: str = key
        self.input_df: pd.DataFrame = input_df
        self.logger: Logger = logger
        self.request_per_second: int = 3
        self.delay: float = 0.37
        self.previous_time = 0
        
        if self._ncbi_key != "":
            self.logger.info("API key provided - settings requests to 10 per second")
            self.eutils_search_path += f"&api_key={self._ncbi_key}"
            self.eutils_fetch_path += f"&7api_key={self._ncbi_key}"
            self.request_per_second = 10
            self.delay = 0.12
        else:
            self.logger.warning(
                "No API key provided - limiting to requests to 3 per second. "
                "Create one at https://account.ncbi.nlm.nih.gov/settings/"
            )
        
        # Add columns to input dataframe then set column order
        self.main_columns: list[str] = ["GSE", "GSM", "SRR", "Rename", "Strand", "Prep Method"]
        self.internal_columns: list[str] = ["search_id", "cell_type", "srx"]
        self.input_df = pd.concat([
            self.input_df,
            pd.DataFrame(columns=self.main_columns + self.internal_columns)
        ])
        self.input_df = self.input_df[self.main_columns + self.internal_columns]
        
        self.__init_sessions__()
    
    def __init_sessions__(self) -> None:
        if NCBI.eutils_session is None:
            NCBI.eutils_session = aiohttp.ClientSession("https://eutils.ncbi.nlm.nih.gov")
        if NCBI.sra_session is None:
            NCBI.sra_session = aiohttp.ClientSession("https://www.ncbi.nlm.nih.gov")
        
        self.eutils_session: aiohttp.ClientSession = NCBI.eutils_session
        self.sra_session: aiohttp.ClientSession = NCBI.sra_session
    
    def create_csv(self) -> None:
        write_df: pd.DataFrame = self.input_df[self.main_columns].copy()
        write_df.to_csv("output_data.csv", sep=",", index=False)
    
    async def __aenter__(self) -> "NCBI":
        return self
    
    async def __aexit__(self, exc_type: Type[BaseException], exc_val: BaseException, exc_tb: TracebackType) -> None:
        await self.eutils_session.close()
        await self.sra_session.close()
    
    async def get(
        self,
        session: aiohttp.ClientSession,
        path: str,
    ) -> aiohttp.ClientResponse:
        self.logger.debug(f"Making request to path: {path}")
        
        current = time.time()
        wait = self.previous_time + self.delay - current
        if wait > 0:
            self.logger.debug(f"Sleeping for {wait:0.2f} seconds")
            await asyncio.sleep(wait)
            self.previous_time = current + wait
        else:
            self.previous_time = current
        self.logger.debug(f"Setting previous time to {self.previous_time}")
        
        response: aiohttp.ClientResponse = await session.get(path)
        while not response.ok:
            if response.status == 429:
                await asyncio.sleep(5)
                response = await session.get(path)
            else:
                raise aiohttp.ClientResponseError(
                    status=response.status,
                    message=f"Request failed, status code: {response.status}",
                    history=response.history,
                    request_info=response.request_info,
                )
        return response
    
    async def search(self) -> None:
        """
        This function will perform a search on the NCBI API for each GSE accession number in the input file.
        It will return a list of IDs, which will be used to fetch the records.
        :return:
        """
        ids = []
        with logging_redirect_tqdm([self.logger]):
            for gsm in tqdm.tqdm(self.input_df["GSM"], leave=False):
                # for gsm in self.input_df["GSM"]:
                self.logger.debug(f"Searching for {gsm}")
                response = await self.get(
                    self.eutils_session,
                    self.eutils_search_path.replace("[accession]", gsm),
                )
                xml_root: Element = ElementTree.fromstring(await response.text())
                ids.append([element.text for element in xml_root.findall('.//Id')])
        
        self.input_df["search_id"] = ids
        self.input_df = self.input_df.explode("search_id", ignore_index=True)
        self.logger.info(f"Search complete - {len(ids)} records found")
    
    async def update_data(self) -> None:
        """
        This function will perform a "fetch" for each of the IDs returned by the search function
        It will provide the `parse_fetch` function with the response, which will be used to parse the plain text into structured data
        :return:
        """
        with logging_redirect_tqdm([self.logger]):
            for gsm in tqdm.tqdm(self.input_df["GSM"].unique(), leave=False):
                ids_list = self.input_df[self.input_df["GSM"] == gsm]["search_id"].tolist()
                cell_type = self.input_df[self.input_df["GSM"] == gsm]["cell_type"].tolist()[0]
                response = await self.get(
                    self.eutils_session,
                    self.eutils_fetch_path.replace("[ids]", ",".join(ids_list))
                )
                
                record = self.parse_fetch(await response.text(), gsm, cell_type)
                self.input_df.loc[self.input_df["search_id"] == record.SEARCH_ID, "GSE"] = record.GSE
                self.input_df.loc[self.input_df["search_id"] == record.SEARCH_ID, "srx"] = record.SRX_ACCESSION
                self.input_df.loc[self.input_df["search_id"] == record.SEARCH_ID, "Rename"] = record.TITLE
        
        self.input_df = self.input_df.dropna(subset=["GSE"])
        await self.srx_to_srr()
        await self.get_prep_method()
        
        self.logger.info(f"Fetch complete - {len(self.input_df)} records fetched")
    
    def parse_fetch(self, response: str, gsm: str, cell_type: str) -> Record:
        """
        This function will parse the plain text provided by the NCBI api into structured data
        :param response: The plain text response returned from NCBI
        :param gsm: The GSM that was used to fetch the record
        :param cell_type: The GSM's cell type
        :return: A Record object
        """
        records = re.split(r"\n(?=\d+\.)", response.strip())
        
        for record in records:
            gse_accession_match = re.search(r'Series\s+Accession:\s+(.*?)\s+', record)
            platform_id_match = re.search(r"Platform\s+Accession:\s+(.*?)\s+", record)
            gsm_accession_match = re.search(r'Sample\s+Accession:\s+(.*?)\s+', record)
            
            if gse_accession_match:
                gse_accession = gse_accession_match.group(1)
                self.logger.debug(f"Found GSE Accession: {gse_accession}")
            elif platform_id_match:
                platform_id = platform_id_match.group(1)
                
                platform_name_match: re.Match[str] | None = re.match(r'^\d+\.\s+(.*?)\n', record)
                platform_name: str = platform_name_match.group(1) if platform_name_match else ""
                self.logger.debug(f"Found Platform {platform_name} with ID {platform_id}")
            elif gsm_accession_match and gsm_accession_match.group(1) == gsm:
                gsm_accession = gsm_accession_match.group(1)
                title_match = re.match(r'\d+\.\s+(.*?)\n', record)
                title = title_match.group(1) if title_match else ""
                
                organism_match = re.search(r'Organism:\s+(.*?)\n', record)
                organism = organism_match.group(1) if organism_match else ""
                
                source_name_match = re.search(r'Source name:\s+(.*?)\n', record)
                source_name = source_name_match.group(1) if source_name_match else ""
                
                platform_match = re.search(r'Platform:\s+(.*?)\s+', record)
                platform_id = platform_match.group(1) if platform_match else ""
                
                srx_link_match = re.search(r'SRA Run Selector:\s+(.*?)\n', record)
                srx_link = srx_link_match.group(1) if srx_link_match else ""
                
                search_id_match = re.search(r"\s+ID:\s+(\d+)", record)
                search_id = search_id_match.group(1) if search_id_match else ""
                
                self.logger.debug(f"Found GSM accession {gsm_accession} with SRX link {srx_link}")
                
                new_record = Record(
                    TITLE=title,
                    GSE=gse_accession,
                    ORGANISM=organism,
                    SOURCE=source_name,
                    PLATFORM_ID=platform_id,
                    PLATFORM_NAME=platform_name,
                    CELL_TYPE=cell_type,
                    SRX_LINK=srx_link,
                    GSM=gsm_accession,
                    SEARCH_ID=search_id
                )
        
        return new_record
    
    async def srx_to_srr(self) -> None:
        """
        This function will parse the SRX link from the NCBI API and return the SRR value
        :return:
        """
        for srx in tqdm.tqdm(self.input_df["srx"], leave=False):
            response: aiohttp.ClientResponse = await self.get(self.sra_session, f"/sra/?term={srx}")
            text: str = await response.text()
            
            srr_match: re.Match[str] | None = re.search(r"trace\.ncbi\.nlm\.nih\.gov/Traces\?run=(SRR\d+)", text)
            srr: str = srr_match.group(1) if srr_match else ""
            
            # Search for <div>:Layout: <span>PAIRED</span></div>
            strand_match: re.Match[str] | None = re.search(r"<div>Layout: <span>(.*?)</span></div>", text)
            strand: str = strand_match.group(1) if strand_match else ""
            
            self.input_df.loc[self.input_df["srx"] == srx, "SRR"] = srr
            self.input_df.loc[self.input_df["srx"] == srx, "Strand"] = strand
    
    async def get_prep_method(self) -> None:
        for gsm in tqdm.tqdm(self.input_df["GSM"], leave=False):
            response = await self.get(self.sra_session, f"/geo/query/acc.cgi?acc={gsm}")
            text = await response.text()
            
            # Search for "total RNA" in response
            prep_method = ""
            if "total rna" in text.lower():
                prep_method = "total"
            elif "polya rna" in text.lower():
                prep_method = "mrna"
            
            self.input_df.loc[self.input_df["GSM"] == gsm, "Prep Method"] = prep_method
    
    def set_rename_column(self) -> None:
        study_number = 0
        for gse in self.input_df["GSE"].unique():
            cell_type = self.input_df[self.input_df["GSE"] == gse]["cell_type"].tolist()[0]
            study_number += 1
            run_number = 0
            for gsm in self.input_df[self.input_df["GSE"] == gse]["GSM"].unique():
                run_number += 1
                replicates = self.input_df[(self.input_df["GSE"] == gse) & (self.input_df["GSM"] == gsm)][
                    "SRR"].tolist()
                replicate_number = 0
                for replicate in replicates:
                    replicate_number += 1
                    name = f"{cell_type}_S{study_number}R{run_number}"
                    if len(replicates) > 1:
                        name += f"r{replicate_number}"
                    self.input_df.loc[self.input_df["SRR"] == replicate, "Rename"] = name
