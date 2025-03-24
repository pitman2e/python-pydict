import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pydict",
    version="0.10.0",
    author="pitman2e",
    author_email="pitman2e at gm__l c_m",
    description="A Dictionary Scalper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pitman2e/pydict",
    project_urls={
        "Bug Tracker": "https://github.com/pitman2e/pydict/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    packages=['pydict'],
    package_dir={"pydict": "py_src/pydict"},
    package_data={'pydict': ['ui/dict.ui']},
    python_requires=">=3.8",
    install_requires=['hanziconv', 'PyQt6', 'pyperclip', 'requests', 'bs4'],
)
