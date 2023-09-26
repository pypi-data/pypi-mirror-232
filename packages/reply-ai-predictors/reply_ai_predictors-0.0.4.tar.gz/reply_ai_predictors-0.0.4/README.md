# Predictors package
This package is used to encapsulate AI models functionality and simplify their usage for direct requests or tuning. The package contains Predictor as a template for other predictors and model wrappers: 
- DaVinciModel
- TextDavinciZeroZeroThree
- GPTThreeFiveTurbo
- CurieModel
Helpers include SafetyChecker, AIAssistantConfigHandler and PresetsHandler. 

## Package installation guide
To install package with pip use:
`pip install reply-ai-predictors`

To install package locally without usage of pip run this command:
`python3 setup.py install`

## Package release guide
1. Change package version in setup files (setup.py and setup.cfg)
2. Rebuild package after the changes (to update generated directories and egg-info files):
`pip install build`
`python -m build`
3. Push the changes to the repo and create a release in Releases tab. 
Create a new tag with new package version to generate release notes. The workflow described in `python-publish.yml` will be used for pushing new package version to pip. 