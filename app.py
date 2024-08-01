import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from data_sets import wc_active_data, wc_inactive_data, gcm_active_data, gcm_inactive_data, get_in_plan, get_out_of_plan
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import datetime as dt

today = dt.datetime.today()
today = today.strftime('%Y%m%d%H%M%S')

# TODO: add in the areas for the map view. And look to deploy and web application and test
# TODO: Add a download button for the HTML map for quicker loading time

#set page
st.set_page_config(page_title="Mercedes-Benz Rentention", page_icon="🌎", layout="wide")

# Set page header
st.header('MERCEDES-BENZ - RETENTION', divider='blue')
st.header('')

#Get the data

def get_data(d_type):
    if d_type == 'WA':
        df = wc_active_data()
        return df
    elif d_type == 'WI':
        df = wc_inactive_data()
        return df
    elif d_type == 'GA':
        df = gcm_active_data()
        return df
    elif d_type == 'GI':
        df = gcm_inactive_data()
        return df


#option menu
from streamlit_option_menu import option_menu
with st.sidebar:
        selected=option_menu(
        menu_title="MAIN MENU",
        options=["WC Active Customers", "WC Inactive Customers", "GCM Active Customers", "GCM Inactive Customers"],
        icons=["book", "book", "book", "book"],
        menu_icon="cast", #option
        default_index=0, #option
        orientation="vertical",)


def av_options(df, options):
    available_options = (df[options].sort_values(ascending=True)).unique().tolist()
    available_options.insert(0, -1)

    if "max_selections" not in st.session_state:
        st.session_state["max_selections"] = len(available_options)

    return available_options


def options_select(available_options, selected_options):
    if selected_options in st.session_state:
        if -1 in st.session_state[selected_options]:
            st.session_state[selected_options] = available_options[1:]
            st.session_state["max_selections"] = len(available_options)
        else:
            st.session_state["max_selections"] = len(available_options)

def side_filter_selection(df):
    show_more_filters = st.sidebar.checkbox('Show More Filters', key='show_filter')
    dealer = st.sidebar.multiselect(
        label='Filter Dealer',
        options=av_options(df, 'Branch'),
        default=av_options(df, 'Branch')[1:],
        key="branch_options",
        on_change=options_select(av_options(df, 'Branch'), 'branch_options'),
        format_func=lambda x: "All" if x == -1 else f"{x}",
        
    )

    vehicle = st.sidebar.multiselect(
        label='Filter Model',
        options=av_options(df, 'Vehicles'),
        default=av_options(df, 'Vehicles')[1:],
        key="model_options",
        on_change=options_select(av_options(df, 'Vehicles'), 'model_options'),
        format_func=lambda x: "All" if x == -1 else f"{x}",
        
    )

    area = st.sidebar.multiselect(
        label='Filter Area',
        options=av_options(df, 'Area'),
        default=av_options(df, 'Area')[1:],
        key="area_options",
        on_change=options_select(av_options(df, 'Area'), 'area_options'),
        format_func=lambda x: "All" if x == -1 else f"{x}",
        
    )
    df_selection = df.query(
        "Branch==@dealer & Vehicles==@vehicle & Area==@area"
    )
    

    if st.session_state.show_filter:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            v_age_r = st.multiselect(
                label='Vehicle Age (Reg Date)',
                options=av_options(df_selection, 'Vehicle_Age_Reg_Date'),
                default=av_options(df_selection, 'Vehicle_Age_Reg_Date')[1:],
                key="v_age_r_options",
                on_change=options_select(av_options(df_selection, 'Vehicle_Age_Reg_Date'), 'v_age_r_options'),
                format_func=lambda x: "All" if x == -1 else f"{x}",
            )
        with col2:
            v_age_p = st.multiselect(
                label='Vehicle Age (Plan End Date)',
                options=av_options(df_selection, 'Vehicle_Age_Plan'),
                default=av_options(df_selection, 'Vehicle_Age_Plan')[1:],
                key="v_age_p_options",
                on_change=options_select(av_options(df_selection, 'Vehicle_Age_Plan'), 'v_age_p_options'),
                format_func=lambda x: "All" if x == -1 else f"{x}",
            )
        with col3:
            age_group = st.multiselect(
                label='Customer Age Group',
                options=av_options(df_selection, 'Age_Group'),
                default=av_options(df_selection, 'Age_Group')[1:],
                key="age_options",
                on_change=options_select(av_options(df_selection, 'Age_Group'), 'age_options'),
                format_func=lambda x: "All" if x == -1 else f"{x}",
            )
        with col4:
            multi_owner = st.multiselect(
                label='Multiple Ownership',
                options=av_options(df_selection, 'Multiple_Ownership'),
                default=av_options(df_selection, 'Multiple_Ownership')[1:],
                key="multi_owner_options",
                on_change=options_select(av_options(df_selection, 'Multiple_Ownership'), 'multi_owner_options'),
                format_func=lambda x: "All" if x == -1 else f"{x}",
            )
        with col5:
            company_owned = st.multiselect(
                label='Company Owned',
                options=av_options(df_selection, 'Company_Owned'),
                default=av_options(df_selection, 'Company_Owned')[1:],
                key="company_options",
                on_change=options_select(av_options(df_selection, 'Company_Owned'), 'company_options'),
                format_func=lambda x: "All" if x == -1 else f"{x}",
            )

        df_selection = df.query(
            "Branch==@dealer & Vehicles==@vehicle & Area==@area & Vehicle_Age_Reg_Date==@v_age_r & Vehicle_Age_Plan==@v_age_p & Age_Group==@age_group & Multiple_Ownership==@multi_owner & Company_Owned==@company_owned"
        )
    
    return df_selection
     

