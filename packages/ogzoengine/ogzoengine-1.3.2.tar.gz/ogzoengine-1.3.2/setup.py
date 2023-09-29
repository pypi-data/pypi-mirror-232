from setuptools import find_packages, setup

with open("ogzoengine/README.md", "r") as f:
    long_description_read = f.read()

setup(
      name='ogzoengine',
      version='1.3.2',
      description='basic pygame engine',
      author='Coguz',
      packages=['ogzoengine'],
      long_description=long_description_read,
      long_description_content_type="text/markdown",
      zip_safe=False,
      classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
      ],
      install_requires=["bson >= 0.5.10"],
      extras_require={
        "dev": ["pytest>=7.0", "twine>=4.0.2"],
      },
      python_requires=">=3.10",
    )