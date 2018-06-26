from setuptools import setup

setup(
    name="impromptu",
    version="0.9.1",
    description="Command-line based forms library. Supports multiple platforms. Has support for autocompletion, logic jumps, typeaheads, and more through an extensible interface.",
    long_description="",
    url="https://github.com/imdaveho/impromptu",
    author="Dave Ho",
    author_email="imdaveho@gmail.com",
    license="MIT",
    classifiers=[],
    packages=["impromptu", "impromptu.fields", "impromptu.utils"],
    keywords="terminal prompt forms cli tooling command-line",
    setup_requires=["intermezzo>=0.1.0"],
    )
