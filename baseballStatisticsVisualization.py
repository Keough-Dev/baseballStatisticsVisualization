# Import all of our necessary libraries

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from textwrap import dedent

# Defining app and reading in css code

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True

# Loading in all of our data and formatting it in order to be used to build
# our Dash visualization

people = pd.read_csv("/Users/CookedKaleDev/Downloads/\
baseballdatabank-2019.2/core/People.csv",
                     usecols = ["playerID","nameFirst","nameLast","weight",
                     "height","bats","throws","debut","finalGame"])

# creating dataframes for pitching, fielding and hitting individual
# statistics, merging them with our people dataset
# and dropping duplicates so that they can properly
# read into our Dash components

# Opted to format these 3 dataframes in the same way separately (instead
# of managing to keep it DRY) due to issues with the df merges persisting
# outside of functions scope

pitching = pd.read_csv("/Users/CookedKaleDev/Downloads/\
baseballdatabank-2019.2/core/Pitching.csv")
pitching = pd.merge(people, pitching, how='left', on='playerID')
pitching = pitching.drop_duplicates(subset = ["playerID" , "yearID"])
fielding = pd.read_csv("/Users/CookedKaleDev/Downloads/\
baseballdatabank-2019.2/core/Fielding.csv")
fielding = pd.merge(people, fielding, how='left', on='playerID')
fielding = fielding.drop_duplicates(subset = ["playerID" , "yearID"])
batting = pd.read_csv("/Users/CookedKaleDev/Downloads/\
baseballdatabank-2019.2/core/Batting.csv")
batting = pd.merge(people, batting, how='left', on='playerID')
batting = batting.drop_duplicates(subset = ["playerID" , "yearID"])

# creating a batting average column using the hits and at bats columns,
# rounding it to 2 decimal places

batting["BA"] = np.round(((batting["H"] / batting["AB"]) * 1000) , 2)

# hall of fame and all star categories will be used for annotations to
# differentiate players in Dash application

hallofFame = pd.read_csv("/Users/CookedKaleDev/Downloads/\
baseballdatabank-2019.2/core/HallOfFame.csv")
all_stars = pd.read_csv("/Users/CookedKaleDev/Downloads/\
baseballdatabank-2019.2/core/AllstarFull.csv")

# awards dataframe will be used to color code individual graphics to show
# seasons in which players won awards
# only MVP, silver slugger, gold glove, and cy young will be used so these
# are extracted from the dataset

Awards_Players = pd.read_csv("/Users/CookedKaleDev/Downloads/\
baseballdatabank-2019.2/core/AwardsPlayers.csv")
Awards_Players = Awards_Players[
(Awards_Players["awardID"] == "Most Valuable Player") |
(Awards_Players["awardID"] == "Silver Slugger") |
(Awards_Players["awardID"] == "Gold Glove") |
(Awards_Players["awardID"] == "Cy Young Award")]

# teams will be read in and an attendance column
# (in hundreds of thousands) will be created
# franchises file will be used to differentiate
# between active and inactive franchises

teams = pd.read_csv("/Users/CookedKaleDev/Downloads/\
baseballdatabank-2019.2/core/Teams.csv")
teams["attendance"] = teams["attendance"] / 100000
franchises = pd.read_csv("/Users/CookedKaleDev/Downloads/\
baseballdatabank-2019.2/core/TeamsFranchises.csv")
franchises = teams.merge(franchises, on = 'franchID', how = 'inner')
franchises = franchises[franchises['active'] == 'Y']

# leagues file will be used to create pivot tables where
# stats can be aggregated and Output
# all categories except for ERA will be aggregated by sum, ERA will be by mean

leagues = teams[((teams["lgID"] == "AL") | (teams["lgID"] == "NL")) &
(teams["yearID"] >= 1901)]
leagues_pivot = leagues.pivot_table(
index = ["yearID"],columns=['lgID'],aggfunc= sum)
leagues_pivot = leagues_pivot.drop(["ERA"], axis = 1)
leagues_pivot_era_temp = leagues.pivot_table(
index = ["yearID"],columns=['lgID'],values = ["ERA"], aggfunc= 'mean')
leagues_pivot = leagues_pivot.join(leagues_pivot_era_temp)

# Manipulating data and utilizing list comprehensions in order to produce
# long lists in proper format to be used for
# Dash dropdown core components

batting_drop = batting.dropna(subset=[
'teamID' , 'playerID' , 'nameFirst', 'nameLast'])
batting_list = [dict((('label' , ((batting_drop["nameLast"].iloc[i]) + "," +
(batting_drop["nameFirst"].iloc[i]) + "(" +
(batting_drop["teamID"].iloc[i]) + ")" )) ,
('value' ,
(batting_drop["playerID"].iloc[i])))) for i in range(len(batting_drop))]

pitching_drop = pitching.dropna(subset=[
'teamID' , 'playerID' , 'nameFirst', 'nameLast'])
pitching_list = [dict((('label' , ((pitching_drop["nameLast"].iloc[i]) + "," +
(pitching_drop["nameFirst"].iloc[i]) + "(" +
(pitching_drop["teamID"].iloc[i]) + ")" )) ,
('value' ,
(pitching_drop["playerID"].iloc[i])))) for i in range(len(pitching_drop))]

teams_drop = teams.drop_duplicates(subset=['teamID' , 'name'])
team_list = [dict((('label' , teams_drop['name'].iloc[i]) ,
('value' , teams_drop['teamID'].iloc[i]))) for i in range(len(teams_drop))]


# Defining all of our Dash core components (DCC)


Footnote = dcc.Markdown(dedent('''
                        _* - Denotes Hall of Fame Inductee_


                        *(#) - Number of All Star Game Appearances*


Data Source - [Lahman's Baseball Database](http://www.seanlahman.com/\
baseball-archive/statistics/)
                                '''), style = {"text-align" : "center"})

