from setuptools import setup, find_packages

setup(
    name="notdiamond",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "python-dotenv>=0.19.0",
        "openai>=1.0.0",
        "pydantic>=2.0.0",
        "requests>=2.31.0",
    ],
) 