#!/usr/bin/env python3
"""
Script to check all categories and their question counts
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.question_manager import question_manager

print("=" * 80)
print("ANALYZING YOUR QUESTION CATEGORIES")
print("=" * 80)

# Get all categories
categories = question_manager.get_question_categories()
print(f"\nTotal Categories: {len(categories)}\n")

# Get count for each category
category_data = []
for cat in categories:
    count = question_manager.get_question_count(category=cat)
    category_data.append((cat, count))

# Sort by count descending
category_data.sort(key=lambda x: x[1], reverse=True)

# Display all categories
for i, (cat, count) in enumerate(category_data, 1):
    print(f"{i:2d}. {cat:<50} ({count:3d} questions)")

print("\n" + "=" * 80)
print(f"TOTAL: {sum(c[1] for c in category_data)} questions across {len(categories)} categories")
print("=" * 80)

