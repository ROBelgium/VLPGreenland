#!/usr/bin/env python
# this is <plotdecay.py>
# ----------------------------------------------------------------------------
# 
# Copyright (c) 2023 by Thomas Forbriger (KIT, GPI, BFO) 
# 
# plot decay of VLP signal
#
# ----
# Licensed under the EUPL, Version 1.1 or – as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
#
# https://joinup.ec.europa.eu/software/page/eupl5
#
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.
# ----
#
# REVISIONS and CHANGES 
#    09/11/2023   V1.0   Thomas Forbriger
# 
# ============================================================================
#

import argparse
import textwrap
from obspy import read, read_inventory
from obspy.clients.fdsn import Client
from obspy.core import UTCDateTime
from modules.invresponse import dumpresp
from modules.VLPtools import groundmotion
from obspy.geodetics import gps2dist_azimuth
from obspy.taup.taup_geo import calc_dist_azi
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal.windows as windows
from matplotlib.ticker import ScalarFormatter
from obspy.imaging.util import ObsPyAutoDateFormatter
from dateutil.rrule import MINUTELY, SECONDLY
from matplotlib.dates import (AutoDateLocator, AutoDateFormatter, 
                              DateFormatter, num2date, date2num)
from matplotlib.ticker import FuncFormatter

# ============================================================================
# define functions

def myparser():
    parser = argparse.ArgumentParser(
            description="Plot source centered wave forms",
            formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
            "network", default=None,
            metavar="NC",
            help="use NC as SEED network code in data request"
            +"\n(default: %(default)s)"
            )
    parser.add_argument(
            "station", default=None,
            metavar="SC",
            help="use SC as SEED station code in data request"
            +"\n(default: %(default)s)"
            )
    parser.add_argument(
            "--begin", default="2023/09/16T12:30:00",
            type=str,
            metavar="DT",
            help="request data for time period starting at DT"
            +"\nformat like: 2020-05-17T00:00:00.000"
            +"\n(default: %(default)s)"
            )
    parser.add_argument(
            "--end", default="2023/09/16T14:30:00",
            type=str,
            metavar="DT",
            help="request data for time period ending at DT"
            +"\nformat like: 2020-05-17T00:00:00.000"
            +"\n(default: %(default)s)"
            )
    parser.add_argument(
            "--outbase", default="pmplot",
            metavar="s",
            type=str,
            help="select a filname base"
            +"\n(default: %(default)s)"
            )
    parser.add_argument(
            "--source", default="72.5,-27.3",
            metavar="lat,lon",
            type=str,
            help="source location"
            +"\n(default: %(default)s)"
            )
    parser.add_argument(
            "--fHP", default=0.005,
            metavar="f",
            type=float,
            help="high-pass frequency / Hz"
            +"\n(default: %(default)s)"
            )
    parser.add_argument(
            "--fLP", default=0.02,
            metavar="f",
            type=float,
            help="low-pass frequency / Hz"
            +"\n(default: %(default)s)"
            )
    parser.add_argument(
            "--traceshift", default=0.0,
            metavar="f",
            type=float,
            help="offset to shift traces"
            +"\n(default: %(default)s)"
            )
    parser.add_argument(
            "--quantity", default="acceleration",
            metavar="q",
            type=str,
            help="kinematic quantity to represent ground motion"
            +"\nmay be: acceleration, displacement, velocity"
            +"\n(default: %(default)s)"
            )
    parser.add_argument(
            "--inbase", default="1d",
            metavar="s",
            type=str,
            help="string to be part of data file name"
            +"\n(default: %(default)s)"
            )
    parser.add_argument(
            "--decay", default=None,
            metavar="Q,A,T",
            action="append",
            type=str,
            help="parameters for decay curve"
            +"\nQ: Q-value of decay for period of 92s"
            +"\nA: initial amplitude"
            +"\nT: time of signal onset"
            +"\n(default: %(default)s)"
            )
    parser.add_argument(
            "--components", default=None,
            metavar="c1[,c2[,..]]",
            type=str,
            help="seismometer components to be included in the plot"
            +"\n(default: %(default)s)"
            )
    parser.add_argument(
            "--figsize", default="27.,18.",
            metavar="w,h",
            type=str,
            help="figure dimensions / cm"
            +"\n(default: %(default)s)"
            )
    parser.add_argument(
            "--titlefontsize", default="large",
            metavar="s",
            type=str,
            help="font size for title"
            +"\n(default: %(default)s)"
            )
    parser.add_argument(
            "--xticklabelrotation", default=0.,
            metavar="a",
            type=float,
            help="angle by which the xtick labels shall be rotated"
            +"\n(default: %(default)s)"
            )
    parser.add_argument(
         "--verbose", action='store_true',
         help="produce verbose terminal output"
         )
    parser.add_argument(
         "--stripdate", action='store_true',
         help="print date in x label, not as part of ticklabels"
         )
    parser.add_argument(
         "--ZNE", action='store_true',
         help="do not rotate to transverse and radial component"
         )
    parser.add_argument(
         "--noshow", action='store_true',
         help="do not produce screen display"
         )

    return parser

