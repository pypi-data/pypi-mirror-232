from setuptools import setup, find_packages
import os
import io

scriptFolder = os.path.dirname(os.path.realpath(__file__))
os.chdir(scriptFolder)

version = '0.49'

with io.open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()


print('version: ', version)
setup(
    name='swmonkey',
    version=version,
    packages=find_packages(),
    package_data={
        'swmonkey': ['pyarmor_runtime_000000/*.so'],
    },
    author='Li Saifei',
    author_email='waltermitty121906@gmail.com',
    description='A tool for monkey test on Linux GUI',
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={
        'console_scripts': [
            'swmonkey = swmonkey.main:swmonkey',
            'swmonkey_runner = swmonkey.runner:main'
        ]
    },
    install_requires=[
        'pyautogui',
        'psutil',
        'pywinctl'
    ]
)
