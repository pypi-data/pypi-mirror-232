from setuptools import find_packages, setup


setup(
      name='ogzoengine',
      version='1.3',
      description='basic pygame engine',
      author='Coguz',
      packages=['ogzoengine'],
      long_description="""Open Source Game Engine License

Version 1.0, September 28, 2023

This software can be used, modified, and distributed under the following conditions:

1. Any modification to the original source of the game engine must be accompanied by a specified notice containing the modified content and the date of the changes.

2. Modified versions must be published under the original name of the game engine.
""",
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