from setuptools import setup, find_packages
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
setup(
    name='researchpal',
    packages=find_packages(),
    version='1.0.1',
    description='Python library for generating literature review',
    author='Veracious.ai',
    author_email='info@researchpal.co',
    license='MIT',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=['researchpal', 'literature review', 'generate literature review', 'python literature'],
    dependencies=[
        'arxiv',
        'bs4',
        'openai',
        'Requests',
        'urlib3',
        'termcolor',
        'tiktoken',
        ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.8",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Unix",
        "Operating System :: Microsoft :: Windows"
    ]
)