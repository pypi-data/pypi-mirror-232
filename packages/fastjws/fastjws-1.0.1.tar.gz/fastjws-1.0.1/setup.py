from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
  name='fastjws',
  version='1.0.1',
  author='EugeneKo',
  author_email='eugene.kochetov02@gmail.com',
  description='This library will help you use JWT authentication in FastAPI!',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/Eugenekochetov02/fastjws',
  packages=find_packages(),
  install_requires=['fastapi>=0.103.1', 'python-jose>=3.3.0'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='example python',
  project_urls={},
  python_requires='>=3.10'
)
