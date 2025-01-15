# Import the necessary libraries, also listen in the requirements.txt file
# While not all the things are being used (LayersControl, Popup), they are included in case you would like to add more layers
# (for instance, one of the CDFI people said counties could be useful to add) or add popups when the version of Shiny
# Becomes compatible
import json
from ipyleaflet import GeoJSON, Map, basemaps, LegendControl, SearchControl, LayersControl, Popup
from ipywidgets import Layout
from shiny import App, ui, reactive
from shinywidgets import output_widget, render_widget, register_widget
from htmltools import HTML, div


# Loading the geojson, which should be in the same folder as app.py
with open('data.geojson', "r") as f:
    natmap = json.load(f)

# Here we define strings for use in formulas throghout the code
embor_str = 'Emergency Borrowing: Likelihood that the average person in a given area would borrow from friends or family to cover a $400 emergency expense'
exbor_str = "Excess Spending Borrowing: Likelihood that the average person in a given area’s spending has exceeded their income and they would borrow from friends or family to cover the excess expenses"
wl_str = "Owed by Others: Likelihood that the average person in a given area is owed money by friends, businesses, or others"
la_str = "Amount Owed by Others: How much money the average person in a given area is likely to be owed by friends, businesses, or others"

# TODO: change to Community Finance colors (maybe)
# Here, we are creating lists that make up our color scheme
embor_color = ["#bfd2ff", "#8aadff", "#4a80ff", "#004cff"]
exbor_color = ["#cebfff", "#ab91ff", "#7a52ff", "#3c00ff"]
wl_color = ["#dcc4ff", "#ba8aff", "#954dff", "#6800ff"]
la_color = ["#e5baff", "#cf82ff", "#ba4aff", "#9d00ff"]

# These numbers come from the model output CSV
# Follows: [min, 25%, 50%, 75%, max]
embor_quartiles = [0.114408	, 0.198014, 0.226183, 0.257190, 0.441033]
exbor_quartiles = [0.048980, 0.080217, 0.089925, 0.103192, 0.221574]
wl_quartiles = [0.002730, 0.009475, 0.012500, 0.017434, 0.064409]
la_quartiles = [689.999309, 1352.286746, 1766.829105, 2504.259972, 12411.070516]

# Defining a function that displays whatever state the user selects in the dropdown menu
def state_choose(fip):
    flist = []
    if fip == -1:
        for f in natmap['features']:
            flist.append(f)
        geodict = {"type": "FeatureCollection", 
                    "name": "nationalmap", 
                    "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } }, 
                    "features":flist}
    else:
        for f in natmap['features']:
            if f['properties']['STATEFIP'] == int(fip):
                flist.append(f)
        geodict = {"type": "FeatureCollection", 
                    "name": "nationalmap", 
                    "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } }, 
                    "features":flist}
    return geodict

# The next four functions are definind how we color individual shapes (features) within the geojson
def em_borrow(feature):
    if feature['properties']['weighted_Emergency_Borrowing'] <= embor_quartiles[1]:
        return {
                "color": "black",
                "fillColor": embor_color[0],  
        }
    elif embor_quartiles[1] < feature['properties']['weighted_Emergency_Borrowing'] <= embor_quartiles[2]:
        return {
            "color": "black",
            "fillColor": embor_color[1],  
        }
    elif embor_quartiles[2] < feature['properties']['weighted_Emergency_Borrowing'] <= embor_quartiles[3]:
        return {
            "color": "black",
            "fillColor": embor_color[2],  
        }
    else:
        return {
            "color": "black",
            "fillColor": embor_color[3],  
        }

def ex_spend_borrow(feature):
    if feature['properties']['Weighted_Excess_Spending_Borrowing'] <= exbor_quartiles[1]:
        return {
                "color": "black",
                "fillColor": exbor_color[0],  
        }
    elif exbor_quartiles[1] < feature['properties']['Weighted_Excess_Spending_Borrowing'] <= exbor_quartiles[2]:
        return {
            "color": "black",
            "fillColor": exbor_color[1],  
        }
    elif exbor_quartiles[2] < feature['properties']['Weighted_Excess_Spending_Borrowing'] <= exbor_quartiles[3]:
        return {
            "color": "black",
            "fillColor": exbor_color[2],  
        }
    else:
        return {
            "color": "black",
            "fillColor": exbor_color[3],  
        }
    
