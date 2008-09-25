from setuptools import setup, find_packages
setup(
    name = "Milkman",
    version = "0.1",
    packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = ['docutils>=0.3'],

    package_data = {
        '': ['*.txt', '*.rst'],
    },
    
    # metadata for upload to PyPI
    author = "Wilkes Joiner",
    author_email = "wilkesjoiner@gmail.com",
    description = "A Django model generator to replace fixtures for testing",
    license = "BSD",
    keywords = "django testing mock stub",
    url = "http://github.com/wilkes/milkman",
)