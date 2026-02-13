from setuptools import setup, find_packages
from pathlib import Path

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="booklet-ocr",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="OCR-based CD booklet to Markdown converter for Obsidian",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/booklet-ocr",
    package_dir={"": "src"},
    py_modules=[
        "main",
        "ocr_processor",
        "hybrid_ocr",
        "markdown_generator",
        "image_utils",
        "config",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "pdf": ["pymupdf4llm>=0.3.0"],
        "dev": ["black", "flake8", "pytest"],
    },
    entry_points={
        "console_scripts": [
            "booklet-ocr=main:main",
        ],
    },
)
