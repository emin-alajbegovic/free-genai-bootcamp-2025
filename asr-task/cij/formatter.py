"""
Japanese Transcript Aligner - Process a single WhisperX JSON file containing multiple segments
and align it with the accurate transcription using OpenAI.
"""

import os
import json
import argparse
from openai import OpenAI
import time
from typing import List, Dict, Any
import dotenv
from string import Template

dotenv.load_dotenv()

def align_transcript_with_llm(
    original_transcript: str,
    whisperx_transcript: str,
    model: str = "gpt-4o"
) -> Dict[str, Any]:
    """
    Use OpenAI's LLM to align an accurate transcription with WhisperX timecodes.
    
    Args:
        accurate_transcription: The accurate transcription text
        whisperx_data: WhisperX JSON data with character timecodes
        model: OpenAI model to use
        
    Returns:
        Dict containing the aligned segments
    """
    # Initialize OpenAI client
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    # Create a prompt for the LLM
    # load file from fromp promots/system-prompt.txt
    with open("prompts/system-prompt.txt", "r", encoding="utf-8") as f:
        system_prompt = f.read()

    # load file from prompts/user-prompt.txt
    # use a template file so we can inject our values into the prompt:
    with open("prompts/user-prompt.txt", "r", encoding="utf-8") as f:
        user_prompt_template = Template(f.read())

    prompt = user_prompt_template.substitute(
        original_transcript=original_transcript,
        whisperx_text=whisperx_transcript
    )

    # Make the API request
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Low temperature for more deterministic results
            response_format={"type": "json_object"}  # Request JSON format
        )
        
        # Extract the JSON response
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        print(f"Error in LLM alignment: {e}")
        # Try a fallback approach with more specific instructions
        try:
            retry_response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt + "\nOutput ONLY valid JSON with no explanations."},
                    {"role": "user", "content": prompt + "\n\nOutput ONLY a valid JSON object with format: {\"segments\": [{\"text\": \"line 1\", \"start\": 0.1, \"end\": 2.3}, ...]}"}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(retry_response.choices[0].message.content)
            
            if "segments" not in result:
                result = {"segments": result}
            
            return result
            
        except Exception as retry_error:
            print(f"Retry failed: {retry_error}")
            # Return a basic fallback with estimated timings
            return create_fallback_alignment(accurate_transcription)

def create_fallback_alignment(accurate_transcription: str) -> Dict[str, List[Dict[str, Any]]]:
    """Create a basic fallback alignment when LLM alignment fails"""
    print("Using fallback alignment method with estimated timings")
    
    # Split by lines
    lines = [line.strip() for line in accurate_transcription.split('\n') if line.strip()]
    
    # Create a basic alignment with estimated times
    segments = []
    start_time = 0.5  # Approximate starting time
    
    for line in lines:
        # Estimate duration based on character count (rough approximation)
        char_count = len(line)
        duration = char_count * 0.2  # Rough estimate: 0.2 seconds per character
        
        segments.append({
            "text": line,
            "start": start_time,
            "end": start_time + duration
        })
        
        start_time += duration
    
    return {"segments": segments}

def process_transcription(accurate_file: str, whisperx_file: str, output_file: str, model: str = "gpt-4o") -> None:
    """
    Process the transcription files and align them
    
    Args:
        accurate_file: Path to accurate transcription text file
        whisperx_file: Path to whisperx JSON file
        output_file: Path to save the aligned JSON output
        model: OpenAI model to use
    """
    try:
        # Read the files
        with open(accurate_file, 'r', encoding='utf-8') as f:
            original_transcript = f.read()
            
        with open(whisperx_file, 'r', encoding='utf-8') as f:
            whisperx_transcript = f.read()#json.load(f)
        
        # Align the transcription
        result = align_transcript_with_llm(original_transcript, whisperx_transcript, model)
        
        # Save the output
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"Successfully aligned {len(result.get('segments', []))} segments")
        print(f"Output saved to {output_file}")
        
    except Exception as e:
        print(f"Error processing transcription: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Align accurate transcription with WhisperX timecodes')
    parser.add_argument('--accurate', required=True, help='Path to accurate transcription text file')
    parser.add_argument('--whisperx', required=True, help='Path to whisperx JSON file')
    parser.add_argument('--output', required=True, help='Path to save aligned output JSON')
    parser.add_argument('--model', default="gpt-4o", help='OpenAI model to use (default: gpt-4o)')
    
    args = parser.parse_args()
    
    process_transcription(args.accurate, args.whisperx, args.output, args.model)

