import typing

import setuptools

import server_check


def load_req() -> typing.List[str]:
	with open('requirements.txt') as f:
		return f.readlines()


VERSION = server_check.__version__

setuptools.setup(
	name="nose_server_check",
	version=VERSION,
	author="Seuling N.",
	description="Check functions of a server",
	long_description="Check functions of a server",
	packages=setuptools.find_packages(exclude=["tests*"]),
	install_requires=load_req(),
	python_requires=">=3.10",
	license="Apache License 2.0",
	entry_points={
		"console_scripts": [
			"run_checks = server_check.run_checks:run_all_checks"
		]
	}
)