def will_to_lend(feature):
    if feature['properties']['weighted_Willing_to_Lend'] <= wl_quartiles[1]:
        return {
                "color": "black",
                "fillColor": wl_color[0],  
        }
    elif wl_quartiles[1] < feature['properties']['weighted_Willing_to_Lend'] <= wl_quartiles[2]:
        return {
            "color": "black",
            "fillColor": wl_color[1],  
        }
    elif wl_quartiles[2] < feature['properties']['weighted_Willing_to_Lend'] <= wl_quartiles[3]:
        return {
            "color": "black",
            "fillColor": wl_color[2],  
        }
    else:
        return {
            "color": "black",
            "fillColor": wl_color[3],  
        }

def lend_amount(feature):
    if feature['properties']['weighted_Amount_Willing_to_Lend'] <= la_quartiles[1]:
        return {
                "color": "black",
                "fillColor": la_color[0],  
        }
    elif la_quartiles[1] < feature['properties']['weighted_Amount_Willing_to_Lend'] <= la_quartiles[2]:
        return {
            "color": "black",
            "fillColor": la_color[1],  
        }
    elif la_quartiles[2] < feature['properties']['weighted_Amount_Willing_to_Lend'] <= la_quartiles[3]:
        return {
            "color": "black",
            "fillColor": la_color[2],  
        }
    else:
        return {
            "color": "black",
            "fillColor": la_color[3],  
        }

# Defining a function that creates text labels for the legend
def legend_ranges(bottom, top):
    if bottom not in la_quartiles and top not in la_quartiles:
        btm = str(round((bottom * 100), 2))
        tp = str(round((top * 100), 2))
        out = btm + ' to ' + tp
    else:
        btm = str(int(round(bottom, 0)))
        tp = str(int(round(top, 0)))
        out = '$' + btm + ' to ' + '$' + tp
    
    
    return out

# Creating a dictionary connecting the strings we created earlier to both coloring functions and legend labels
funcdict = {embor_str: [[em_borrow], {legend_ranges(embor_quartiles[0], embor_quartiles[1]): embor_color[0], 
                                      legend_ranges(embor_quartiles[1], embor_quartiles[2]): embor_color[1], 
                                      legend_ranges(embor_quartiles[2], embor_quartiles[3]): embor_color[2], 
                                      legend_ranges(embor_quartiles[3], embor_quartiles[4]): embor_color[3]}, 
                        ["Emergency Borrowing (%)"]], 
            exbor_str: [[ex_spend_borrow], {legend_ranges(exbor_quartiles[0], exbor_quartiles[1]): exbor_color[0], 
                                            legend_ranges(exbor_quartiles[1], exbor_quartiles[2]):exbor_color[1], 
                                            legend_ranges(exbor_quartiles[2], exbor_quartiles[3]):exbor_color[2], 
                                            legend_ranges(exbor_quartiles[3], exbor_quartiles[4]): exbor_color[3]}, 
                        ["Excess Spending Borrowing (%)"]], 
            wl_str: [[will_to_lend], {legend_ranges(wl_quartiles[0], wl_quartiles[1]): wl_color[0], 
                                      legend_ranges(wl_quartiles[1], wl_quartiles[2]):wl_color[1], 
                                      legend_ranges(wl_quartiles[2], wl_quartiles[3]):wl_color[2], 
                                      legend_ranges(wl_quartiles[3], wl_quartiles[4]): wl_color[3]}, 
                    ["Willingness to Lend (%)"]], 
            la_str: [[lend_amount], {legend_ranges(la_quartiles[0], la_quartiles[1]): la_color[0], 
                                     legend_ranges(la_quartiles[1], la_quartiles[2]):la_color[1], 
                                     legend_ranges(la_quartiles[2], la_quartiles[3]):la_color[2], 
                                     legend_ranges(la_quartiles[3], la_quartiles[4]): la_color[3]}, 
                    ["Amount Owed by Others"]]}

