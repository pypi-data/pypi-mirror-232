import ast


def get_used_names(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    tree = ast.parse(content)
    used_names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    return used_names
