import setuptools

from src.metadata import VERSION

with open('../README.md', 'r', encoding = 'utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name = 'pytextforge',
    version = VERSION,
    author = 'Rojas, Roberto',
    description = 'One module to generate files from a template',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/RobertoRojas/PyTextForge',
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    packages = ['pytextforge'],
    package_dir = {'pytextforge': 'src'},
    entry_points={ 'console_scripts': ['pytextforge = src.__main__:main' ] },
    install_requires=[
        'colorama==0.4.6',
        'Jinja2==3.1.2',
        'MarkupSafe==2.1.3'
    ],
    python_requires = '>=3.6'
)