# ----------------------------------------------------------------------------
def main():
    parser = myparser()

    args = parser.parse_args()

    # read data and metadata from file
    mseedbase=args.network+"."+args.station
    stread=read(mseedbase+"*"+args.inbase+"*.mseed")
    st=stread.select(network=args.network, station=args.station)
    inv=read_inventory(mseedbase+"*"+args.inbase+"*.xml")
    st.attach_response(inv)

    endtime=st[0].stats.endtime
    for tr in st:
        if endtime > st[0].stats.endtime:
            endtime=st[0].stats.endtime
    st.trim(endtime=endtime)

    if args.verbose:
        print("read time series data:")
        print(st)
        print(inv)

    st=st.filter("lowpass", freq=args.fLP)
    for tr in st:
        tr.data = tr.data - tr.data[0]
    # apply low-pass twice (a measure against marine microseisms)
    st=st.filter("lowpass", freq=args.fLP)
    for tr in st:
        tr.data = tr.data - tr.data[0]
    st=st.filter("highpass", freq=args.fHP)

    stconv=groundmotion(st.copy(), inv, args.fHP, args.quantity, args.verbose)
    st.clear()

    # rotate to radial and transverse
    coo=inv.get_coordinates(stconv[0].id)
    slat,slon=[float(x) for x in args.source.split(",")]
    if args.verbose:
        print("station at %8.2f°N %8.2f°E" % (coo["latitude"],
                                              coo["longitude"]))
        print("source  at %8.2f°N %8.2f°E" % (slat, slon))

##   epi_dist, az, baz = gps2dist_azimuth(slat, slon,
##                                        coo["latitude"], 
##                                        coo["longitude"])
    epi_dist, az, baz = calc_dist_azi(slat, slon,
                                      coo["latitude"],
                                      coo["longitude"],
                                      6371., 0.)
    stationlabel=("station %s at %.2f°N %.2f°E   distance %.2f° BAZ N%.2f°E" %
                 (args.network+"."+args.station,
                  coo["latitude"],
                  coo["longitude"], epi_dist, baz))
    sourcelabel=("source at %.2f°N %.2f°E   station azimuth N%.2f°E" % 
                (slat, slon, az))
    if args.verbose:
        print("%20s: %10.3f°" % ("epicentral distance", epi_dist))
        print("%20s: %10.3f°" % ("azimuth", az))
        print("%20s: %10.3f°" % ("BAZ (backazimuth)", baz))

    strot=stconv.copy()
    strot.rotate(method="->ZNE", inventory=inv)
    if args.ZNE:
        Cx="E"
        Cy="N"
        comps=["Z", "N", "E"]
    else:
        strot.rotate(method="NE->RT", back_azimuth=baz)
        Cx="T"
        Cy="R"
        comps=["Z", "R", "T"]

    if args.verbose:
        print(strot)