# This dict is used in the State Choose function as the user decides which state to display
statedict = {'United States': {'fipscode': -1, 'coordinates': (37.8187, -91.1454)}, 
             'Alabama': {'fipscode': 1, 'coordinates': (32.3182, -86.9023)}, 
             'Alaska': {'fipscode': 2, 'coordinates': (63.5888, -154.4931)}, 
             'Arizona': {'fipscode': 4, 'coordinates': (34.0489, -111.0937)}, 
             'Arkansas': {'fipscode': 5, 'coordinates': (35.2010, -91.8318)}, 
             'California': {'fipscode': 6, 'coordinates': (36.7783, -119.4179)}, 
             'Colorado': {'fipscode': 8, 'coordinates': (39.5501, -105.7821)}, 
             'Connecticut': {'fipscode': 9, 'coordinates': (41.6032, -73.0877)}, 
             'Delaware': {'fipscode': 10, 'coordinates': (38.9108, -75.5277)}, 
             'District of Columbia': {'fipscode': 11, 'coordinates': (38.9072, -77.0369)}, 
             'Florida': {'fipscode': 12, 'coordinates': (27.6648, -81.5158)}, 
             'Georgia': {'fipscode': 13, 'coordinates': (32.1574, -82.9071)}, 
             'Hawaii': {'fipscode': 15, 'coordinates': (19.8987, -155.6659)}, 
             'Idaho': {'fipscode': 16, 'coordinates': (43.6081, -116.5087)}, 
             'Indiana': {'fipscode': 18, 'coordinates': (40.5512, -85.6024)}, 
             'Illinois': {'fipscode': 17, 'coordinates': (40.6331, -89.3985)}, 
             'Iowa': {'fipscode': 19, 'coordinates': (41.8780, -93.0977)}, 
             'Kansas': {'fipscode': 20, 'coordinates': (39.0119, -98.4842)}, 
             'Kentucky': {'fipscode': 21, 'coordinates': (37.8393, -84.2700)}, 
             'Louisiana': {'fipscode': 22, 'coordinates': (30.5191, -91.5209)}, 
             'Maine': {'fipscode': 23, 'coordinates': (45.2538, -69.4455)}, 
             'Maryland': {'fipscode': 24, 'coordinates': (39.0458, -76.6413)}, 
             'Massachusetts': {'fipscode': 25, 'coordinates': (42.4072, -71.3824)}, 
             'Michigan': {'fipscode': 26, 'coordinates': (42.2331, -84.3272)}, 
             'Minnesota': {'fipscode': 27, 'coordinates': (46.7296, -94.6859)}, 
             'Mississippi': {'fipscode': 28, 'coordinates': (32.3547, -89.3985)}, 
             'Missouri': {'fipscode': 29, 'coordinates': (37.9643, -91.8318)}, 
             'Montana': {'fipscode': 30, 'coordinates': (46.8797, -110.3626)}, 
             'Nebraska': {'fipscode': 31, 'coordinates': (41.4925, -99.9018)}, 
             'Nevada': {'fipscode': 32, 'coordinates': (38.8026, -116.4194)}, 
             'New Hampshire': {'fipscode': 33, 'coordinates': (43.1939, -71.5724)}, 
             'New Jersey': {'fipscode': 34, 'coordinates': (40.0583, -74.4057)}, 
             'New Mexico': {'fipscode': 35, 'coordinates': (34.9727, -105.0324)}, 
             'New York': {'fipscode': 36, 'coordinates': (40.7128, -74.0060)}, 
             'North Carolina': {'fipscode': 37, 'coordinates': (35.7596, -79.0193)}, 
             'North Dakota': {'fipscode': 38, 'coordinates': (47.5515, -101.0020)}, 
             'Ohio': {'fipscode': 39, 'coordinates': (40.4173, -82.9071)}, 
             'Oklahoma': {'fipscode': 40, 'coordinates': (35.0078, -97.0929)}, 
             'Oregon': {'fipscode': 41, 'coordinates': (43.8041, -120.5542)}, 
             'Pennsylvania': {'fipscode': 42, 'coordinates': (41.2033, -77.1945)}, 
             'Rhode Island': {'fipscode': 44, 'coordinates': (41.5801, -71.4774)}, 
             'South Carolina': {'fipscode': 45, 'coordinates': (33.8361, -81.1637)}, 
             'South Dakota': {'fipscode': 46, 'coordinates': (43.9695, -99.9018)}, 
             'Tennessee': {'fipscode': 47, 'coordinates': (35.5175, -86.5804)}, 
             'Texas': {'fipscode': 48, 'coordinates': (31.9686, -99.9018)}, 
             'Utah': {'fipscode': 49, 'coordinates': (40.7607, -111.8939)}, 
             'Vermont': {'fipscode': 50, 'coordinates': (44.5588, -72.5778)}, 
             'Virginia': {'fipscode': 51, 'coordinates': (37.4316, -78.6569)}, 
             'Washington': {'fipscode': 53, 'coordinates': (47.7511, -120.7401)}, 
             'West Virginia': {'fipscode': 54, 'coordinates': (38.5976, -80.4549)}, 
             'Wisconsin': {'fipscode': 55, 'coordinates': (43.7844, -88.7879)}, 
             'Wyoming': {'fipscode': 56, 'coordinates': (43.0760, -107.2903)}
}

