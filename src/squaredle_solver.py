"""
Squaredle Solver - Automated daily puzzle solver

This script fetches the daily Squaredle puzzle from the API, decodes the
encoded words using base64 and custom alphabet substitution, and outputs
the solution words.
"""

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
    
    print(f"Found puzzle for {today_date_str}")
    print(f"Required words data: {len(word_scores)} characters")
    print(f"Optional words data: {len(optional_word_scores)} characters")
    
    # TODO: Implement actual decoding logic
    # For now, return empty lists until decoding is implemented
    return [], []


def display_results(required_words, optional_words):
    """Display puzzle results"""
    print(f"\n{'='*50}")
    print(f"SQUAREDLE SOLUTION - {datetime.now().strftime('%Y-%m-%d')}")
    print(f"{'='*50}")
    
    if required_words:
        print(f"\nRequired Words ({len(required_words)}):")
        for word in sorted(required_words):
            print(f"• {word}")
    
    if optional_words:
        print(f"\nOptional Words ({len(optional_words)}):")
        for word in sorted(optional_words):
            print(f"• {word}")
    
    total_words = len(required_words) + len(optional_words)
    print(f"\nTotal words found: {total_words}")
    print(f"{'='*50}")



def main():
    """Main entry point"""
    try:
        required_words, optional_words = solve_puzzle()
        display_results(required_words, optional_words)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()