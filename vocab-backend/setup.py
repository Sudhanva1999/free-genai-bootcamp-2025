#!/usr/bin/env python
import os
import sys
from models.database import Database

# Initial groups to populate
INITIAL_GROUPS = [
    "Colors",
    "Cities",
    "Parks",
    "Animals",
    "Fruits",
    "Vegetables",
    "Numbers",
    "Days of Week",
    "Months",
    "Family Relations",
    "Basic Marathi Vocabulary"
]

# Some initial words for each group
INITIAL_WORDS = {
    "Colors": [
        {"english": "red", "marathi": "लाल"},
        {"english": "blue", "marathi": "निळा"},
        {"english": "green", "marathi": "हिरवा"},
        {"english": "yellow", "marathi": "पिवळा"},
        {"english": "black", "marathi": "काळा"}
    ],
    "Basic Marathi Vocabulary": [
        {"english": "water", "marathi": "पाणी"},
        {"english": "food", "marathi": "अन्न"},
        {"english": "hello", "marathi": "नमस्कार"},
        {"english": "thank you", "marathi": "धन्यवाद"},
        {"english": "yes", "marathi": "हो"}
    ]
}

def setup_database():
    """Initialize the database with predefined groups and words."""
    print("Setting up the database...")
    
    # Create database instance and initialize tables
    db = Database()
    db.initialize_db()
    
    # Add groups and words
    for group_name in INITIAL_GROUPS:
        print(f"Adding group: {group_name}")
        group_id = db.add_group(group_name)
        
        # Add words if available for this group
        if group_name in INITIAL_WORDS:
            print(f"Adding words for group: {group_name}")
            db.add_words(group_id, INITIAL_WORDS[group_name])
    
    print("Database setup complete!")

if __name__ == "__main__":
    setup_database()