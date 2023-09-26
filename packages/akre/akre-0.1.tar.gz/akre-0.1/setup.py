import setuptools

setuptools.setup(
  name = 'akre',
  packages=['akre'],
  version = '0.1',
  license='MIT',
  description = 'Boiler plate for creating an ML model',
  author = 'Elsa Tamara',
  author_email = 'elsaatamara@gmail.com',
  url = 'https://github.com/elsatmr/akre-create-model.git',
  download_url = 'https://github.com/elsatmr/akre-create-model.git/archive/v_01.tar.gz',
  keywords = ['machine_learning', 'model', 'boilerplate', 'ml'],
  install_requires=[
    'nbformat'
  ],
  entry_points={
    'console_scripts': [
        'akre = akre.create_akre_model:main'
    ]
  },
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)