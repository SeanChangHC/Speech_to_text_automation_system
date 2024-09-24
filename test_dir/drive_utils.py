# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

import os.path
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# import logging

# logging.basicConfig(level=logging.DEBUG)

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]


def list_files_in_folder(service, folder_id=""):
    if not folder_id:
        results = (service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute())
    else:
        query = f"'{folder_id}' in parents"
        results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        return []
    else:
        print(f'List all files in the folder {folder_id}:')
        for item in items:
            print(f"{item['name']} ({item['id']})")
    return items
            
def download_file(service, file_id, file_name, output_dir):
    """Download a file from Google Drive."""
    request = service.files().get_media(fileId=file_id)
    file_path = os.path.join(output_dir, file_name)
    with io.FileIO(file_path, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")
            return file_path

def download_all_files_in_folder(service, folder_id, output_dir):
    """Download all files in a specified folder."""
    files = list_files_in_folder(service, folder_id)
    if not files:
        print("No files found.")
        return
    for file in files:
        print(f"Downloading {file['name']} ({file['id']})")
        downloaed_fp = download_file(service, file['id'], file['name'], output_dir)

def authenticate():
    creds = None
    script_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(script_dir, "..", "credentials", "0729_token.json")
    new_token_path = "/tmp/0729_token.json"
    
    client_secrets_path = os.path.join(script_dir, "..", "credentials", "0729_credentials.json")
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except:
                os.remove(token_path)
                creds = None
        
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(new_token_path, "w") as token:
            token.write(creds.to_json())
    return creds

def delete_file(service, file_id):
    """
    Deletes a file from Google Drive given its file ID.

    Parameters:
    service (Resource): The Google Drive API service instance.
    file_id (str): The ID of the file to be deleted.

    Returns:
    None
    """
    try:
        service.files().delete(fileId=file_id).execute()
        print(f"File {file_id} deleted successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
  """Shows basic usage of the Drive v3 API.
  Prints the names and ids of the first 10 files the user has access to.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  creds = authenticate()
  try:
    service = build("drive", "v3", credentials=creds)
    
    folder_id = '16Lp1cRzG78S2srPmtZJYpMuunlbCSASu' # Replace with your folder ID
    
    output_dir = './download_audio'  # Replace with your desired output directory
    
    list_files_in_folder(service, folder_id)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    download_all_files_in_folder(service, folder_id, output_dir)
    
  except HttpError as error:
    # TODO(developer) - Handle errors from drive API.
    print(f"An error occurred: {error}")

# if __name__ == "__main__":
#   main()