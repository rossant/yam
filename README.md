# Remote controller for Yamaha AV network systems

This Python module provides a `RemoteController` class and a CLI tool to control a Yamaha AV network system.

## Dependencies

* Python 2 or Python 3
* six
* xmltodict

## Installation

```bash
git clone https://github.com/rossant/yam.git
cd yam
python setup.py install
```

## Usage

```bash
yam power on
yam tuner
yam preset 5
yam server
yam list
yam select 3
yam play
yam pause
yam stop
yam nav myartist myalbum mysingle
```

## Notes

* This script is customized to my home audio installation -- you'll have to edit the module to make it work on your own installation.
* There is no documentation.
