import pathlib

import pkg_resources
from setuptools import setup, find_packages

with pathlib.Path('requirements.txt').open() as requirements_txt:
    install_requires = [
        str(requirement)
        for requirement
        in pkg_resources.parse_requirements(requirements_txt)
    ]


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='PyCDArc',
      version='0.1.5',
      description='Python implementation of CDA',
      long_description=readme(),
      classifiers=[
          'Development Status :: 3 - Alpha',  # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
          'Intended Audience :: Developers',  # Define that your audience are developers
          'Topic :: Software Development :: Build Tools',
          'Programming Language :: Python :: 3.10',  # Specify which pyhton versions that you want to support
      ],
      keywords=['CDA', 'ClinicalDocumentArchitecture', 'Health'],
      url='https://github.com/EliaMenoni/PyCDA',
      author='Elia Menoni',
      author_email='eliamenoni@emenoni.eu',
      license='Proprietary',
      packages=find_packages(),
      install_requires=install_requires,
      package_data={'PyCDArc.Templating': ['dbs/CDA_TEMPLATES']},
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'],
      entry_points={
          'console_scripts': ['PyCDArc=PyCDArc.run:run'],
      }
      )
