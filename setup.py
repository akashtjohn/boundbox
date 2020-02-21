import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="boundbox", 
    version="0.0.1",
    author="Akash Thomas",
    author_email="akash.thomas1618@gmail.com",
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
