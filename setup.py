from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="modelos2026-normalizacion-ponderacion-agregacion",
    version="1.0.0",
    author="Leonardo Navarro",
    author_email="leonardo@example.com",
    description="Herramienta integral para análisis de decisiones multicriterio",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Leonavarro2287/Modelos2026_Normalizacion_Ponderacion_Agregacion",
    project_urls={
        "Bug Tracker": "https://github.com/Leonavarro2287/Modelos2026_Normalizacion_Ponderacion_Agregacion/issues",
        "Documentation": "https://github.com/Leonavarro2287/Modelos2026_Normalizacion_Ponderacion_Agregacion/blob/main/README.md",
        "Source Code": "https://github.com/Leonavarro2287/Modelos2026_Normalizacion_Ponderacion_Agregacion",
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    keywords="decision-making multicriteria TOPSIS AHP CRITIC RIM normalization aggregation",
)
