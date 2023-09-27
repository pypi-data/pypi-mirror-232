import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="TwitAnalysis",
    version="1.1",
    author="Michael Mondoro",
    author_email="michaelmondoro@gmail.com",
    description="Package for analyzing Twitter data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/michaelMondoro/TwitAnalysis",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "tweepy==4.12.1",
        "PyYAML",
        "termcolor",
        "progress",
        "prettytable",
        "textblob",
    ],
    python_requires='>=3.10',
)
