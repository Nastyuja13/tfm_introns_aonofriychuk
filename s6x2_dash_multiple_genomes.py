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

slctd_comp_taxa = [{'label': 'Kingdom', 'value': 'kingdom'},
	{'label': 'Phylum', 'value': 'phylum'},
	{'label': 'Class', 'value': 'class_'},
	{'label': 'Order', 'value': 'order_'},
	{'label': 'Family', 'value': 'family'}
	]

slctd_gene_type = [{'label': 'All genes', 'value': 'all_g'}, 
	{'label': 'Protein-coding genes', 'value': 'prot_g'}
	]

slctd_gene_int = [{'label': 'All genes', 'value': 'all_in'}, 
	{'label': 'Only intron-containing genes', 'value': 'only_in'}
	]

slctd_intron_type = [{'label': 'All introns', 'value': 'ai'}, 
	{'label': 'First introns', 'value': 'fi'}, 
	{'label': 'Total intron length', 'value': 'ti'}
	]

pca_options = [{'label': 'Genome length', 'value': 'genome_length'}, 
				{'label': 'Gene number', 'value': 'gene_num'}, 
				{'label': 'Intronic gene number', 'value': 'genes_with_introns_num'}, 
				{'label': 'Transcript number', 'value': 'trans_num'}, 
				{'label': 'Exon number', 'value': 'exon_num'}, 
				{'label': 'Gene density', 'value': 'gene_dens'},
				{'label': 'Intronic gene density', 'value': 'intron_gene_dens'}, 
				{'label': 'Average gene length', 'value': 'avg_gene_len'}, 
				{'label': 'Average intronic gene lengh', 'value': 'avg_intron_gene_len'},
				{'label': 'Average exon length','value': 'avg_exon_len'},
				{'label': 'Average exon length in intonic genes','value': 'avg_exon_len_in_int_genes'},
				{'label': 'Average transcripts per gene', 'value': 'avg_trans_per_gene'},
				{'label': 'Average exons per transcripts', 'value': 'avg_exon_per_trans'},
				{'label': 'Average exons per gene', 'value': 'avg_exon_per_gene'}, 
				{'label': 'Average intron number per gene', 'value': 'avg_intron_num_per_gene'},
				{'label': 'Average intron number per intronic gene', 'value': 'avg_intron_num_per_gene_with_introns'}, 
				{'label': 'Average intron length', 'value': 'avg_intron_len'}, 
				{'label': 'Average first intron length', 'value': 'avg_first_intron_len'},
				{'label': 'Average total intron length', 'value': 'avg_total_intron_len'}]


stat_features = {'genome_length': 'Genome length', 
				'gene_num': 'Gene number', 
				'genes_with_introns_num': 'Intronic gene number', 
				'trans_num': 'Transcript number', 
				'exon_num': 'Exon number', 
				'gene_dens': 'Gene density',
				'intron_gene_dens': 'Intronic gene density', 
				'avg_gene_len': 'Average gene length', 
				'avg_intron_gene_len': 'Average intronic gene lengh',
				'avg_exon_len': 'Average exon length',
				'avg_exon_len_in_int_genes': 'Average exon length in intonic genes', 
				'avg_trans_per_gene': 'Average transcripts per gene',
				'avg_exon_per_trans': 'Average exons per transcripts',
				'avg_exon_per_gene': 'Average exons per gene', 
				'avg_intron_num_per_gene': 'Average intron number per gene',
				'avg_intron_num_per_gene_with_introns': 'Average intron number per intronic gene', 
				'avg_intron_len': 'Average intron length', 
				'avg_first_intron_len': 'Average first intron length',
				'avg_total_intron_len': 'Average total intron length'}

av_taxons = {'kingdom': 'Kingdom', 'phylum': 'Phylum', 'class_': 'Class',
	'order_': 'Order', 'family': 'Family'}

# Dash layout 

