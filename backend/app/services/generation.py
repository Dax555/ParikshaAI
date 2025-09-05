# app/services/generation.py
import random
import re

def extract_topic(text: str) -> str:
    """
    Very basic keyword/topic extractor.
    You can extend with NLP later if needed.
    """
    keywords = re.findall(r"\b(?:process|scheduling|threads|memory|paging|deadlock|filesystem|synchronization|semaphores)\b", text.lower())
    return keywords[0] if keywords else "shell scripting in operating systems"

def generate_coding_question(text: str, unique=True, broader_topic=True) -> str:
    topic = extract_topic(text)
    variations = [
        f"Write a shell script to simulate {topic}.",
        f"Create a shell script that accepts user input and demonstrates {topic}.",
        f"Write a shell script to automate a task related to {topic} (e.g., file management, process handling).",
        f"Implement a shell script that logs system information and relates it to {topic}."
    ]
    return random.choice(variations)

def generate_error_question(text: str, unique=True, broader_topic=True) -> str:
    topic = extract_topic(text)
    variations = [
        f"The following shell script related to {topic} contains an error. Identify and fix it:\n\n```sh\n#!/bin/bash\necho \"Enter filename:\"\nread file\nif [ -f $file ]\nthen\n    echo \"File exists\"\nelse\n    echo \"File not found\"\nfi\n```",
        f"A shell script intended to demonstrate {topic} is not working as expected. Describe one common mistake and provide the corrected version.",
        f"A student wrote a shell script for {topic} but forgot to add proper error handling. Explain what went wrong and fix it."
    ]
    return random.choice(variations)
