from setuptools import setup, find_packages
from os.path import dirname, join, isfile
readme_exists = True
long_description = ""

# Get the long description from the README file if it exists
if isfile(join(dirname(__file__), "README.md")):
	README_PATH = join(dirname(__file__), "README.md")
elif isfile(join(dirname(__file__), "docs/README.md")):
	README_PATH = join(dirname(__file__), "docs/README.md")
else:
	readme_exists = False

# Get the long description from the README file if it exists
if readme_exists:
	with open(README_PATH) as file:
		long_description = file.read()

setup(
	name = "Selene_wdm_4.0.1",
	version = "0.9.9",
	author = "Yevhen Halitsyn",
	description = "last version Selene + webdriver-manager 4.0.1",
	long_description = long_description,
	long_description_content_type = "text/markdown",
	packages = find_packages()
)