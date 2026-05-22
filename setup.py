from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="modelos2026",
    version="1.0.0",
    author="Leonardo Navarro",
    author_email="leonardo@example.com",
    description="Herramienta para análisis de decisiones multicriterio: Normalización, Ponderación y Agregación",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Leonavarro2287/Modelos2026_Normalizacion_Ponderacion_Agregacion",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "matplotlib>=3.4.0",
        "ipywidgets>=7.6.0",
        "openpyxl>=3.0.0",
        "jupyter>=1.0.0",
    ],
)
