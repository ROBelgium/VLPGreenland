# Fig 4B: Propagation of the VLP signal around the Earth

Plot beams (in 100km bins) of the VLP signal around the globe.

This code reads waveforms that were already sorted by distance (`waveforms_24.pt`). These are a by-product of the beamforming code (see `supplementary/...`).

Python requirements:

- numpy, scipy, matplotlib
- pytorch
- obspy
