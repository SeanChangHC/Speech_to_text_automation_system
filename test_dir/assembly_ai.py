
import assemblyai as aai
import os
# Function to convert an M4A file to MP3

def convert_to_seconds(time_str):
    # Split the time string into hours, minutes, and seconds
    hours, minutes, seconds = map(int, time_str.split(':'))
    # Calculate total seconds
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return float(total_seconds)
  
def format_time(milliseconds):
    seconds = milliseconds / 1000
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def is_time_between(time, start, end):
    return start <= time <= end

def segment_transformation(segments, speaker_list):
  chunk_timestamp_context = ""
  index = 0
  speaker_content = ""
  for i, segment in enumerate(segments):
    start = float(segment['start'])
    end = float(segment['end'])
    text = segment['text']
    window = 1
    if end - start < 1:
      window = 0.3
    if is_time_between(end-window, float(speaker_list[index][0][0]), float(speaker_list[index][0][1])):
      speaker_content += f"{text} "
    else:
      chunk_timestamp_context += f"{speaker_list[index][1]}: {speaker_content}\n"
      
      if i == len(segments) - 1:
        chunk_timestamp_context += f"{speaker_list[index][1]}: {text}\n"
        break
      index += 1
      speaker_content = f"{text} "

  return chunk_timestamp_context


def transcribe_assembly(file_path):
  ASSEMBLY_API_KEY = os.getenv("ASSEMBLY_API_KEY")
  aai.settings.api_key = ASSEMBLY_API_KEY
  config = aai.TranscriptionConfig(speaker_labels=True)
  print(f'assembly config: {config}')
  transcriber = aai.Transcriber()
  
  print(f'config: {config}')
  transcript = transcriber.transcribe(
    file_path,
    config=config
  )
  def convert_to_seconds(time_str):
    # Split the time string into hours, minutes, and seconds
    hours, minutes, seconds = map(int, time_str.split(':'))
    # Calculate total seconds
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return float(total_seconds)
  def format_time(milliseconds):
    seconds = milliseconds / 1000
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

  formatted_transcript = []
  for utterance in transcript.utterances:
    speaker = utterance.speaker
    start_time = convert_to_seconds(format_time(utterance.start))
    end_time = convert_to_seconds(format_time(utterance.end))
    text = utterance.text
    formatted_utterance = [(start_time, end_time), f"Speaker {speaker}"]
    formatted_transcript.append(formatted_utterance)
    
  return formatted_transcript

# transcribe_assembly('./AIfuture.mp3')