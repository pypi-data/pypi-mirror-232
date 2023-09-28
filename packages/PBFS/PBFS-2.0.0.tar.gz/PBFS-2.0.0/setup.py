from setuptools import setup, find_packages


desc = "Performance Based Feature selection Technique: Prototype"

setup(
    name='PBFS',
    version='2.0.0',
    description= desc,
    long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
    long_description_content_type='text/markdown',
    url = 'https://github.com/hongzhu6129/HidenFeatures',
    author = 'Movin Fernandes, Prof. Hong Zhu',
    author_email= 'movin.fernandes@hotmail.com, hzhu@brookes.ac.uk',
    maintainer='Movin Fernandes',
    maintainer_email='movin.fernandes@hotmail.com',
    license='MIT',
    keywords=['Feature selection','Machine learning','Feature engineering','Performance based','open source'],
    packages=find_packages(),
    install_requires = '' ,
    include_package_data=True,
    
)
