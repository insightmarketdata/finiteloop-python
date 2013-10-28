import os


def find_packages(root):
    packages = []

    for dirname, dirnames, filenames in os.walk(root):
        package = os.path.split(dirname)

        if (os.path.exists(os.path.join(dirname, '__init__.py'))
                and not package[-1].startswith(".")):

            packages.append(".".join(package))

    return packages
