from setuptools import setup


def long_description():
    with open("README.md") as readme:
        return readme.read()


setup(
    name="gues",
    version="0.3.0",
    author="Alex Markham",
    author_email="alex.markham@causal.dev",
    description="This package is for (hybrid and) score-based causal structure learning, using unconditional equivalence classes to reduce the search space.",
    long_description_content_type="text/markdown",
    long_description=long_description(),
    license="GNU Affero General Public License 3 or later (AGPL 3+)",
    packages=["gues"],
    python_requires="~=3.11",
    install_requires=["numpy"],
    extras_require={
        "reproduce_astat": [
            "numpy~=1.24.3",
            "scipy~=1.11.1",
            "matplotlib~=3.7.1",
            "pandas~=2.0.2",
            "seaborn~=0.12.2",
            "big-O~=0.11.0",
            "pycurl~=7.45.2",
            "p-tqdm~=1.4.0",
        ]
    },
    scripts=["scripts/reproduce_astat"],
)
