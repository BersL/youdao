from setuptools import setup, find_packages

setup(
	name = 'youdao',
	version = '1.0',
	author = 'Bers',
	author_email = 'Me@Bersl.com',
	description = 'A tool of looking up words and fetching data on http://dict.youdao.com',
	license = 'BSD',
	packages = find_packages(),
	install_requires=['requests', 'beautifulsoup4'],
	entry_points = {
		'console_scripts' : ['youdao=src.youdao:main']
	}
);