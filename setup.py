from setuptools import setup

setup(name="milkman",
    version="0.2.2",
    packages = ["milkman"],
    author="Wilkes Joiner, Chuck Collins",
    author_email="chuck.collins@gmail.com",
    install_requires=["docutils>=0.3"],
    license = "MIT",
    keywords = "django testing mock stub",
    description = "Testing django without all the fixtures",
    url="http://testdjango.org/",
    long_description=open("docs/index.txt", "rb").read()
)
