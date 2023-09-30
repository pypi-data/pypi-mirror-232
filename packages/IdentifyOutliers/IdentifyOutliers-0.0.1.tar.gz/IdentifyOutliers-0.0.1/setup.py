from setuptools import setup

setup(
    name='IdentifyOutliers',
    version='0.0.1',
    packages=['IdentifyOutliers'],
    install_requires=[
        'pandas',
        'scikit-learn',
        'numpy'
    ],
    author='Amith Lokugamage',
    author_email='amithpdn@gmail.com',
    description='IdentifyOutliers provides a combined functionality of scaling data using the standard scaler approach while also removing outliers based on a z-score threshold for panda\'s projects.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/amithpdn/IdentifyOutliers/',
    keywords = ['Data Science', 'Outliers', 'Data Preprocessing'], 
    python_requires='>=3.6'
)
