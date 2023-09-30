# Changelog

All notable changes to `libcasm-clexulator` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [2.0a2] - 2023-09-28

### Fixed

- Fixed calculation of homogeneous mode space when some sites do not include a local DoF


## [2.0a1] - 2023-08-20

This release separates out casm/clexulator from CASM v1. It creates a Python package, libcasm.clexulator, that enables using casm/clexulator and may be installed via pip install, using scikit-build, CMake, and pybind11. This release also includes usage and API documentation for using libcasm.clexulator, built using Sphinx.

### Added

- Added Python package libcasm.clexulator
- Added scikit-build, CMake, and pybind11 build process
- Added GitHub Actions for unit testing
- Added GitHub Action build_wheels.yml for Python x86_64 wheel building using cibuildwheel
- Added Cirrus-CI .cirrus.yml for Python aarch64 and arm64 wheel building using cibuildwheel
- Added Python documentation

### Removed

- Removed autotools build process
- Removed boost dependencies
