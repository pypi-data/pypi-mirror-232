import os
import typer


def convert_camel_case_to_snake_case(name):
    return "".join(["_" + c.lower() if c.isupper() else c for c in name]).lstrip("_")


def assert_file_exist(file_path):
    if not os.path.exists(file_path):
        typer.echo(f"Error: The file: ({file_path}) not found.")
        raise typer.Exit(code=1)


def assert_file_is_python_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    if file_extension != '.py':
        typer.echo(f"Error: The file: ({file_path}) is not a Python file.")
        raise typer.Exit(code=1)
