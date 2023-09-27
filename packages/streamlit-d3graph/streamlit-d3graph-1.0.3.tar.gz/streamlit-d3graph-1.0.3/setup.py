import setuptools

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

NAME = "streamlit-d3graph"

VERSION = "1.0.3"

INSTALL_REQUIRES = ["d3graph>=2.4.10", "streamlit", "seaborn"]

setuptools.setup(
    name=NAME,
    version=VERSION,
    author="Snehan Kekre",
    author_email="contact@snehankekre.com",
    description="A simple component to display d3graph network graphs in Streamlit apps.",  # noqa: E501
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/snehankekre/streamlit-d3graph",
    install_requires=INSTALL_REQUIRES,
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
