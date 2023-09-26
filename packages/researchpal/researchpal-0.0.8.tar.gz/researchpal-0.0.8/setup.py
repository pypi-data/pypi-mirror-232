from setuptools import setup, find_packages
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
setup(
    name='researchpal',
    packages=find_packages(include=['literature_review', 'literature_review.generate_literature_review']),
    version='0.0.8',
    description='Python library for generating literature review',
    author='Veracious.ai',
    author_email='info@researchpal.co',
    license='MIT',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=['researchpal', 'literature review', 'generate literature review', 'python literature'],
    install_requires=[
        'arxiv',
        'beautifulsoup4',
        'openai',
        'python-dotenv',
        'Requests',
        'setuptools',
        'setuptools',
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