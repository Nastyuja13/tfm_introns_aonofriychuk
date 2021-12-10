# Dashboard for several genomes

import config
import pandas as pd
import sqlite3
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pli
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from dash import Dash, dcc, html, Input, Output


# Start Dash

app = Dash(__name__)

# DB to use

database = config.GENERAL_DB_DIR / 'GenomesDb.sql'

# Selector values

radio_genome_select = [{'label': 'Kingdom', 'value': 'kingdom'},
	{'label': 'Phylum', 'value': 'phylum'},
	{'label': 'Class', 'value': 'class_'},
	{'label': 'Order', 'value': 'order_'},
	{'label': 'Family', 'value': 'family'},
	{'label': 'Concrete species', 'value': 'concrete'},
	{'label': 'All', 'value': 'all'}
	]

slctd_comp_taxa = [{'label': 'By kingdom', 'value': 'kingdom'},
	{'label': 'By Phylum', 'value': 'phylum'},
	{'label': 'By class', 'value': 'class_'},
	{'label': 'By order', 'value': 'order_'},
	{'label': 'By family', 'value': 'family'}
	]

slctd_gene_type = [{'label': 'All genes', 'value': 'all_g'}, 
	{'label': 'Protein-coding genes', 'value': 'prot_g'}
	]

slctd_intron_type = [{'label': 'All introns', 'value': 'ai'}, 
	{'label': 'First introns', 'value': 'fi'}, 
	{'label': 'Total intron length', 'value': 'ti'}
	]


# Dash layout 

app.layout = html.Div([
	# Title
	html.H1("Intronic analysis across species", style={'text-align': 'center'}),
	# Selctors
	html.Div(id='data_selection', children = [
		## Genome selector
		html.Div(id='genomes_selection', children = [
			html.H3("Please, select genomes to compare:", style={'text-align': 'center'}), 
			html.Table(children = [
				html.Tbody([
					html.Tr(children = [
						html.Td(
							dcc.RadioItems(id='slctd_spc_radio', 
								options=radio_genome_select, 
								value='kingdom', 
								style={'display': 'flex', 'align-items': 'center', 
									'justify-content': 'center', 'width': "100%"},
								labelStyle = {'display': 'inline-block'})),
						html.Td(
							dcc.Dropdown(id='slctd_spc_drop', 
								options=[], 
								multi=True, 
								value=[], 
								style={}))])])])]), 
		## Coloring, gene & intron selectors
		html.Div(id='comparison_selectors', children = [
			html.Table(
				html.Tbody([
					html.Tr(
						[html.Td(
							html.H3("Please, select how to compare genomes:", 
								style={'text-align': 'center'})),
						html.Td(
							html.H3("Please, select which genes to consider:", 
								style={'text-align': 'center'})), 
						html.Td(
							html.H3("Please, select which introns to consider:",
								style={'text-align': 'center'}))]), 
					html.Tr([
						html.Td(dcc.RadioItems(id='slctd_comp_taxa', 
								options=slctd_comp_taxa,
								value='kingdom', 
								style={'display': 'flex', 'align-items': 'center', 
									'justify-content': 'center', 'width': "100%"},
								labelStyle = {'display': 'inline-block'})), 
						html.Td(dcc.RadioItems(id='slctd_gene_type', 
								options=slctd_gene_type, 
								value='all_g', 
								style={'display': 'flex', 'align-items': 'center', 
									'justify-content': 'center', 'width': "100%"},
								labelStyle = {'display': 'inline-block'})), 
						html.Td(dcc.RadioItems(id='slctd_intron_type', 
								options=slctd_intron_type, 
								value='ai', 
								style={'display': 'flex', 'align-items': 'center', 
									'justify-content': 'center', 'width': "100%"},
								labelStyle = {'display': 'inline-block'}))
						])
					]))])]),
	#html.Br(), 
	# Graphs
	html.Div(id='graph_display', children = [
		dcc.Tabs(id="graph_selection", value='genome_length', children=[
			dcc.Tab(label='Genome length vs intron length', value='genome_length'),
			dcc.Tab(label='PCA', value='pca'),
			dcc.Tab(label='Barchart of the number of genes', value='bar_num_genes'),
			dcc.Tab(label='Barchart of the average number of introns per gene', value='bar_num_introns'),
			dcc.Tab(label='Barchart of the average intron length', value='bar_avg_intron_len'),
			dcc.Tab(label='Intron length boxplot', value='boxplot'),
			dcc.Tab(label='Intron length distribution', value='distribution')
			]
			),
		html.Div(id='tabs-content-example-graph', children = [
			dcc.Graph(id='example_graph', figure={})
			]
			)
		]
		),
	# stores the intermediate value
    dcc.Store(id='genomes_to_represent', data=[])
	]
	)


