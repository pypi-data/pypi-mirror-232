from cli.colors import colored


def convert_file_size(file_size: int) -> str:
    if file_size < 1024:
        return f"{file_size:,} bytes"
    elif file_size < 1048576:
        return f"{file_size / 1024:,.2f} KB"
    elif file_size < 1073741824:
        return f"{file_size / 1048576:,.2f} MB"
    else:
        return f"{file_size / 1073741824:,.2f} GB"


def print_file_details(filename: str, size_bytes: int, url: str, prefix: str = ' ' * 4):
    names_col_len = 12
    values_col_len = max(len(url), len(filename))
    rows = ['╔' + ('═' * (names_col_len + 2)) + '╦' + ('═' * (values_col_len + 2)) + '╗']

    data = [
        ('Filename'.rjust(names_col_len), filename.ljust(values_col_len)),
        ('Size'.rjust(names_col_len), convert_file_size(size_bytes).ljust(values_col_len)),
        ('Download URL'.rjust(names_col_len), url.ljust(values_col_len))
    ]

    for (i, (name, value)) in enumerate(data):
        value_color = 'white' if i in [0, 1] else 'blue'
        rows.append('║ ' + name + ' ║ ' + colored(value, value_color, bold=True) + ' ║')
        if i != len(data) - 1:
            rows.append('╠' + ('═' * (names_col_len + 2)) + '╬' + ('═' * (values_col_len + 2)) + '╣')
    rows.append('╚' + ('═' * (names_col_len + 2)) + '╩' + ('═' * (values_col_len + 2)) + '╝')

    for row in rows:
        print(prefix + row)
