import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyvitae",
    version="2.0.2",
    author="Jin-Hong Du",
    author_email="jinhongd@andrew.cmu.edu",
    packages=["VITAE"],
    description="Joint Trajectory Inference for Single-cell Genomics Using Deep Learning with a Mixture Prior",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jaydu1/VITAE",
    install_requires=[
        "tensorflow >= 2.3",
        "tensorflow_probability >= 0.11",
        "pandas", 
        "jupyter", 
        "umap-learn >= 0.5.0", 
        "matplotlib", 
        "numba", 
        "seaborn", 
        "leidenalg", 
        "scikit-learn",        
        "scikit-misc", 
        "scikit-learn-extra", 
        "networkx",
        "statsmodels",
        "scanpy>=1.8.2",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)