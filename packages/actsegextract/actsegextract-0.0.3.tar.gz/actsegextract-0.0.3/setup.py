import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="actsegextract", ## 소문자 영단어
    version="0.0.3", ##
    author="Sunkyeong Lee", ## ex) Sunkyeong Lee
    author_email="sunkyeong.lee@concentrix.com  ", ##
    description="segid extracting tool for team act", ##
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SunkyeongLee/aanlayticsact_segExtract", ##
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)