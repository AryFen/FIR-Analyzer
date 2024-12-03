import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import streamlit as st
import json

st.set_page_config(
    layout="wide",
)

st.markdown(
    r"""
    <style>
    .stAppViewBlockContainer {
            padding-top: 2rem;
            padding-left: -3rem;
        }
    </style>
    """, unsafe_allow_html=True
)

with open('counties.geojson') as f:
    counties = json.load(f)

for feature in counties['features']:
    feature['properties']['GEO_ID'] = feature['properties']['GEO_ID'][-5:].lstrip('0')

df = pd.read_csv('CurrentData.csv', dtype={"FIPS": str})
df = df[~(df == -1).any(axis=1)]

if 'year' not in st.session_state:
    st.session_state.year = 2021

if 'filter_criteria' not in st.session_state:
    st.session_state.filter_criteria = {}

if 'current_filter' not in st.session_state:
    st.session_state.current_filter = None

if 'show_filtered_map' not in st.session_state:
    st.session_state.show_filtered_map = False

if 'county_FIPS' not in st.session_state:
    st.session_state.county_FIPS = '1001'

if 'county_name' not in st.session_state:
    st.session_state.county_name = 'Autauga, Alabama'

def makeCompatible(buttonStr):
    if buttonStr == 'Food Insecurity Rate':
        return 'FIR'
    elif buttonStr == 'Income Per Capita':
        return 'IncomePerCapita'
    elif buttonStr == 'Unemployment Rate':
        return 'FinalUR'
    elif buttonStr == 'Year':
        return 'Year'
    else:
        return 'FinalCPM'

def applyChanges():
    st.session_state.show_filtered_map = True

    filtered_df = df[df['Year'] == 2021]
    for name, (min_val, max_val) in st.session_state.filter_criteria.items():
        filtered_df = filtered_df[(filtered_df[name] >= min_val) & (filtered_df[name] <= max_val)]
    
    fig_filtered = px.choropleth(
        filtered_df,
        geojson=counties,
        locations='FIPS',
        featureidkey="properties.GEO_ID",
        color_discrete_sequence=["orange"],
        scope="usa",
        hover_name='County',
        title=f"Map With Filters Applied (2021)"
    )
    fig_filtered.update_geos(showlakes=True, lakecolor='rgb(255, 255, 255)')
    fig_filtered.update_layout(
        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',
        title_font_color="salmon",
        font=dict(
            family="monospace",
            size=14,
            color="salmon"
        ),
        title_font_size=20,
        title_y=0.98, 
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        geo=dict(
            bgcolor="#0e1117",
            lakecolor='#0e1117',
            showlakes=True,
            showcoastlines=False,
            showland=True,
            landcolor='#0e1117',
        )
    )
    fig_filtered.update(layout_showlegend=False)
    
    return fig_filtered

if st.session_state.show_filtered_map:
    applyChanges()

def addFilter():
    name, value_range = st.session_state.current_filter
    if name not in st.session_state.filter_criteria:
        st.session_state.filter_criteria[name] = value_range

