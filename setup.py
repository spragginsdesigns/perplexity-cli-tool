from setuptools import setup, find_packages

setup(
    name="perplexity-cli",
    version="0.1.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
        "httpx>=0.24.0",
        "pydantic>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "pplx=perplexity_cli.cli:app",
        ],
    },
    python_requires=">=3.7",
    author="Your Name",
    author_email="your.email@example.com",
    description="CLI tool for querying Perplexity API",
    keywords="perplexity, cli, ai",
    url="https://github.com/yourusername/perplexity-cli-tool",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)