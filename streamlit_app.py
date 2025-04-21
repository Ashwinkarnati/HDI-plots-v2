# pyright: reportMissingModuleSource=false
# pyright: reportMissingImports=false
import streamlit as st
import pandas as pd
import app.constants as constants
from app.utils import (
    get_country_coords,
    get_state_coords,
    save_csv,
    get_countries,
    get_indian_states
)

from app.visualizations.matplotlib_module import MatplotlibModule

def get_world_state(params):
    """Initialize the app state"""
    if "world" not in st.session_state:
        st.session_state["world"] = True
    if "world" in params:
        st.session_state["world"] = True if params.get("world")[0] == "true" else False
    return st.session_state["world"]

def get_countries_and_states():
    """Get the list of countries and states"""
    countries = get_countries()
    indian_states = get_indian_states()
    return countries, indian_states

def get_indices():
    """Get the education indices"""
    indices = constants.edu_indices
    india_indices = constants.india_edu_indices
    return indices, india_indices

def get_query_params():
    """Get the query parameters"""
    params = st.query_params.to_dict()
    for k, v in params.items():
        params[k] = v.split(",")
    return params

def get_selected_options(params):
    """Get the selected options from the query parameters"""
    selected_options = params.get("gender", [])
    selected_other_indicators = params.get("other", [])
    if len(selected_options) == 0:
        selected_options = ["Female"]
    return selected_options, selected_other_indicators

def get_selected_x_and_y(params, indices):
    """Get the selected x and y values from the query parameters"""
    selected_x, selected_y = indices[0], indices[1]
    try:
        selected_x = constants.cleaned_indices[params.get("x", indices)[0]]
    except:
        pass
    try:
        selected_y = constants.cleaned_indices[params.get("y", indices)[0]]
    except:
        pass
    return selected_x, selected_y

def get_selected_countries_and_states(params, world, countries, indian_states):
    """Get the selected countries and states from the query parameters"""
    selected_countries = []
    selected_states = []

    if world:
        selected_countries = params.get("c", ["India"])
    else:
        selected_states = params.get("s", ["Kerala"])

    return selected_countries, selected_states

def set_page_config():
    """Set the page configuration"""
    st.set_page_config(
        page_title="HDI Visualization Dashboard",
        page_icon="🌏",
        layout="centered",
        initial_sidebar_state="expanded"
    )

def create_sidebar():
    """Create sidebar with information"""
    with st.sidebar:
        st.title("About")
        st.markdown("""
        **Human Development Index (HDI) Visualization Tool**
        
        This interactive dashboard allows you to explore education and development indicators across countries and Indian states.
        
        - Select between **World** or **India** view
        - Choose indicators to visualize
        - Compare multiple regions
        - Download data and charts
        """)
        
        st.markdown("---")
        st.markdown("**Data Sources:**")
        st.markdown("- World Bank Development Indicators")
        st.markdown("- Indian Census Data")
        st.markdown("---")
        st.markdown("Created with ❤️ using Streamlit")

