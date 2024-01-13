import os
from os.path import join

import numpy as np
import pandas as pd
from bokeh.document import Document
from bokeh.embed import server_document
from bokeh.layouts import column, row
from bokeh.models import Select
from bokeh.plotting import figure
from bokeh.themes import Theme
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

theme = Theme(filename=join(settings.THEMES_DIR, "theme.yaml"))


def visualization_handler(doc: Document) -> None:
    df = pd.read_csv(os.path.join(os.getcwd(), "../data/heart.csv")).copy()
    columns = sorted(df.columns)

    def create_figure():
        xs = df[x.value].values
        x_title = x.value.title()

        hist, edges = np.histogram(xs, density=False, bins=50)
        p = figure(title=x_title, tools="", background_fill_color="#fafafa")
        p.quad(
            top=hist,
            bottom=0,
            left=edges[:-1],
            right=edges[1:],
            fill_color="navy",
            line_color="white",
            alpha=0.5,
        )

        p.y_range.start = 0
        p.legend.location = "center_right"
        p.legend.background_fill_color = "#fefefe"
        p.xaxis.axis_label = x_title
        p.yaxis.axis_label = "Frequency"
        p.grid.grid_line_color = "white"
        return p

    def callback(attr: str, *args, **kwargs) -> None:
        layout_plot.children[1] = create_figure()

    x = Select(title="x-axis", value="age", options=columns)
    x.on_change("value", callback)

    controls = column(x, width=200)
    layout_plot = row(controls, create_figure())

    doc.theme = theme
    doc.add_root(layout_plot)
    doc.title = "Raw data histogram"


def visualization(request: HttpRequest) -> HttpResponse:
    script = server_document(request.build_absolute_uri())
    return render(request, "visualization.html", dict(script=script))