Footnote_Team = dcc.Markdown(dedent('''
                        _* - Denotes Active Franchise_


                        *(#) - Number of World Series Wins*


Data Source - [Lahman's Baseball Database](http://www.seanlahman.com/\
baseball-archive/statistics/)
                                       '''), style = {"text-align" : "center"})

Footnote_League = dcc.Markdown(dedent('''
Data Source - [Lahman's Baseball Database](http://www.seanlahman.com/\
baseball-archive/statistics/)
                                       '''), style = {"text-align" : "center"})

Stats_Graph_Bat = dcc.Graph(id="STATS_GRAPH_BAT")

Stats_Graph_Pitch = dcc.Graph(id="STATS_GRAPH_PITCH")

Stats_Graph_Field = dcc.Graph(id="STATS_GRAPH_FIELD")

Stats_Graph_Bat_Team = dcc.Graph(id="STATS_GRAPH_BAT_TEAM")

Stats_Graph_Pitch_Team = dcc.Graph(id="STATS_GRAPH_PITCH_TEAM")

Stats_Graph_Field_Team = dcc.Graph(id="STATS_GRAPH_FIELD_TEAM")

Stats_Graph_Bat_League = dcc.Graph(id="STATS_GRAPH_BAT_LEAGUE")

Stats_Graph_Pitch_League = dcc.Graph(id="STATS_GRAPH_PITCH_LEAGUE")

Stats_Graph_Field_League = dcc.Graph(id="STATS_GRAPH_FIELD_LEAGUE")

Tabs_Main = dcc.Tabs(id="TABS_MAIN", value='tab-player', children=[
                dcc.Tab(label='Individual Player Stats', value='tab-player'),
                dcc.Tab(label='Team Stats', value='tab-team'),
                dcc.Tab(label='League Stats', value='tab-league')
                                                                 ]
                    )

Tabs = dcc.Tabs(id="TABS", value='tab-bat', children=[
                dcc.Tab(label='Batting Stats', value='tab-bat'),
                dcc.Tab(label='Pitching Stats', value='tab-pitch'),
                dcc.Tab(label='Fielding Stats', value='tab-field')
                                                     ]
                )

Tabs_Team = dcc.Tabs(id="TABS_TEAM", value='tab-bat-team', children=[
                    dcc.Tab(label='Batting Stats', value='tab-bat-team'),
                    dcc.Tab(label='Pitching Stats', value='tab-pitch-team'),
                    dcc.Tab(label='Fielding Stats', value='tab-field-team')
                                                                     ]
                    )

Tabs_League = dcc.Tabs(id="TABS_LEAGUE", value='tab-bat-league', children=[
                      dcc.Tab(label='Batting Stats', value='tab-bat-league'),
                      dcc.Tab(label='Pitching Stats', value='tab-pitch-league'),
                      dcc.Tab(label='Fielding Stats', value='tab-field-league')
                                                                         ]
                       )

Batting_Stats_Dropdown = dcc.Dropdown(
                           id = "DROPDOWN_STATS",
                           options = [

                       {'label': "Runs", 'value': "R"},
                       {'label': "Doubles", 'value': "2B"},
                       {'label': "Triples", 'value': "3B"},
                       {'label': "Homeruns", 'value': "HR"},
                       {'label': "RBIs", 'value': "RBI"},
                       {'label': "Stolen Bases", 'value': "SB"},
                       {'label': "Batting Average", 'value': "BA"},
                       {'label': "Caught Stealing", 'value': "CS"},
                       {'label': "Walks", 'value': "BB"},
                       {'label': "Strike Outs", 'value': "SO"},
                       {'label': "Intentional Walks", 'value': "IBB"},
                       {'label': "Hit By Pitch", 'value': "HBP"},
                       {'label': "Grounded in to Double Play", 'value': "GIDP"},
                       {'label': "Sacrifice Hits", 'value': "SH"},
                       {'label': "Sacrifice Flies", 'value': "SF"}

                                       ],
                            value = "HR"
                                      )

Batting_Stats_Dropdown_Team = dcc.Dropdown(
                               id = "DROPDOWN_STATS_TEAM",
                               options = [

                               {'label': "Runs", 'value': "R"},
                               {'label': "Doubles", 'value': "2B"},
                               {'label': "Triples", 'value': "3B"},
                               {'label': "Homeruns", 'value': "HR"},
                               {'label': "Hits", 'value': "H"},
                               {'label': "Stolen Bases", 'value': "SB"},
                               {'label': "At Bats", 'value': "AB"},
                               {'label': "Caught Stealing", 'value': "CS"},
                               {'label': "Walks", 'value': "BB"},
                               {'label': "Strike Outs", 'value': "SO"},
                               {'label': "Hit By Pitch", 'value': "HBP"},
                               {'label': "Sacrifice Flies", 'value': "SF"},
                               {'label': "Team Wins" , 'value': "W"}

                                           ],
                                value = "HR"
                                          )


Pitching_Stats_Dropdown = dcc.Dropdown(
                               id = "DROPDOWN_STATS_PITCH",
                               options = [

                        {'label': "Wins", 'value': "W"},
                        {'label': "Losses", 'value': "L"},
                        {'label': "Games", 'value': "G"},
                        {'label': "Games Started", 'value': "GS"},
                        {'label': "Complete Games", 'value': "CG"},
                        {'label': "Shutouts", 'value': "SHO"},
                        {'label': "Saves", 'value': "SV"},
                        {'label': "Earned Runs", 'value': "ER"},
                        {'label': "Home Runs Allowed", 'value': "HR"},
                        {'label': "Strike Outs", 'value': "SO"},
                        {'label': "Walks", 'value': "BB"},
                        {'label': "Opponent Batting Average", 'value': "BAOpp"},
                        {'label': "Earned Run Average", 'value': "ERA"},
                        {'label': "Runs Allowed", 'value': "R"},
                        {'label': "Balks", 'value': "BK"}

                                          ],
                               value = "ERA"
                                         )

