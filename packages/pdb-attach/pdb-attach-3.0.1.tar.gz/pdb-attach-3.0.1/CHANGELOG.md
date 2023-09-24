# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

### [3.0.1](///compare/v3.0.0...v3.0.1) (2023-09-23)


### Bug Fixes

* detach without hanging and free up server for new connections 528cb8a, closes #25

## [3.0.0](///compare/v2.0.0...v3.0.0) (2022-04-13)


### ⚠ BREAKING CHANGES

* breaks public API

### Bug Fixes

* properly handle pdb interact command 751c8dc, closes #18

## [2.0.0](///compare/v1.1.0...v2.0.0) (2022-02-18)


### ⚠ BREAKING CHANGES

* listen and unlisten functions have moved, breaking the API.

* seperate server, signal, and detach functionality c6a4861

## [1.1.0](///compare/v1.0.6...v1.1.0) (2021-08-08)


### Features

* client side API b6b5116, closes #12

### [1.0.6](///compare/v1.0.5...v1.0.6) (2021-04-11)


### Bug Fixes

* properly handle empty string e948e09, closes #11

### [1.0.5](///compare/v1.0.4...v1.0.5) (2020-12-12)


### Bug Fixes

* raise a warning on Windows 15f1902, closes #4

### [1.0.4](///compare/v1.0.3...v1.0.4) (2020-11-30)


### Bug Fixes

* bring type stub up to date ade0144
* drop pbr a145f1a
* use correct path for VERSIONS.txt 22cf87d

### [1.0.3](///compare/v1.0.2...v1.0.3) (2020-11-30)


### Bug Fixes

* dont upload multiple versions to PyPI b8fe6db

### [1.0.2](///compare/v1.0.1...v1.0.2) (2020-11-30)


### Bug Fixes

* python requirements 5d19ae3

### [1.0.1](///compare/v1.0.0...v1.0.1) (2020-11-30)


### Bug Fixes

* dont specify platform 277fe24
