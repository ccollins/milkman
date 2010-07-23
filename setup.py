from setuptools import setup


VERSION = __import__("milkman").__version__


long_description = ""
try:
    long_description = open("docs/index.txt", "rb").read()
except:
    pass


setup(name="milkman",
    version=VERSION,
    packages = ["milkman"],
    author="Wilkes Joiner, Chuck Collins",
    author_email="chuck.collins@gmail.com",
    install_requires=["docutils>=0.3"],
    license = "MIT",
    keywords = "django testing mock stub",
    description = "Testing django without all the fixtures",
    url="http://testdjango.org/",
    long_description=long_description
)
