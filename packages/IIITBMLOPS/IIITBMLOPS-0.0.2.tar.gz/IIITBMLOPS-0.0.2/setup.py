import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="IIITBMLOPS",
    version="0.0.2",
    author="subbhashit mukherjee",
    author_email="subbhashitmukherjee@gmail.com",
    packages=["MLOX"],
    description="ML operations Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/23subbhashit/MLOX/",
    license='MIT',
    python_requires='>=3.6',
    install_requires=[
        'numpy>=1.16.6',
        'pandas>=1.0.5',
        'seaborn>=0.10.1',
        'matplotlib>=3.2.2',
        'scikit-learn>=0.23.2',
    ]
)