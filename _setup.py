from setuptools import setup

setup(
	name='computil',
	version='1.0.0',
	description='Composition Utilities',
	author='Amir Teymuri',
	author_email='amiratwork22@gmail.com',
	packages=['computil'],
	install_requires=['python-rtmidi', 'MIDIUtil', 'mido', 'numpy'],
)

