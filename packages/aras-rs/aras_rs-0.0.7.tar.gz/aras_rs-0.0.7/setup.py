from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='aras_rs',
  version='0.0.7',
  description='A recommender system and calculating metrics such as Top@k, Recall@k, and One-hit accuracy for recommender systems',
  long_description_content_type="text/markdown",
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='https://aras.kntu.ac.ir/',  
  author='Alireza Jahani',
  author_email='alirezajahani.earno@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='Recommender_system', 
  packages=find_packages(),
  install_requires=['pandas','numpy', 'lightgbm','datetime'] 
)