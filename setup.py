from setuptools import setup, find_packages

setup(
    name="modelos_decision",
    version="1.0.0",
    description="Herramientas de Modelos de Decisión Multicriterio para Google Colab",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "scipy",
        "matplotlib",
        "ipywidgets",
        "openpyxl",
    ],
    python_requires=">=3.7",
)