app.layout = html.Div([
	# Title
	html.H1("Intronic variation analysis across species", 
		style={'text-align': 'center', 'font-family': '"Arial", Arial, sans-serif'}),
	# Selctors
	html.Div(id='data_selection', children = [
		## Genome selector
		html.Div(id='genomes_selection', children = [
			html.H3("Select which genomes to compare:", 
				style={'text-align': 'center', 'font-family': '"Arial", Arial, sans-serif',
								'border-radius': "5px", 'background': "#E5ECF6"}), 
			html.Table(children = [
				html.Tbody([
					html.Tr(children = [
						html.Td(
							dcc.RadioItems(id='slctd_spc_radio', 
								options=radio_genome_select, 
								value='kingdom', 
								style={'display': 'flex', 'align-items': 'center', 
									'justify-content': 'center', 'width': "100%",
									'font-family': '"Arial", Arial, sans-serif'},
								labelStyle = {'display': 'inline-block'})),
						html.Td(
							dcc.Dropdown(id='slctd_spc_drop', 
								options=[], 
								multi=True, 
								value=[], 
								style={}))])])], style={'width': '100%', 'table-layout': 'fixed',
									'font-family': '"Arial", Arial, sans-serif'})]), 
		## Coloring, gene & intron selectors
		html.Div(id='comparison_selectors', children = [
			html.Table(
				html.Tbody([
					html.Tr(
						[html.Td(
							html.H3("Select taxon to compare genomes:", 
								style={'text-align': 'center', 'font-family': '"Arial", Arial, sans-serif',
								'border-radius': "5px", 'background': "#E5ECF6"})),
						html.Td(
							html.H3("Select gene biotype to consider:", 
								style={'text-align': 'center', 'font-family': '"Arial", Arial, sans-serif',
								'border-radius': "5px", 'background': "#E5ECF6"})),
						html.Td(
							html.H3("Select which genes to consider:", 
								style={'text-align': 'center', 'font-family': '"Arial", Arial, sans-serif',
								'border-radius': "5px", 'background': "#E5ECF6"})),
						html.Td(
							html.H3("Select which introns to consider:",
								style={'text-align': 'center', 'font-family': '"Arial", Arial, sans-serif',
								'border-radius': "5px", 'background': "#E5ECF6"}))]), 
					html.Tr([
						html.Td(dcc.RadioItems(id='slctd_comp_taxa', 
								options=slctd_comp_taxa,
								value='kingdom', 
								style={'display': 'flex', 'align-items': 'center', 
									'justify-content': 'center', 'width': "100%",
									'font-family': '"Arial", Arial, sans-serif'},
								labelStyle = {'display': 'inline-block'})), 
						html.Td(dcc.RadioItems(id='slctd_gene_type', 
								options=slctd_gene_type, 
								value='all_g', 
								style={'display': 'flex', 'align-items': 'center', 
									'justify-content': 'center', 'width': "100%",
									'font-family': '"Arial", Arial, sans-serif'},
								labelStyle = {'display': 'inline-block'})),
						html.Td(dcc.RadioItems(id='slctd_gene_int', 
								options=slctd_gene_int, 
								value='all_in', 
								style={'display': 'flex', 'align-items': 'center', 
									'justify-content': 'center', 'width': "100%",
									'font-family': '"Arial", Arial, sans-serif'},
								labelStyle = {'display': 'inline-block'})), 
						html.Td(dcc.RadioItems(id='slctd_intron_type', 
								options=slctd_intron_type, 
								value='ai', 
								style={'display': 'flex', 'align-items': 'center', 
									'justify-content': 'center', 'width': "100%",
									'font-family': '"Arial", Arial, sans-serif'},
								labelStyle = {'display': 'inline-block'}))
						])
					]), style={'width': '100%', 'table-layout': 'fixed'})])]),
	#html.Br(), 
	# Graphs
	html.Div(id='graph_display', children = [
		dcc.Tabs(id="graph_selection", value='genome_length', children=[
			dcc.Tab(label='Genome length vs intron length', value='genome_length'),
			dcc.Tab(label='PCA', value='pca', children=[
				dcc.Dropdown(id='slctd_pca_feat', 
								options=pca_options, 
								multi=True, 
								value=['gene_num', 'gene_dens', 'avg_gene_len', 
								'avg_intron_num_per_gene', 'avg_intron_len'], 
								style={})]),
			dcc.Tab(label='Barchart of the number of genes', value='bar_num_genes'),
			dcc.Tab(label='Barchart of the density of genes', value='bar_dens_genes'),
			dcc.Tab(label='Barchart of the average gene length', value='bar_avg_gene_len'),
			dcc.Tab(label='Barchart of the average exon length', value='bar_avg_exon_len'),
			dcc.Tab(label='Barchart of the average number of introns', value='bar_num_introns'),
			dcc.Tab(label='Barchart of the average intron length', value='bar_avg_intron_len'),
			dcc.Tab(label='Intron length boxplot', value='boxplot'),
			dcc.Tab(label='Intron length distribution', value='distribution')
			]
			),
		html.Div(id='tabs-content-example-graph', children = [
			dcc.Graph(id='example_graph', figure={}, style={'width': '100%', 'height': '700px'})
			]
			)
		]
		),
	# stores the intermediate value
    dcc.Store(id='genomes_to_represent', data=[]),

    # Footer
    html.Footer(children=[
    	html.P("Anastasiya Onofriychuk Bulatóvych",
    		style={'text-align': 'center', 'font-family': '"Arial", Arial, sans-serif'}),
    	html.P("Master's Degree of Bioinformatics & Biostatistics, UOC",
    		style={'text-align': 'center', 'font-family': '"Arial", Arial, sans-serif'})])
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

	query1 = 'SELECT DISTINCT({tax}) FROM taxonomy ORDER BY {tax} ASC'.format(tax=tax)
	query2 = 'SELECT species, gff_name FROM species ORDER BY species ASC'

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
     Input(component_id='slctd_gene_int', component_property='value'),
     Input(component_id='slctd_intron_type', component_property='value'),
     Input(component_id='graph_selection', component_property='value'),
     Input(component_id='slctd_pca_feat', component_property='value')]
)
def represent_graphs(genomes, taxon, taxon_to_color, gene_type, gene_int_type, intron_type, graph_type, pca_selection, database = database):

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
		boxplot = 'box_all'
		distribution = 'dist_all'
	elif intron_type == 'fi':
		introns = 'avg_first_intron_len'
		boxplot = 'box_1'
		distribution = 'dist_1'
	elif intron_type == 'ti':
		introns = 'avg_total_intron_len'
		boxplot = 'box_tot'
		distribution = 'dist_tot'

	if taxon in ['all', 'concrete']:
		taxon = 'gff_name_id'

	# Choose stats by considering all genes or only intron-containing ones

	if gene_int_type == 'all_in':

		gene_num = 'gene_num'
		gene_dens = 'gene_dens'
		avg_gene_len = 'avg_gene_len'
		avg_exon_len = 'avg_exon_len'
		avg_int_num = 'avg_intron_num_per_gene'

	elif gene_int_type == 'only_in':

		gene_num = 'genes_with_introns_num'
		gene_dens = 'intron_gene_dens'
		avg_gene_len = 'avg_intron_gene_len'
		avg_exon_len = 'avg_exon_len_in_int_genes'
		avg_int_num = 'avg_intron_num_per_gene_with_introns'


	db_connect = sqlite3.connect(database)
	cur = db_connect.cursor()

	# Construct the graph selected
	if graph_type == 'genome_length':

		query = 'SELECT spc.species, spc.genome_length, s.{introns}, t.{taxon_to_color} FROM {stats_tab} s JOIN species spc ON (spc.gff_name = s.gff_name_id) JOIN taxonomy t ON (spc.gff_name = t.gff_name_id) WHERE spc.gff_name IN (%s)'.format(introns=introns, taxon_to_color=taxon_to_color, stats_tab=stats_tab) % ','.join('?'*len(genomes))

		df = pd.read_sql_query(query, db_connect, params = tuple(genomes))

		fig = px.scatter(df, x='genome_length', y=introns, color=df[taxon_to_color], 
			labels={'genome_length': 'Genome length (bp)', introns: stat_features[introns] + " (bp)"})

		# text=df['species']

	elif graph_type == 'pca':

		if (taxon == taxon_to_color) or (taxon == 'gff_name_id'):
			query = 'SELECT spc.species, spc.genome_length, s.*, t.{taxon_to_color} FROM {stats_tab} s JOIN species spc ON (spc.gff_name = s.gff_name_id) JOIN taxonomy t ON (spc.gff_name = t.gff_name_id) WHERE spc.gff_name IN (%s)'.format(taxon_to_color=taxon_to_color, stats_tab=stats_tab) % ','.join('?'*len(genomes))
		else:
			query = 'SELECT spc.species, spc.genome_length, s.*, t.{taxon}, t.{taxon_to_color}  FROM {stats_tab} s JOIN species spc ON (spc.gff_name = s.gff_name_id) JOIN taxonomy t ON (spc.gff_name = t.gff_name_id) WHERE spc.gff_name IN (%s)'.format(taxon=taxon, taxon_to_color=taxon_to_color, stats_tab=stats_tab) % ','.join('?'*len(genomes))

		df = pd.read_sql_query(query, db_connect, params = tuple(genomes))

		features = pca_selection

		X = df[features]

		pca = PCA(n_components=3)
		components = pca.fit_transform(X)
		loadings = pca.components_.T * np.sqrt(pca.explained_variance_)

		fig = go.Figure()
		# , text=df['name']
		fig = px.scatter(components, x=0, y=1, color=df[taxon_to_color], symbol=df[taxon],
			labels={'0': 'PC 1', '1': 'PC 2'})

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
				text=stat_features[feature],
			)

	elif graph_type == 'bar_num_genes':

		query = 'SELECT spc.name, s.{gene_num}, t.species, t.{taxon_to_color} FROM {stats_tab} s JOIN species spc ON (spc.gff_name = s.gff_name_id) JOIN taxonomy t ON (spc.gff_name = t.gff_name_id) WHERE spc.gff_name IN (%s)'.format(gene_num = gene_num, taxon_to_color=taxon_to_color, stats_tab=stats_tab) % ','.join('?'*len(genomes))

		df = pd.read_sql_query(query, db_connect, params = tuple(genomes))

		fig = px.bar(df, x='species', y=gene_num, color=df[taxon_to_color],
			labels={'species': '', gene_num: stat_features[gene_num]})	

	elif graph_type == 'bar_dens_genes':

		query = 'SELECT spc.name, s.{gene_dens}, t.species, t.{taxon_to_color} FROM {stats_tab} s JOIN species spc ON (spc.gff_name = s.gff_name_id) JOIN taxonomy t ON (spc.gff_name = t.gff_name_id) WHERE spc.gff_name IN (%s)'.format(gene_dens= gene_dens, taxon_to_color=taxon_to_color, stats_tab=stats_tab) % ','.join('?'*len(genomes))

		df = pd.read_sql_query(query, db_connect, params = tuple(genomes))

		fig = px.bar(df, x='species', y=gene_dens, color=df[taxon_to_color],
			labels={'species': '', gene_dens: stat_features[gene_dens] + " (genes/Mbp)"})

	elif graph_type == 'bar_avg_gene_len':

		query = 'SELECT spc.name, s.{avg_gene_len}, t.species, t.{taxon_to_color} FROM {stats_tab} s JOIN species spc ON (spc.gff_name = s.gff_name_id) JOIN taxonomy t ON (spc.gff_name = t.gff_name_id) WHERE spc.gff_name IN (%s)'.format(avg_gene_len = avg_gene_len, taxon_to_color=taxon_to_color, stats_tab=stats_tab) % ','.join('?'*len(genomes))

		df = pd.read_sql_query(query, db_connect, params = tuple(genomes))

		fig = px.bar(df, x='species', y=avg_gene_len, color=df[taxon_to_color],
			labels={'species': '', avg_gene_len: stat_features[avg_gene_len] + " (bp)"})


	elif graph_type == 'bar_avg_exon_len':

		query = 'SELECT spc.species, s.{avg_exon_len}, t.{taxon_to_color} FROM {stats_tab} s JOIN species spc ON (spc.gff_name = s.gff_name_id) JOIN taxonomy t ON (spc.gff_name = t.gff_name_id) WHERE spc.gff_name IN (%s)'.format(avg_exon_len=avg_exon_len, taxon_to_color=taxon_to_color, stats_tab=stats_tab) % ','.join('?'*len(genomes))

		df = pd.read_sql_query(query, db_connect, params = tuple(genomes))

		fig = px.bar(df, x='species', y=avg_exon_len, color=df[taxon_to_color],
			labels={'species': '', avg_exon_len: stat_features[avg_exon_len] + " (bp)"})

	elif graph_type == 'bar_num_introns':

		query = 'SELECT spc.name, s.{avg_int_num}, t.species, t.{taxon_to_color} FROM {stats_tab} s JOIN species spc ON (spc.gff_name = s.gff_name_id) JOIN taxonomy t ON (spc.gff_name = t.gff_name_id) WHERE spc.gff_name IN (%s)'.format(avg_int_num=avg_int_num, taxon_to_color=taxon_to_color, stats_tab=stats_tab) % ','.join('?'*len(genomes))

		df = pd.read_sql_query(query, db_connect, params = tuple(genomes))

		fig = px.bar(df, x='species', y=avg_int_num, color=df[taxon_to_color],
			labels={'species': '', avg_int_num: stat_features[avg_int_num]})

	elif graph_type == 'bar_avg_intron_len':

		query = 'SELECT spc.species, s.{introns}, t.{taxon_to_color} FROM {stats_tab} s JOIN species spc ON (spc.gff_name = s.gff_name_id) JOIN taxonomy t ON (spc.gff_name = t.gff_name_id) WHERE spc.gff_name IN (%s)'.format(introns=introns, taxon_to_color=taxon_to_color, stats_tab=stats_tab) % ','.join('?'*len(genomes))

		df = pd.read_sql_query(query, db_connect, params = tuple(genomes))

		fig = px.bar(df, x='species', y=introns, color=df[taxon_to_color],
			labels={'species': '', introns: stat_features[introns] + " (bp)"})

	elif graph_type == 'boxplot':

		graph = boxplot

		query2 = 'SELECT spc.gff_name, g.{graph}, t.{taxon_to_color} FROM species spc JOIN {graph_tab} g ON (spc.gff_name = g.gff_name_id) JOIN taxonomy t ON (spc.gff_name = t.gff_name_id) WHERE spc.gff_name IN (%s) ORDER BY t.{taxon_to_color} ASC'.format(graph = graph, taxon_to_color=taxon_to_color, graph_tab = graph_tab) % ','.join('?'*len(genomes))

		df = pd.read_sql_query(query2, db_connect, params = tuple(genomes))

		fig = go.Figure()

		# Set colors for boxplots and distribution plots

		taxons = list(set(df[taxon_to_color]))
		colors = {}

		j = 0
		for tax in taxons:
			colors[tax] = px.colors.qualitative.Plotly[j]

			j = j + 1

			if j == len(px.colors.qualitative.Plotly):
				j = 0


		for index, row in df.iterrows():

			grph = df[graph][index]
			tx = df[taxon_to_color][index]
			fig0 = pli.from_json(grph)
			fig0.data[0].update(marker= {'color': colors[tx]}, name = fig0.data[0].name + ', ' + tx)
			fig.add_trace(fig0.data[0])

		# yaxis=dict(range=[-1500, 12000]),
		fig.update_layout( yaxis_title= stat_features[introns] + " (bp)")

	elif graph_type == 'distribution':
		graph = distribution

		#query2 = 'SELECT spc.gff_name, g.{graph}, t.{taxon_to_color} FROM species spc JOIN {graph_tab} g ON (spc.gff_name = g.gff_name_id) WHERE spc.gff_name IN (%s)'.format(graph = graph, graph_tab = graph_tab) % ','.join('?'*len(genomes))
		query2 = 'SELECT spc.gff_name, g.{graph}, t.{taxon_to_color} FROM species spc JOIN {graph_tab} g ON (spc.gff_name = g.gff_name_id) JOIN taxonomy t ON (spc.gff_name = t.gff_name_id) WHERE spc.gff_name IN (%s) ORDER BY t.{taxon_to_color} ASC'.format(graph = graph, taxon_to_color=taxon_to_color, graph_tab = graph_tab) % ','.join('?'*len(genomes))
		
		df = pd.read_sql_query(query2, db_connect, params = tuple(genomes))

		fig = go.Figure()

		#fig.for_each_trace(lambda trace: trace.update(marker_symbol="square") if trace.name == "setosa" else (),
			#) colorway=px.colors.qualitative.Prism
			
		# Set colors for boxplots and distribution plots

		taxons = list(set(df[taxon_to_color]))
		colors = {}

		j = 0
		for tax in taxons:
			colors[tax] = px.colors.qualitative.Plotly[j]

			j = j + 1

			if j == len(px.colors.qualitative.Plotly):
				j = 0
				

		for index, row in df.iterrows():

			grph = df[graph][index]
			tx = df[taxon_to_color][index]
			if grph == '':
				continue
			fig0 = pli.from_json(grph)
			fig0.data[0].update(marker= {'color': colors[tx]}, name = fig0.data[0].name + ', ' + tx)
			fig.add_trace(fig0.data[0])

		fig.update_layout(yaxis_title= "Frequency", xaxis_title = "Log10 (" + stat_features[introns] + " (bp))")

	fig.update_layout(legend_title_text=av_taxons[taxon_to_color])

	return (fig,)


# Start the dashboard

if __name__ == "__main__":

	app.run_server(host='0.0.0.0', debug=True, port=8050)