from setuptools import setup, find_packages

setup(
    name="interpreter-smol",
    version="0.1.0",
    description="A simplified Open-Interpreter alternative built on SmolaGents",
    author="velinxs",
    author_email="velinxs1@gmail.com",
    packages=find_packages(include=['smolagents', 'smolagents.*']),
    install_requires=[
        "smolagents>=1.0.0",
    ],
    extras_require={
        "gemini": ["google-genai>=1.0.0"],
        "complete": [
            "google-genai>=1.0.0",
            "litellm>=1.0.0",
            "pillow>=9.0.0",
            "numpy>=1.20.0",
            "pandas>=1.3.0",
            "matplotlib>=3.4.0",
        ],
    },
    entry_points={
        'console_scripts': [
            'interpreter-smol=interpreter_smol.cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
	"Programming Language :: Python :: 3.11",
	"Programming Language :: Python :: 3.12"
    ],
)