Pitching_Stats_Dropdown_Team = dcc.Dropdown(
                               id = "DROPDOWN_STATS_PITCH_TEAM",
                               options = [

                               {'label': "Complete Games", 'value': "CG"},
                               {'label': "Shutouts", 'value': "SHO"},
                               {'label': "Saves", 'value': "SV"},
                               {'label': "Earned Runs", 'value': "ER"},
                               {'label': "Home Runs Allowed", 'value': "HRA"},
                               {'label': "Strike Outs", 'value': "SOA"},
                               {'label': "Walks", 'value': "BBA"},
                               {'label': "Runs Allowed", 'value': "RA"},
                               {'label': "Earned Run Average", 'value': "ERA"},
                               {'label': "Hits Allowed", 'value': "HA"},
                               {'label': "Team Wins" , 'value': "W"}

                                          ],
                               value = "RA"
                                         )

Fielding_Stats_Dropdown = dcc.Dropdown(
                               id = "DROPDOWN_STATS_FIELD",
                               options = [

                        {'label': "Putouts", 'value': "PO"},
                        {'label': "Assists", 'value': "A"},
                        {'label': "Double Plays", 'value': "DP"},
                        {'label': "Errors", 'value': "E"},
                        {'label': "Passed Balls (for catchers)", 'value': "PB"},
                        {'label': "Wild Pitches (for catchers)", 'value': "WP"},
                        {'label': "Opponents Caught Stealing (for catchers)",
                        'value': "CS"},
                        {'label': "Opponent Stolen Bases (for catchers)",
                        'value': "SB"}

                                          ],
                               value = "E"
                                         )


Fielding_Stats_Dropdown_Team = dcc.Dropdown(
                                id = "DROPDOWN_STATS_FIELD_TEAM",
                                options = [

                               {'label': "Errors", 'value': "E"},
                               {'label': "Double Play", 'value': "DP"},
                               {'label': "Team Wins" , 'value': "W"}

                                          ],
                                value = "E"
                                         )

Team_Stats_Dropdown = dcc.Dropdown(
                                id = "DROPDOWN_TEAM_STATS",
                                options = [

                               {'label': "Wins", 'value': "W"},
                               {'label': "Attendance (in Hundreds of Thousands)",
                               'value': "attendance"}

                                          ],
                                value = "W"
                                         )



rangeslider_year_league = dcc.RangeSlider(
                                id="RANGESLIDER_YEAR_LEAGUE",
                                marks = {1910 : {'label': '1910',
                                         'style':{'color':'white'}},
                                         1920 : {'label': '1920',
                                         'style':{'color':'white'}},
                                         1930 : {'label': '1930',
                                         'style':{'color':'white'}},
                                         1940 : {'label': '1940',
                                         'style':{'color':'white'}},
                                         1950 : {'label': '1950',
                                         'style':{'color':'white'}},
                                         1960 : {'label': '1960',
                                         'style':{'color':'white'}},
                                         1970 : {'label': '1970',
                                         'style':{'color':'white'}},
                                         1980 : {'label': '1980',
                                         'style':{'color':'white'}},
                                         1990 : {'label': '1990',
                                         'style':{'color':'white'}},
                                         2000 : {'label': '2000',
                                         'style':{'color':'white'}},
                                         2010 : {'label': '2010',
                                         'style':{'color':'white'}},
                                         },
                                min   = leagues_pivot.index.min(),
                                max   = leagues_pivot.index.max(),
                                step  = 1,
                                value = [ leagues_pivot.index.min() ,
                                          leagues_pivot.index.max() ]
                               )

player_dropdown = dcc.Dropdown(
                                 id = "DROPDOWN_PLAYER",
                                 options = batting_list,
                                 value = "mauerjo01",
                               )


player_dropdown_pitchers = dcc.Dropdown(
                                 id = "DROPDOWN_PLAYER_PITCH",
                                 options = pitching_list,
                                 value = "clemero02"
                               )


teams_dropdown = dcc.Dropdown(
                       id = "DROPDOWN_TEAM",
                       options = team_list,
                       value = "MIN"
                              )


league_dropdown = dcc.Dropdown(
                        id = "DROPDOWN_LEAGUE",
                        options = [

                           {'label': "National League", 'value': "NL"},
                           {'label': "American League", 'value': "AL"},
                           {'label': "Both Leagues", 'value': "Both"},

                                  ],
                        value = "Both"
                                 )

# Building the app layout

app.layout = html.Div(

                  style={'backgroundColor': 'black'},
                  children=[

                  html.H1('Baseball Statistics Visualization Database',
                  style = {"text-align" : "center" ,
                  'color' : 'white', 'font' : 'Cursive'},),

                  html.Div([Tabs_Main], style = {'color' : 'black'},),
                  html.Div(id="TABS_DISPLAY_MAIN"),


                       ])

# Setting up app callbacks

# call back for which main tab is selected (players, teams, or leagues)
# and returning that tab's content and layout

@app.callback(Output('TABS_DISPLAY_MAIN', 'children'),
              [Input('TABS_MAIN', 'value')])
def render_content(tab_main):
    if tab_main == 'tab-player':
        return    html.Div([
                  html.Div([Tabs]),
                  html.Div(id="TABS_DISPLAY"),
                          ])
    elif tab_main == 'tab-team':
         return   html.Div([
                  html.Div([Tabs_Team]),
                  #html.Div([Active_Check]),
                  html.Div(id="TABS_DISPLAY_TEAM"),
                           ])
    elif tab_main == 'tab-league':
         return   html.Div([
                  html.Div([Tabs_League]),
                  html.Div(id="TABS_DISPLAY_LEAGUE"),
                           ])

# Callbacks for individual players

# return tab contents for individual players based on whether batting,
# pitching, or fielding is selected
# returing the player dropdown, stats dropdown, and corresponding graph

@app.callback(Output('TABS_DISPLAY', 'children'),
              [Input('TABS', 'value')])
