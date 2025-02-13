from setuptools import setup, find_packages

setup(
    name="file_reporter",
    version="0.1.0",
    author="Robert Alexander Massinger",
    author_email="robert.massinger@nutshell-solutions.de",
    description="A brief description of your package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/rob9999/my-python-package",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pathspec==0.12.1",
        "setuptools==65.5.0",
        # List your package dependencies here
    ],
)