def main():
    """Main function"""
    # Set up page and sidebar
    set_page_config()
    create_sidebar()
    
    # Custom CSS for better styling
    st.markdown(constants.custom_style, unsafe_allow_html=True)
    st.markdown("""
    <style>
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            padding: 10px 24px;
        }
        .stSelectbox, .stMultiSelect {
            padding: 8px;
            border-radius: 8px;
        }
        .stSlider {
            padding: 8px 0;
        }
        .css-1aumxhk {
            background-color: #f0f2f6;
            border-radius: 8px;
            padding: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    params = get_query_params()
    world = get_world_state(params)
    countries, indian_states = get_countries_and_states()
    indices, india_indices = get_indices()
    selected_options, selected_other_indicators = get_selected_options(params)
    selected_x, selected_y = get_selected_x_and_y(params, indices)
    selected_countries, selected_states = get_selected_countries_and_states(params, world, countries, indian_states)

    cleaned_indices_reversed = {v: k for k, v in constants.cleaned_indices.items()}

    # Header section
    st.title("🌍 Human Development Indicators Dashboard")
    st.markdown("Visualize and compare education and development metrics across regions and time periods.")
    st.markdown("---")

    # World/India toggle
    col1, col2 = st.columns(2)
    if col1.button("🌐 World View", type="primary" if world else "secondary", key="world_button"):
        st.query_params["world"] = "true"
        world = True
        st.rerun()

    if col2.button("🇮🇳 India View", type="primary" if not world else "secondary", key="india_button"):
        st.query_params["world"] = "false"
        world = False
        st.rerun()

    # Main controls section
    with st.container():
        st.subheader("Visualization Settings")
        
        # Axis selection
        col1, col2 = st.columns(2)
        if world:
            if selected_y not in indices:
                selected_y = indices[0]
            selected_y = col1.selectbox("Y-Axis Metric", indices, 
                                      index=indices.index(selected_y), 
                                      key="y_axis_selectbox",
                                      help="Select the indicator to display on the Y-axis")
            
            selected_x = col2.selectbox("X-Axis Metric", constants.time_indices, 
                                      index=0, disabled=True, 
                                      key="x_axis_selectbox",
                                      help="Time is always on the X-axis")
        else:
            if selected_y not in india_indices:
                selected_y = india_indices[0]
            selected_y = col1.selectbox("Y-Axis Metric", india_indices, 
                                      index=india_indices.index(selected_y), 
                                      key="y_axis_selectbox_india")
            selected_x = col2.selectbox("X-Axis Metric", constants.time_indices, 
                                      index=0, disabled=True, 
                                      key="x_axis_selectbox_india")

        # Gender selection (only for education indicators)
        if world and selected_y in constants.edu_indices or not world:
            st.markdown("**Gender Selection**")
            gender_cols = st.columns(3)
            options = ['Both', 'Male', 'Female']
            
            checkbox_state1 = gender_cols[0].checkbox(options[0], 
                                                     value=options[0] in selected_options, 
                                                     key="both_checkbox")
            checkbox_state2 = gender_cols[1].checkbox(options[1], 
                                                     value=options[1] in selected_options, 
                                                     key="male_checkbox")
            checkbox_state3 = gender_cols[2].checkbox(options[2], 
                                                     value=options[2] in selected_options, 
                                                     key="female_checkbox")

            selected_options = []
            for i, checkbox in enumerate([checkbox_state1, checkbox_state2, checkbox_state3]):
                if checkbox:
                    selected_options.append(options[i])

        # Region selection
        st.markdown("**Region Selection**")
        if world:
            selected_countries = st.multiselect("Select Countries", countries, 
                                             default=selected_countries, 
                                             key="countries_multiselect",
                                             help="Select countries to compare")
            # selected_states = st.multiselect("Select Indian States (for comparison)", 
            #                                indian_states, 
            #                                default=selected_states, 
            #                                key="states_multiselect_world")
            
            # Year range slider
            try:
                start_year = int(params.get("sy", [1960])[0])
                end_year = int(params.get("ey", [2020])[0])
            except:
                start_year = 1960
                end_year = 2020
                
            selected_years = st.slider("Year Range", 
                                      min_value=1960, 
                                      max_value=2020, 
                                      value=(start_year, end_year), 
                                      key="years_slider")
        else:
            selected_states = st.multiselect("Select States", 
                                          indian_states, 
                                          selected_states, 
                                          key="states_multiselect_india")

        # Additional indicators
        st.markdown("**Additional Indicators**")
        if world:
            indicator_cols = st.columns(4)
            other_indicators = ['Life Expectancy', 'Total Fertility Rate', 'GDP per Capita', 'Human Development Index']
        else:
            indicator_cols = st.columns(3)
            other_indicators = ['Life Expectancy', 'Total Fertility Rate', 'GDP per Capita']
            
        selected_other_indicators = []
        for i, indicator in enumerate(other_indicators):
            if indicator_cols[i].checkbox(indicator, 
                                        value=indicator in params.get("other", []), 
                                        key=f"{indicator.lower()}_checkbox"):
                selected_other_indicators.append(indicator)

        # Display options
        st.markdown("**Display Options**")
        display_cols = st.columns(2)
        try:
            vertical_view = params.get("vertical", ["false"])[0].lower() == "true"
        except:
            vertical_view = False
            
        vertical_view = display_cols[0].checkbox("Vertical Layout", 
                                               value=vertical_view, 
                                               key="vertical_view_checkbox",
                                               help="Arrange charts vertically instead of horizontally")
        
        # Prepare data for visualization
        selected_ys = []
        for selected_option in selected_options:
            selected_ys.append((f"{selected_option} {selected_y}", selected_option))
            
        if not selected_ys:  # If no gender selected (for non-education indicators)
            selected_ys.append((selected_y, ""))

        # Create visualizations
        plotter = MatplotlibModule(len(selected_other_indicators) + 1, vertical=vertical_view)
        
        # Education indicator plot
        all_coords = []
        if world:
            # Plot states first (dotted lines)
            if len(selected_states) > 0:
                for selected_state in selected_states:
                    for selected_y_t, gender in selected_ys:
                        state_coords = get_state_coords(selected_state, selected_y_t)
                        if state_coords:
                            all_coords.append((selected_state, gender, state_coords))
                
                if all_coords:
                    all_coords = sorted(all_coords, key=lambda x: x[2]["y"][0], reverse=True)
                    plotter.create_plot(all_coords, selected_x, selected_y, dotted=True)
                    plotter.reduce_subplot_no()

            # Plot countries
            all_coords = []
            for selected_country in selected_countries:
                for selected_y_t, gender in selected_ys:
                    country_coords = get_country_coords(selected_country, selected_y_t, selected_years)
                    if country_coords is not None and not country_coords.empty:
                        all_coords.append((selected_country, gender, country_coords))
            
            if all_coords:
                all_coords = sorted(all_coords, key=lambda x: x[2]["y"][0], reverse=True)
                plotter.create_plot(all_coords, selected_x, selected_y)
        else:
            # India view - only states
            all_coords = []
            for selected_state in selected_states:
                for selected_y_t, gender in selected_ys:
                    state_coords = get_state_coords(selected_state, selected_y_t)
                    if state_coords is not None and not state_coords.empty:
                        all_coords.append((selected_state, gender, state_coords))

            if all_coords:
                all_coords = sorted(all_coords, key=lambda x: x[2]["y"][0], reverse=True)
                plotter.create_plot(all_coords, selected_x, selected_y, dotted=True)

        # Additional indicators plots
        for indicator in selected_other_indicators:
            data = []
            if world:
                # States first
                if len(selected_states) > 0:
                    state_data = []
                    for selected_state in selected_states:
                        state_coords = get_state_coords(selected_state, indicator)
                        if state_coords:
                            state_data.append((selected_state, "", state_coords))
                    if state_data:
                        plotter.create_plot(state_data, selected_x, indicator, dotted=True)
                        plotter.reduce_subplot_no()

                # Countries
                country_data = []
                for selected_country in selected_countries:
                    country_coords = get_country_coords(selected_country, indicator, selected_years)
                    if country_coords is not None and not country_coords.empty:
                        country_data.append((selected_country, "", country_coords))
                if country_data:
                    plotter.create_plot(country_data, selected_x, indicator)
            else:
                # India view - only states
                state_data = []
                for selected_state in selected_states:
                    state_coords = get_state_coords(selected_state, indicator)
                    if state_coords is not None and not state_coords.empty:
                        state_data.append((selected_state, "", state_coords))
                if state_data:
                    plotter.create_plot(state_data, selected_x, indicator, dotted=True)

        # Display and download options
        if world and selected_countries:
            st.markdown("---")
            st.subheader("Download Options")
            col1, col2 = st.columns(2)
            
            file_name = f"{selected_x[:3]}_{selected_y[:3]}"
            if selected_y in constants.edu_indices:
                c_selected_y = selected_options[0] + " " + selected_y if selected_options else selected_y
            else:
                c_selected_y = selected_y
                
            csv_snippet = save_csv(selected_countries, selected_x, c_selected_y, selected_years)
            with open("chart.csv", "rb") as f:
                data_bytes = f.read()
                col1.download_button(
                    label="📥 Download Data (CSV)",
                    data=data_bytes,
                    file_name=f"{file_name}.csv",
                    mime="text/csv",
                    key="data_download_button",
                    help="Download the data used in this visualization"
                )

            plotter.save_plot("chart.png")
            with open("chart.png", "rb") as f:
                image_bytes = f.read()
                col2.download_button(
                    label="📊 Download Chart (PNG)",
                    data=image_bytes,
                    file_name=f"{file_name}.png",
                    mime="image/png",
                    key="graph_download_button",
                    help="Download the chart as an image"
                )

        # Display the plot
        st.pyplot(plotter.get_fig())

        # Footnotes
        st.markdown("---")
        with st.expander("Data Notes"):
            st.markdown("""
            - **Education data** represents the percentage ofpopulation aged 20-24 who have completed:
                - **Primary Education**: 6 years of education
                - **Lower Secondary Education**: 9 years ofeducation
                - **Higher Secondary Education**: 12 years ofeducation
            - **College Completion**: 16 years of education
        - Data sources may vary by country and indicator
        - Some indicators may not be available for all yearsorregions
        """)

    # Update query parameters
    if world:
        st.query_params.update({
            "c": ",".join(selected_countries),
            "x": cleaned_indices_reversed[selected_x],
            "y": cleaned_indices_reversed[selected_y],
            "sy": selected_years[0],
            "ey": selected_years[1],
            "gender": ",".join(selected_options),
            "other": ",".join(selected_other_indicators),
            "world": "true",
            "vertical": str(vertical_view).lower()
        })
    else:
        st.query_params.update({
            "s": ",".join(selected_states),
            "y": cleaned_indices_reversed[selected_y],
            "gender": ",".join(selected_options),
            "other": ",".join(selected_other_indicators),
            "world": "false",
            "vertical": str(vertical_view).lower()
        })

if __name__ == "__main__":
    main()