import re


def tokenize(code):

    token_patterns = [

        ('KEYWORD', r'\b(if|else|elif|for|while|def|class|return|try|except|finally|with|import|from|as|True|False|None)\b'),

        ('NUMBER', r'\b\d+(\.\d+)?\b'),

        ('STRING', r'"[^"]*"|\'[^\']*\''),

        ('OPERATOR', r'==|!=|<=|>=|\+|\-|\*|\/|=|<|>'),

        ('PUNCTUATION', r'[\(\)\[\]\{\}:,\.]'),

        ('IDENTIFIER', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),

        ('NEWLINE', r'\n'),

        ('SKIP', r'[ \t]+'),

        ('MISMATCH', r'.')
    ]

    master_pattern = '|'.join(
        f'(?P<{name}>{pattern})'
        for name, pattern in token_patterns
    )

    tokens = []

    for match in re.finditer(master_pattern, code):

        token_type = match.lastgroup

        token_value = match.group()

        if token_type == 'SKIP':
            continue

        elif token_type == 'MISMATCH':

            tokens.append((
                'INVALID',
                token_value
            ))

        else:

            tokens.append((
                token_type,
                token_value
            ))

    return tokens