import pandas as pd
import pymysql
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt

# Function to create MySQL connection
def create_connection():
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="Davinci1123!",
        database="Red_bus_details"
    )
    return connection

# Function to load data from MySQL with specified columns
def load_data(query, columns=None):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    if columns is None:
        columns = [i[0] for i in cursor.description]
    data = pd.DataFrame(result, columns=columns)
    cursor.close()
    connection.close()
    return data

# Function to fetch unique values for filter options based on conditions
def get_filter_options(column_name, conditions=None):
    query = f"SELECT DISTINCT {column_name} FROM red_bus_details.busdetails"
    if conditions:
        query += f" WHERE {conditions} AND {column_name} IS NOT NULL;"
    else:
        query += " WHERE " + column_name + " IS NOT NULL;"
    data = load_data(query)
    return data[column_name].unique()

# Function to display the filter page
def display_filters_page():
    st.title("Choose Your Bus: ")

    # Getting unique values for each filter based on conditions
    transport_names = get_filter_options('transport_name')
    selected_transport = st.selectbox("Select State Transport Name", options=["All"] + list(transport_names))

    # Building condition for start location filter based on selected transport
    start_location_condition = None
    if selected_transport != "All":
        start_location_condition = f"transport_name = '{selected_transport}'"
    start_locations = get_filter_options('start_location', start_location_condition)
    selected_start_location = st.selectbox("Select Start Location", options=["All"] + list(start_locations))

    # Building condition for end location filter based on selected start location
    end_location_condition = None
    if selected_start_location != "All":
        if start_location_condition:
            end_location_condition = f"transport_name = '{selected_transport}' AND start_location = '{selected_start_location}'"
        else:
            end_location_condition = f"start_location = '{selected_start_location}'"
    end_locations = get_filter_options('end_location', end_location_condition)
    selected_end_location = st.selectbox("Select End Location", options=["All"] + list(end_locations))

    # Building conditions for other filters
    ac_types = get_filter_options('standardized_ac_type', end_location_condition)
    selected_ac_type = st.selectbox("Select AC Type", options=["All"] + list(ac_types))
    
    seat_types = get_filter_options('standardized_seat_type', end_location_condition)
    selected_seat_type = st.selectbox("Select Seat Type", options=["All"] + list(seat_types))
    
    bus_time_categories = get_filter_options('bus_time_category', end_location_condition)
    selected_bus_time_category = st.selectbox("Select Bus Time Category", options=["All"] + list(bus_time_categories))
    
    # Addind a rating filter as a toggle slider (range: 0-5, step: 0.1)
    rating_range = st.slider("Select Rating Range", min_value=0.0, max_value=5.0, value=(0.0, 5.0), step=0.1)

    # Building the query based on filters
    filters = []
    if selected_transport != "All":
        filters.append(f"transport_name = '{selected_transport}'")
    if selected_start_location != "All":
        filters.append(f"start_location = '{selected_start_location}'")
    if selected_end_location != "All":
        filters.append(f"end_location = '{selected_end_location}'")
    if selected_ac_type != "All":
        filters.append(f"standardized_ac_type = '{selected_ac_type}'")
    if selected_seat_type != "All":
        filters.append(f"standardized_seat_type = '{selected_seat_type}'")
    if selected_bus_time_category != "All":
        filters.append(f"bus_time_category = '{selected_bus_time_category}'")
    # Adding the rating filter to the query
    filters.append(f"bus_rating BETWEEN {rating_range[0]} AND {rating_range[1]}")

    where_clause = " AND ".join(filters)
    if where_clause:
        query = f"SELECT bus_name, departure_time, duration, reaching_time, price, bus_rating FROM red_bus_details.busdetails WHERE {where_clause};"
    else:
        query = "SELECT bus_name, departure_time, duration, reaching_time, price, bus_rating FROM red_bus_details.busdetails;"

    # Loading and displaying filtered data
    data = load_data(query)
    if not data.empty:
        st.dataframe(data)
    else:
        st.write("No data available for the selected filters.")


