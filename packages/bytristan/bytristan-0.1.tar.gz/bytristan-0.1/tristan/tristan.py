import os  # made by tristan
import sys  # made by tristan
import tokenize  # made by tristan

# Define the default comment ending
default_comment_ending = "tristan"  # made by tristan

def rainbow_text(text):  # made by tristan
    colors = ['\033[91m', '\033[92m', '\033[93m', '\033[94m', '\033[95m', '\033[96m']  # made by tristan
    result = ''  # made by tristan
    for i, char in enumerate(text):  # made by tristan
        result += colors[i % len(colors)] + char  # made by tristan
    result += '\033[0m'  # made by tristan
    return result  # made by tristan

def tristanprint(*args, **kwargs):  # made by tristan
    print(*args, **kwargs)  # made by tristan

def enforce_tristan(filename):  # made by tristan
    comment_ending = getattr(sys.modules[__name__], "antiskid", default_comment_ending)  # made by tristan
    
    with open(filename, 'r') as file:  # made by tristan
        content = file.read()  # made by tristan
        tokens = list(tokenize.generate_tokens(lambda L=iter(content.splitlines(True)): next(L)))  # made by tristan

    cute_comment_found = any("# tristan is cute" in line for line in content.splitlines())  # made by tristan
    if not cute_comment_found:  # made by tristan
        raise SyntaxError(f"{filename}: The code must contain at least one '# tristan is cute' comment")  # made by tristan

    for token_type, token_string, start, end, line in tokens:  # made by tristan
        if token_type == tokenize.NEWLINE:  # made by tristan
            if not line.strip().endswith(f"# made by {comment_ending}"):  # made by tristan
                raise SyntaxError(f"{filename}: Line {start[0]} does not end with '# made by {comment_ending}'")  # made by tristan

def start_enforcement():  # made by tristan
    # Check user code  # made by tristan
    user_script = sys.argv[0]  # made by tristan
    if user_script and os.path.abspath(user_script) != os.path.abspath(__file__):  # made by tristan
        enforce_tristan(user_script)  # made by tristan

    # Print we love tristan 3 times  # made by tristan
    comment_ending = getattr(sys.modules[__name__], "antiskid", default_comment_ending)  # made by tristan
    for _ in range(3):  # made by tristan
        tristanprint(rainbow_text(f"we love {comment_ending}"))  # made by tristan
