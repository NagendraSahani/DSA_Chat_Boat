def print_line():
    print("=" * 60)


def clean_input(text: str):
    return text.strip()


def is_exit(text: str, exit_command: str):
    return text.lower() == exit_command.lower()