def display_analysis_page():
    st.title("Bus Data Analysis")

    # Fetching unique options for filters
    transport_names = get_filter_options('transport_name')
    ac_types = get_filter_options('standardized_ac_type')
    seat_types = get_filter_options('standardized_seat_type')

    # Selectbox inputs for the analysis
    selected_transport = st.selectbox("Select Transport Name", options=["All"] + list(transport_names))
    selected_ac_type = st.selectbox("Select AC Type", options=["All"] + list(ac_types))
    selected_seat_type = st.selectbox("Select Seat Type", options=["All"] + list(seat_types))

    # Building the query based on selected filters
    filters = []
    if selected_transport != "All":
        filters.append(f"transport_name = '{selected_transport}'")
    if selected_ac_type != "All":
        filters.append(f"standardized_ac_type = '{selected_ac_type}'")
    if selected_seat_type != "All":
        filters.append(f"standardized_seat_type = '{selected_seat_type}'")

    where_clause = " AND ".join(filters)
    query = f"SELECT price, bus_rating, seat_availability, standardized_ac_type, standardized_seat_type, duration FROM red_bus_details.busdetails"
    if where_clause:
        query += f" WHERE {where_clause};"

    # Loading data based on filters
    data = load_data(query)

    # Displaying the plots if data is available
    if not data.empty:
        # Bar Graph for Bus Type vs Count
        st.subheader("Bus Type vs Number of Buses")
        bus_type_counts = data['standardized_ac_type'].value_counts().reset_index()
        bus_type_counts.columns = ['Bus Type', 'Count']
        fig10 = px.bar(bus_type_counts, x='Bus Type', y='Count', title="Number of Buses by Bus Type")
        st.plotly_chart(fig10)

        # Bar Graph for Seat Type vs Count
        st.subheader("Seat Type vs Number of Buses")
        seat_type_counts = data['standardized_seat_type'].value_counts().reset_index()
        seat_type_counts.columns = ['Seat Type', 'Count']
        fig11 = px.bar(seat_type_counts, x='Seat Type', y='Count', title="Number of Buses by Seat Type")
        st.plotly_chart(fig11)

        # Pie Chart for AC Type (AC vs Non-AC)
        st.subheader(f"{selected_transport} AC vs Non-AC Bus Distribution")
        ac_type_counts = data['standardized_ac_type'].value_counts().reset_index()
        ac_type_counts.columns = ['AC Type', 'Count']
        fig12 = px.pie(ac_type_counts, names='AC Type', values='Count', title="AC vs Non-AC Buses")
        st.plotly_chart(fig12)

        # Pie Chart for Seat Type Distribution
        st.subheader(f"{selected_transport} Seat Type Distribution")
        seat_type_counts = data['standardized_seat_type'].value_counts().reset_index()
        seat_type_counts.columns = ['Seat Type', 'Count']
        fig13 = px.pie(seat_type_counts, names='Seat Type', values='Count', title="Seat Type Distribution")
        st.plotly_chart(fig13)
        
        # Price vs Bus Type
        st.subheader("Price vs Bus Type")
        fig1 = px.box(data, x='standardized_ac_type', y='price', title="Price by Bus Type")
        st.plotly_chart(fig1)

        # Price vs Seat Type
        st.subheader("Price vs Seat Type")
        fig2 = px.box(data, x='standardized_seat_type', y='price', title="Price by Seat Type")
        st.plotly_chart(fig2)

        # Price vs Bus Type and Seat Type
        st.subheader("Price vs Bus Type and Seat Type")
        fig3 = px.scatter(data, x='standardized_ac_type', y='price', color='standardized_seat_type', 
                          title="Price by Bus Type and Seat Type")
        st.plotly_chart(fig3)

        # Duration vs Price
        st.subheader("Price vs Duration")
        fig4 = px.scatter(data, x='duration', y='price', title="Price by Duration")
        st.plotly_chart(fig4)

        # Ratings vs Bus Type
        st.subheader("Ratings vs Bus Type")
        fig5 = px.box(data, x='standardized_ac_type', y='bus_rating', title="Ratings by Bus Type")
        st.plotly_chart(fig5)

        # Ratings vs Seat Type
        st.subheader("Ratings vs Seat Type")
        fig6 = px.box(data, x='standardized_seat_type', y='bus_rating', title="Ratings by Seat Type")
        st.plotly_chart(fig6)

        # Ratings vs Price
        st.subheader("Ratings vs Price")
        fig7 = px.scatter(data, x='price', y='bus_rating', title="Ratings by Price")
        st.plotly_chart(fig7)

        # Seat Availability vs Ratings
        st.subheader("Seat Availability vs Ratings")
        fig8 = px.scatter(data, x='bus_rating', y='seat_availability', title="Seat Availability by Ratings")
        st.plotly_chart(fig8)

        # Seat Availability vs Price
        st.subheader("Seat Availability vs Price")
        fig9 = px.scatter(data, x='price', y='seat_availability', title="Seat Availability by Price")
        st.plotly_chart(fig9)

        

    else:
        st.write("No data available for the selected filters.")

def display_book_bus_page():
    st.title("Book Your Bus")

    # Fetching unique transport names
    transport_names = get_filter_options('transport_name')
    selected_transport = st.selectbox("Select Transport Name", options=["All"] + list(transport_names))

    if selected_transport != "All":
        # Query to fetch routes and route links based on the selected transport
        query = f"SELECT route_name, route_link FROM red_bus_details.busdetails WHERE transport_name = '{selected_transport}'"
        route_data = load_data(query, columns=["route_name", "route_link"])

        # Grouping by route_name to only show unique routes
        unique_routes = route_data.drop_duplicates(subset='route_name')

        if not unique_routes.empty:
            st.write(f"Available Routes for {selected_transport}:")
            for index, row in unique_routes.iterrows():
                route_name = row['route_name']
                route_link = row['route_link']
                
                # Displaying unique route name and "Book Now" button
                st.write(route_name)
                if st.button("Book Now", key=f"book_now_{index}"):
                    st.write(f"Redirecting to {route_link}...")
                    st.write(f"[Book Now]({route_link})", unsafe_allow_html=True)
        else:
            st.write(f"No routes available for {selected_transport}.")
    else:
        st.write("Please select a transport name.")


# Streamlit app configuration
icon_path = "C:/Users/LENOVO/Desktop/StreamLit/env/Scripts/redbusimage.png"
st.set_page_config(page_title="RedBus Application", page_icon=icon_path )

# Initializing session state
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'

# Function to display the main page with sidebar navigation
def display_main_page():
    st.sidebar.title("Navigation")
    option = st.sidebar.radio("Go to", ["Filters", "Analysis", "Book Bus"])

    if option == "Filters":
        display_filters_page()
    elif option == "Analysis":
        display_analysis_page()
    elif option == "Book Bus":
        display_book_bus_page()
    

# Displaying content based on session state
if st.session_state.page == 'welcome':
    # Center the welcome message
    col1, col2, col3 = st.columns([4, 20, 2])
    with col2:
        st.title("Welcome to RedBus App!")
    
    # Center the button
    col1, col2, col3 = st.columns([4, 2, 4])
    with col2:
        if st.button("Let's Explore"):
            st.session_state.page = 'main'
    st.image("C:/Users/LENOVO/Desktop/StreamLit/env/Scripts/banner_home_page.png")
    
else:
    display_main_page()
