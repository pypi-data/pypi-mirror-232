import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hollowdb",
    version="0.0.1",
    author="FirstBatch Team",
    author_email="developer@firstbatch.xyz",
    description="HollowDB client is the simplest way to use HollowDB, a decentralized & privacy-preserving key-value "
                "database.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://docs.hollowdb.xyz/",
    project_urls={
        "HollowDB": "https://hollowdb.xyz/",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8"
)
