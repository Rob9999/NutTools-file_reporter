import os
from pathlib import Path
import sys
import datetime
import fnmatch
import pathspec


def get_file_info(filepath):
    """Get information about a file."""
    file_info = {
        "path": filepath,
        "name": os.path.basename(filepath),
        "modification_date": datetime.datetime.fromtimestamp(
            os.path.getmtime(filepath)
        ).strftime("%Y-%m-%d %H:%M:%S"),
        "size": os.path.getsize(filepath),
        "type": "Directory" if os.path.isdir(filepath) else "File",
    }
    return file_info


def read_file_content(filepath):
    """Read the content of the file if it is ASCII or UTF-8."""
    try:
        with open(filepath, "r") as file:
            content = file.read()
        return content
    except Exception as e:
        return f"Error reading file content: {str(e)}"


def load_or_create_ignore_list(ignore_file):
    """
    Load the list of files and directories to ignore from a file, or create a default ignore file if it does not exist.
    Args:
        ignore_file (str): The path to the ignore file.
    Returns:
        list: A list of patterns to ignore, with trailing slashes removed.
    """
    if not os.path.exists(ignore_file):
        # Create a default .ignore file if it does not exist
        os.makedirs(os.path.dirname(ignore_file), exist_ok=True)
        with open(ignore_file, "w", encoding="utf-8") as file:
            file.write("# Add patterns to ignore files or directories\n")
            file.write("# For example:\n")
            file.write("# .git/\n")
            file.write("# __pycache__/\n")
            file.write("# build/\n")
            file.write("# secret/\n")
            file.write("# temp/\n")
            file.write("# .env\n")
            file.write("# *.log\n")
            file.write("# *.db\n")
            file.write(".git/\n")
            file.write("secret/\n")

        return []  # Return an empty list if ignore file is newly created
    with open(ignore_file, "r", encoding="utf-8") as file:
        lines = [
            line.strip() for line in file if line.strip() and not line.startswith("#")
        ]
        return [line.rstrip("/") for line in lines]


def get_ignore_spec(ignore_patterns):
    """Create a PathSpec object from ignore patterns."""
    spec = pathspec.PathSpec.from_lines("gitwildmatch", ignore_patterns)
    return spec


def should_ignore(filepath, spec):
    """Check if a file or directory should be ignored based on the loaded spec."""
    return spec.match_file(filepath)


def generate_report(directory, ignore_list):
    """Generate a report of all files in the directory and its subdirectories."""
    print("generate_report: ", directory, ignore_list)
    output_lines = []
    ignore_spec = get_ignore_spec(ignore_list)
    for root, _, files in os.walk(directory):
        if should_ignore(root, ignore_spec):
            continue
        for file in files:
            filepath = os.path.join(root, file)
            if should_ignore(filepath, ignore_spec):
                continue
            file_info = get_file_info(filepath)
            output_lines.append(
                f"\r\n\r\nDATEI\r\n[{file_info['path']}]\nName: {file_info['name']}\r\nGeändert: {file_info['modification_date']}\r\nGröße: {file_info['size']} Bytes\r\nTyp: {file_info['type']}\r\n"
            )
            output_lines.append(f"{read_file_content(filepath)}")
    return "\r\n".join(output_lines)


def save_report_to_file(report, output_path):
    """Save the report to a file."""
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(report)


def print_help():
    """Print the help message."""
    help_message = (
        "Usage: python script.py <directory> [--ignore-file <path>]\n\n"
        "Options:\n"
        "  --help          Show this help message and exit\n"
        "  --ignore-file   Specify a custom .ignore file path\n\n"
        "Description:\n"
        "  This script generates a report of all files in the specified directory\n"
        "  and its subdirectories. The report includes file metadata and content.\n\n"
        "  Patterns to exclude files or directories can be added to the specified\n"
        "  .ignore file or the default locations."
    )
    print(help_message)


def find_ignore_file(custom_path):
    """
    Determine the correct .ignore file to use based on the provided custom path or default locations.

    Args:
        custom_path (str): A custom path to the .ignore file provided by the user.

    Returns:
        str: The path to the .ignore file.
             Rules: If a custom path is provided, it returns that path.
                    Otherwise, it checks for the .ignore file in the current working directory under
                    the .file_reporter directory.
                    If not found, it defaults to the .ignore file in the user's home directory under
                    the .file_reporter directory.
    """
    if custom_path:
        return custom_path
    cwd_ignore_file = os.path.join(os.getcwd(), ".file_reporter", ".ignore")
    if os.path.exists(cwd_ignore_file):
        return cwd_ignore_file
    return os.path.join(os.path.expanduser("~"), ".file_reporter", ".ignore")


def main():
    print("args: ", sys.argv)
    # Validate the command line arguments
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    # Display help message if --help or -h is provided as an argument
    if "--help" in sys.argv or "-h" in sys.argv:
        print_help()
        sys.exit(0)
    # Get the directory path from the command line arguments
    directory = sys.argv[1]
    if not os.path.exists(directory):
        print(f"The specified directory does not exist: {directory}")
        sys.exit(1)
    # Check if a custom ignore file is specified
    custom_ignore_path = None
    if "--ignore-file" in sys.argv:
        try:
            custom_ignore_path = sys.argv[sys.argv.index("--ignore-file") + 1]
        except IndexError:
            print("Error: --ignore-file option requires a path argument.")
            sys.exit(1)
    # Find the correct ignore file to use
    ignore_file = find_ignore_file(custom_ignore_path)
    # Load or create the ignore list
    ignore_list = load_or_create_ignore_list(ignore_file)
    # Generate the report
    report = generate_report(directory, ignore_list)
    # Save the report to a file
    output_file = os.path.join(os.getcwd(), "file_report.txt")
    save_report_to_file(report, output_file)
    print(f"Report saved to: {output_file}")


if __name__ == "__main__":
    main()
