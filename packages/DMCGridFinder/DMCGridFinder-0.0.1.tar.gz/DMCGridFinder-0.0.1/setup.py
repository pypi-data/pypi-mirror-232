import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
name="DMCGridFinder",
    version="0.0.1",
    author="P. Bischoff",
    author_email="peter.bischoff@ikts.fraunhofer.de",
    description="Approximate DMC target positions from sets of coordinates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'scikit-learn==1.1.3',
        'scikit-image==0.19.3',
        'pystrich==0.8',
        'pandas',
    ],
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    python_requires='>=3.9',
)
