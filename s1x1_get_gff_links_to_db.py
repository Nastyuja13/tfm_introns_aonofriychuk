import config

import requests
from bs4 import BeautifulSoup

import s1x2_genomes_db_creation as genome_db


def get_full_genome_gff3_url(ensembl_response_html, url, spc):

    # print(f'{url=}')
    ensembl_release = url.split('/')[-3]
    if 'release' not in ensembl_release:
        ensembl_release = url.split('/')[-4]
    if '_collection' in url:
        ensembl_release = url.split('/')[-5]

    ensembl_release = ensembl_release.split('-')[-1]

    soup = BeautifulSoup(ensembl_response_html, 'html.parser')
    links = soup.find_all('a')
    full_genome_gff3_url = ''

    expected_extension = f'.{ensembl_release}.gff3.gz'

    if len(links) == 0:
        err = f'Error obtaining the {spc} full GFF link'
        print(err)
        with open(config.ERRORLOG_DIR / 'ErrorLogEnsemblTables.txt','a') as errorlog:
            errorlog.write(err + '\n')
        print(RuntimeError('No links available'))
    else:
        full_genome_gff3_url_name = [link.attrs['href'] for link in links if expected_extension in link.attrs['href']][0]
        full_genome_gff3_url = f'{url}/{full_genome_gff3_url_name}'

        return full_genome_gff3_url, ensembl_release


def _parse_ensembl_table(html, ensembl_site):

	# Open Ensembl html file, previously downloaded, with the species table
    soup = BeautifulSoup(html, 'html.parser')
    # Obtain all tables in the html
    tables = soup.find_all('tbody')

    # Create directory for the Ensembl species type we're downloading
    ##gff_cache_dir = config.GFF_CACHE_DIR / ensembl_site
    ##gff_cache_dir.mkdir(exist_ok=True)
    ##dbs_cache_dir = config.DBS_CACHE_DIR / ensembl_site
    ##dbs_cache_dir.mkdir(exist_ok=True)

    # List that will contain all species general info and url to gff file
    speciess = []

    # For species (table_row) in species table (tables[1])
    for table_row in tables[1].find_all('tr'):

        # Find all td elements
        tds = table_row.find_all('td')

        # Get first info. species name and their common name
        ## If the tds[1] has more than 1 element (species and common name)
        if len(tds[1].contents) > 1:
            species_name = tds[1].contents[-1].text
            common_name = tds[1].contents[0].text
        ## If the tds[1] has only 1 element (only species name)
        else:
            species_name = tds[1].text
            common_name = ''

        print(species_name)

        # Get the url to the repository with gff files of the species
        ## If cannot download the html, add error to errorlog file
        gff_url = tds[9].find_all('a')[-1].attrs['href']

        try:
            ensembl_response_html = requests.get(gff_url).text
        except requests.exceptions.ConnectionError:
            err = f'Error downloading the {species_name} GFF repository: {url}'
            print(err)
            with open(config.ERRORLOG_DIR /'ErrorLogEnsemblTables.txt','a') as errorlog:
                errorlog.write(err + '\n')
            continue

        full_gff3_url, ensembl_release = get_full_genome_gff3_url(ensembl_response_html,
                                                                  gff_url, spc=species_name)

        if len(full_gff3_url) == 0:
            err = f'Error downloading the {species_name} GFF'
            print(err)
            with open(config.ERRORLOG_DIR /'ErrorLogEnsemblTables.txt','a') as errorlog:
                errorlog.write(err + '\n')
            continue

        #assembly_info_url = tds[1].find_all('a')[-1].attrs['href']
        #assembly_info_url += 'Info/Annotation/#assembly'

        #try:
            #golden_path_len = _get_assembly_golden_path_len(assembly_info_url, ensembl_release)
        #except RuntimeError:
            #golden_path_len = None

        #gff_path = get_and_store_web_file(full_gff3_url, ignore_date=True,
                                          #store_dir=gff_cache_dir)
        
        species = ' '.join(species_name.split()[:2]).replace('[', '').replace(']', '')

        #if '[' in species:
            #raise RuntimeError(f'{species}')

        #id_ = ensembl_site + '_' + gff_path.name.split('.gff')[0].replace('.', '_').lower()

        gff_file = full_gff3_url.split('/')[-1]

        species_info = {'name': species_name,
                        'species': species,
                        'common_name': common_name,
                        'species_type': ensembl_site,
                        'gff_link': full_gff3_url,
                        'gff_file': gff_file
                        #'gff_path': gff_path,
                        #'golden_path_len': golden_path_len,
                        #'id': id_
                        }

        speciess.append(species_info)

    return speciess


def get_ensembl_species_info(ensembl_sites=None):

    htmls = {'metazoa': config.ENSEMBL_METAZOA_HTML,
             'fungi': config.ENSEMBL_FUNGI_HTML,
             'protists': config.ENSEMBL_PROTISTS_HTML,
             'main': config.ENSEMBL_HTML,
             'plant': config.ENSEMBL_PLANTS_HTML
             }

    if ensembl_sites is None:
        ensembl_sites = list(htmls.keys())
    
    species_info = []

    for site in ensembl_sites:
        print(f'\n ### Now processing {site} ###')
        html = htmls[site].open('rt').read()
        new_species_info = _parse_ensembl_table(html, site)
        species_info = species_info + new_species_info
    
    return species_info

if __name__ == '__main__':

    speciess = get_ensembl_species_info()
    genome_db.species_info_to_db(speciess)