import os
import click
import shutil

from .template.pkg.utils import get_data_path

TEMPLATE_DIR = get_data_path("template")

def replace_placeholders(root_dir, product_name):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if not filename.endswith(('.py', '.txt')):  # ここでテキストファイルの拡張子を指定します。
                continue
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            content = content.replace("{{PRODUCT_NAME}}", product_name)
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)

@click.command()
@click.argument('product_name')
def pyxel_app(product_name):
    """Copy the product template and replace placeholders with the given product name."""
    destination = os.path.join(os.getcwd(), product_name)
    shutil.copytree(TEMPLATE_DIR, destination)
    replace_placeholders(destination, product_name)
    click.echo(f"Product '{product_name}' has been created!")

if __name__ == '__main__':
    pyxel_app()
