from setuptools import setup, find_packages


setup(
    name='Python-FOSS-HRTest',
    version='0.2',
    license='MIT',
    author="suryateja",
    author_email='suryateja.d@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/3PPMSTest/Python-FOSS-HRTest',
    keywords='Python-FOSS-HRTest',
    install_requires=[
          'scikit-learn',
      ],

)