def metrics(df):
    from streamlit_extras.metric_cards import style_metric_cards
    col1, col2, col3 = st.columns(3)

    col1.metric(label="Total Vehicles", value=df['Branch'].count(), delta="All vehicles")

    col2.metric(label="In Plan", value=get_in_plan(df),delta='In Plan')

    col3.metric(label="Out Of Plan", value=get_out_of_plan(df),delta='Out Of Plan')

    style_metric_cards(background_color="#ffffff",border_left_color="#18334C",box_shadow="3px")

def table(df):
    shouldDisplayPivoted = st.checkbox("Pivot Table", key="checked")

    gb = GridOptionsBuilder()

    gb.configure_default_column(
        resizable=True,
        filterable=True,
        sortable=True,
        editable=False,  
        )

    gb.configure_column(field="Vehicles", header_name="Vehicle", width=80, rowGroup=shouldDisplayPivoted, sort='asc')

    gb.configure_column(
        field="Mileage Category",
        header_name="Mileage Category",
        tooltipField="Mileage Category",
        pivot=True,
    )

    gb.configure_column(
        field="Branch",
        header_name="Total",
        width=100,
        aggFunc="count",
        valueFormatter="value.toLocaleString()",
    )

    gb.configure_grid_options(
        tooltipShowDelay=0,
        pivotMode=shouldDisplayPivoted,
        suppressAggFuncInHeader=True
    )

    gb.configure_grid_options(
        autoGroupColumnDef=dict(
            minWidth=300,
            pinned="left",
            cellRendererParams=dict(suppressCount=True)
        )
    )
    if st.session_state.checked:
        go = gb.build()
        AgGrid(df, gridOptions=go, height=1000, fit_columns_on_grid_load=ColumnsAutoSizeMode.FIT_CONTENTS)
    else:
        shwdata = st.multiselect('Columns To Show :', df.columns, default=['Branch', 'Multiple_Ownership', 'Company', 'Company_Owned', 'Age_Group', 'Suburb', 'Area', 'Last Interaction Type', 'Last Interaction Date', 'Body Number', '1st Section', '2nd Section', '3rd Section', 'Vehicle_Age_Reg_Date', 'Vehicles', 'Model', 'Mileage Category', 'Ownership', 'Customer Type', 'Planned end date', 'Vehicle_Age_Plan', 'Plan'])
        AgGrid(df[shwdata], height=1000)

