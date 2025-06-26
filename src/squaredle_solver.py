"""
Squaredle Solver - Automated daily puzzle solver

This script fetches the daily Squaredle puzzle from the API, decodes the
encoded words using base64 and custom alphabet substitution, and outputs
the solution words.
Credits for decoding cipher logic : https://gist.github.com/utaha1228/b42516e67bb90d2bf06554d29243165a
"""

import base64
import json
import re
import sys
from datetime import datetime
import requests

API_URL = "https://squaredle.app/api/today-puzzle-config.js"

def fetch_puzzle_data():
    """Fetch puzzle data from Squaredle API"""
    response = requests.get(API_URL)
    response.raise_for_status()
    return response.text


def extract_puzzle_info(js_content):
    """Extract date and config from JavaScript response"""
    date_match = re.search(r'gTodayDateStr\s*=\s*["\']([^"\']+)["\']', js_content)
    if not date_match:
        raise ValueError("Could not find gTodayDateStr in response")
    
    config_match = re.search(r'gPuzzleConfig\s*=\s*(\{.*?\});', js_content, re.DOTALL)
    if not config_match:
        raise ValueError("Could not find gPuzzleConfig in response")
    
    today_date_str = date_match.group(1) # capture only the date
    puzzle_config = json.loads(config_match.group(1)) # extract entire json under gPuzzleConfig
    
    return today_date_str, puzzle_config


def decode_squaredle_words(encoded_string):
    """Decode Squaredle words using custom alphabet and base64 decoding"""
    if not encoded_string:
        return []
    
    try:
        alphabet = "5pyf0gcrl1a9oe3ui8d2htn67sqjkxbmw4vzPYFGCRLAOEUIDHTNSQJKXBMWVZ"
        
        # Apply cipher: shift each character by -12 positions in the alphabet
        def cipher_char(char):
            index = alphabet.find(char)
            if index == -1:
                return char  # Character not in alphabet, return as-is
            return alphabet[(index - 12 + len(alphabet)) % len(alphabet)]
        
        # Apply cipher to entire string
        cipher_decoded = ''.join(cipher_char(char) for char in encoded_string)
        
        # Then decode from base64
        decoded_bytes = base64.b64decode(cipher_decoded)
        decoded_text = decoded_bytes.decode('utf-8')
        
        return [decoded_text.strip()] if decoded_text.strip() else []
        
    except Exception as e:
        print(f"Warning: Failed to decode words: {e}", file=sys.stderr)
        return []


def solve_puzzle():
    """Solve the current Squaredle puzzle"""
    print("Fetching puzzle data...")
    js_content = fetch_puzzle_data()
    
    print("Extracting puzzle configuration...")
    today_date_str, puzzle_config = extract_puzzle_info(js_content)
    
    # Get puzzle data
    puzzles = puzzle_config['puzzles']
    if today_date_str not in puzzles:
        # Use latest available date
        today_date_str = max(puzzles.keys())
    
    today_puzzle = puzzles[today_date_str]
    word_scores = today_puzzle['wordScores']
    optional_word_scores = today_puzzle.get('optionalWordScores', '')
    
    # Extract Word of the Day (no cipher applied)
    word_of_the_day = ''
    if 'wordOfTheDay' in today_puzzle and 'term' in today_puzzle['wordOfTheDay']:
        word_of_the_day = today_puzzle['wordOfTheDay']['term']
    
    print(f"Found puzzle for {today_date_str}")
    print(f"Required words data: {len(word_scores)} characters")
    print(f"Optional words data: {len(optional_word_scores)} characters")
    
    # Decode the solution
    print("Decoding words...")
    required_words = decode_squaredle_words(word_scores)
    optional_words = decode_squaredle_words(optional_word_scores)
    
    print(f"Successfully decoded puzzle solutions!")
    
    return required_words, optional_words, word_of_the_day


def display_results(required_words, optional_words, word_of_the_day):
    """Display puzzle results"""
    print(f"\n{'='*50}")
    print(f"SQUAREDLE SOLUTION - {datetime.now().strftime('%Y-%m-%d')}")
    print(f"{'='*50}")

    # Bonus word of the day
    if word_of_the_day:
        print(f"\nBonus Word of the Day: {word_of_the_day}")
    
    if required_words:
        print(f"\nRequired Words:")
        for words_text in required_words:
            print(f"{words_text}")
    
    if optional_words:
        print(f"\nOptional Words:")
        for words_text in optional_words:
            print(f"{words_text}")
    
    # Count total individual words
    total_required = len(required_words[0].split(',')) if required_words and required_words[0] else 0
    total_optional = len(optional_words[0].split(',')) if optional_words and optional_words[0] else 0
    
    print(f"\nTotal words found: {total_required + total_optional}")
    print(f"{'='*50}")



def main():
    """Main entry point"""
    try:
        required_words, optional_words, wotd = solve_puzzle()
        display_results(required_words, optional_words, wotd)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()