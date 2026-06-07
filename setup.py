#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SnippetMind-CLI: AI-Powered Smart Code Snippet Manager
Setup configuration
"""

from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='snippetmind-cli',
    version='1.0.0',
    description='🧠 SnippetMind-CLI: AI-Powered Smart Code Snippet Manager with Semantic Search',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='gitstq',
    author_email='',
    url='https://github.com/gitstq/SnippetMind-CLI',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click>=8.0.0',
        'rich>=13.0.0',
        'colorama>=0.4.4',
        'requests>=2.28.0',
    ],
    extras_require={
        'ai': ['sentence-transformers>=2.2.0', 'torch>=2.0.0'],
    },
    entry_points={
        'console_scripts': [
            'snippetmind=snippetmind.cli:main',
            'sm=snippetmind.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    keywords='snippet code manager ai semantic search developer productivity cli',
    project_urls={
        'Bug Reports': 'https://github.com/gitstq/SnippetMind-CLI/issues',
        'Source': 'https://github.com/gitstq/SnippetMind-CLI',
    },
)
