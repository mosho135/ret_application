import pandas as pd
import streamlit as st

def wc_active_data():
    df = pd.read_csv('wc_active.csv', encoding='latin-1', low_memory=False)
    return df

def wc_inactive_data():
    df = pd.read_csv('wc_inactive.csv', encoding='latin-1', low_memory=False)
    return df

def wc_semiactive_data():
    df = pd.read_csv('wc_semiactive.csv', encoding='latin-1', low_memory=False)
    return df

def gcm_active_data():
    df = pd.read_csv('gcm_active.csv', encoding='latin-1', low_memory=False)
    return df

def gcm_semiactive_data():
    df = pd.read_csv('gcm_semiactive.csv', encoding='latin-1', low_memory=False)
    return df

def gcm_inactive_data():
    df = pd.read_csv('gcm_inactive.csv', encoding='latin-1', low_memory=False)
    return df

def get_in_plan(df):
    in_plan = df.loc[df['Plan'] == 'In Plan'].copy()
    in_plan = in_plan['Plan'].count()
    return in_plan

def get_out_of_plan(df):
    out_plan = df.loc[df['Plan'] == 'Out Of Plan'].copy()
    out_plan = out_plan['Plan'].count()
    return out_plan
