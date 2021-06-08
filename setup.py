import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="boundbox", 
    version="0.0.5",
    author="Akash Thomas",
    author_email="akashthomasjohn@gmail.com",
    description="Package for bounding boxes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/akash1729/boundbox",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
