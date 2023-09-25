import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SpacemanX",
    version="0.99",
    author="Droidtown Linguistic Tech. Co. Ltd.",
    author_email="info@droidtown.co",
    description="SpacemanX is a module used to create space (make room) between semi-width and full-width characters.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Droidtown/SpacemanX",
    project_urls={
        "Source": "https://github.com/Droidtown/SpacemanX",
    },
    license="MIT License",
    keywords=[
        "NLP",
        "Chinese word segmentation",
        "computational linguistics",
        "language",
        "linguistics",
        "natural language",
        "natural language processing",
        "natural language understanding",
        "parsing",
        "syntax",
        "text analytics"
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        #"Environment :: Console",
        "Intended Audience :: Developers",
        "Natural Language :: Chinese (Traditional)",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6.1",
)