def Main():

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:

        year = st.slider(label="", min_value=2011, max_value=2021, value=st.session_state.year)

        st.session_state.year = year

        filtered_df = df[df['Year'] == st.session_state.year]

        if filtered_df.empty:
            st.warning("No data available for the selected year.")
            return

        fig = px.choropleth(
            filtered_df,
            geojson=counties,
            locations='FIPS',         
            color='FIR',              
            featureidkey="properties.GEO_ID",
            color_continuous_scale="YlOrRd",
            range_color=(0, 20),
            scope="usa",
            hover_name='County',
            title=f"Food Insecurity Rates By County ({year})",
            labels = {'FIR': 'FIR2'}
        )

        fig.update_layout(
            plot_bgcolor='#0e1117',
            paper_bgcolor='#0e1117',
            title_font_color="salmon",
            font=dict(
                family="monospace",
                size=14,
                color="salmon"
            ),
            title_font_size=20,
            title_y=0.98, 
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            geo=dict(
                bgcolor="#0e1117",
                lakecolor='#0e1117',
                showlakes=True,
                showcoastlines=False,
                showland=True,
                landcolor='#0e1117',
            ),
            coloraxis=dict(
                colorbar=dict(
                    title="FIR (%)",
                    titlefont=dict(
                        family="monospace",
                        size=16,
                        color="salmon"
                    ),
                    tickfont=dict(
                        family="monospace",
                        size=12,
                        color="salmon"
                    )
                )
            )
        )

        fig.update_traces(
            hovertemplate="<b>County: %{customdata[0]}</b><br>County FIPS: %{location}<br>Food Insecurity: %{z:.2f}%<extra></extra>",
            customdata=filtered_df[['County']].values
        )
        fig.update(layout_coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=False)
    
        with st.container(height=375):
            x_options = ["Food Insecurity Rate", "Income Per Capita", "Unemployment Rate", "Cost Per Meal", "Year"]
            y_options = ["Food Insecurity Rate", "Income Per Capita", "Unemployment Rate", "Cost Per Meal"]
            selected_x = st.selectbox("Select X", x_options, index=4)
            selected_y = st.selectbox('Select Y', y_options)
            x_df = makeCompatible(selected_x)
            y_df = makeCompatible(selected_y)
            st.session_state.county_FIPS = st.text_input('Enter FIPS')
            if st.button('Create Chart'):
                if x_df == 'Year':
                    graph_df = df.copy()
                    graph_df = graph_df[graph_df['FIPS'] == st.session_state.county_FIPS]
                    st.session_state.county_name = graph_df['County'].iloc[0]
                    graph_df = graph_df[['Year', y_df]]

                    y_min = graph_df[y_df].min() * 0.9
                    y_max = graph_df[y_df].max() * 1.1

                    plt.figure(figsize=(10, 5))
                    plt.gcf().patch.set_facecolor('#0e1117')
                    plt.gca().set_facecolor('#0e1117')
                    plt.plot(graph_df[x_df], graph_df[y_df], color='orange')
                    plt.xticks(color='orange', fontname='monospace')
                    plt.yticks(color='orange', fontname='monospace')
                    plt.title(st.session_state.county_name + ' | ' + x_df + ' | ' + y_df, fontsize=15, color='orange', fontname='monospace')  # Set title font size, weight, color, and style
                    ax = plt.gca() 
                    ax.spines['top'].set_color('orange') 
                    ax.spines['right'].set_color('orange')
                    ax.spines['left'].set_color('orange')   
                    ax.spines['bottom'].set_color('orange')

                    plt.ylim(y_min, y_max)

                    st.pyplot(plt)
                else:
                    graph_df = df.copy()
                    graph_df = graph_df[graph_df['FIPS'] == st.session_state.county_FIPS]
                    st.session_state.county_name = graph_df['County'].iloc[0]
                    graph_df = graph_df[[x_df, y_df]]

                    y_min = graph_df[y_df].min() * 0.9
                    y_max = graph_df[y_df].max() * 1.1

                    plt.figure(figsize=(10, 5))
                    plt.gcf().patch.set_facecolor('#0e1117')
                    plt.gca().set_facecolor('#0e1117') 
                    plt.plot(graph_df[x_df], graph_df[y_df], color='orange')
                    plt.xticks(color='orange', fontname='monospace') 
                    plt.yticks(color='orange', fontname='monospace')
                    plt.title(st.session_state.county_name + ' | ' + x_df + ' | ' + y_df, fontsize=15, color='orange', fontname='monospace')  # Set title font size, weight, color, and style
                    ax = plt.gca() 
                    ax.spines['top'].set_color('orange') 
                    ax.spines['right'].set_color('orange')
                    ax.spines['left'].set_color('orange')
                    ax.spines['bottom'].set_color('orange')

                    plt.ylim(y_min, y_max)

                    st.pyplot(plt)

    with col2:
        filter_options = ["Food Insecurity Rate", "Income Per Capita", "Unemployment Rate", "Cost Per Meal"]

        st.markdown(
            """
            <style>
            .custom-container {
                margin-top: 70px; /* Padding around the container */
            }
            </style>
            <div class="custom-container">
            """,
            unsafe_allow_html=True,
        )

        with st.container(height=400):

            if st.button('Clear Filters'):
                st.session_state.filter_criteria = {}  

            selected_filter = st.selectbox("Select Filter", filter_options)

            if selected_filter == "Food Insecurity Rate":
                minFIR = filtered_df['FIR'].min()
                maxFIR = filtered_df['FIR'].max()
                food_insecurity_rate = st.slider("Food Insecurity Rate (%)", minFIR, maxFIR, (10.0, 20.0))
                st.session_state.current_filter = ('FIR', tuple(list(food_insecurity_rate)))

            elif selected_filter == "Income Per Capita":
                minIPC = filtered_df['IncomePerCapita'].min()
                maxIPC = filtered_df['IncomePerCapita'].max()
                inc_capita = st.slider("Income Per Capita ($)", minIPC, maxIPC, (50000.0, 200000.0))
                st.session_state.current_filter = ('IncomePerCapita', tuple(list(inc_capita)))

            elif selected_filter == "Unemployment Rate":
                minUR = filtered_df['FinalUR'].min()
                maxUR = filtered_df['FinalUR'].max()
                unemployment_rate = st.slider("Unemployment Rate (%)", minUR, maxUR, (5.0, 10.0))
                st.session_state.current_filter = ('FinalUR', tuple(list(unemployment_rate)))

            elif selected_filter == "Cost Per Meal":
                minCPM = filtered_df['FinalCPM'].min()
                maxCPM = filtered_df['FinalCPM'].max()
                cost_per_meal = st.slider("Cost Per Meal ($)", minCPM, maxCPM, (5.0, 7.0))
                st.session_state.current_filter = ('FinalCPM', tuple(list(cost_per_meal)))

            if st.button(label="Add Filter"):
                addFilter()
            
            for name, value_range in st.session_state.filter_criteria.items():
                st.button(f'{name}: {value_range}')
            
            st.markdown(
                """
                </div>
                """,
                unsafe_allow_html=True,
            )

        if st.button(label='Apply Changes'):
            filtered_map = applyChanges() 
            st.plotly_chart(filtered_map, use_container_width=True)

    with col3:
        st.markdown(
            """
            <div style='font-size:130px; margin-top:32px; padding-left: 10px;margin-right:0px; text-align: center'>
                🕊️
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.container(height=230):
            st.write("Placeholder for List")
        
        with st.container(height=450):
            reporter_df = df.copy()
            reporter_df = reporter_df[reporter_df['Year'] == 2021]
            reporter_df = reporter_df[['FIR', 'FIPS', 'County']]
            sorted_df = reporter_df.sort_values(by='FIR', ascending=False)
            st.markdown(
                """
                <div style='font-size:20px; margin-bottom: 15px; margin-top: 5px'>
                    Counties Sorted By FIR
                </div>
                """,
                unsafe_allow_html=True
            )
            for index, row in sorted_df.iterrows():
                st.button(f'{row["County"]}: {row["FIR"]}%')

Main()