# Callbacks for the data & graphs

@app.callback(
    [Output(component_id='slctd_spc_drop', component_property='options'), 
     Output(component_id='slctd_spc_drop', component_property='value'),
     Output(component_id='slctd_spc_drop', component_property='style')],
    [Input(component_id='slctd_spc_radio', component_property='value')]
)
def choose_genomes(slctd_spc_radio, db = database):

	tax = slctd_spc_radio

	query1 = 'SELECT DISTINCT({}) FROM taxonomy'.format(tax)
	query2 = 'SELECT name, gff_name FROM species'

	db_connect = sqlite3.connect(db)
	cur = db_connect.cursor()

	if tax == 'concrete':
		cur.execute(query2)
		choices = [{'label': element[0], 'value': element[1]} for element in cur.fetchall()]
		db_connect.close()
		default_value = choices[0]['value']
		style = {}
	elif tax == 'all':
		cur.execute(query2)
		choices = [{'label': element[0], 'value': element[1]} for element in cur.fetchall()]
		db_connect.close()
		default_value = [choice['value'] for choice in choices] 
		style = {'display': 'none'}
	else:
		cur.execute(query1)
		choices = [{'label': element[0], 'value': element[0]} for element in cur.fetchall()]
		db_connect.close()
		default_value = choices[0]['value']
		style = {}


	return choices, default_value, style


@app.callback(
    [Output(component_id='genomes_to_represent', component_property='data')],
    [Input(component_id='slctd_spc_drop', component_property='value'),
     Input(component_id='slctd_spc_radio', component_property='value')]
)
def select_genomes(chosen_genomes, taxon, database = database):

	db_connect = sqlite3.connect(database)
	cur = db_connect.cursor()


	if isinstance(chosen_genomes, str) == True:
		a_list = []
		a_list.append(chosen_genomes)
		chosen_genomes = a_list


	if taxon in ['all', 'concrete']:
		genomes = chosen_genomes
	else:
		query = 'SELECT spc.gff_name FROM species spc JOIN taxonomy t ON (spc.gff_name = t.gff_name_id) WHERE t.{} IN (%s)'.format(taxon) % ','.join('?'*len(chosen_genomes))
		cur.execute(query, chosen_genomes)
		genomes = [element[0] for element in cur.fetchall()]


	return (genomes,)


