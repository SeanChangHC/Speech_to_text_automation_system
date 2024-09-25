from pydub import AudioSegment
import os

def split_audio(input_file, output_folder, max_size_mb=25, bitrate="128k"):
    """
    Splits an MP3 audio file into chunks not exceeding max_size_mb.

    Args:
        input_file (str): Path to the input MP3 file.
        output_folder (str): Directory where chunks will be saved.
        max_size_mb (int): Maximum size of each chunk in megabytes.
        bitrate (str): Bitrate for the output MP3 files (e.g., "128k").
    
    Returns:
        List[str]: List of file paths to the created audio chunks.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Load the audio file
    print(f"input_file for split_audio: {input_file}")
    audio = AudioSegment.from_mp3(input_file)
    total_size_bytes = os.path.getsize(input_file)
    max_size_bytes = max_size_mb * 1024 * 1024
    print(f"total_size_bytes: {total_size_bytes}")
    # Calculate the number of chunks needed
    num_chunks = -(-total_size_bytes // max_size_bytes)  # Ceiling division
    chunk_length_ms = len(audio) // num_chunks

    chunk_paths = []
    for i in range(num_chunks):
        start_ms = i * chunk_length_ms
        end_ms = (i + 1) * chunk_length_ms if i < num_chunks - 1 else len(audio)
        
        chunk = audio[start_ms:end_ms]
        
        # Export the chunk as an MP3 file
        chunk_filename = f"chunk_{i+1}.mp3"
        chunk_path = os.path.join(output_folder, chunk_filename)
        chunk.export(chunk_path, format="mp3", bitrate=bitrate)
        
        # Verify the exported file size
        chunk_size = os.path.getsize(chunk_path)
        print(f"chunk_size: {chunk_size / (1024*1024):.2f}MB")
        if chunk_size > max_size_bytes:
            print(f"Warning: Chunk {i+1} exceeds {max_size_mb}MB. Actual size: {chunk_size / (1024*1024):.2f}MB")
        
        chunk_paths.append(chunk_path)
        print(f"Created chunk {i+1}/{num_chunks}: {chunk_path}")

    print(f"Split {input_file} into {num_chunks} chunks")
    return chunk_paths

def convert_m4a_to_mp3(input_file, output_file):
    # Load the M4A file
    audio = AudioSegment.from_file(input_file, format='m4a')
    # Export the audio as an MP3 file
    audio.export(output_file, format='mp3')
    print(f"Converted {input_file} to {output_file}")


# Usage
# input_file = "./AIfuture.mp3"
# output_folder = "./download_audio"
# split_audio(input_file, output_folder)

# Example usage
# split_audio("/function/AI Pioneer Shows The Power of AI AGENTS - The Future Is Agentic.mp3", '/function/chunks', 25)
