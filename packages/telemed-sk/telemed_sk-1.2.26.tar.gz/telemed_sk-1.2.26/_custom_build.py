import os
from wheel.bdist_wheel import bdist_wheel
from glob import glob
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py as _build_py
from Cython.Build import cythonize


package_dir = "telemed_sk"
EXCLUDE_FILES = []


def get_ext_paths(root_dir, exclude_files):
    """get filepaths for compilation"""
    paths = []
    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            if os.path.splitext(filename)[1] != '.py':
                continue
            file_path = os.path.join(root, filename)
            if file_path in exclude_files:
                continue
            paths.append(file_path)
    return paths


class CommandBdistWheel(bdist_wheel):
    # Called almost exactly before filling `.whl` archive
    def write_wheelfile(self, *args, **kwargs):
        dr = f'{self.bdist_dir}/telemed_sk*'
        paths = [
            path for path in glob(f'{dr}/**/*.py', recursive=True)
            #if os.path.basename(path) != '__init__.py'
        ]
        paths.extend([
            path for path in glob(f'{dr}/**/*.c', recursive=True)
        ])
        for path in paths:
            os.remove(path)
        super().write_wheelfile(*args, **kwargs)

    def finalize_options(self):
        bdist_wheel.finalize_options(self)
        self.root_is_pure = False


class build_py(_build_py):
    def run(self):
        self.run_command("build_ext")
        return super().run()

    def initialize_options(self):
        super().initialize_options()
        if self.distribution.ext_modules == None:
            self.distribution.ext_modules = [] 

        self.distribution.ext_modules.extend(cythonize(
          get_ext_paths(package_dir, EXCLUDE_FILES),
          compiler_directives={'language_level': 3}
        ))
