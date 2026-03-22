from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8", errors="ignore")

setup(
    name="claude-interpreter",
    version="0.4.0",
    description="Open Interpreter-like REPL powered by Claude Code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="velinxs",
    author_email="velinxs1@gmail.com",
    url="https://github.com/velinxs/interpreter_smolagent",
    packages=find_packages(include=["claude_interpreter", "claude_interpreter.core"]),
    install_requires=[
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "claude-interpreter=claude_interpreter.core.interpreter:main",
            "ci=claude_interpreter.core.interpreter:main",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="ai interpreter repl claude open-interpreter cli",
)
