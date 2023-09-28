from setuptools import setup, find_packages

setup(
    name='snusbase_scraper',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'beautifulsoup4',
    ],
    author='Deagan',
    author_email='deaganm656@gmail.com',
    description='a scraper for snusbase that returns results in a dictionary',
    long_description='a scraper for snusbase that returns results in a dictionary',
    long_description_content_type='text/markdown',
    url='https://github.com/SnusbaseScraper/SnusbaseScraper',
)