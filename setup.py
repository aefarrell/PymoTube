import setuptools

with open("README.md", "r") as fh:
    description = fh.read()

setuptools.setup(
    name="PymoTube",
    version="0.0.1",
    author="Allan Farrell",
    author_email="allanf@protonmail.com",
    packages=["atmotube"],
    description="A simple API for retrieving data from an AtmoTube via bluetooth",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/aefarrell/PymoTube",
    license='MIT',
    python_requires='>=3.13',
    install_requires=['bleak']
)
