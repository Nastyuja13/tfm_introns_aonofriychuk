# dash for 1 genome

import config
import random
import pandas as pd
import sqlite3
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import s4x2_genome_stat_funcs as gs


app = Dash(__name__)

db = sqlite3.connect(config.GENERAL_DB_DIR / 'GenomesDb.sql')

#df = pd.read_sql_query("SELECT stats.*, species.species FROM stats LEFT JOIN species ON stats.gff_name_id == species.gff_name", db)
#print(df)
#species = [{"label": row[-1], "value": str(row[0])+'.sql'} for row in df.itertuples(index=False, name="species")]
#print(species)

df = pd.read_sql_query("SELECT gff_name, species FROM species WHERE species_type LIKE 'metazoa'", db)
species = [{"label": row[1], "value": str(row[0])+'.sql'} for row in df.itertuples(index=False, name="species")]

print(species[0])

app.layout = html.Div([ 
    html.H1("Analysis of one genome", style={'text-align': 'center'}),

    html.Div(id='output_container', children=[], style={'text-align': 'center'}),

    html.Br(),

    html.Div(id='dropdown_container', children = [
        dcc.Dropdown(id='slct_genome', options=species, multi=False,
            value='Caenorhabditis_elegans.WBcel235.51.sql', style={'width': "40%"})],
        style={'align': 'center'}
        ),

    html.Br(),

    html.Div(id='master_container', children = [
        html.Div(id='stats_container', style = {'width': "50%", 'float': "left"}),
        html.Div(id='histo_container', style = {'width': "50%", 'float': "right"}),
        html.Div(id='graph_container', children = [

            dcc.RadioItems(id='slct_introns',
                options=[
                    {'label': 'All Intron Sizes', 'value': 'ais'},
                    {'label': 'First Intron Sizes', 'value': 'fis'},
                    {'label': 'Total intron Sizes', 'value': 'tis'}
                ],
                value='ais',
                style={'align': 'center'},
                labelStyle = {'display': 'inline-block'}
            ),

            html.Div(id='distrib_container', children = [

                dcc.Graph(id='distrib_graph', figure={})

                ]),
            html.Div(id='boxplot_container', children = [

                dcc.Graph(id='boxplot_graph', figure={})

                ])
        ])   
    ], style = {'width': "100%"})
    ])

db.close()

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='distrib_graph', component_property='figure'),
     Output(component_id='boxplot_graph', component_property='figure')],
    [Input(component_id='slct_genome', component_property='value'),
     Input(component_id='slct_introns', component_property='value')]
)
def update_graph(sql_slctd, introns_slctd):
    print(sql_slctd)
    print(introns_slctd)

    species_slctd = sql_slctd.split('.')[0]

    if species_slctd[0] == '_':
            species_slctd = species_slctd[1:]

    species_slctd = species_slctd.split('_')[0] + ' ' + species_slctd.split('_')[1]
    species_slctd = species_slctd[0].upper() + species_slctd[1:]

    container = "The species chosen by user was: {}".format(species_slctd),

    db_connect = sqlite3.connect(config.NEW_DB_DIR / sql_slctd)
    cur = db_connect.cursor()
    cur.execute('SELECT gene_id, start, end FROM genes WHERE biotype LIKE "protein_coding"')

    genes_lens = {gene[0]: {'start': gene[1], 'end': gene[2]} for gene in cur.fetchall()}
    genes = genes_lens.keys()

    all_introns = []
    all_tot_introns = []
    all_first_introns = []

    data = {}

    for gene in genes:

        cur.execute('SELECT trans_id FROM transcripts WHERE gene_id = ?', (gene,))
        transcripts = [trans[0] for trans in cur.fetchall()]

        transcript_id = random.choice(transcripts)

        cur.execute('SELECT exon_id, start, end, strand FROM exons WHERE transcript_id = ?', (transcript_id,))
        exons = {exon[0]: {'start': exon[1], 'end': exon[2], 'strand': exon[3]} for exon in cur.fetchall()}

        ex_len = gs.exon_len(exons)
        tot_ex_len = gs.total_exon_len(ex_len)
        if len(ex_len) > 1:
            int_len = gs.intron_len(exons)
            tot_int_len = gs.total_intron_len(gs.intron_len(exons))

            all_introns = all_introns + int_len
            all_tot_introns.append(tot_int_len)
            all_first_introns.append(int_len[0])
        else:
            pass

    all_first_introns = sorted(all_first_introns)

    db_connect.close()

    if introns_slctd == 'ais':
        a = all_introns
        b = 'All_introns_len'
    elif introns_slctd == 'fis':
        a = all_first_introns
        b = 'First_introns_len'
    elif introns_slctd == 'tis':
        a = all_tot_introns
        b = 'Total_introns_len'

    data[b] = a
    data['species'] = [species_slctd for element in range(0, len(a))]

    df1 = pd.DataFrame(data=data)

    distrib_graph = px.histogram(df1, x=b)
    boxplot_graph = px.box(df1, x=b)

    return container, distrib_graph, boxplot_graph


if __name__ == "__main__":

    app.run_server(debug=True)