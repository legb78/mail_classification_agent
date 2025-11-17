"""
Configuration du package Python
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mail-classification-agent",
    version="1.0.0",
    author="Mail Classification Agent Team",
    author_email="ticketsdata5@gmail.com",
    description="Agent de traitement automatique de tickets par e-mail",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-repo/mail-classification-agent",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Communications :: Email",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "mail-agent=main:main",
        ],
    },
)