# This dict is what will be used for the radio (circle) buttons
radiodict = {embor_str: [em_borrow], 
             exbor_str: [ex_spend_borrow], 
             wl_str: [will_to_lend], 
             la_str: [lend_amount]}



# app_ui is what Shiny uses to establish what the app looks like for users
app_ui = ui.page_sidebar(
    
    ui.sidebar(
      # Dropdown Menu
      ui.input_select(
          'select', 
          'Select a state:', 
          choices = list(statedict.keys()), 
          ), 
      # Individual buttons
      ui.input_radio_buttons(  
          "radio",  
          "Select a variable:",  
          choices = list(radiodict.keys()), 
          width = '100%',  
      ),  
      bg="#E9EFFF"),  
    ui.page_fluid(
      # Map
      output_widget("map"),
      ui.layout_columns(
        div(HTML(
          'Public service of <strong><a href="https://www.communityfi.org">Community Finance</a></strong>'
        )),
        div(HTML(
          '<a href="https://github.com/communityfinance/peer-lending-map">View code on Github</a>'
        )).add_style("text-align: right;")
      )
    ),
    title="Peer Lending in the United States"
)


# def server is how we add reactive elements that respond to user inputs
def server(input, output, session):
    # Here is where the map is actually created
    @render_widget
    def map():
        m = Map(
          basemap=basemaps.CartoDB.Positron, 
          center=(40.871157, -77.552356), 
          layout=Layout(height='750px'),
          zoom=6)  

        # Creating the PUMAs layer
        PUMAs = GeoJSON(
            data = state_choose("42"), 
            style = {
                "opacity": 1,  
                "dashArray": "1",  
                "fillOpacity": 0.80,  
                "weight": 1.0,  
            }, 
            hover_style={"color": "white", "dashArray": "0", "fillOpacity": 0.7}, 
            style_callback = em_borrow,     
        )

        # Creating the legend
        leg = LegendControl({"loww":"#e5baff", "mediumm":"#cf82ff", "Highh":"#ba4aff", "Highestt": "#9d00ff"}, title="Legend", position="bottomright")
        m.add(leg)

        # Adding a search bar to look for cities
        m.add(SearchControl(
            position="topleft",
            url='https://nominatim.openstreetmap.org/search?format=json&q={s}',
            zoom=5,
            ))

        # Adding the layer to the map
        m.add_layer(PUMAs) 
     
        return m  

    # This changes what variable is displayed on the map and relies on the dictionaries we created earlier, linking the 
    # function dictionaries and the radio dictionaries (from which users select an option)
    @reactive.effect
    def update_variable():
        map.widget.layers[1].style_callback =  funcdict[input.radio()][0][0]
        map.widget.controls[2].legend = funcdict[input.radio()][1]
        map.widget.controls[2].title = funcdict[input.radio()][2][0]

    # Similarly, this reactive effect changes which shapes (states) are being shown
    # It also changes the zoom level to assist seeing smaller states
    @reactive.effect
    def update_state():
        map.widget.layers[1].data = state_choose(statedict[input.select()]['fipscode'])
        map.widget.center = statedict[input.select()]['coordinates']
        q = statedict[input.select()]['fipscode']
        bigstates = [2, 6, 48]
        smallstates = [10, 11, 23, 24, 25, 33, 34, 36, 44, 50, 54]
        if q == -1:
            map.widget.zoom = 4
        elif q in bigstates:
            map.widget.zoom = 5
        elif q in smallstates:
            map.widget.zoom = 7
        else:
            map.widget.zoom = 6
    
    

app = App(app_ui, server)
