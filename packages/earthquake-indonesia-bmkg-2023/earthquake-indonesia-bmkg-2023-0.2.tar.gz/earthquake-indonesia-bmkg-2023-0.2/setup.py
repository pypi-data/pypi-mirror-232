import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="earthquake-indonesia-bmkg-2023",
    version="0.2",
    author="Rendra Faris",
    author_email="farisrendra@gmail.com",
    description="This package provides the latest earthquake data in Indonesia from BMKG",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/faris-r/earthquake-bmkg",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable"
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6"
)