def render_content(tab):
    if tab == 'tab-bat':
        return html.Div([
            html.H3('BATTING STATS', style = {"text-align" : "center" ,
            'color' : 'white', 'font' : 'Cursive'},),
            html.Div([player_dropdown],id="DROP_DOWN_ONE"),
            html.Div([Batting_Stats_Dropdown],id="DROP_DOWN_TWO"),
            html.Div([
                  Stats_Graph_Bat
                  ], style={'marginTop': 25},
                     id="GRAPH_CONTAINER_BAT"),
            html.Div([Footnote], style = {"text-align" : "center" ,
            'color' : 'white'}, id="FOOTNOTE"),
        ])
    elif tab == 'tab-pitch':
        return html.Div([
            html.H3('PITCHING STATS', style = {"text-align" : "center" ,
            'color' : 'white', 'font' : 'Cursive'},),
            html.Div([player_dropdown_pitchers],id="DROP_DOWN_FIVE"),
            html.Div([Pitching_Stats_Dropdown],id="DROP_DOWN_THREE"),
            html.Div([
                  Stats_Graph_Pitch
                  ], style={'marginTop': 25},
                     id="GRAPH_CONTAINER_PITCH"),
            html.Div([Footnote], style = {"text-align" : "center" ,
            'color' : 'white'}, id="FOOTNOTE"),
        ])
    elif tab == 'tab-field':
        return html.Div([
            html.H3('FIELDING STATS', style = {"text-align" : "center" ,
            'color' : 'white', 'font' : 'Cursive'},),
            html.Div([player_dropdown],id="DROP_DOWN_ONE"),
            html.Div([Fielding_Stats_Dropdown],id="DROP_DOWN_FOUR"),
            html.Div([
                  Stats_Graph_Field
                  ], style={'marginTop': 25},
                     id="GRAPH_CONTAINER_FIELD"),
            html.Div([Footnote], style = {"text-align" : "center" ,
            'color' : 'white'}, id="FOOTNOTE"),
        ])

# Callbacks for individual batting stats

# return either the batting, pitching, or fielding graph and update these graphs
# based on changes
# to the website's input, reading in the player and stat selected

@app.callback(Output("STATS_GRAPH_BAT", "figure"),
              [Input("DROPDOWN_PLAYER", "value"),
               Input("DROPDOWN_STATS", "value")
               ])

def when_triggers_update_graph(
    Playerid,
    Stat
):


# create empty lists so that season stats can be read in based on whether or not
# a player won an award that year
# and color code the reulting bar graph (award season bars are displayed
# slightly off center so that MVP seasons
# can be displayed alongside other awards won in that season)
# if statement in place to account for missing years in which a player did not
# play, appending a 0 for that year

    SSx = []
    SSy = []
    MVPx = []
    MVPy = []
    Otherx = []
    Othery = []

    for i in range(int(batting[(batting["playerID"] == Playerid)].yearID.min())
    , int(batting[(batting["playerID"] == Playerid)].yearID.max()) + 1):

        if i not in batting[batting["playerID"] == Playerid].yearID.unique():
              Othery.append(0)
              Otherx.append(i)
        elif i not in np.array(Awards_Players[(Awards_Players["playerID"] ==
        Playerid) & ((Awards_Players["awardID"] == "Most Valuable Player")
              | (Awards_Players["awardID"] == "Silver Slugger"))].yearID):
              Othery.append(batting.loc[(batting["playerID"] == Playerid) &
              (batting["yearID"] == i) , Stat].item())
              Otherx.append(i)
        if i in np.array(Awards_Players[(Awards_Players["playerID"] == Playerid)
        & (Awards_Players["awardID"] == "Silver Slugger")].yearID):
              SSy.append((batting.loc[(batting["playerID"] == Playerid) &
              (batting["yearID"] == i) , Stat]).item())
              SSx.append(i)
        if i in np.array(Awards_Players[(Awards_Players["playerID"] == Playerid)
        & (Awards_Players["awardID"] == "Most Valuable Player")].yearID):
              MVPy.append((batting.loc[(batting["playerID"] == Playerid) &
              (batting["yearID"] == i) , Stat]).item())
              MVPx.append(i)


    return  go.Figure(
             data = [
             go.Bar(

               x = Otherx,
               y = Othery,
               marker =dict(color= 'rgb(040,140,210)'),
               name = "Season Stat",
               width = [.7]*len(Otherx),
               offset = [-0.35]*len(Otherx),
                   ),

              go.Bar(

               x  = SSx,
               y  = SSy,
               marker =dict(color= 'rgb(150,160,160)'),
               name = "Silver Slugger Season",
               width = [.7]*len(Otherx),
               offset = [-0.375]*len(Otherx),
                    ),

               go.Bar(

               x  = MVPx,
               y  = MVPy,
               marker =dict(color= 'rgb(220,060,050)'),
               name = "MVP Season",
               width = [.6]*len(MVPx),
               offset = [-.125]*len(MVPx),
                    )


                    ],

               layout = go.Layout(
               title  = '<b>{} <b>{} {HOF} ({})</b><br>{}'.format(
               people[people["playerID"] == Playerid].nameFirst.item(),people[
               people["playerID"] == Playerid].nameLast.item(), Stat,
               all_stars[all_stars["playerID"] == Playerid].playerID.count(),
               HOF = '*' if any(hallofFame[hallofFame["inducted"] ==
               "Y"].playerID == Playerid) else ''),
               xaxis={'tickformat': 'd',
               'tickmode' : 'linear',
               'title' : '<b>{}'.format('Year')},
               yaxis={
               'title' : '<b>{}'.format(Stat)}
               )

                      )

# Callbacks for individual pitching stats

@app.callback(Output("STATS_GRAPH_PITCH", "figure"),
              [Input("DROPDOWN_PLAYER_PITCH", "value"),
               Input("DROPDOWN_STATS_PITCH", "value")
               ])

