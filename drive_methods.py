import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint as pp
from google.oauth2 import service_account
import streamlit as st
import json

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

#creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json",scope)
# creds = service_account.Credentials.from_service_account_info(
#     st.secrets["gcp_service_account"],
#     scopes=scope
# )

# creds_dict = json.loads(st.secrets["gcp_service_account"]["json"])

# creds = service_account.Credentials.from_service_account_info(
#     creds_dict,
#     scopes=scope
# )
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)
client = gspread.authorize(creds)

sheet = client.open("Contacts").sheet1   
# data = sheet.get_all_records() 
# pp(data)

# row = sheet.row_values(2)
# pp(row)
# col = sheet.col_values(2)
# pp(col)

# insertRow = ["1","Bhabhoria"]
# sheet.insert_row(insertRow,3)
# print("The row has been added")

def write_data(data):
    sheet.insert_row(data,2)

