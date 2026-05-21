def fix_brackets(line):

    open_brackets = line.count('(')
    close_brackets = line.count(')')

    if open_brackets > close_brackets:

        line += ')'

    return line