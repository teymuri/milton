from setuptools import setup, find_packages


with open('README.md') as file:
    long_description = file.read()

setup(name='computil',
      version='HEAD',
      description='composition utilities',
      author='Amir Teymuri',
      author_email='amiratwork22@gmail.com',
      license='MIT',
      url='https://github.com/teymuri/computil.git',
      packages=find_packages(where="src"),
      package_dir = {'': 'src'},
      # package_data={
      #     '' : ['License.txt', 'README.rst', 'documentation/*'],
      #     'examples' : ['single-note-example.py', 'c-major-scale.py']},
      # include_package_data = True,
      # platforms='Platform Independent',
      # classifiers=[
      #       'Development Status :: 4 - Beta',
      #       'Intended Audience :: Developers',
      #       'Programming Language :: Python :: 2',
      #       'Programming Language :: Python :: 2.7',
      #       'Programming Language :: Python :: 3',
      #       'Programming Language :: Python :: 3.2',
      #       'Programming Language :: Python :: 3.3',
      #       'Programming Language :: Python :: 3.4',
      #       'Programming Language :: Python :: 3.5',
      #       'License :: OSI Approved :: MIT License',
      #       'Operating System :: OS Independent',
      #       'Topic :: Multimedia :: Sound/Audio :: MIDI',
      #     ],
      keywords = 'Music Composition',
      long_description=long_description
     )

