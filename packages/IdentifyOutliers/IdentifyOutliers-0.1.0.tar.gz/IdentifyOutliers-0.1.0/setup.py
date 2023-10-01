from setuptools import setup

setup(
    name='IdentifyOutliers',
    version='0.1.0',
    packages=['IdentifyOutliers'],
    install_requires=[
        'pandas',
        'scikit-learn',
        'numpy'
    ],
    author='Amith Lokugamage',
    author_email='amithpdn@gmail.com',
    description='A Python package for efficient scaling and outlier handling of pandas DataFrames using the some of the most popular outlier elimination approaches.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/amithpdn/IdentifyOutliers/',
    keywords = ['Data Science', 'Outliers', 'Data Preprocessing'], 
    python_requires='>=3.6'
)
