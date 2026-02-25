from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="osint-lab",
    version="2.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A unified OSINT platform for cybersecurity intelligence gathering",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/osint-lab",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Flask>=3.0.0",
        "flask-cors>=4.0.0",
        "requests>=2.31.0",
        "dnspython>=2.4.2",
        "python-whois>=0.8.0",
        "ipwhois>=1.2.0",
        "Pillow>=10.1.0",
        "PyPDF2>=3.0.1",
        "python-docx>=1.1.0",
        "pyOpenSSL>=23.3.0",
        "beautifulsoup4>=4.12.2",
        "lxml>=4.9.3",
        "phonenumbers>=8.13.26",
        "aiohttp>=3.9.1",
        "PySocks>=1.7.1",
    ],
    entry_points={
        "console_scripts": [
            "osint-lab=app:main",
        ],
    },
)
