from setuptools import setup, find_packages

setup(
    name="decision_models",
    version="0.1.0",
    description="Paquete Python para Toma de Decisiones Multicriterio (MCDA) en Google Colab",
    author="Leonavarro2287",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "scipy",
        "matplotlib",
        "ipywidgets",
        "ipython",
        "openpyxl"
    ],
    python_requires=">=3.8",
)
