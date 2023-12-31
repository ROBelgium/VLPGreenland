# Figure S19-21: Polarisation analysis of VLP ground motion

This folder contains the python code and a shell script to reproduce
the content of subplot Fig. 4C in the manuscript.

The following python modules are required for import:
argparse, textwrap, obspy, matplotlib, numpy, scipy, dateutil, operator

## Files in this directory

`polarizationplots.sh`: Run this shell script to produce the diagram files.

`dldata.py`: Python program to download time series and metadata.

`plotstation.py`: Python program to run the polarization analysis and create diagrams.

`modules/VLPtools.py`: Python module for application of response simulation
filters.

`modules/invresponse.py`: Python module to create terminal dump of obspy
inventory data.

`modules/pazfilter.py`: Python module with various helpers to handle recursive
time series filters.

## Earthquakes to be considered on 2023-09-16
The parameters in `polarizationplots.sh` are set to avoid interference with
stronger signals from earthquakes.
The following list is obtained from the 
[GEOFON FDSNws](http://geofon.gfz-potsdam.de/fdsnws/event/1/query?start=2023-09-16&end=2023-09-17&limit=40&format=text):

| #EventID    | Time                       | Latitude   | Longitude   | Depth/km | Author | Catalog | Contributor | ContributorID | MagType | Magnitude | MagAuthor | EventLocationName                    | EventType |
| ----------- | -------------------------- | ---------- | ----------- | -------- | ------ | ------- | ----------- | ------------- | ------- | --------- | --------- | ------------------------------------ | --------- |
| gfz2023sfda | 2023-09-16T22:51:24.68     | 40.774000  | 51.897000   | 10.0     |        |         | GFZ         | gfz2023sfda   | mb      | 4.53      |           | Caspian Sea                          |           |
| gfz2023sezy | 2023-09-16T21:17:39.72     | -0.451000  | 133.341000  | 10.0     |        |         | GFZ         | gfz2023sezy   | M       | 4.91      |           | West Papua Region, Indonesia         |           |
| gfz2023sezv | 2023-09-16T21:14:02.85     | -7.549000  | 127.492000  | 162.7    |        |         | GFZ         | gfz2023sezv   | mb      | 4.49      |           | Banda Sea                            |           |
| gfz2023sezc | 2023-09-16T20:52:51.06     | -13.298000 | 167.101000  | 10.0     |        |         | GFZ         | gfz2023sezc   | M       | 5.09      |           | Vanuatu Islands                      |           |
| gfz2023sevw | 2023-09-16T19:14:15.38     | -41.066000 | -89.111000  | 10.0     |        |         | GFZ         | gfz2023sevw   | M       | 5.07      |           | Southeast of Easter Island           |           |
| gfz2023sevs | 2023-09-16T19:08:57.51     | -24.297000 | -67.562000  | 227.4    |        |         | GFZ         | gfz2023sevs   | mb      | 4.0       |           | Chile-Argentina Border Region        |           |
| gfz2023seuj | 2023-09-16T18:28:17.4      | 44.799000  | 150.286000  | 29.7     |        |         | GFZ         | gfz2023seuj   | mb      | 4.57      |           | East of Kuril Islands                |           |
| gfz2023sesm | 2023-09-16T17:31:09.37     | -58.032000 | -25.533000  | 10.0     |        |         | GFZ         | gfz2023sesm   | mb      | 4.93      |           | South Sandwich Islands Region        |           |
| gfz2023sepj | 2023-09-16T15:56:48.33     | 55.616000  | 160.274000  | 185.2    |        |         | GFZ         | gfz2023sepj   | mb      | 4.47      |           | Kamchatka Peninsula, Russia          |           |
| gfz2023sepg | 2023-09-16T15:53:51.89     | 50.489000  | 6.409000    | 2.0      |        |         | GFZ         | gfz2023sepg   | ML      | 2.78      |           | Germany                              |           |
| gfz2023selc | **2023-09-16T13:47:58.09** | -13.761000 | 66.216000   | 10.0     |        |         | GFZ         | gfz2023selc   | **Mw**  | **5.4**   |           | **Mid-Indian Ridge**                 |           |
| gfz2023sekm | 2023-09-16T13:29:31.05     | 6.750000   | -72.998000  | 151.6    |        |         | GFZ         | gfz2023sekm   | M       | 4.91      |           | Northern Colombia                    |           |
| gfz2023sedt | 2023-09-16T10:04:54.21     | 3.896000   | 126.360000  | 10.0     |        |         | GFZ         | gfz2023sedt   | M       | 5.0       |           | Talaud Islands, Indonesia            |           |
| gfz2023seay | 2023-09-16T08:39:30.59     | -6.009000  | 151.307000  | 10.0     |        |         | GFZ         | gfz2023seay   | M       | 5.06      |           | New Britain Region, Papua New Guinea |           |
| gfz2023sdwf | 2023-09-16T06:16:01.29     | 45.576000  | 26.453000   | 124.5    |        |         | GFZ         | gfz2023sdwf   | M       | 3.35      |           | Romania                              |           |
| gfz2023sdnw | 2023-09-16T02:03:21.46     | 38.693000  | 18.012000   | 10.0     |        |         | GFZ         | gfz2023sdnw   | Mw      | 3.99      |           | Ionian Sea                           |           |
| gfz2023sdnv | 2023-09-16T02:01:49.9      | -30.761000 | -178.345000 | 10.0     |        |         | GFZ         | gfz2023sdnv   | mb      | 5.32      |           | Kermadec Islands, New Zealand        |           |
| gfz2023sdmt | 2023-09-16T01:29:20.45     | -5.742000  | 102.927000  | 29.5     |        |         | GFZ         | gfz2023sdmt   | Mw      | 4.4       |           | Southern Sumatra, Indonesia          |           |

