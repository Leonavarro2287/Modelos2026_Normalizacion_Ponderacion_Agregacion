from setuptools import setup, find_packages

setup(
    name="mpa_modelos",
    version="0.1.0",
    description="Herramientas de Normalización, Ponderación y Agregación Multicriterio para Google Colab",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "scipy",
        "matplotlib",
        "ipywidgets",
        "openpyxl",
    ],
)
