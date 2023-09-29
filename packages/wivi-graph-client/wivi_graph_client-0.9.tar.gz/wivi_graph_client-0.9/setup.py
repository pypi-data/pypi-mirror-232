from setuptools import setup, find_packages

setup(
    name="wivi_graph_client",
    version="0.9",
    packages=find_packages(),
    install_requires=[
        "requests",
        "graphql-core",
    ],
    py_modules=["client"],
    author="Haseeb Saif Ullah",
    author_email="hsaif@intrepidcs.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
