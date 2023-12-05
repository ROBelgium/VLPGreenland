# Fig 4B: Propagation of the VLP signal around the Earth

Plot beams (in 100km bins) of the VLP signal around the globe.

`download.py`: Download seismograms

`prep.py`: Pre-process seismograms (instrument response correction, ...)

`prep_moveout.ipynb`: Prepare distance-sorted waveforms file for plotting routine

`plot_fig4B.py`: Computes distance-binned beams and plots waveforms.

Python requirements:

- numpy, scipy, matplotlib
- pytorch
- obspy
- tqdm
- geokernels
