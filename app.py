import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from data_sets import wc_active_data, wc_semiactive_data, wc_inactive_data, gcm_active_data, gcm_semiactive_data, gcm_inactive_data, get_in_plan, get_out_of_plan
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import datetime as dt
import hmac
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

today = dt.datetime.today()
today = today.strftime('%Y%m%d%H%M%S')

# Password check

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if "password" in st.session_state:
            if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
                st.session_state["password_correct"] = True
                del st.session_state["password"]  # Don't store the password.
            else:
                st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

# TODO: add in the areas for the map view. And look to deploy and web application and test
# TODO: Add a download button for the HTML map for quicker loading time

#set page
st.set_page_config(page_title="Mercedes-Benz Rentention", page_icon="🌎", layout="wide")

# Set page header
st.header('MERCEDES-BENZ - RETENTION', divider='blue')
st.header('')


@st.cache_resource
def get_gspread_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["google"], scope
    )
    client = gspread.authorize(creds)
    return client

# @st.cache_data
# def fetch_sheet_data(_sheet, name):
#     worksheet = _sheet.get_all_records()
#     df = pd.DataFrame(worksheet)
#     return df
#
#
# client = get_gspread_client()
# st.cache_data.clear()
# invoice_workbook = client.open("mbwc_map_data")
# wc_active_df = invoice_workbook.worksheet("wc_active")
# wc_semiactive_df = invoice_workbook.worksheet("wc_semiactive")
# wc_inactive_df = invoice_workbook.worksheet("wc_inactive")
# gcm_active_df = invoice_workbook.worksheet("gcm_active")
# gcm_semiactive_df = invoice_workbook.worksheet("gcm_semiactive")
# gcm_inactive_df = invoice_workbook.worksheet("gcm_inactive")
#
# #Get the data
#
# @st.cache_data
# def get_data(d_type):
#     if d_type == 'WA':
#         df = fetch_sheet_data(wc_active_df, "wc_active")
#         return df
#     if d_type == 'WS':
#         df = fetch_sheet_data(wc_semiactive_df, "wc_semiactive")
#         return df
#     if d_type == 'WI':
#         df = fetch_sheet_data(wc_inactive_df, "wc_inactive")
#         return df
#     if d_type == 'GA':
#         df = fetch_sheet_data(gcm_active_df, "gcm_active")
#         return df
#     if d_type == 'GS':
#         df = fetch_sheet_data(gcm_semiactive_df, "gcm_semiactive")
#         return df
#     if d_type == 'GI':
#         df = fetch_sheet_data(gcm_inactive_df, "gcm_inactive")
#         return df

@st.cache_data(ttl=300)
def fetch_sheet_data(_sheet):
    worksheet = _sheet.get_all_records()
    df = pd.DataFrame(worksheet)
    return df


@st.cache_resource
def get_sheet():
    _client = get_gspread_client()
    # TODO: Change the sheet source when going live
    return _client.open("mbwc_map_data_test").sheet1

sheet = get_sheet()


def get_data(d_type, data_sheet):
    mapping = {
        "WA": "wc_active",
        "WS": "wc_semiactive",
        "WI": "wc_inactive",
        "GA": "gcm_active",
        "GS": "gcm_semiactive",
        "GI": "gcm_inactive",
    }

    _df = fetch_sheet_data(data_sheet)

    if d_type == 'WA':
        w_df = _df.loc[(_df['Branch'] != 'Mercedes-Benz Grand Central Motors') & (_df['Active_Status'] == 'Active')].copy()
        return w_df
    if d_type == 'WS':
        w_df = _df.loc[(_df['Branch'] != 'Mercedes-Benz Grand Central Motors') & (_df['Active_Status'] == 'Semi-Active')].copy()
        return w_df
    if d_type == 'WI':
        w_df = _df.loc[(_df['Branch'] != 'Mercedes-Benz Grand Central Motors') & (_df['Active_Status'] == 'Inactive')].copy()
        return w_df
    if d_type == 'GA':
        g_df = _df.loc[(_df['Branch'] == 'Mercedes-Benz Grand Central Motors') & (_df['Active_Status'] == 'Active')].copy()
        return g_df
    if d_type == 'GS':
        g_df = _df.loc[(_df['Branch'] == 'Mercedes-Benz Grand Central Motors') & (_df['Active_Status'] == 'Semi-Active')].copy()
        return g_df
    if d_type == 'GI':
        g_df = _df.loc[(_df['Branch'] == 'Mercedes-Benz Grand Central Motors') & (_df['Active_Status'] == 'Inactive')].copy()
        return g_df



