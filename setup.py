from setuptools import setup, find_packages

setup(
    name="ness-search",
    version='0.0.2', 
    packages=find_packages(),
    install_requires=[requirement.strip('\n') for requirement in open('requirements.txt')],
    entry_points={
        'console_scripts': [
            'ness = ness.app:main'
        ]
    },
    author="Frederico Schmitt Kremer; Thiago Carvalho",
    author_email="fred.s.kremer@gmail.com",
    description="NESS: Vector-based Alignment-free Sequence Search",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    keywords="bioinformatics machine-learning data science",
    project_urls={
        "Source Code": "https://github.com/omixlab/ness"
    }
)