def when_triggers_update_graph(
    Playerid,
    Stat
):

    CYx = []
    CYy = []
    MVPx = []
    MVPy = []
    Otherx = []
    Othery = []

    for i in range(int(pitching[(pitching["playerID"] == Playerid)].yearID.min()
    ) , int(pitching[(pitching["playerID"] == Playerid)].yearID.max()) + 1):

        if i not in pitching[pitching["playerID"] == Playerid].yearID.unique():
            Othery.append(0)
            Otherx.append(i)
        elif i not in np.array(Awards_Players[(Awards_Players["playerID"] ==
        Playerid) & ((Awards_Players["awardID"] == "Most Valuable Player")
            | (Awards_Players["awardID"] == "Cy Young Award"))].yearID):
              Othery.append((pitching.loc[(pitching["playerID"] == Playerid) &
              (pitching["yearID"] == i) , Stat]).item())
              Otherx.append(i)
        if i in np.array(Awards_Players[(Awards_Players["playerID"] == Playerid)
        & (Awards_Players["awardID"] == "Cy Young Award")].yearID):
              CYy.append((pitching.loc[(pitching["playerID"] == Playerid) &
              (pitching["yearID"] == i) , Stat]).item())
              CYx.append(i)
        if i in np.array(Awards_Players[(Awards_Players["playerID"] == Playerid)
        & (Awards_Players["awardID"] == "Most Valuable Player")].yearID):
              MVPy.append((pitching.loc[(pitching["playerID"] == Playerid) &
              (pitching["yearID"] == i) , Stat]).item())
              MVPx.append(i)

    return  go.Figure(
             data = [

             go.Bar(

               x  = Otherx,
               y  = Othery,
               marker =dict(color= 'rgb(040,140,210)'),
               name = "Season Stat",
               width = [.7]*len(Otherx),
               offset = [-.35]*len(Otherx),
                   ),

              go.Bar(

               x  = CYx,
               y  = CYy,
               marker =dict(color= 'rgb(000,170,017)'),
               name = "Cy Young Season",
               width = [.7]*len(CYx),
               offset = [-.375]*len(CYx),
                    ),

               go.Bar(

               x  = MVPx,
               y  = MVPy,
               marker =dict(color= 'rgb(220,060,050)'),
               name = "MVP Season",
               width = [.6]*len(MVPx),
               offset = [-.125]*len(MVPx),
                    )


                    ],

               layout = go.Layout(
               title  = '<b>{} <b>{} {HOF} ({})</b><br>{}'.format(
               people[people["playerID"] == Playerid].nameFirst.item(),people[
               people["playerID"] == Playerid].nameLast.item(), Stat,
               all_stars[all_stars["playerID"] == Playerid].playerID.count(),
               HOF = '*' if any(hallofFame[hallofFame["inducted"] ==
               "Y"].playerID == Playerid) else ''),
               xaxis={'tickformat': 'd',
               'tickmode' : 'linear',
               'title' : '<b>{}'.format('Year')},
               yaxis={
               'title' : '<b>{}'.format(Stat)}
               )

                      )

# Callbacks for individual fielding stats

@app.callback(Output("STATS_GRAPH_FIELD", "figure"),
              [Input("DROPDOWN_PLAYER", "value"),
               Input("DROPDOWN_STATS_FIELD", "value")
               ])

def when_triggers_update_graph(
    Playerid,
    Stat
):

    GGx = []
    GGy = []
    MVPx = []
    MVPy = []
    Otherx = []
    Othery = []

    for i in range(int(fielding[(fielding["playerID"] == Playerid)].yearID.min()
    ) , int(fielding[(fielding["playerID"] == Playerid)].yearID.max()) + 1):

        if i not in fielding[fielding["playerID"] == Playerid].yearID.unique():
              Othery.append(0)
              Otherx.append(i)
        elif i not in np.array(Awards_Players[(Awards_Players["playerID"] ==
        Playerid) & ((Awards_Players["awardID"] == "Most Valuable Player")
              | (Awards_Players["awardID"] == "Gold Glove"))].yearID):
              Othery.append((fielding.loc[(fielding["playerID"] == Playerid) &
              (fielding["yearID"] == i) , Stat]).item())
              Otherx.append(i)
        if i in np.array(Awards_Players[(Awards_Players["playerID"] == Playerid)
        & (Awards_Players["awardID"] == "Gold Glove")].yearID):
              GGy.append((fielding.loc[(fielding["playerID"] == Playerid) &
              (fielding["yearID"] == i) , Stat]).item())
              GGx.append(i)
        if i in np.array(Awards_Players[(Awards_Players["playerID"] == Playerid)
        & (Awards_Players["awardID"] == "Most Valuable Player")].yearID):
              MVPy.append((fielding.loc[(fielding["playerID"] == Playerid) &
              (fielding["yearID"] == i) , Stat]).item())
              MVPx.append(i)

    return  go.Figure(
               data = [
               go.Bar(

               x = Otherx,
               y = Othery,
               marker =dict(color= 'rgb(040,140,210)'),
               name = "Season Stat",
               width = [.7]*len(Otherx),
               offset = [-.35]*len(Otherx),
                   ),

              go.Bar(

               x  = GGx,
               y  = GGy,
               marker =dict(color= 'rgb(140,140,005)'),
               name = "Gold Glove Season",
               width = [.7]*len(GGx),
               offset = [-.375]*len(GGx),
                    ),

               go.Bar(

               x  = MVPx,
               y  = MVPy,
               marker =dict(color= 'rgb(220,060,050)'),
               name = "MVP Season",
               width = [.6]*len(MVPx),
               offset = [-.125]*len(MVPx),
                    )


                    ],

               layout = go.Layout(
               title  = '<b>{} <b>{} {HOF} ({}) </b><br>{}'.format(
               people[people["playerID"] == Playerid].nameFirst.item(),people[
               people["playerID"] == Playerid].nameLast.item(),
               all_stars[all_stars["playerID"] == Playerid].playerID.count(),
               Stat, HOF = '*' if any(hallofFame[hallofFame["inducted"] ==
               "Y"].playerID == Playerid) else ''),
               xaxis={'tickformat': 'd',
               'tickmode' : 'linear',
               'title' : '<b>{}'.format('Year')},
               yaxis={
               'title' : '<b>{}'.format(Stat)}
               )

                      )

