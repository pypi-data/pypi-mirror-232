# Data processing package

This package is dedicated to providing functionality for processing data in text, HTML formats and etc. for further usage in predictors and endpoints. The package consists of services EmailsProcessor, TextParser, HTMLParser and helpers such as TextValidator. 

## Package installation guide
To install package with pip use:
`pip install reply-data-processing`

To install package locally without usage of pip run this command in virtual env from the directory of the package:
`python3 setup.py install`

## Package release guide
1. Change package version in setup files (setup.py and setup.cfg)
2. Rebuild package after the changes (to update generated directories and egg-info files):
`pip install build`
`python -m build`
3. Push the changes to the repo and create a release in Releases tab. 
Create a new tag with new package version to generate release notes. The workflow described in `python-publish.yml` will be used for pushing new package version to pip. 