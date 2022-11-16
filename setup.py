#!/usr/bin/env python

from setuptools import setup

requirements = '''
numpy
nibabel
scipy
joblib
numba
snakemake
ipykernel
'''.strip().split()

if __name__ == "__main__":
    setup(
        name='tvb_hip',
        version='0.8.0',
        install_requires=requirements,
    )