# Callbacks for team stats

# returning tab contents based on whether team hitting, pitching,
# or fielding tab is selected
# return all of our Dash divs and the corresponding graph

@app.callback(Output('TABS_DISPLAY_TEAM', 'children'),
              [Input('TABS_TEAM', 'value')])
def render_content(tab):

    if tab == 'tab-bat-team':
        return html.Div([
            html.H3('BATTING STATS', style = {"text-align" : "center" ,
            'color' : 'white', 'font' : 'Cursive'},),
            html.Div([teams_dropdown],id="DROP_DOWN_SIX"),
            html.Div([Batting_Stats_Dropdown_Team],id="DROP_DOWN_EIGHT"),
            html.Div([Team_Stats_Dropdown],id="DROPDOWN_TWELVE"),
            html.Div([
                  Stats_Graph_Bat_Team
                  ], style={'marginTop': 25},
                     id="GRAPH_CONTAINER_BAT_TEAM"),
            html.Div([Footnote_Team], style = {"text-align" : "center" ,
            'color' : 'white'}, id="FOOTNOTE_TWO"),
        ])

    elif tab == 'tab-pitch-team':
        return html.Div([
            html.H3('PITCHING STATS', style = {"text-align" : "center" ,
            'color' : 'white', 'font' : 'Cursive'},),
            html.Div([teams_dropdown],id="DROP_DOWN_SIX"),
            html.Div([Pitching_Stats_Dropdown_Team],id="DROP_DOWN_NINE"),
            html.Div([Team_Stats_Dropdown],id="DROPDOWN_TWELVE"),
            html.Div([
                  Stats_Graph_Pitch_Team
                  ], style={'marginTop': 25},
                     id="GRAPH_CONTAINER_PITCH_TEAM"),
            html.Div([Footnote_Team], style = {"text-align" : "center" ,
            'color' : 'white'}, id="FOOTNOTE_TWO"),
        ])

    elif tab == 'tab-field-team':
        return html.Div([
            html.H3('FIELDING STATS', style = {"text-align" : "center" ,
            'color' : 'white', 'font' : 'Cursive'},),
            html.Div([teams_dropdown],id="DROP_DOWN_SIX"),
            html.Div([Fielding_Stats_Dropdown_Team],id="DROP_DOWN_TEN"),
            html.Div([Team_Stats_Dropdown],id="DROPDOWN_TWELVE"),
            html.Div([
                  Stats_Graph_Field_Team
                  ], style={'marginTop': 25},
                     id="GRAPH_CONTAINER_FIELD_TEAM"),
            html.Div([Footnote_Team], style = {"text-align" : "center" ,
            'color' : 'white'}, id="FOOTNOTE_TWO"),
        ])

# Callbacks for team hitting stats

# Read in the team selected, and the two stats selected and output the
# corresponding graph

@app.callback(Output("STATS_GRAPH_BAT_TEAM", "figure"),
              [Input("DROPDOWN_TEAM", "value"),
               Input("DROPDOWN_STATS_TEAM", "value"),
               Input("DROPDOWN_TEAM_STATS", "value")
               ])

def when_triggers_update_graph(
    Teamname,
    Stat,
    Stat2
):
             return  go.Figure(
             data = [
             go.Bar(

               x  = list(range(teams[teams['teamID'] == Teamname].yearID.min() ,
               teams[teams['teamID'] == Teamname].yearID.max() + 1)),
               y  = (teams.loc[((teams["teamID"] == Teamname) & (
               teams["yearID"] >= teams["yearID"].min()) &
               (teams["yearID"] <= teams["yearID"].max())) , Stat]),
               name = Stat,
               marker =dict(color= 'rgb(040,140,210)'),
                   ),
             go.Bar(

               x  = list(range(teams[teams['teamID'] == Teamname].yearID.min() ,
               teams[teams['teamID'] == Teamname].yearID.max() + 1)),
               y  = (teams.loc[((teams["teamID"] == Teamname) & (
               teams["yearID"] >= teams["yearID"].min()) &
               (teams["yearID"] <= teams["yearID"].max())) , Stat2]),
               name = Stat2,
               marker =dict(color= 'rgb(220,060,050)'),
                   )
                    ],
               layout = go.Layout(
               title  = '<b>{} {ACT} (<b>{}) </b><br>{} vs {}'.format(
               Teamname,
               teams[(teams["teamID"] == Teamname) &
               (teams["WSWin"] == "Y")].yearID.count(), Stat, Stat2,
               ACT = '*' if Teamname in franchises.franchName.unique()
               else ''),
               xaxis={'tickformat': 'd',
               'tickmode' : 'linear',
               'title' : '<b>{}'.format('Year')},
               yaxis={
               'title' : '<b>{}'.format('Values')}
               )

                      )


# Callbacks for team pitching stats

@app.callback(Output("STATS_GRAPH_PITCH_TEAM", "figure"),
              [Input("DROPDOWN_TEAM", "value"),
               Input("DROPDOWN_STATS_PITCH_TEAM", "value"),
               Input("DROPDOWN_TEAM_STATS", "value")
               ])

