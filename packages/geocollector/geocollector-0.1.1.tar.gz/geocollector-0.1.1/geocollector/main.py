import sys
import asyncio

from geocollector.api import NCBI
from geocollector.logger import get_logger
from geocollector.cli import parse_args
from geocollector.settings import NCBIsettings


async def _start():
    args = parse_args(sys.argv[1:])
    settings = NCBIsettings(API_KEY=args.api_key, INPUT_FILE=args.input_file)
    logger = get_logger(args.verbosity)
    
    async with NCBI(key=settings.API_KEY, input_df=settings.DATA_FRAME, logger=logger) as api:
        await api.search()
        await api.update_data()
        api.set_rename_column()
        api.create_csv()


def main() -> None:
    asyncio.run(_start())


if __name__ == '__main__':
    """
    INPUT -> CLI -> SETTINGS -> SEARCH API -> RECORDS -> FETCH RECORDS -> OUTPUT
    
    GSE
    GSM
    SRR
    Rename
    Strand
    Prep Method
    Platform Code
    Platform Name
    Source
    Cell Characteristics
    Replicate Name
    Strategy
    Publication
    Extra Notes
    """
    main()
