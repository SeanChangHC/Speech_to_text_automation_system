import sys
import os
# from test import transcribe_0729

from problem_handle import check_ffmpeg, check_tmp_permissions, verify_file_integrity
# Add the directory containing test.py to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'test_dir'))
# Now we can import the function from test.py
from test_dir import transcribe_0729, Timer

def handler(event, context):
    print("Received event: " + str(event))
    print("transcribe_0729 start")
    
    # Get arguments from the command line
    args = sys.argv[2:]  # Skip the first two arguments which are the script name and the handler
    
    print(f"Arguments: {args}")
    # Pass the arguments to the transcribe_0729 function
    
    ffmpeg_available = check_ffmpeg()
    
    if not ffmpeg_available:
        print("FFmpeg is not available. Exiting.")
    
    tmp_permissions = check_tmp_permissions()
    if not tmp_permissions:
        print("Temporary directory permissions are not set correctly. Exiting.")
    
    # file_integrity = verify_file_integrity('./AIfuture.mp3', '/tmp/AIfuture.mp3')
    # if not file_integrity:
    #     print("File integrity check failed. Exiting.")
        
    with Timer("transcribe_0729"):
        result = transcribe_0729(*args)

    return f'Hello from AWS Lambda using Python {sys.version}! Result: {result}, FFmpeg available: {ffmpeg_available}, tmp_permissions: {tmp_permissions}'

# handler(None, None)