# @st.cache_data(ttl=300)  # cache for 5 minutes
# def load_all_data():
#     client = get_gspread_client()
#     workbook = client.open("mbwc_map_data")
#
#     sheet_names = [
#         "wc_active",
#         "wc_semiactive",
#         "wc_inactive",
#         "gcm_active",
#         "gcm_semiactive",
#         "gcm_inactive",
#     ]
#
#     data = {}
#
#     for name in sheet_names:
#         worksheet = workbook.worksheet(name)
#         records = worksheet.get_all_records()
#         data[name] = pd.DataFrame(records)
#
#     return data
#
#
# def get_data(d_type):
#     mapping = {
#         "WA": "wc_active",
#         "WS": "wc_semiactive",
#         "WI": "wc_inactive",
#         "GA": "gcm_active",
#         "GS": "gcm_semiactive",
#         "GI": "gcm_inactive",
#     }
#
#     all_data = load_all_data()
#
#     sheet_name = mapping.get(d_type)
#
#     if sheet_name is None:
#         return pd.DataFrame()  # safe fallback
#
#     return all_data.get(sheet_name, pd.DataFrame())

#option menu
from streamlit_option_menu import option_menu
with st.sidebar:
    selected=option_menu(
        menu_title="MAIN MENU",
        options=["WC Active Customers", "WC Semi-Active Customers", "WC Inactive Customers", "GCM Active Customers", "GCM Semi-Active Customers", "GCM Inactive Customers"],
        icons=["book", "book", "book", "book", "book", "book"],
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

    branch_opts       = av_options(df, 'Branch')
    sdealer_opts      = av_options(df, 'Selling_Dealer')
    stype_opts        = av_options(df, 'Selling_ActionType')
    vehicle_opts      = av_options(df, 'Vehicles')
    area_opts         = av_options(df, 'Area')

    dealer = st.sidebar.multiselect(
        label='Filter Current Dealer',
        options=branch_opts,
        default=branch_opts[1:],
        key="branch_options",
        format_func=lambda x: "All" if x == -1 else f"{x}",
    )

    sell_dealer = st.sidebar.multiselect(
        label='Filter Selling Dealer',
        options=sdealer_opts,
        default=sdealer_opts[1:],
        key="sdealer_options",
        format_func=lambda x: "All" if x == -1 else f"{x}",
    )

    sell_dealer_actiontype = st.sidebar.multiselect(
        label='Filter Selling Dealer New / Used',
        options=stype_opts,
        default=stype_opts[1:],
        key="stype_options",
        format_func=lambda x: "All" if x == -1 else f"{x}",
    )

    vehicle = st.sidebar.multiselect(
        label='Filter Model',
        options=vehicle_opts,
        default=vehicle_opts[1:],
        key="model_options",
        format_func=lambda x: "All" if x == -1 else f"{x}",
    )

    area = st.sidebar.multiselect(
        label='Filter Area',
        options=area_opts,
        default=area_opts[1:],
        key="area_options",
        format_func=lambda x: "All" if x == -1 else f"{x}",
    )

    df_selection = df.query(
        "Branch==@dealer & Vehicles==@vehicle & Area==@area & Selling_Dealer==@sell_dealer & Selling_ActionType==@sell_dealer_actiontype"
    )

    if st.session_state.show_filter:
        v_age_r_opts     = av_options(df_selection, 'Vehicle_Age_Reg_Date')
        v_age_p_opts     = av_options(df_selection, 'Vehicle_Age_Plan')
        age_opts         = av_options(df_selection, 'Age_Group')
        multi_owner_opts = av_options(df_selection, 'Multiple_Ownership')
        company_opts     = av_options(df_selection, 'Company_Owned')
        salesexec_opts   = av_options(df_selection, 'Sales_Executive')

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            v_age_r = st.multiselect(
                label='Vehicle Age (Reg Date)',
                options=v_age_r_opts,
                default=v_age_r_opts[1:],
                key="v_age_r_options",
                format_func=lambda x: "All" if x == -1 else f"{x}",
            )
        with col2:
            v_age_p = st.multiselect(
                label='Vehicle Age (Plan End Date)',
                options=v_age_p_opts,
                default=v_age_p_opts[1:],
                key="v_age_p_options",
                format_func=lambda x: "All" if x == -1 else f"{x}",
            )
        with col3:
            age_group = st.multiselect(
                label='Customer Age Group',
                options=age_opts,
                default=age_opts[1:],
                key="age_options",
                format_func=lambda x: "All" if x == -1 else f"{x}",
            )
        with col4:
            multi_owner = st.multiselect(
                label='Multiple Ownership',
                options=multi_owner_opts,
                default=multi_owner_opts[1:],
                key="multi_owner_options",
                format_func=lambda x: "All" if x == -1 else f"{x}",
            )
        with col5:
            company_owned = st.multiselect(
                label='Company Owned',
                options=company_opts,
                default=company_opts[1:],
                key="company_options",
                format_func=lambda x: "All" if x == -1 else f"{x}",
            )

        sales_executive = st.multiselect(
            label='Sales Executive',
            options=salesexec_opts,
            default=salesexec_opts[1:],
            key="salesexec_options",
            format_func=lambda x: "All" if x == -1 else f"{x}",
        )

        df_selection = df.query(
            "Branch==@dealer & Vehicles==@vehicle & Area==@area & Selling_Dealer==@sell_dealer & Selling_ActionType==@sell_dealer_actiontype & Vehicle_Age_Reg_Date==@v_age_r & Vehicle_Age_Plan==@v_age_p & Age_Group==@age_group & Multiple_Ownership==@multi_owner & Company_Owned==@company_owned & Sales_Executive==@sales_executive"
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

    if st.session_state.checked:
        pivot_df = pd.crosstab(df['Vehicles'], df['Mileage Category']).reset_index()
        pivot_df = pivot_df.rename(columns={'Vehicles': 'Group'}).sort_values('Group')

        mileage_cols = [c for c in pivot_df.columns if c != 'Group']

        col_defs = [
            {
                "field": "Group",
                "headerName": "Group",
                "pinned": "left",
                "sortable": True,
                "sort": "asc",
                "filter": True,
                "resizable": True,
                "minWidth": 150,
            }
        ]
        for col in mileage_cols:
            col_defs.append({
                "headerName": col,
                "children": [
                    {
                        "field": col,
                        "headerName": "Total",
                        "width": 120,
                        "type": "numericColumn",
                        "resizable": True,
                        "sortable": True,
                    }
                ],
            })

        grid_options = {
            "columnDefs": col_defs,
            "defaultColDef": {"resizable": True, "sortable": True, "filter": True},
        }

        AgGrid(pivot_df, gridOptions=grid_options, height=1000, fit_columns_on_grid_load=ColumnsAutoSizeMode.FIT_CONTENTS)
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

# Clear filter session state when the page changes so stale WC keys don't
# bleed into GCM views (and vice versa), which would cause queries to return 0 rows.
if st.session_state.get('current_page') != selected:
    filter_keys = [
        'branch_options', 'sdealer_options', 'stype_options',
        'model_options', 'area_options', 'max_selections',
        'v_age_r_options', 'v_age_p_options', 'age_options',
        'multi_owner_options', 'company_options', 'salesexec_options',
        'show_filter',
    ]
    for _key in filter_keys:
        if _key in st.session_state:
            del st.session_state[_key]
    st.session_state['current_page'] = selected

if selected=='WC Active Customers':
    df = get_data('WA', sheet)
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
elif selected=='WC Semi-Active Customers':
    df = get_data('WS', sheet)
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
    df = get_data('WI', sheet)
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
    df = get_data('GA', sheet)
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
elif selected=='GCM Semi-Active Customers':
    df = get_data('GS', sheet)
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
    df = get_data('GI', sheet)
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

