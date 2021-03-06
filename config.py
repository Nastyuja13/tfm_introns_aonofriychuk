
from pathlib import Path
import getpass

HOME_DIR = Path.home()
USER = getpass.getuser()

if USER == 'jose':
    BASE_DIR = HOME_DIR / 'magnet' / 'analyses' / 'intron_size'
    SOURCE_DATA_DIR = BASE_DIR / 'source_data'

elif USER == 'anastasiya':
    BASE_DIR = HOME_DIR / 'Desktop' / 'TFM' / 'tfm_intron_scripts'
    SOURCE_DATA_DIR = HOME_DIR / 'Desktop' / 'TFM' / 'tfm_intron_data' / 'ensembl_files'
    SOURCE_DATA_DIR2 = HOME_DIR / 'Desktop' / 'TFM' / 'tfm_intron_data'
    NEW_DOWNLOAD_DIR = SOURCE_DATA_DIR2 / 'gff3'
    NEW_DOWNLOAD_DIR.mkdir(exist_ok=True)
    NEW_DB_DIR = SOURCE_DATA_DIR2 / 'speciesDB'
    NEW_DB_DIR.mkdir(exist_ok=True)
    GENERAL_DB_DIR = SOURCE_DATA_DIR2 / 'genomesDB'
    GENERAL_DB_DIR.mkdir(exist_ok=True)
    ERRORLOG_DIR = HOME_DIR / 'Desktop' / 'TFM' / 'tfm_errorlog'
    ERRORLOG_DIR.mkdir(exist_ok=True)

elif USER == 'intron_docker':
    #HOME_DIR = Path('TFM_aonofriychuk') 
    BASE_DIR = Path('tfm_scripts')
    SOURCE_DATA_DIR2 = Path('tfm_data')
    SOURCE_DATA_DIR = SOURCE_DATA_DIR2 / 'ensembl_files'
    NEW_DOWNLOAD_DIR = SOURCE_DATA_DIR2 / 'gff3'
    NEW_DB_DIR = SOURCE_DATA_DIR2 / 'speciesDB'
    GENERAL_DB_DIR = SOURCE_DATA_DIR2 / 'genomesDB'
    ERRORLOG_DIR = Path('tfm_errorlog')


ENSEMBL_PLANTS_HTML = SOURCE_DATA_DIR / 'ensembl_plants_genomes_table.html'
ENSEMBL_HTML = SOURCE_DATA_DIR / 'ensembl_genomes_table.html'
ENSEMBL_METAZOA_HTML = SOURCE_DATA_DIR / 'ensembl_metazoa_genomes_table.html'
ENSEMBL_FUNGI_HTML = SOURCE_DATA_DIR / 'ensembl_fungi_genomes_table.html'
ENSEMBL_PROTISTS_HTML = SOURCE_DATA_DIR / 'ensembl_protists_genomes_table.html'

#CACHE_DIR = BASE_DIR / 'cache'
#CACHE_DIR.mkdir(exist_ok=True)
#GFF_CACHE_DIR = CACHE_DIR / 'gff'
#GFF_CACHE_DIR.mkdir(exist_ok=True)
#DBS_CACHE_DIR = CACHE_DIR / 'dbs'
#DBS_CACHE_DIR.mkdir(exist_ok=True)

#GENES_TABLE = 'genes'

#MALFORMED_GFF = ['Hordeum_vulgare.IBSC_v2.51.gff3.gz']