# start plot
    newstart=UTCDateTime(args.begin)
    newend=UTCDateTime(args.end)
    st=strot.trim(starttime=newstart, endtime=newend)
     
    width, height=[float(x) for x in args.figsize.split(",")]
    fig = plt.figure(figsize=(width/2.54,height/2.54))
    fig.autofmt_xdate()
    ax=fig.gca()
    ax.xaxis_date()
    locator = AutoDateLocator(minticks=4, maxticks=10)
    locator.intervald[MINUTELY] = [1, 2, 5, 10, 15, 30]
    locator.intervald[SECONDLY] = [1, 2, 5, 10, 15, 30]
    formatter=ObsPyAutoDateFormatter(locator)
    if args.stripdate:
        formatter.scaled[1/(24*60)] = '%H:%M'
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(locator)
    plt.setp(ax.get_xticklabels(), fontsize='small', 
             rotation=args.xticklabelrotation)
    #yshift=args.traceshift*np.max(np.abs(st.max()))
    yshift=args.traceshift
    if args.components is not None:
        comps=args.components.split(",")
    offsetstart=yshift*(len(comps)-1)/2.
    for i, c in enumerate(comps):
        stp=st.select(channel="*"+c)
        for trace in stp:
            traceoffset=offsetstart-i*yshift
            if c=="Z":
                Zoffset=traceoffset
                label=trace.get_id()
                alpha=1.
            elif c=="T":
                label="transverse"
                alpha=0.7
            elif c=="R":
                label="radial"
                alpha=0.7
            else:
                label=trace.get_id()
                alpha=0.7
            x_values = ((trace.times() / 86400) +
                        date2num(trace.stats.starttime.datetime))
            plt.plot(x_values, trace.data+traceoffset, 
                     label="%s" %(label),
                     linewidth=1., alpha=alpha)

# plot decay
    if args.decay is not None:
        linestyles=['-', '--', '-.', ':']
        for i, decay in enumerate(args.decay):
            strQ, strA, strT=decay.split(",")
            Q=float(strQ)
            A=float(strA)
            T=UTCDateTime(strT)
            Tosc=91.9
            omosc=2.*np.pi/Tosc
            Td=2.*Q/omosc
            h=1./(2.*Q)
            print("Td=%f s   Tosc=%f s   Q=%f   h=%f" %
                  (Td, Tosc, Q, h))
            curvelabel=("%f exp(-t / %7.3fs)" % (A, Td))

            dur=newend-T
            xvalues=np.arange(0.,dur,1.)
            curve=A*np.exp(-xvalues/Td)
            x_values = ((xvalues / 86400) + date2num(T.datetime))
            plt.plot(x_values, curve+Zoffset, 
                     linestyle='-', linewidth=3,
                     color='white', alpha=0.5)
            plt.plot(x_values, curve+Zoffset, label="Q=%.0f" %(Q),
                     linestyle=linestyles[i], linewidth=1,
                     color='black')

# labels and annotation
    if args.stripdate:
        ax.set_xlabel("UTC on %s" % str(st[0].stats.starttime)[0:10])
    ax.set_ylabel(st[0].stats.units)
    ax.grid(linestyle=':')
    ax.legend(ncol=5, loc='upper right')

    bandpasslabel=("bandpass: %7.3f Hz - %7.3f Hz" % (args.fHP, args.fLP))
    fig.suptitle("%s  %s\n%s\n%s" % 
                   (st[0].stats.starttime, bandpasslabel,
                    stationlabel, sourcelabel),
                 fontsize=args.titlefontsize)
    outbase=args.outbase+"-"+args.network+"-"+args.station
    fig.savefig(outbase+".pdf")
    fig.savefig(outbase+".png")
    fig.savefig(outbase+".svg")
    if not args.noshow:
        plt.show()

# ============================================================================
if __name__ == "__main__":
    main()

# ----- END OF plotdecay.py ----- 
