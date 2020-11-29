# -*- coding: utf-8 -*-
"""
Loan Calculator - Navbar

@author: shuhui
"""
import dash_bootstrap_components as dbc
import dash_html_components as html

PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

def Navbar():
    navbar = dbc.Navbar(
        html.A(dbc.Row([
            html.Img(src=PLOTLY_LOGO, height="30px"),
            dbc.NavbarBrand("Plotly dash", className="ml-2"),
            ],
            align = "center",
            no_gutters = True
        )),
            color="#B0C4DE",
            light=True,
    )
    return navbar