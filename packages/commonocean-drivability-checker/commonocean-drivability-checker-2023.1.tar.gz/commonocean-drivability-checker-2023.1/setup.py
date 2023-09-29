from setuptools import setup, dist, find_packages


class BinaryDistribution(dist.Distribution):
    """ Make sure the setup.py will be a binary distribution. """

    def has_ext_modules(foo):
        return True


setup(
    name='commonocean-drivability-checker',
    version='2023.1',
    description='Drivability checker for CommonOcean scenarios.',
    url='https://commonocean.cps.cit.tum.de',
    author='Technical University of Munich',
    author_email='commonocean@lists.lrz.de',
    license='BSD',
    data_files=[('.', ['LICENSE'])],

    # Source
    distclass=BinaryDistribution,
    zip_safe=False,
    include_package_data=True,
    packages=['commonocean_dc'],
    package_data={'commonocean_dc': ['*.so']},

    # Requirements
    python_requires='>=3.8',
    install_requires=[
        'commonroad-drivability-checker==2023.1',
        'numpy<=1.22.4',
        'scipy<=1.7.2',
        'matplotlib<=3.5.3',
        'polygon3>=3.0.8',
        'shapely>=1.6.4',
        'triangle>=20200424',
        'commonocean-io==2023.1',
        'commonocean-vessel-models==1.0.0',
        'commonocean-rules==1.0.2',
        'jupyter>=1.0.0',
        'pandoc>=1.0.2',
        'sphinx_rtd_theme>=0.4.3',
        'sphinx>=3.0.3',
        'nbsphinx_link>=1.3.0',
        'nbsphinx>=0.6.1',
        'breathe>=4.18.0',

    ],

    # Additional information
    classifiers=[
        "Programming Language :: C++",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
)
