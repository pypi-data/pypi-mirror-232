import os
from importlib.machinery import SourceFileLoader
from setuptools import setup, find_packages

version = (
    SourceFileLoader("llmstudio.version", os.path.join("llmstudio", "version.py")).load_module().VERSION
)

with open(os.path.join("requirements", "core-requirements.txt")) as f:
    CORE_REQUIREMENTS = f.read().splitlines()

setup(
    name="llmstudio",
    author="TensorOps",
    url="https://llmstudio.ai/",
    project_urls={
        "Source Code": "https://github.com/tensoropsai/llmstudio",
        "Bug Tracker": "https://github.com/tensoropsai/llmstudio/issues",
    },
    author_email="contact@tensorops.ai",
    description="Prompt Perfection at Your Fingertips",
    keywords="ml ai llm llmstudio tensorops",
    


    version=version,
    packages=find_packages(where='llmstudio'),
    install_requires=CORE_REQUIREMENTS,
    package_dir={"": "llmstudio"},
)