def when_triggers_update_graph(
    Teamname,
    Stat,
    Stat2
):

             return  go.Figure(
             data = [
             go.Bar(

               x  = list(range(teams[teams['teamID'] == Teamname].yearID.min() ,
               teams[teams['teamID'] == Teamname].yearID.max() + 1)),
               y  = (teams.loc[((teams["teamID"] == Teamname) &
               (teams["yearID"] >= teams["yearID"].min()) &
               (teams["yearID"] <= teams["yearID"].max())) , Stat]),
               name = Stat,
               marker =dict(color= 'rgb(040,140,210)'),
                   ),
             go.Bar(

               x  = list(range(teams[teams['teamID'] == Teamname].yearID.min() ,
               teams[teams['teamID'] == Teamname].yearID.max() + 1)),
               y  = (teams.loc[((teams["teamID"] == Teamname) &
               (teams["yearID"] >= teams["yearID"].min()) &
               (teams["yearID"] <= teams["yearID"].max())) , Stat2]),
               name = Stat2,
               marker =dict(color= 'rgb(220,060,050)'),
                   )
                     ],
               layout = go.Layout(
               title  = '<b>{} {ACT} (<b>{}) </b><br>{} vs {}'.format(
               Teamname,
               teams[(teams["teamID"] == Teamname) &
               (teams["WSWin"] == "Y")].yearID.count(), Stat, Stat2,
               ACT = '*' if Teamname in franchises.franchName.unique()
               else ''),
               xaxis={'tickformat': 'd',
               'tickmode' : 'linear',
               'title' : '<b>{}'.format('Year')},
               yaxis={
               'title' : '<b>{}'.format(Stat)}
               )

                      )

# Callbacks for team fielding stats

@app.callback(Output("STATS_GRAPH_FIELD_TEAM", "figure"),
              [Input("DROPDOWN_TEAM", "value"),
               Input("DROPDOWN_STATS_FIELD_TEAM", "value"),
               Input("DROPDOWN_TEAM_STATS", "value")
               ])

def when_triggers_update_graph(
    Teamname,
    Stat,
    Stat2
):

             return  go.Figure(
             data = [
             go.Bar(

               x  = list(range(teams[teams['teamID'] == Teamname].yearID.min() ,
               teams[teams['teamID'] == Teamname].yearID.max() + 1)),
               y  = (teams.loc[((teams["teamID"] == Teamname) & (
               teams["yearID"] >= teams["yearID"].min()) &
               (teams["yearID"] <= teams["yearID"].max())) , Stat]),
               name = Stat,
               marker =dict(color= 'rgb(040,140,210)'),
                   ),
             go.Bar(

               x  = list(range(teams[teams['teamID'] == Teamname].yearID.min() ,
               teams[teams['teamID'] == Teamname].yearID.max() + 1)),
               y  = (teams.loc[((teams["teamID"] == Teamname) & (
               teams["yearID"] >= teams["yearID"].min()) &
               (teams["yearID"] <= teams["yearID"].max())) , Stat2]),
               name = Stat2,
               marker =dict(color= 'rgb(220,060,050)'),
                   )
                     ],
               layout = go.Layout(
               title  = '<b>{} {ACT} (<b>{}) </b><br>{} vs {}'.format(
               Teamname,
               teams[(teams["teamID"] == Teamname) &
               (teams["WSWin"] == "Y")].yearID.count(), Stat, Stat2,
               ACT = '*' if Teamname in franchises.franchName.unique()
               else ''),
               xaxis={'tickformat': 'd',
               'tickmode' : 'linear',
               'title' : '<b>{}'.format('Year')},
               yaxis={
               'title' : '<b>{}'.format(Stat)}
               )

                      )


# Callbacks for league stats

# display appropriate tabs for whether league hitting, pitching,
# or fielding tab is selected, including
# rangeslider to select different time frames to be displayed by the graph

@app.callback(Output('TABS_DISPLAY_LEAGUE', 'children'),
              [Input('TABS_LEAGUE', 'value')])
def render_content(tab):
    if tab == 'tab-bat-league':
        return html.Div([
            html.H3('BATTING STATS', style = {"text-align" : "center" ,
            'color' : 'white', 'font' : 'Cursive'},),
            html.Div([league_dropdown],id="DROP_DOWN_SEVEN"),
            html.Div([Batting_Stats_Dropdown_Team],id="DROP_DOWN_EIGHT"),
            html.Div([rangeslider_year_league],id="SLIDER_FOUR"),
            html.Div([
                  Stats_Graph_Bat_League
                  ], style={'marginTop': 35},
                     id="GRAPH_CONTAINER_BAT_LEAGUE"),
            html.Div([Footnote_League], style = {"text-align" : "center" ,
            'color' : 'white'}, id="FOOTNOTE_THREE"),
        ])
    elif tab == 'tab-pitch-league':
        return html.Div([
            html.H3('PITCHING STATS', style = {"text-align" : "center" ,
            'color' : 'white', 'font' : 'Cursive'},),
            html.Div([league_dropdown],id="DROP_DOWN_SEVEN"),
            html.Div([Pitching_Stats_Dropdown_Team],id="DROP_DOWN_NINE"),
            html.Div([rangeslider_year_league],id="SLIDER_FOUR"),
            html.Div([
                  Stats_Graph_Pitch_League
                  ], style={'marginTop': 35},
                     id="GRAPH_CONTAINER_PITCH_LEAGUE"),
            html.Div([Footnote_League], style = {"text-align" : "center" ,
            'color' : 'white'}, id="FOOTNOTE_THREE"),
        ])
    elif tab == 'tab-field-league':
        return html.Div([
            html.H3('FIELDING STATS', style = {"text-align" : "center" ,
            'color' : 'white', 'font' : 'Cursive'},),
            html.Div([league_dropdown],id="DROP_DOWN_SEVEN"),
            html.Div([Fielding_Stats_Dropdown_Team],id="DROP_DOWN_TEN"),
            html.Div([rangeslider_year_league],id="SLIDER_FOUR"),
            html.Div([
                  Stats_Graph_Field_League
                  ], style={'marginTop': 35},
                     id="GRAPH_CONTAINER_FIELD_LEAGUE"),
            html.Div([Footnote_League], style = {"text-align" : "center" ,
            'color' : 'white'}, id="FOOTNOTE_THREE"),
        ])

