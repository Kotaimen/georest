from setuptools import setup


def get_requires():
    with open('requirements.txt') as f:
        return sorted(filter(None, f.readlines()))

setup(
    name='georest',
    version='0.1.0',
    packages=[
        'georest',
        'georest.storage',
        'georest.storage.buckets',
        'georest.geo',
        'georest.model',
        'georest.view',
    ],
    include_package_data=True,
    zip_safe=False,  # not allowed as zip package
    platforms='any',
    # test_suite='nose.collector',
)
