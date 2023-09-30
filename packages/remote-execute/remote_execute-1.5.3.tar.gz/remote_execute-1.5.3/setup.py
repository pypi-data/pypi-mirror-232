from setuptools import setup, find_packages
with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='remote_execute',
    version='1.5.3',
    description='Execute remote code fetched from a URL',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='WavaDev',
    author_email='admin@wavadev.xyz',
    url='https://github.com/Zyno-LLC/remote-execute',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'requests',
        'python-dotenv',
    ],
)