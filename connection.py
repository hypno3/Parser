import gspread
from oauth2client.service_account import ServiceAccountCredentials

def init_connection():

    SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    CREDENTIALS_FILE = "api/turing-outrider-404322-25a821927f30.json"

    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
    gc = gspread.authorize(credentials)
    return gc.open_by_key("1KH1n2IyqdxanuCLy370GC_vKGolRtUS4mO5DtDnYTJU").sheet1

def append_data(worksheet, data, cell):
    worksheet.update_acell(cell, data)  #add data to the defined cell

 



