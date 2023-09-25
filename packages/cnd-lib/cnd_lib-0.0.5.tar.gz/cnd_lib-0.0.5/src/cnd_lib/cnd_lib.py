import os


class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class CndLib:
    colors = {
        'e': Bcolors.FAIL,  # Error
        'v': Bcolors.WARNING,  # Event
        'd': Bcolors.OKBLUE,  # display (default)
        's': Bcolors.OKGREEN,  # Success (default)
        'c': Bcolors.OKCYAN,  # Cyan (nothing special, just different color)
    }

    def __init__(self):
        print("CndLib")

    @staticmethod
    def get_lib_folder():
        base = 'src'
        all_dir = filter(os.path.isdir, [os.path.join(base, f) for f in os.listdir(base)])
        return list(all_dir)[0]
        # print(list(filter(os.path.isdir, os.listdir('src'))))

    @staticmethod
    def create_folder(path):
        if not os.path.isdir(path):
            CndLib.cprint(f"Create Folder {path}", 's')
            os.makedirs(path)

    @staticmethod
    def folders(base, snake):
        return [
            f'{base}', 
            f'{base}/src', 
            f'{base}/src/{snake}', 
            f'{base}/tests'
        ]

    @staticmethod
    def files(base, snake):
        return [
            {"name": f'{base}/src/{snake}/__init__.py', "content": 'from .__version__ import (__version__)  # noqa: F401\n'},
            {"name": f'{base}/src/{snake}/__version__.py', "content": '__version__ = "0.0.1"\n'},
            {"name": f'{base}/tests/requirements.txt', "content": 'expects\nmockito\nhatch\n'},
            {"name": f'{base}/requirements.txt', "content": ''},
            {"name": f'{base}/.coveragerc', "content": '[report]\nshow_missing = True\nomit =\n   */opt/*\n   tests/*\n   /opt/homebrew/lib/python3.9/*\n   lib/*\n'},
            {"name": f'{base}/README.md', "content": f'# {base}'},
            {"name": f'{base}/tests/vars.py', "content": ''},
            {"name": f'{base}/.envrc', "content": 'source ~/bin/venv-start\n'},
            {"name": f'{base}/pyproject.toml', "content": f'[project]\nname = "{snake}"'},
            {"name": f'{base}/.gitlab-ci.yml', "content": "include: 'https://gitlab.com/changendevops/common/-/raw/main/python-toml-lib.yml'"},
        ]

    @staticmethod
    def new_lib(name):
        base_folder = CndLib._to_camel_case(name)
        for folder in CndLib.folders(base_folder, name):
            CndLib.create_folder(folder)
        for file in CndLib.files(base_folder, name):
            CndLib.write_file(file["name"], file["content"])


    @staticmethod
    def new_module(name):
        name = name.lower()
        lib_folder = CndLib.get_lib_folder()
        content = f"class {CndLib._to_camel_case(name)}:\n    def __init__(self):\n        pass"
        CndLib.write_file(f'{lib_folder}/{name}.py', content)
        content = "from mockito import when, mock, unstub\nfrom expects import *\nfrom mamba import description, context, it\n"
        as_name = lib_folder.split('/')[-1]
        content += f"import tests.vars as vars\nimport {lib_folder.replace('/', '.')} as {as_name}\n\n\n"
        instance_name = f"{as_name}.{name}.{CndLib._to_camel_case(name)}"
        content += f"with description('{CndLib._to_camel_case(name)}') as self:\n    with before.each:\n        unstub()\n        self.instance = {instance_name}()\n\n"
        content += f"    with context(\"__init__\"):\n        with it(\"shoud get an instance\"):\n            expect(isinstance(self.instance, {instance_name})).to(equal(True))"
        CndLib.write_file(f'tests/{name}_spec.py', content)

        CndLib.append_file(f'{lib_folder}/__init__.py', f"\nfrom .{name} import {CndLib._to_camel_case(name)}  # noqa: F401")

    @staticmethod
    def _to_camel_case(str):
        temp = str.split('_')
        res = ''.join(ele.title() for ele in temp[0:])
        return res

    @staticmethod
    def cprint(message, color_set):
        print(CndLib.colors[color_set] + message + Bcolors.ENDC)

    @staticmethod
    def append_file(filename, content):
        f = open(filename, "a")
        f.write(content)
        f.close()
        CndLib.cprint(f"File {filename} updated", 's')

    @staticmethod
    def write_file(filename, content):
        if os.path.isfile(filename):
            CndLib.cprint(f"File {filename} already exist", 'e')
            return None
        f = open(filename, "w")
        f.write(content)
        f.close()
        CndLib.cprint(f"File {filename} created", 's')
