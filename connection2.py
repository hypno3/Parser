import os
import re
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import tkinter as tk
from tkinter import filedialog
import gspread

def select_file():
    # Show the window of the file selection
    file_path = filedialog.askopenfilename(
        title="Select JSON file",
        filetypes=[("JSON files", "*.json")]
    )
    return file_path

def upload_file():
    input("Please specify the JSON files for Google Sheets API, press ENTER to continue...")
    upload_directory = "api/"
    file_path = select_file()
    if file_path:  # If the file has been selected
        # Check the file exnetsion
        if not file_path.lower().endswith('.json'):
            print("Selected file is not JSON file.")
            return
        # File name
        file_name = os.path.basename(file_path)

        # Path to the file in the upload directory
        destination = os.path.join(upload_directory, file_name)

        # File copy process to the destination  folder (api/)
        with open(file_path, 'rb') as f_source:
            with open(destination, 'wb') as f_destination:
                f_destination.write(f_source.read())

        print(f"File {file_name} has been successfully uploaded to {upload_directory}")
        return file_name
    else:
        print("The file has not been selected")

def init_connection(upload_file):
    file_name = upload_file()
    SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    CREDENTIALS_FILE = "api/" + file_name
    shared_email = input("Enter your email to create the SF_PARSING shared folder on your drive and put Google Sheet there\n")
    credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPE)
    
    # Use googleapiclient for the work with Google Drive API
    drive_service = build('drive', 'v3', credentials=credentials)
    gspread_client = gspread.authorize(credentials)
    
    # Folder existance check
    folder_name = 'SF_PARSING'
    response = drive_service.files().list(
        q=f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}'",
        spaces='drive',
        fields='nextPageToken, files(id, name)'
    ).execute()
    folder = None
    for file in response.get('files', []):
        # Check if the folder with this name already exists
        if file.get('name') == folder_name:
            folder = file
            print(f"Found existing folder: {folder_name}")
            folder_id = folder.get('id')
            break
    
    # Create folder in Google Drive if it does not exist
    if not folder:
        folder_metadata = {
            'name': 'SF_PARSING',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
        folder_id = folder.get('id')
        print(f"Creating new folder, Folder ID: {folder.get('id')}")

        # Share the permission to folder
        user_permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': shared_email
        }
        drive_service.permissions().create(
            fileId=folder.get('id'),
            body=user_permission,
            fields='id',
        ).execute()

    sheet_name = "parsing_data"

    # Look for the Google Sheet file within the folder
    response = drive_service.files().list(
        q=f"'{folder_id}' in parents and name='{sheet_name}' and mimeType='application/vnd.google-apps.spreadsheet'",
        fields="files(id, name)"
    ).execute()
    files = response.get('files', [])
    
    # Check if the file already exists
    if files:
        print(f"File '{sheet_name}' found in folder '{folder_name}'.")
        spreadsheet_id = files[0].get('id')
        spreadsheet = gspread_client.open_by_key(spreadsheet_id)
    else:
        print(f"Creating new Google Sheet '{sheet_name}' in folder '{folder_name}'.")
        spreadsheet = gspread_client.create(sheet_name, folder_id=folder_id)
        spreadsheet.share(shared_email, perm_type='user', role='writer')

    # Get the first worksheet of the spreadsheet
    worksheet = spreadsheet.get_worksheet(0)
    return worksheet
        
def append_data_rows(worksheet, row_data):
    worksheet.append_row(row_data, value_input_option='USER_ENTERED')

def append_data_cells(worksheet, data, cell):
    worksheet.update_acell(cell, data)  #add data to the defined cell



