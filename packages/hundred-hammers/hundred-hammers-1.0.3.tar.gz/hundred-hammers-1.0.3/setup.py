from setuptools import setup

setup(name='hundred_hammers',
      version='1.0.3',
      description='Batch execution of ML models to a dataset',
      url='http://github.com/vgarciasc/hundred_hammers',
      author='Vinicius Garcia',
      author_email='vinizinho@vinizinho.net',
      license='MIT',
      packages=['hundred_hammers'],
      install_requires=[
          "seaborn", "scikit-learn", "pandas",
          "matplotlib", "adjustText", "tqdm",
          "schema", "pytest"],
      zip_safe=False)
