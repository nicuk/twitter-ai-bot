from setuptools import setup, find_packages

setup(
    name="elion",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'tweepy==4.14.0',
        'python-dotenv==1.0.0',
        'schedule==1.2.0',
        'requests>=2.25.1',
        'selenium==4.15.2',
        'webdriver-manager==4.0.1',
        'python-dateutil>=2.8.2',
        'openai>=1.0.0',
        'beautifulsoup4>=4.9.3',
        'feedparser>=6.0.2'
    ],
    author="Nico",
    description="Elion - AI-powered Twitter Bot for Crypto Trading",
    python_requires=">=3.8",
)
