from setuptools import setup, find_packages
from pathlib import Path

# Read README.md for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "interpreter_smol" / "README.md").read_text()

setup(
    name="interpreter-smol",
    version="0.2.0",
    description="A powerful interpreter with evolving agents built on SmolaGents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="velinxs",
    author_email="velinxs1@gmail.com",
    url="https://github.com/velinxs/interpreter_smolagent",
    packages=find_packages(include=['interpreter_smol', 'interpreter_smol.*']),
    package_data={
        'interpreter_smol': [
            'prompts/*.yaml',  # Include YAML prompt files
            'README.md',
            'EVOLVE.md',
        ]
    },
    install_requires=[
        "smolagents>=1.0.0",
        "pyyaml>=6.0.0",
        "litellm>=1.0.0",
        "requests>=2.25.0",
    ],
    extras_require={
        "gemini": ["google-genai>=1.0.0"],
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.5.0"],
        "complete": [
            "google-genai>=1.0.0",
            "openai>=1.0.0",
            "anthropic>=0.5.0",
            "pillow>=9.0.0",
            "numpy>=1.20.0",
            "pandas>=1.3.0",
            "matplotlib>=3.4.0",
            "psutil>=5.8.0",  # For system monitoring
            "beautifulsoup4>=4.9.0",  # For web scraping
        ],
    },
    entry_points={
        'console_scripts': [
            'interpreter-smol=interpreter_smol.cli:main',
            'evolve=interpreter_smol.evolve:main',  # Add evolve command
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",  # Upgraded from Alpha
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
    ],
    keywords="ai interpreter agents llm automation code-execution evolving-agents",
)
