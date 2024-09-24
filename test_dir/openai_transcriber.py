import os
from openai import OpenAI
from audio_processing import split_audio
import traceback

class transcribe_OPENAI:
  def __init__(self):
    self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    self.client = OpenAI(api_key=self.OPENAI_API_KEY)

  def is_time_between(self, time, start, end):
    return start <= time <= end

  def segment_transformation(self, segments, speaker_list, fp):
    chunk_timestamp_context = ""
    index = 0
    speaker_content = ""
    for i, segment in enumerate(segments):
      try:
        start = float(segment['start'])
        end = float(segment['end'])
        text = segment['text']
        
        # Check if index is within the bounds of speaker_list
        if index >= len(speaker_list):
          print(f"Warning: Reached end of speaker_list at segment {i}. Stopping processing.\n")
          print(f'index: {index}, fp: {fp}\n')
          with open('./debug_output.txt', 'w') as f:
            f.write(f'segments:\n{segments}\n\n')
            f.write(f'speaker_list:\n{speaker_list}\n\n')
          
        speaker_start_time = speaker_list[index][0][0]
        speaker_end_time = speaker_list[index][0][1]
        speaker = speaker_list[index][1]
        window = 1
        if end - start < 1:
          window = 0.3
        if self.is_time_between(end-window, speaker_start_time, speaker_end_time):
          speaker_content += f"{text} "
        else:
          chunk_timestamp_context += f"{speaker}: {speaker_content}\n"
          
          if i == len(segments) - 1:
            chunk_timestamp_context += f"{speaker}: {text}\n"
            break
          index += 1
          speaker_content = f"{text} "
      except Exception as e:
        traceback.print_exc()
        print(f'index:{index}')
        print(f'segments:\n{segments}')
        print(f'speaker_list:\n{speaker_list}')
        
        raise e

    return chunk_timestamp_context

  def transcribe(self, file_path, speaker_list:list, output_dir_root="/tmp/download_audio"):
    transcriptions = ""
    full_text = ""
    # Check the size of the audio file
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > 25:
      print(f'File size: {file_size_mb} MB')
      # Split the audio into chunks
      output_dir = f"{output_dir_root}/chunks"
      print(f'start split_audio')
      
      chunks = split_audio(file_path, output_dir)
      
      # Process each chunk separately
      for chunk_file_path in chunks:
        audio_file = open(chunk_file_path, "rb")
        chunk_transcription = self.client.audio.transcriptions.create(
          model="whisper-1",
          file=audio_file,
          response_format="verbose_json"
        )
        
        print(f'Deleted chunk file path:{chunk_file_path}')
        audio_file.close()
        
        transcriptions += self.segment_transformation(chunk_transcription.segments, speaker_list, chunk_file_path)
        
        full_text += chunk_transcription.text
        os.remove(chunk_file_path)
      
    else:
      # Process the entire audio file
      audio_file = open(file_path, "rb")
      transcription = self.client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="verbose_json"
      )
      full_text += transcription.text
      transcriptions += self.segment_transformation(transcription.segments, speaker_list, file_path)
      audio_file.close()

    return transcriptions, full_text
  
  def generate_corrected_transcript(self, 
                                    temperature,
                                    audio_text,
                                    output_dir, 
                                    system_prompt="You are a helpful assistant. Your task is to correct any spelling discrepancies in the transcribed text. Only add necessary punctuation such as periods, commas, and capitalization, and use only the context provided.",
                                    ):

    response = self.client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        temperature=temperature,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": audio_text
            }
        ]
    )

    return response.choices[0].message.content

  def summarize(self, corrected_text):
    response = self.client.chat.completions.create(
      model="gpt-4o-mini-2024-07-18",
      messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Please summarize the following transcript. The summary should capture the main points and key details of the text while conveying the transcript's intended meaning accurately. Ensure that the summary is well-organized and easy to read.: {corrected_text}"},
      ]
    )
    summary = response.choices[0].message.content
    return summary
  
  def give_it_a_name(self, context):
    response = self.client.chat.completions.create(
      model="gpt-4o-mini-2024-07-18",
      messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Please provide a short, descriptive name for the following transcript. The name should be concise and capture the essence of the text accurately. Ensure that the name is engaging and informative, drawing the reader's attention to the content of the text.: {context}"},
      ]
    )
    name = response.choices[0].message.content
    return name