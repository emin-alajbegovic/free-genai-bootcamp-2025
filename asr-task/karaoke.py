#!/usr/bin/env python3
import json
import subprocess
import os
from pathlib import Path

def load_transcription(json_file):
    """Load the transcription data from the JSON file."""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def format_time(seconds):
    """Format time in seconds to ASS format (H:MM:SS.cc)"""
    hours = int(seconds / 3600)
    minutes = int((seconds % 3600) / 60)
    seconds = seconds % 60
    centiseconds = int((seconds - int(seconds)) * 100)
    return f"{hours}:{minutes:02d}:{int(seconds):02d}.{centiseconds:02d}"

def create_ass_subtitle_file(data, output_file):
    """Create an ASS subtitle file with karaoke highlighting effects."""
    # ASS header
    ass_content = """[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
Timer: 100.0000

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Noto Sans CJK,48,&HFFFFFF,&H000000,&H000000,&H000000,0,0,0,0,100,100,0,0,1,2,0,8,20,20,200,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    
    # Extract word timing information
    words = data['word_segments']
    
    # For each word, create a dialogue line that shows the word in red during its time window
    for i, word in enumerate(words):
        start_time = format_time(word['start'])
        end_time = format_time(word['end'])
        current_word = word['word']
        
        # Create a dialogue line that highlights this word
        # We'll have one dialogue event per word, with the current word highlighted in red
        highlighted_text = ""
        
        # Create the full text with the current word highlighted
        for j, w in enumerate(words):
            if j == i:
                # This is the current word - highlight it
                highlighted_text += "{\\c&H0000FF&}" + w['word'] + "{\\c&HFFFFFF&}"
            else:
                # This is not the current word - normal color
                highlighted_text += w['word']
        
        # Add the dialogue line
        ass_content += f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{highlighted_text}\n"
    
    # Write the ASS content to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(ass_content)
    
    return output_file

def create_karaoke_video(audio_file, json_file, output_file):
    """Create a karaoke video from audio and JSON transcription data."""
    # Load the transcription data
    data = load_transcription(json_file)
    
    # Create an ASS subtitle file
    subtitle_file = "karaoke_subtitles.ass"
    create_ass_subtitle_file(data, subtitle_file)
    
    # Calculate video duration from the last word's end time
    duration = data['word_segments'][-1]['end']
    
    # FFmpeg command to create the video
    ffmpeg_cmd = [
        'ffmpeg',
        '-y',  # Overwrite output file if it exists
        '-i', audio_file,  # Input audio file
        '-f', 'lavfi',  # Use lavfi filter
        '-i', f'color=black:s=1280x720:d={duration}',  # Create black background
        '-vf', f'ass={subtitle_file}:fontsdir=/usr/share/fonts/opentype/noto',  # Add ASS subtitles with font directory
        '-c:a', 'aac',  # Audio codec
        '-shortest',  # End when the shortest input ends
        output_file  # Output file
    ]
    
    # Execute FFmpeg command
    subprocess.run(ffmpeg_cmd, check=True)
    
    # Clean up temporary file
    os.remove(subtitle_file)
    
    print(f"Karaoke video created: {output_file}")

def main():
    # Set file paths
    script_dir = Path(__file__).parent
    audio_file = script_dir / "wake_up_converted.wav"
    json_file = script_dir / "wake_up_words.json"
    output_file = script_dir / "karaoke_output.mp4"
    
    # Create the karaoke video
    create_karaoke_video(str(audio_file), str(json_file), str(output_file))

if __name__ == "__main__":
    main()