# Callbacks for league hitting

# Read in whether both leagues or one of the two specific
# leagues should be displayed,
# as well as the stat selected and the range of years input to the rangeslider,
# returning the corresponding graph

@app.callback(Output("STATS_GRAPH_BAT_LEAGUE", "figure"),
              [Input("DROPDOWN_LEAGUE", "value"),
               Input("DROPDOWN_STATS_TEAM", "value"),
               Input("RANGESLIDER_YEAR_LEAGUE", "value")
               ])

def when_triggers_update_graph(
    Lgname,
    Stat,
    Year
):
         if Lgname == "Both":

             return  go.Figure(
             data = [
             go.Bar(

               x  = list(range(Year[0] , Year[1])),
               y  = leagues_pivot[Stat]["AL"].loc[Year[0] : Year[1]],
               marker =dict(color= 'rgb(040,140,210)'),
               name = "American League",
                   ),
             go.Bar(

               x  = list(range(Year[0] , Year[1])),
               y  = leagues_pivot[Stat]["NL"].loc[Year[0] : Year[1]],
               marker =dict(color= 'rgb(220,060,050)'),
               name = "National League",
                   )
                     ],
               layout = go.Layout(
               title  = '<b>{} </b><br>{}'.format(
               'American League vs National League', Stat),
               xaxis={'tickformat': 'd',
               'tickmode' : 'linear',
               'title' : '<b>{}'.format('Year')},
               yaxis={
               'title' : '<b>{}'.format(Stat)}
               )

                      )

         else:

             return  go.Figure(
             data = [
             go.Bar(

               x  = list(range(Year[0] , Year[1])),
               y  = leagues_pivot[Stat][Lgname].loc[Year[0] : Year[1]],
                   )],
               layout = go.Layout(
               title  = '<b>{} </b><br>{}'.format(Lgname, Stat),
               xaxis={'tickformat': 'd',
               'tickmode' : 'linear',
               'title' : '<b>{}'.format('Year')},
               yaxis={
               'title' : '<b>{}'.format(Stat)}
               )

                      )

# Callbacks for league pitching

@app.callback(Output("STATS_GRAPH_PITCH_LEAGUE", "figure"),
              [Input("DROPDOWN_LEAGUE", "value"),
               Input("DROPDOWN_STATS_PITCH_TEAM", "value"),
               Input("RANGESLIDER_YEAR_LEAGUE", "value")
               ])

def when_triggers_update_graph(
    Lgname,
    Stat,
    Year
):

         if Lgname == "Both":

             return  go.Figure(
             data = [
              go.Bar(

               x  = list(range(Year[0] , Year[1])),
               y  = leagues_pivot[Stat]["AL"].loc[Year[0] : Year[1]],
               marker =dict(color= 'rgb(040,140,210)'),
               name = "American League",
                   ),
             go.Bar(

               x  = list(range(Year[0] , Year[1])),
               y  = leagues_pivot[Stat]["NL"].loc[Year[0] : Year[1]],
               marker =dict(color= 'rgb(220,060,050)'),
               name = "National League",
                   )

                    ],
               layout = go.Layout(
               title  = '<b>{} </b><br>{}'.format(
               'American League vs National League', Stat),
               xaxis={'tickformat': 'd',
               'tickmode' : 'linear',
               'title' : '<b>{}'.format('Year')},
               yaxis={
               'title' : '<b>{}'.format(Stat)}
               )

                      )

         else:

             return  go.Figure(
             data = [
             go.Bar(

               x  = list(range(Year[0] , Year[1])),
               y  = leagues_pivot[Stat][Lgname].loc[Year[0] : Year[1]],
                   )],
               layout = go.Layout(
               title  = '<b>{} </b><br>{}'.format(Lgname, Stat),
               xaxis={'tickformat': 'd',
               'tickmode' : 'linear',
               'title' : '<b>{}'.format('Year')},
               yaxis={
               'title' : '<b>{}'.format(Stat)}
               )

                      )

# Callbacks for league fielding


@app.callback(Output("STATS_GRAPH_FIELD_LEAGUE", "figure"),
              [Input("DROPDOWN_LEAGUE", "value"),
               Input("DROPDOWN_STATS_FIELD_TEAM", "value"),
               Input("RANGESLIDER_YEAR_LEAGUE", "value")
               ])

def when_triggers_update_graph(
    Lgname,
    Stat,
    Year
):

         if Lgname == "Both":

             return  go.Figure(
             data = [
              go.Bar(

               x  = list(range(Year[0] , Year[1])),
               y  = leagues_pivot[Stat]["AL"].loc[Year[0] : Year[1]],
               marker =dict(color= 'rgb(040,140,210)'),
               name = "American League",
                   ),
             go.Bar(

               x  = list(range(Year[0] , Year[1])),
               y  = leagues_pivot[Stat]["NL"].loc[Year[0] : Year[1]],
               marker =dict(color= 'rgb(220,060,050)'),
               name = "National League",
                   )

                    ],
               layout = go.Layout(
               title  = '<b>{} </b><br>{}'.format(
               'American League vs National League', Stat),
               xaxis={'tickformat': 'd',
               'tickmode' : 'linear',
               'title' : '<b>{}'.format('Year')},
               yaxis={
               'title' : '<b>{}'.format(Stat)}
               )

                      )

         else:

             return  go.Figure(
             data = [
             go.Bar(

               x  = list(range(Year[0] , Year[1])),
               y  = leagues_pivot[Stat][Lgname].loc[Year[0] : Year[1]],
                   )],
               layout = go.Layout(
               title  = '<b>{} </b><br>{}'.format(Lgname, Stat),
               xaxis={'tickformat': 'd',
               'tickmode' : 'linear',
               'title' : '<b>{}'.format('Year')},
               yaxis={
               'title' : '<b>{}'.format(Stat)}
               )

                      )

# Running the app

if __name__ == '__main__':
    app.run_server(debug=False)
