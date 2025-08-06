from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="distribuciones-lucero-stock",
    version="1.0.0",
    author="Distribuciones Lucero",
    description="Sistema de gestión de inventario para Distribuciones Lucero",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=[
        "streamlit>=1.46.1",
        "pandas>=2.3.1",
        "paramiko>=3.5.1", 
        "schedule>=1.2.2",
        "requests>=2.31.0",
    ],
)