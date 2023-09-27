import sys
import asyncio

from api import NCBI
from logger import get_logger
from cli import parse_args
from settings import NCBIsettings


async def main() -> None:
    args = parse_args(sys.argv[1:])
    settings = NCBIsettings(API_KEY=args.api_key, INPUT_FILE=args.input_file)
    logger = get_logger(args.verbosity)
    
    async with NCBI(key=settings.API_KEY, input_df=settings.DATA_FRAME, logger=logger) as api:
        await api.search()
        await api.update_data()
        api.set_rename_column()
        api.create_csv()


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
    asyncio.run(main())
