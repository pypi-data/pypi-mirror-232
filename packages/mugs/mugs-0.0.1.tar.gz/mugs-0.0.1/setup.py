#!/usr/bin/python3


pkgname="mugs"
pkgnamefull="An efficient data structure"
version=[0,0,1]
license="BSD-3-Clause"
url="https://github.com/lingfeiwang/"+pkgname
author="Lingfei Wang"
author_email="Lingfei.Wang.github@outlook.com"



def pkg_setup():
	from setuptools import setup
	from os import path
	pkgnameu=pkgname[0].upper()+pkgname[1:].lower()
	with open(path.join(path.abspath(path.dirname(__file__)),'README.rst'),encoding='utf-8') as f:
		long_description=f.read()
	setup(name=pkgname,
		version='.'.join(map(str,version)),
		author=author,
		author_email=author_email,
		description=pkgnamefull,
		long_description=long_description,
		long_description_content_type='text/x-rst',
		url=url,
		install_requires=['numpy','torch'],
		classifiers=['Development Status :: 1 - Planning',
			'License :: OSI Approved :: BSD License',
			'Environment :: GPU :: NVIDIA CUDA',
			# 'Framework :: Pytest',
			'Intended Audience :: Science/Research',
			'Intended Audience :: Developers',
			'Operating System :: OS Independent',
			'Programming Language :: Python :: 3',
			'Topic :: Scientific/Engineering :: Bio-Informatics',
			'Topic :: Software Development :: Libraries :: Python Modules',
		],
		license=license,
		packages=[pkgname],
		package_dir={pkgname:path.join('src',pkgname)},
	)

pkg_setup()
