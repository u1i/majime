import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="majime",
    version="0.0.3",
    author="Uli Hitzel",
    author_email="uli.hitzel@gmail.com",
    description="Dead Simple API Unit Tests",
    #long_description="A simple but powerful toolkit to perform unit testing on REST APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/u1i/majime",
    packages=['majime'],
    install_requires=['requests', 'pyyaml'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
      entry_points={
          'console_scripts': [
              'majime = majime.__main__:main'
          ]
      }
)
