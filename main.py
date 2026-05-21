from lexer import tokenize
from parser import parse
from error_detector import detect_errors
from ai_fixer import auto_fix

# Read sample code
with open("samples/sample_code.py", "r") as file:
    code = file.read()

print("===== ORIGINAL CODE =====")
print(code)

# Lexical Analysis
tokens = tokenize(code)

print("\n===== TOKENS =====")
for token in tokens:
    print(token)

# Parsing
print("\n===== PARSER =====")
print(parse(tokens))

# Error Detection
error = detect_errors(code)

if error:
    print("\n===== ERROR DETECTED =====")
    print("Message:", error["message"])
    print("Line:", error["line"])
    print("Code:", error["text"])

    # Auto Fix
    fixed_code = auto_fix(code)

    print("\n===== FIXED CODE =====")
    print(fixed_code)

else:
    print("\nNo syntax errors found.")