@app.callback(
    [Output(component_id='example_graph', component_property='figure')],
    [Input(component_id='genomes_to_represent', component_property='data'),
     Input(component_id='slctd_spc_radio', component_property='value'),
     Input(component_id='slctd_comp_taxa', component_property='value'),
     Input(component_id='slctd_gene_type', component_property='value'),
     Input(component_id='slctd_intron_type', component_property='value'),
     Input(component_id='graph_selection', component_property='value')]
)
def represent_graphs(genomes, taxon, taxon_to_color, gene_type, intron_type, graph_type, database = database):

	# Choose DB tables depending on the type of genes
	if gene_type == 'all_g':
		stats_tab = 'stats'
		graph_tab = 'graphs'
	elif gene_type == 'prot_g':
		stats_tab = 'stats_prot'
		graph_tab = 'graphs_prot'

	# Choose graph names in DB depending on the introns chosen
	if intron_type == 'ai':
		introns = 'avg_intron_len'
	elif intron_type == 'fi':
		introns = 'avg_first_intron_len'
	elif intron_type == 'ti':
		introns = 'avg_total_intron_len'

	if taxon in ['all', 'concrete']:
		taxon = 'gff_name_id'

	# General queries

	barchart_query = 'SELECT spc.name, s.avg_intron_num_per_gene, t.{taxon_to_color} FROM {stats_tab} s JOIN species spc ON (spc.gff_name = s.gff_name_id) JOIN taxonomy t ON (spc.gff_name = t.gff_name_id) WHERE spc.gff_name IN (%s)'.format(taxon_to_color=taxon_to_color, stats_tab=stats_tab) % ','.join('?'*len(genomes))


	db_connect = sqlite3.connect(database)
	cur = db_connect.cursor()

	# Construct the graph selected
	if graph_type == 'genome_length':

		query = 'SELECT spc.name, spc.genome_length, s.{introns}, t.{taxon_to_color} FROM {stats_tab} s JOIN species spc ON (spc.gff_name = s.gff_name_id) JOIN taxonomy t ON (spc.gff_name = t.gff_name_id) WHERE spc.gff_name IN (%s)'.format(introns=introns, taxon_to_color=taxon_to_color, stats_tab=stats_tab) % ','.join('?'*len(genomes))

		df = pd.read_sql_query(query, db_connect, params = tuple(genomes))

		fig = px.scatter(df, x='genome_length', y=introns, color=df[taxon_to_color], labels=df['name'])

	elif graph_type == 'pca':

		if taxon == taxon_to_color:
			query = 'SELECT spc.name, spc.genome_length, s.*, t.{taxon_to_color}  FROM {stats_tab} s JOIN species spc ON (spc.gff_name = s.gff_name_id) JOIN taxonomy t ON (spc.gff_name = t.gff_name_id) WHERE spc.gff_name IN (%s)'.format(taxon_to_color=taxon_to_color, stats_tab=stats_tab) % ','.join('?'*len(genomes))
		else:
			query = 'SELECT spc.name, spc.genome_length, s.*, t.{taxon}, t.{taxon_to_color}  FROM {stats_tab} s JOIN species spc ON (spc.gff_name = s.gff_name_id) JOIN taxonomy t ON (spc.gff_name = t.gff_name_id) WHERE spc.gff_name IN (%s)'.format(taxon=taxon, taxon_to_color=taxon_to_color, stats_tab=stats_tab) % ','.join('?'*len(genomes))

		df = pd.read_sql_query(query, db_connect, params = tuple(genomes))

		all_features = ['gene_num', 'genes_with_introns_num', 'trans_num', 'exon_num', 'gene_dens',
		'intron_gene_dens', 'avg_gene_len', 'avg_intron_gene_len', 'avg_trans_per_gene',
		'avg_exon_per_trans', 'avg_exon_per_gene', 'avg_intron_num_per_gene', 
		'avg_intron_num_per_gene_with_introns', 'avg_intron_len', 'avg_first_intron_len', 
		'avg_total_intron_len']

		features = ['gene_dens', 'intron_gene_dens', 'avg_gene_len', 'avg_intron_gene_len',
		            'avg_intron_num_per_gene', 'avg_intron_len', 'avg_first_intron_len',
					'avg_total_intron_len', 'avg_intron_num_per_gene_with_introns']

		X = df[features]

		pca = PCA(n_components=3)
		components = pca.fit_transform(X)
		loadings = pca.components_.T * np.sqrt(pca.explained_variance_)

		fig = go.Figure()
		# , text=df['name']
		fig = px.scatter(components, x=0, y=1, color=df[taxon_to_color], symbol=df[taxon])

		fig.update_traces(marker=dict(size=9, line=dict(width=1, color='DarkSlateGrey')), 
						  selector=dict(mode='markers'))

		for i, feature in enumerate(features):
			fig.add_shape(
				type='line',
				x0=0, y0=0,
				x1=loadings[i, 0],
				y1=loadings[i, 1]
			)
			fig.add_annotation(
				x=loadings[i, 0],
				y=loadings[i, 1],
				ax=0, ay=0,
				xanchor="center",
				yanchor="bottom",
				text=feature,
			)

	elif graph_type == 'bar_num_genes':

		query = 'SELECT spc.name, s.gene_num, t.{taxon_to_color} FROM {stats_tab} s JOIN species spc ON (spc.gff_name = s.gff_name_id) JOIN taxonomy t ON (spc.gff_name = t.gff_name_id) WHERE spc.gff_name IN (%s)'.format(taxon_to_color=taxon_to_color, stats_tab=stats_tab) % ','.join('?'*len(genomes))

		df = pd.read_sql_query(query, db_connect, params = tuple(genomes))

		fig = px.bar(df, x='name', y='gene_num', color=df[taxon_to_color])

	elif graph_type == 'bar_num_introns':

		query = 'SELECT spc.name, s.avg_intron_num_per_gene, t.{taxon_to_color} FROM {stats_tab} s JOIN species spc ON (spc.gff_name = s.gff_name_id) JOIN taxonomy t ON (spc.gff_name = t.gff_name_id) WHERE spc.gff_name IN (%s)'.format(taxon_to_color=taxon_to_color, stats_tab=stats_tab) % ','.join('?'*len(genomes))

		df = pd.read_sql_query(query, db_connect, params = tuple(genomes))

		fig = px.bar(df, x='name', y='avg_intron_num_per_gene', color=df[taxon_to_color])

	elif graph_type == 'bar_avg_intron_len':

		query = 'SELECT spc.species, s.{introns}, t.{taxon_to_color} FROM {stats_tab} s JOIN species spc ON (spc.gff_name = s.gff_name_id) JOIN taxonomy t ON (spc.gff_name = t.gff_name_id) WHERE spc.gff_name IN (%s)'.format(introns=introns, taxon_to_color=taxon_to_color, stats_tab=stats_tab) % ','.join('?'*len(genomes))

		df = pd.read_sql_query(query, db_connect, params = tuple(genomes))

		fig = px.bar(df, x='species', y=introns, color=df[taxon_to_color])

	elif graph_type == 'boxplot':

		graph = 'box_1'

		query2 = 'SELECT spc.gff_name, g.{graph} FROM species spc JOIN {graph_tab} g ON (spc.gff_name = g.gff_name_id) WHERE spc.gff_name IN (%s)'.format(graph = graph, graph_tab = graph_tab) % ','.join('?'*len(genomes))

		df = pd.read_sql_query(query2, db_connect, params = tuple(genomes))

		fig = go.Figure()

		for index, row in df.iterrows():

			grph = df[graph][index]
			fig0 = pli.from_json(grph)
			fig.add_trace(fig0.data[0])

		fig.update_layout(yaxis=dict(range=[-1500, 10000]))

	elif graph_type == 'distribution':
		graph = 'dist_1'

		query2 = 'SELECT spc.gff_name, g.{graph} FROM species spc JOIN {graph_tab} g ON (spc.gff_name = g.gff_name_id) WHERE spc.gff_name IN (%s)'.format(graph = graph, graph_tab = graph_tab) % ','.join('?'*len(genomes))

		df = pd.read_sql_query(query2, db_connect, params = tuple(genomes))

		fig = go.Figure()

		for index, row in df.iterrows():

			grph = df[graph][index]
			if grph == '':
				continue
			fig0 = pli.from_json(grph)
			fig.add_trace(fig0.data[0])

		fig.update_layout(xaxis=dict(range=[0, 1500]))

	return (fig,)


# Start the dashboard

if __name__ == "__main__":

	app.run_server(debug=True)