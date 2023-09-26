from setuptools import setup, find_packages

setup(
    name="unitools",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[],
    url="https://github.com/MrTwister96/unitools",
    license="MIT",
    author="Schalk Olivier",
    author_email="olivierschalk1@gmail.com",
    description="A python library that contains various tools that I have found useful over the years.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.6"
)