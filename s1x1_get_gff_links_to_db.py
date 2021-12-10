import config

import requests
from bs4 import BeautifulSoup

import s1x2_genomes_db_creation as genome_db
import s4x2_genome_stat_funcs as gs


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

        
        species = ' '.join(species_name.split()[:2]).replace('[', '').replace(']', '')

        gff_file = full_gff3_url.split('/')[-1]
        gff_name = gff_file[:-8]

        genome_length = gs.get_golden_path_len(gff_name, ensembl_site)

        species_info = {'name': species_name,
                        'species': species,
                        'common_name': common_name,
                        'species_type': ensembl_site,
                        'release': int(gff_file.split('.')[-3]),
                        'genome_length': genome_length,
                        'gff_name': gff_name,
                        'gff_file': gff_file,
                        'gff_link': full_gff3_url
                        }

        speciess.append(species_info)

    return speciess


def get_ensembl_species_info(ensembl_sites=None):

    htmls = {'main': config.ENSEMBL_HTML,
             'plant': config.ENSEMBL_PLANTS_HTML,
             'metazoa': config.ENSEMBL_METAZOA_HTML,
             'protists': config.ENSEMBL_PROTISTS_HTML,
             'fungi': config.ENSEMBL_FUNGI_HTML
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

def _remove_duplicates(speciess):

    filtered_spc = []

    existent_spc = []

    # Concrete subspecies to save
    subspc_to_keep = ['Duck', 'Mallard', 'Mexican tetra', 
                      'Dingo', 'Dog', 'Goat', 'Common carp', 'Mouse', 'Sheep', 'Pig']

    # Concrete species to exclude as they do not have introns (fungi and protists)
    # and 'Hordeum vulgare', a plant which has exons of the same gene in different strands

    spc_to_exclude = ['Hordeum vulgare', # plants
                      'Angomonas deanei', 'Leishmania infantum', 'Leptomonas pyrrhocoris', # protists
                      'Leptomonas seymouri', 'Perkinsela sp.', 'Phytomonas sp.', 'Strigomonas culicis', 
                      'Tritrichomonas foetus', 'Trypanosoma conorhini', 'Trypanosoma cruzi', 
                      'Trypanosoma rangeli', 'Trypanosoma theileri',
                      'Amphiamblys sp.', 'Anncaliia algerae', 'Enterocytozoon bieneusi', # fungi
                      'Enterocytozoon hepatopenaei', 'Enterospora canceri', 'Hepatospora eriocheir',
                      'Nematocida displodere', 'Nematocida sp.', 'Pseudoloma neurophilia', 
                      'Saccharomyces arboricola', 'Saccharomyces kudriavzevii', 'Spraguea lophii', 
                      'Trachipleistophora hominis', 'Vittaforma corneae']

    for species in speciess:

        if species['species'] in spc_to_exclude:
            pass
        elif species['species'] not in existent_spc:
            existent_spc.append(species['species'])
            filtered_spc.append(species)
        elif species['common_name'] in subspc_to_keep:
            filtered_spc.append(species)
        else:
            pass

    return filtered_spc


if __name__ == '__main__':

    speciess = get_ensembl_species_info()
    print(len(speciess))
    speciess = _remove_duplicates(speciess)
    print(len(speciess))
    genome_db.species_info_to_db(speciess)