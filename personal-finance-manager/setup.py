from setuptools import setup, find_packages

setup(
    name="personal-finance-manager",
    version="1.0.0",
    description="A command-line Personal Finance Management Application",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "colorama>=0.4.6",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "finance-manager=src.cli:main",
        ],
    },
)