def map_data(df, is_gcm='N'):
    df = df.loc[df['Has_Coord'] == 'Y']
    a_keys = ('latitude', 'longitude')
    a_records = []
    map_df = df[['latitude', 'longitude']].copy()
    for key, row in map_df.iterrows():
        a_records.append({key:row[key] for key in a_keys})

    for record in a_records:
        record['latitude'] = float(record['latitude'])
        record['longitude'] = float(record['longitude'])

    if is_gcm != 'Y':    
        map = folium.Map(location=[-34.01453443432472, 18.888931274414066], zoom_start=10)

        mCluster = MarkerCluster(name='Marker Cluster Test').add_to(map)

        for pnt in a_records:
            folium.Marker(location=[pnt['latitude'], pnt['longitude']]).add_to(mCluster)

        # Main Markers
        folium.Marker(location=[-33.895458306137, 18.512036576174], popup='Mercedes-Benz Century City', icon=folium.Icon(color='green')).add_to(map)
        folium.Marker(location=[-34.065767388821, 18.456759936389], popup='Mercedes-Benz Constantiaberg', icon=folium.Icon(color='green')).add_to(map)
        folium.Marker(location=[-33.767200700131, 18.915303532893], popup='Mercedes-Benz Paarl', icon=folium.Icon(color='green')).add_to(map)
        folium.Marker(location=[-33.924933865967, 18.855452410056], popup='Mercedes-Benz Stellenbosch', icon=folium.Icon(color='green')).add_to(map)
        folium.Marker(location=[-33.920401592702, 18.434058725105], popup='Mercedes-Benz Culemborg', icon=folium.Icon(color='red')).add_to(map)

        st_data = st_folium(map, width=1000)
    else:
        map = folium.Map(location=[-26.249698933197603, 28.166885375976566], zoom_start=10)

        mCluster = MarkerCluster(name='Marker Cluster Test').add_to(map)

        for pnt in a_records:
            folium.Marker(location=[pnt['latitude'], pnt['longitude']]).add_to(mCluster)

        # Main Markers
        folium.Marker(location=[-25.978329985392, 28.118513090591], popup='Mercedes-Benz Grand Central Motors', icon=folium.Icon(color='green')).add_to(map)

        st_data = st_folium(map, width=1000)

@st.cache_data
def convert_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

if selected=='WC Active Customers':
    df = get_data('WA')
    df_selection = side_filter_selection(df)
    
    metrics(df_selection)
    veiw_filter = st.radio(
        label='Filter between Views',
        options=['Table', 'Map']
    )
    if veiw_filter == 'Table':
        table(df_selection)
    else:
        map_data(df_selection)

    csv = convert_to_csv(df_selection)

    download1 = st.download_button(
        label="Download Results",
        data=csv,
        file_name=f'ret-download-{today}.csv',
        mime='text/csv'
    )
elif selected=='WC Inactive Customers':
    df = get_data('WI')
    df_selection = side_filter_selection(df)
    metrics(df_selection)
    veiw_filter = st.radio(
        label='Filter between Views',
        options=['Table', 'Map']
    )
    if veiw_filter == 'Table':
        table(df_selection)
    else:
        map_data(df_selection)

    csv = convert_to_csv(df_selection)

    download1 = st.download_button(
        label="Download Results",
        data=csv,
        file_name=f'ret-download-{today}.csv',
        mime='text/csv'
    )
elif selected=='GCM Active Customers':
    df = get_data('GA')
    df_selection = side_filter_selection(df)
    metrics(df_selection)
    veiw_filter = st.radio(
        label='Filter between Views',
        options=['Table', 'Map']
    )
    if veiw_filter == 'Table':
        table(df_selection)
    else:
        map_data(df_selection, 'Y')

    csv = convert_to_csv(df_selection)

    download1 = st.download_button(
        label="Download Results",
        data=csv,
        file_name=f'ret-download-{today}.csv',
        mime='text/csv'
    )
elif selected=='GCM Inactive Customers':
    df = get_data('GI')
    df_selection = side_filter_selection(df)
    metrics(df_selection)
    veiw_filter = st.radio(
        label='Filter between Views',
        options=['Table', 'Map']
    )
    if veiw_filter == 'Table':
        table(df_selection)
    else:
        map_data(df_selection, 'Y')

    csv = convert_to_csv(df_selection)

    download1 = st.download_button(
        label="Download Results",
        data=csv,
        file_name=f'ret-download-{today}.csv',
        mime='text/csv'
    )

