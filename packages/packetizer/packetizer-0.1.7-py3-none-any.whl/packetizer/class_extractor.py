import ast


class ClassExtractor(ast.NodeVisitor):
    def __init__(self):
        self.classes = {}
        self.imports = []

    def visit_Import(self, node):
        for n in node.names:
            self.imports.append(f"import {n.name}")

    def visit_ImportFrom(self, node):
        module = node.module
        names = [n.name for n in node.names]
        self.imports.append(f"from {module} import {', '.join(names)}")

    def visit_ClassDef(self, node):
        source_lines = ast.unparse(node).split('\n')
        self.classes[node.name] = "\n".join(source_lines)
