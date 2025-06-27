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
from pathlib import Path
import requests

API_URL = "https://squaredle.app/api/today-puzzle-config.js"

def extract_puzzle_data():
    """Fetch puzzle data from Squaredle API and extract date and config"""
    response = requests.get(API_URL)
    response.raise_for_status()
    js_content = response.text
    
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
    print("Extracting puzzle data...")
    today_date_str, puzzle_config = extract_puzzle_data()
    
    # Get puzzle data
    puzzles = puzzle_config['puzzles']
    if today_date_str not in puzzles:
        # Use latest available date
        today_date_str = max(puzzles.keys())
    
    today_puzzle = puzzles[today_date_str]
    word_scores = today_puzzle['wordScores']
    
    # Extract Word of the Day (no cipher applied)
    word_of_the_day = ''
    if 'wordOfTheDay' in today_puzzle and 'term' in today_puzzle['wordOfTheDay']:
        word_of_the_day = today_puzzle['wordOfTheDay']['term']
    
    print(f"Found puzzle for {today_date_str}")
    
    # Decode the solution
    print("Decoding words...")
    required_words = decode_squaredle_words(word_scores)
    
    print(f"Successfully decoded puzzle solutions!")
    
    return required_words, word_of_the_day

def group_words_by_length(words_list):
    """Group words by their length"""
    if not words_list or not words_list[0]:
        return {}
    
    # Split comma-separated word lists into individual words
    all_words = []
    for words_text in words_list:
        if words_text:
            all_words.extend([word.strip() for word in words_text.split(',')])
    
    # Group by length
    grouped = {}
    for word in all_words:
        if word:  # Skip empty strings
            length = len(word)
            if length not in grouped:
                grouped[length] = []
            grouped[length].append(word.lower())
    
    # Sort words within each group
    for length in grouped:
        grouped[length].sort()
    
    return grouped


def hide_word(word):
    """Hide a word with asterisks, showing only first and last letters"""
    # Reveal letters based on word length
    if len(word) in (4, 5):
        middle_length = len(word) - 2
        return word[0] + '*' * middle_length + word[-1]
    elif len(word) in (6, 7):
        middle_length = len(word) - 3
        return word[0] + word[1] + '*' * middle_length + word[-1]
    else:  
        middle_length = len(word) - 4
        return word[0] + word[1] + '*' * middle_length + word[-2] + word[-1]

def generate_html_content(required_groups, word_of_the_day):
    """Generate HTML content for word groups"""
    html_parts = []
    
    # Required words
    for length in sorted(required_groups.keys()):
        words = required_groups[length]
        word_divs = []
        for word in words:
            hidden = hide_word(word)
            word_divs.append(f'<div class="word" data-word="{word}" data-hidden="{hidden}">{hidden}</div>')
        
        html_parts.append(f'''
        <div class="word-group">
            <h2>⭐ {length} Letter Words</h2>
            <div class="word-list">
                {' '.join(word_divs)}
            </div>
        </div>
        ''')

    # Word of the day section
    if word_of_the_day:
        wotd_hidden = hide_word(word_of_the_day.lower())
        html_parts.append(f'''
            <div class="word-group">
                <h2>💎 Bonus Word of the Day</h2>
                <div class="word-list">
                    <div class="word" data-word="{word_of_the_day.lower()}" data-hidden="{wotd_hidden}">{wotd_hidden}</div>
                </div>
            </div>
        ''')
    
    return '\n'.join(html_parts)


def generate_html_page(required_words, word_of_the_day):
    """Generate the complete HTML page"""
    required_groups = group_words_by_length(required_words)
    html_content = generate_html_content(required_groups, word_of_the_day)
    
    template_path = Path(__file__).parent.parent / "docs" / "template.html"
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    current_date = datetime.now().strftime('%A, %B %d, %Y')
    final_html = template.replace('{{DATE}}', current_date).replace('{{CONTENT}}', html_content)
    
    output_path = Path(__file__).parent.parent / "docs" / "index.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    return required_groups


def display_results(required_words, word_of_the_day):
    """Display puzzle results and generate HTML"""
    print(f"\n{'='*50}")
    print(f"SQUAREDLE SOLUTION - {datetime.now().strftime('%Y-%m-%d')}")
    print(f"{'='*50}")

    try:
        required_groups = generate_html_page(required_words, word_of_the_day)
        
        # Bonus word of the day
        if word_of_the_day:
            print(f"\nBonus Word of the Day: {word_of_the_day}")
        
        # Display required words by length
        if required_groups:
            print(f"\nRequired Words:")
            for length in sorted(required_groups.keys()):
                print(f"  {length}-letter words ({len(required_groups[length])}): {', '.join(required_groups[length])}")
        
        # Count totals
        total_required = sum(len(words) for words in required_groups.values())
        total_bonus = 1 if word_of_the_day else 0
        
        print(f"\nTotal words found: {total_required + total_bonus}")
        print(f"  - Required: {total_required}")
        print(f"  - Bonus: {total_bonus}")
        
        print("HTML page generated successfully!")
        
    except Exception as e:
        print(f"Failed to generate HTML: {e}")
    
    print(f"{'='*50}") # formatting console solution

def main():
    try:
        required_words, wotd = solve_puzzle()
        display_results(required_words, wotd)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()