# dash proof of concept

import config
import dash
from dash import dcc
from dash import html
import pandas as pd
import sqlite3
import plotly.express as px

app = dash.Dash(__name__)

db = sqlite3.connect(config.GENERAL_DB_DIR / 'GenomesDb.sql')

df = pd.read_sql_query("SELECT species_type, count(DISTINCT species) FROM species GROUP BY species_type", db)

print(df)

df2 = pd.read_sql_query("SELECT gff_name_id, gene_num FROM stats", db)


app.layout = html.Div(
    children=[
        html.H1(children="Types of genomes",),
        html.P(
            children="The types of genomes present in the"
            " obtained database, sorted according to their"
            " type & ENSEMBL repository.",
        ),
        dcc.Graph(
            figure={
                "data": [
                    {
                        "x": df["species_type"],
                        "y": df["count(DISTINCT species)"],
                        "type": "bar",
                    },
                ],
                "layout": {"title": "Genome types in DB"},
            },
        ),
        html.H1(children='Number of genes among species'),
        html.P(
            children='Graph with the number of genes of each species'),
        dcc.Graph(
            figure={
            "data":[
                    {
                    "x": df2["gff_name_id"],
                    "y": df2["gene_num"],
                    "type": "bar",
                    }
            ],
            "layout": {"title": "Gene number for each species"},
            }
        )
    ]
)

db.close()

if __name__ == "__main__":

    app.run_server(debug=True)
