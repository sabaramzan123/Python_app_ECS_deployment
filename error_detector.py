import re
import keyword


def detect_errors(code):

    errors = []

    lines = code.splitlines()

    stack = []

    defined_vars = set()

    keywords_with_colon = [
        "if", "elif", "else",
        "for", "while",
        "def", "class",
        "try", "except",
        "finally", "with"
    ]

    python_keywords = set(keyword.kwlist)

    builtins = {
        "print", "len", "range",
        "int", "str", "float",
        "list", "dict", "set",
        "tuple", "input",
        "True", "False"
    }

    # ---------------------------------------------------
    # LINE BY LINE SCAN
    # ---------------------------------------------------

    for line_no, raw_line in enumerate(lines, start=1):

        line = raw_line.rstrip()

        stripped = line.strip()

        if not stripped:
            continue

        # ---------------------------------------------------
        # REMOVE COMMENTS
        # ---------------------------------------------------

        if "#" in stripped:
            stripped = stripped.split("#")[0].strip()

        if not stripped:
            continue

        # ---------------------------------------------------
        # FIRST WORD
        # ---------------------------------------------------

        first_word = stripped.split()[0].split("(")[0]

        # ---------------------------------------------------
        # MISSING COLON
        # ---------------------------------------------------

        if first_word in keywords_with_colon:

            if not stripped.endswith(":"):

                errors.append({
                    "line": line_no,
                    "message": f"Missing ':' after '{first_word}'"
                })

        # ---------------------------------------------------
        # BRACKET CHECK
        # ---------------------------------------------------

        for char in stripped:

            if char in "([{":
                stack.append((char, line_no))

            elif char in ")]}":

                if not stack:

                    errors.append({
                        "line": line_no,
                        "message": f"Extra closing '{char}'"
                    })

                    continue

                opening, opening_line = stack.pop()

                pairs = {
                    "(": ")",
                    "[": "]",
                    "{": "}"
                }

                if pairs[opening] != char:

                    errors.append({
                        "line": line_no,
                        "message": f"Mismatched '{opening}' and '{char}'"
                    })

        # ---------------------------------------------------
        # INDENTATION CHECK
        # ---------------------------------------------------

        spaces = len(raw_line) - len(raw_line.lstrip())

        if spaces % 4 != 0:

            errors.append({
                "line": line_no,
                "message": "Indentation should be multiple of 4 spaces"
            })

        # ---------------------------------------------------
        # SEMICOLON CHECK
        # ---------------------------------------------------

        if ";" in stripped:

            errors.append({
                "line": line_no,
                "message": "Semicolon ';' not needed in Python"
            })

        # ---------------------------------------------------
        # ASSIGNMENT INSIDE IF
        # ---------------------------------------------------

        if stripped.startswith("if "):

            if "=" in stripped:

                bad_assignment = (
                    "==" not in stripped
                    and "!=" not in stripped
                    and ">=" not in stripped
                    and "<=" not in stripped
                    and ":=" not in stripped
                )

                if bad_assignment:

                    errors.append({
                        "line": line_no,
                        "message": "Use '==' instead of '=' in condition"
                    })

        # ---------------------------------------------------
        # INVALID VARIABLE NAMES
        # ---------------------------------------------------

        assign_match = re.match(
            r"([a-zA-Z0-9_]+)\s*=",
            stripped
        )

        if assign_match:

            var = assign_match.group(1)

            if var[0].isdigit():

                errors.append({
                    "line": line_no,
                    "message": f"Invalid variable name '{var}'"
                })

            elif keyword.iskeyword(var):

                errors.append({
                    "line": line_no,
                    "message": f"'{var}' is reserved keyword"
                })

            else:
                defined_vars.add(var)

        # ---------------------------------------------------
        # FUNCTION DEFINITIONS
        # ---------------------------------------------------

        func_match = re.match(
            r"def\s+([a-zA-Z_]\w*)",
            stripped
        )

        if func_match:

            func_name = func_match.group(1)

            defined_vars.add(func_name)

        # ---------------------------------------------------
        # FOR LOOP VARIABLES
        # ---------------------------------------------------

        for_match = re.match(
            r"for\s+([a-zA-Z_]\w*)\s+in",
            stripped
        )

        if for_match:

            loop_var = for_match.group(1)

            defined_vars.add(loop_var)

        # ---------------------------------------------------
        # REMOVE STRINGS BEFORE TOKEN CHECK
        # ---------------------------------------------------

        line_without_strings = re.sub(
            r'".*?"|\'.*?\'',
            '',
            stripped
        )

        # ---------------------------------------------------
        # UNDEFINED VARIABLES
        # ---------------------------------------------------

        tokens = re.findall(
            r"\b[a-zA-Z_]\w*\b",
            line_without_strings
        )

        ignore_tokens = {
            "if", "for", "while",
            "def", "class",
            "return", "import",
            "from", "as", "in",
            "try", "except",
            "finally", "with",
            "elif", "else"
        }

        for token in tokens:

            if (
                token not in defined_vars
                and token not in python_keywords
                and token not in builtins
                and token not in ignore_tokens
            ):

                if not stripped.startswith("def "):

                    errors.append({
                        "line": line_no,
                        "message": f"Undefined variable '{token}'"
                    })

        # ---------------------------------------------------
        # DIVISION BY ZERO
        # ---------------------------------------------------

        if re.search(r"/\s*0\b", stripped):

            errors.append({
                "line": line_no,
                "message": "Possible division by zero"
            })

        # ---------------------------------------------------
        # EXTRA TEXT AFTER STATEMENT
        # ---------------------------------------------------

        if re.search(r"\)\s+[a-zA-Z_]", stripped):

            if "if " not in stripped:

                errors.append({
                    "line": line_no,
                    "message": "Unexpected text after statement"
                })

        # ---------------------------------------------------
        # IMPORT CHECK
        # ---------------------------------------------------

        if stripped.startswith("import "):

            module = stripped.replace("import", "").strip()

            try:
                __import__(module)

            except:

                errors.append({
                    "line": line_no,
                    "message": f"Module '{module}' not found"
                })

        # ---------------------------------------------------
        # DANGEROUS EVAL
        # ---------------------------------------------------

        if "eval(" in stripped:

            errors.append({
                "line": line_no,
                "message": "Use of eval() is dangerous"
            })

    # ---------------------------------------------------
    # UNCLOSED BRACKETS
    # ---------------------------------------------------

    while stack:

        bracket, bracket_line = stack.pop()

        errors.append({
            "line": bracket_line,
            "message": f"Unclosed '{bracket}'"
        })

    # ---------------------------------------------------
    # REMOVE DUPLICATES
    # ---------------------------------------------------

    unique_errors = []

    seen = set()

    for error in errors:

        key = (
            error["line"],
            error["message"]
        )

        if key not in seen:

            seen.add(key)

            unique_errors.append(error)

    # ---------------------------------------------------
    # SORT BY LINE NUMBER
    # ---------------------------------------------------

    unique_errors.sort(
        key=lambda x: x["line"]
    )

    return unique_errors