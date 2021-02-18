from setuptools import setup, find_packages
setup(
    name="ness",
    version="0.1",
    packages=find_packages(),

    install_requires=[requirement.strip('\n') for requirement in open('requirements.txt')],
    author="Frederico Schmitt Kremer",
    author_email="fred.s.kremer@gmail.com",
    description="NESS: an alignment-free tool for sequence search based on word embedding",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    keywords="bioinformatics machine-learning data science",
    project_urls={
        "Source Code": "https://github.com/omixlab/ness"
    }
)