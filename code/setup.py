from setuptools import setup

setup(
    name="cbl",
    version="0.1",
    py_modules=["main"],
    install_requires=[
        "typer[all]",
        "rich",
        "GitPython",
        "rapidfuzz",
        "packaging"
    ],
    entry_points={
        "console_scripts": [
            "cbl=main:app"
        ],
    },
)
