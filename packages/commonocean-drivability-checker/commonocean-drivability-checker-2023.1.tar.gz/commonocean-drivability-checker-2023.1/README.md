CommonOcean Drivability Checker
------------------------------

Collision avoidance, kinematic feasibility, and water-compliance must be 
validated to ensure the drivability of planned motions for autonomous 
vessels. The CommonOcean Drivability Checker toolbox unifies these checks 
in order to simplify the development and validation of motion planning 
algorithms. It is compatible with the CommonOcean benchmark suite, which 
additionally facilitates and drastically reduces the effort of the development
of motion planning algorithms. The CommonOcean Drivability Checker is based on the [CommonRoad Drivability Checker](https://gitlab.lrz.de/tum-cps/commonroad-drivability-checker).


Installing the drivability checker is possible with the following command line (considering that your using Python 3.8):

```
pip install -e .
```

Make sure that every requirement is installed and start jupyter notebook to run the [tutorials](./tutorials)

Please visit our [website for more installation instructions and documentation](https://commonocean.cps.cit.tum.de/commonocean-dc).

## Changelog

Compared to version 2022.1, the following features have been added and changed:

### Added

- New auxiliary function to check the drivability with respect to the depth of shallows/waters 

### Changed

- Improved constructing static obstacles representing collidable waters boundary from the Navigationable Area specified in the XML scenarios
- The installation of third-party libraries is not necessary anymore, due to a refactoring in the module
- The module now uses the new version of CommonOcean IO (2023.1)
- The package is no longer compatible with Python 3.7

**If you use our drivability checker for research, please consider citing our papers:**
```
@inproceedings{Krasowski2022a,
	author = {Krasowski, Hanna and Althoff, Matthias},
	title = {CommonOcean: Composable Benchmarks for Motion Planning on Oceans},
	booktitle = {Proc. of the IEEE International Conference on Intelligent Transportation Systems},
	year = {2022},
}

@inproceedings{Pek2020,
	author = {Christian Pek, Vitaliy Rusinov, Stefanie Manzinger, Murat Can Üste, and Matthias Althoff},
	title = {CommonRoad Drivability Checker: Simplifying the Development and Validation of Motion Planning Algorithms},
	booktitle = {Proc. of the IEEE Intelligent Vehicles Symposium},
	year = {2020},
}

```
