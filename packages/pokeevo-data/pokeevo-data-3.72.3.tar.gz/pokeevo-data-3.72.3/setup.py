from setuptools import setup, find_packages

setup(
    name="pokeevo-data",
    version="3.72.3",
    description="A Python module for scraping Pokémon data.",
    author="ohioman02",
    author_email="gdnunuuwu@gmail.com",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
)
