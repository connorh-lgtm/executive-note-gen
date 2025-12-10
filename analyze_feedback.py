#!/usr/bin/env python3
"""
Simple script to analyze feedback data
"""
import json
import glob
from collections import Counter
from datetime import datetime

def analyze_feedback():
    feedback_files = glob.glob('feedback/*.json')
    
    if not feedback_files:
        print("No feedback files found!")
        return
    
    print(f"📊 Feedback Analysis")
    print(f"=" * 50)
    print(f"Total feedback submissions: {len(feedback_files)}")
    print()
    
    feedback_types = []
    message_types = []
    has_improvements = 0
    improvement_examples = []
    
    for file in sorted(feedback_files):
        try:
            with open(file) as f:
                data = json.load(f)
                feedback_types.append(data['feedback_type'])
                message_types.append(data['metadata']['message_type'])
                
                if data.get('improved_version'):
                    has_improvements += 1
                    improvement_examples.append({
                        'file': file,
                        'type': data['feedback_type'],
                        'original_subject': data['original_output']['subject'],
                        'improved': data['improved_version'][:200] + '...' if len(data['improved_version']) > 200 else data['improved_version']
                    })
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    print(f"Feedback Types:")
    for type, count in Counter(feedback_types).most_common():
        percentage = (count / len(feedback_files)) * 100
        print(f"  {type.capitalize()}: {count} ({percentage:.1f}%)")
    print()
    
    print(f"Message Types:")
    for type, count in Counter(message_types).most_common():
        percentage = (count / len(feedback_files)) * 100
        print(f"  {type}: {count} ({percentage:.1f}%)")
    print()
    
    print(f"Feedback with Improvements: {has_improvements} ({(has_improvements/len(feedback_files)*100):.1f}%)")
    print()
    
    if improvement_examples:
        print(f"\n📝 Sample Improvements:")
        print(f"=" * 50)
        for i, example in enumerate(improvement_examples[:3], 1):
            print(f"\n{i}. {example['type'].upper()} - {example['original_subject']}")
            print(f"   Improved version:")
            print(f"   {example['improved']}")
    
    # Calculate positive/negative ratio
    positive = feedback_types.count('positive')
    negative = feedback_types.count('negative')
    if positive + negative > 0:
        ratio = positive / (positive + negative) * 100
        print(f"\n✨ Success Rate: {ratio:.1f}% positive feedback")
        
        if ratio >= 80:
            print(f"   🎉 Excellent! Users love the output!")
        elif ratio >= 60:
            print(f"   👍 Good! Room for improvement.")
        else:
            print(f"   ⚠️  Needs work. Review negative feedback.")

if __name__ == "__main__":
    analyze_feedback()
