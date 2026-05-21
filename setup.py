from setuptools import setup

setup(
    name="modelos_decision",
    version="1.0.0",
    description="Herramientas de Modelos de Decisión Multicriterio para Google Colab",
    py_modules=[
        "linea1_estadistica",
        "linea2_normalizacion",
        "linea3_ponderaciones",
        "linea4_agregacion",
        "linea5_ahp",
        "linea6_topsis",
        "linea7_rim",
    ],
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
