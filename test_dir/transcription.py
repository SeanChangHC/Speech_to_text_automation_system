
from openai import OpenAI
import os
from email.mime.text import MIMEText
import traceback
from datetime import datetime
from googleapiclient.discovery import build
from dotenv import load_dotenv
from .openai_transcriber import transcribe_OPENAI
from .assembly_ai import transcribe_assembly
from .email_utils import send_email
from .drive_utils import authenticate, list_files_in_folder, download_file, delete_file
from .timer import Timer
import shutil

# from pydub import AudioSegment

# Load environment variables from .env file
load_dotenv()
    
def transcribe_0729(*args):
# Extend the recipients list with additional arguments if any
  
  if args:
      recipients.extend(args)
  
  # email setup
  contents = []
  app_passowrd = os.getenv("app_password")
  sender = "smalldragon89@gmail.com"
  recipients = ["smalldragon89@gmail.com"]
  
  # driver
  driver_creds = authenticate()
  service = build("drive", "v3", credentials=driver_creds)
  folder_id = '16Lp1cRzG78S2srPmtZJYpMuunlbCSASu'
  
  # local setup
  output_dir = '/tmp/download_audio'  # Replace with your desired output directory
  
  if not os.path.exists(output_dir):
      os.makedirs(output_dir)
  
  date_string = datetime.now().strftime('%Y%m%d')
  
  # list all files in the driver folder
  files_on_drive_folder = list_files_in_folder(service, folder_id)

  # if no files found, return
  if not files_on_drive_folder:
    print(f"No files found in the drive folder: {folder_id}.")
    return f"No files found in the drive folder: {folder_id}."
  
  # handle each file
  for file in files_on_drive_folder:
    # download the file to output_dir
    with Timer("Download"):
      print(f"Downloading {file['name']} id:({file['id']})")
      downloaded_fp = download_file(service, file['id'], file['name'], output_dir)
    
  # TESTING
  # downloaded_fp = "./test_dir/AIfuture.mp3"
  # output_dir = './test_dir/download_audio'
  # TESTING
  
  with Timer("transcribe_assembly"):
    # get the speakers using assembly
    speaker_list = transcribe_assembly(downloaded_fp)
    print(f'speaker_list:\n{speaker_list}')
    

    # TESTING
    # import json
    # speaker_list_file = 'speaker_list.json'
    # with open(speaker_list_file, 'w') as f:
    #     json.dump(speaker_list, f, indent=2)
    
    # print(f"Speaker list exported to {speaker_list_file}")
    # with open('./speaker_list.json', 'r') as f:
    #     speaker_list = json.load(f)
    
    # print(f"Speaker list loaded from speaker_list.json")
    # print(f"Number of entries in speaker_list: {len(speaker_list)}")
    # TESTING
    
  # transcribe the file
  with Timer("transcribe"):
    print("Transbribe with OpenAI start!")
    # # openai
    openai_transcriber = transcribe_OPENAI()
    speaker_content, original_text = openai_transcriber.transcribe(downloaded_fp, speaker_list, output_dir)
    subject = f'{openai_transcriber.give_it_a_name(speaker_content)}_{date_string}'
    print(f'subject:{subject}\n\n\n')
    print(f'speaker_content:\n{speaker_content}\n\n\n')
    
    # TESTING
    # Export the speaker content to a JSON file
    # speaker_content_file = 'speaker_content.json'
    # with open(speaker_content_file, 'w') as f:
    #     json.dump(speaker_content, f, indent=2)
    
    # print(f"Speaker content exported to {speaker_content_file}")
    # TESTING
    
    
  with Timer("send_email"):
    send_email(subject, speaker_content, sender, recipients, app_passowrd)
    
  # delete file
  # print(f'delete driver file')
  # delete_file(service, file['id'])
  
  print(f'deleting {downloaded_fp}')
  os.remove(downloaded_fp)
    
  # Remove the output directory
  print(f'deleting {output_dir}')
  shutil.rmtree(output_dir)
  
  return "Success!"




