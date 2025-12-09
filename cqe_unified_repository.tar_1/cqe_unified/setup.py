from setuptools import setup, find_packages

setup(
    name="cqe",
    version="5.0.0",
    description="Cartan Quadratic Equivalence - Unified System",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "networkx>=2.6.0",
        "matplotlib>=3.4.0",
    ],
)
