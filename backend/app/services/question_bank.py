import random

# This list contains only the coding questions, which matches what the backend provides.
coding_questions = [
    "Write a shell script that finds all files larger than 10MB in the /var/log directory and archives them into a single tar.gz file.",
    "Create a shell script that takes a process name as an argument and prints its PID, CPU usage, and Memory usage. If the process is not running, it should print an error message.",
    "Write a shell script to monitor a specific user's login activity. The script should report the last 5 login times for that user.",
    "Develop a shell script that reads a list of server IPs from a file named 'servers.txt' and checks if each server is reachable using the 'ping' command.",
    "Create a shell script that counts the number of files and sub-directories within a given directory path (passed as an argument) without using 'ls -R'.",
    "Write a script that finds all symbolic links in your home directory and lists both the link name and the file it points to.",
    "Write a shell script that creates a daily backup of a specified directory and renames the backup file with the current date (e.g., backup-YYYY-MM-DD.tar.gz).",
]

def get_random_questions():
    """
    Selects a single random coding question.
    This function's output perfectly matches what the ft and backend expect.
    """
    return {
        "code_question": random.choice(coding_questions),
    }
