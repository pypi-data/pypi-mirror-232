from setuptools import setup, find_packages
with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='remote_execute',
    version='1.5.4',
    description='Execute remote code fetched from a URL',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='WavaDev',
    author_email='admin@wavadev.xyz',
    url='https://github.com/Zyno-LLC/remote-execute',
    install_requires=['tqdm', 'requests'],
    entry_points={'console_scripts': ['remote-execute=remote_execute.executor:main']},
    py_modules=['remote_execute'],  # Add this line to import execute_remote into other Python scripts
)