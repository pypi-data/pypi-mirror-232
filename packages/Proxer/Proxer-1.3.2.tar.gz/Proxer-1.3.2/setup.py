from setuptools import setup, find_packages

setup(
    name='Proxer',
    version='1.3.2',
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4==4.12.2",
        "colorama==0.4.6",
        "requests",
    ],
    author='Shypilo Oleksandr',
    author_email='ssshipilo@gmail.com',
    description='Proxer - get a free working proxy simply and free of charge',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/ssshipilo/Proxer',
    project_urls={
        "Documentation": "https://github.com/ssshipilo/Proxer/blob/main/git/documentation.md",
        "Source Code": "https://github.com/ssshipilo/Proxer",
    },
)