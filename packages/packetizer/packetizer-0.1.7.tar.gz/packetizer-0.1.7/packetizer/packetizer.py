import ast
import os
import typer

from packetizer.class_extractor import ClassExtractor
from packetizer.utils import assert_file_exist, assert_file_is_python_file
from packetizer.writers import write_to_files

app = typer.Typer()


@app.command()
def main(file: str):
    output_dir, _ = os.path.splitext(file)

    assert_file_exist(file)
    assert_file_is_python_file(file)

    with open(file, "r") as f:
        content = f.read()

    tree = ast.parse(content)
    extractor = ClassExtractor()
    extractor.visit(tree)

    write_to_files(extractor.classes, extractor.imports, output_dir)


if __name__ == "__main__":
    app()

