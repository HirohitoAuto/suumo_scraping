import pandas as pd

import streamlit as st

df = pd.read_csv("data/fukuoka_convinient/formatted/20250323.csv")
st.dataframe(df)
