# Figure 4C: Three-component recording at II.BFO.10 (STS-6A)

This folder contains the python code and shell script required to reproduce
the content of subplot Fig. 4C in the manuscript.

The following python modules are required for import:
argparse, textwrap, obspy, matplotlib, numpy, scipy, dateutil, operator

`Fig4C.sh`: Run this shell script to produce the diagram files.

`dldata.py`: Python program to download time series and metadata.

`plotdecay.py`: Python program to create time series diagrams.

`modules/VLPtools.py`: Python module for application of response simulation
filters.

`modules/invresponse.py`: Python module to create terminal dump of obspy
inventory data.

`modules/pazfilter.py`: Python module with various helpers to handle recursive
time series filters.
