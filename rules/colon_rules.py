def fix_missing_colon(line):

    keywords = ['if', 'for', 'while', 'def', 'class', 'else']

    stripped = line.strip()

    for keyword in keywords:

        if stripped.startswith(keyword) and not stripped.endswith(':'):

            return line + ':'

    return line