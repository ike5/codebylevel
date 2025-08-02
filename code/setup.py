from setuptools import setup
from setuptools.command.install import install
import subprocess
import sys


class PostInstallCommand(install):
    def run(self):
        install.run(self)
        try:
            print("Running post-install script to install shell completion...")
            retcode = subprocess.call([sys.executable, "post_install.py"])
            if retcode != 0:
                print(f"Warning: post-install script exited with code {retcode}")
            else:
                print("Post-install script completed successfully.")
        except Exception as e:
            print(f"Error running post-install script: {e}")


setup(
    name="cbl",
    version="0.1",
    description="CLI tool for code-by-level documentation management",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/cbl",
    license="MIT",
    python_requires=">=3.8",
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
    cmdclass={
        "install": PostInstallCommand,
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
