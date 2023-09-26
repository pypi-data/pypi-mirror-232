import setuptools

with open("README.md", "r", encoding="utf-8", newline="\n") as fh:
    long_description = fh.read()

setuptools.setup(
    name='ask_question',
    version='1.2.3',
    packages=setuptools.find_packages(),
    install_requires=[
    ],
    author="Henry Letellier",
    author_email="henrysoftwarehouse@protonmail.com",
    description="A module that simplifies the boiling process when asking the user a question via a TTY interface.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Hanra-s-work/ask_question",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
