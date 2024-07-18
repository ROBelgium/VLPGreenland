#!/usr/bin/env python
# this is <plotstation.py>
# ----------------------------------------------------------------------------
# 
# Copyright (c) 2023 by Thomas Forbriger (KIT, GPI, BFO) 
# 
# plot data for a single station
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
#    30/09/2023   V1.0   Thomas Forbriger
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
from matplotlib.ticker import LogFormatter

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
            "--source", default="72.833,-27.0",
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
            "--FFTbandwidth", default=3.,
            metavar="f",
            type=float,
            help="relative width of the frequency band displayed for the FFT"
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
         "--scalepertrace", action='store_false',
         help="adjust amplitude scale for each trace separately"
         )
    parser.add_argument(
         "--FFTlogscale", action='store_true',
         help="Use a logarithmic scale for the FFT frequency axis"
         )
    parser.add_argument(
            "--inbase", default="1d",
            metavar="s",
            type=str,
            help="string to be part of data file name"
            +"\n(default: %(default)s)"
            )
    parser.add_argument(
         "--verbose", action='store_true',
         help="produce verbose terminal output"
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
# FFT quick hack
def myfft(x, dt):
  xtap=x*windows.hann(len(x), sym=False)
  result = np.abs(np.fft.rfft(xtap))*dt
  freq = np.fft.rfftfreq(len(xtap),dt)
  return [freq, result]

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
    else:
        strot.rotate(method="NE->RT", back_azimuth=baz)
        Cx="T"
        Cy="R"

    if args.verbose:
        print(strot)

    newstart=UTCDateTime(args.begin)
    newend=UTCDateTime(args.end)
    st=strot.trim(starttime=newstart, endtime=newend)

    fig = plt.figure(figsize=(20./2.54,29./2.54))
    pmfig,tsfig=fig.subfigures(2,1,height_ratios=[0.7,0.3])

    units=st[0].stats.units
    tlunits=units.replace("/", "/\n")

    st.plot(fig=tsfig, equal_scale=(args.scalepertrace))
    for ax in fig.axes:
        #ax=fig.gca()
        ax.set_ylabel(tlunits)
        #ax.set_title("bandpass: %7.3f Hz - %7.3f Hz" % (fHP, fLP))
        ax.grid()

#    pmaxs=outerfigs[1].subplots(ncols=2,nrows=2)

    stZ=st.select(channel="*Z")
    stx=st.select(channel="*"+Cx)
    sty=st.select(channel="*"+Cy)
    maxv=0.
    for tr in st:
        vmax=np.max(np.abs(tr.data))
        if vmax > maxv:
            maxv = vmax
#    maxv *= 1.05
    if args.verbose:
        print("maximum amplitude: %7.3f" % maxv)

    axxy=pmfig.add_subplot(2,2,1)
    axZy=pmfig.add_subplot(2,2,2)
    axxZ=pmfig.add_subplot(2,2,3)
    pmfig.subplots_adjust(hspace=0.15)

    axxZ.sharex(axxy)
    axZy.sharey(axxy)

    for ax in [axxy, axZy, axxZ]:
        #ax.set_aspect("equal", adjustable="box", share=True)
        ax.set_aspect("equal", adjustable="box")

    axxZ.plot(stx[0].data, stZ[0].data, label="Z-"+Cx)
    axxZ.set_xlabel(Cx+" "+units)
    axxZ.set_ylabel("Z "+units)
    axxZ.set_ylim(-maxv, maxv)

    axZy.plot(stZ[0].data, sty[0].data, label=Cy+"-Z")
    axZy.set_xlabel("Z "+units)
    axZy.set_xlim(maxv, -maxv)

    axxy.plot(stx[0].data, sty[0].data, label=Cy+"-"+Cx)
    axxy.set_ylabel(Cy+" "+units)
    axxy.set_xlim(-maxv, maxv)
    axxy.set_ylim(-maxv, maxv)

    if args.ZNE:
        # plot BAZ
        BAZx=maxv*np.sin(np.pi*baz/180.)
        BAZy=maxv*np.cos(np.pi*baz/180.)
        axxy.plot([0.,BAZx],[0.,BAZy],
                color="red", label="BAZ")

    ticks=axxy.get_xticks()
    print(ticks)
    dtick=-2*ticks[0]/4
    print(dtick)
    ticks=np.arange(ticks[0], ticks[-1]+dtick/2, dtick)
    print(ticks)

    for ax in [axxy, axZy, axxZ]:
        ax.grid()
        ax.legend()

    # unwrapped cube display
    axZy.set_xlim(maxv, -maxv)

    for ax in [axxy, axxZ]:
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)

    axZy.set_xticks(np.flip(ticks))
    axZy.set_yticks(ticks)

    for ax in [axxy, axZy, axxZ]:
        print("x: ", ax.get_xticks())
        print("y: ", ax.get_yticks())

    # run and display FFT
    ffts=dict()
    maxv=0.
    for tr in st:
        chan=tr.stats.channel
        freq, ffts[chan]=myfft(tr.data, tr.stats.delta)
        vmax=np.max(ffts[chan])
        if vmax > maxv:
            maxv=vmax
    ax=pmfig.add_subplot(2,2,4)
    for chan in sorted(ffts.keys()):
        if args.FFTlogscale:
            ax.semilogx(freq*1.e3, ffts[chan]/maxv, label=chan)
        else:
            ax.plot(freq*1.e3, ffts[chan]/maxv, label=chan)
    freqmar=np.sqrt(args.FFTbandwidth*args.fHP/args.fLP)
    if freqmar < 1.1:
        freqmar=1.1
    if args.FFTlogscale:
        formatter=LogFormatter(minor_thresholds=(1.5,1.5))
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_minor_formatter(formatter)
        ax.tick_params(which='both', length=3, width=1, pad=1)
    ax.set_xlim(args.fHP*1.e3/freqmar, args.fLP*1.e3*freqmar)
    ax.set_xlabel('frequency / mHz')
    ax.set_ylabel('FFT (hanned)')
    ax.grid(which='major', axis='both', linewidth=.7, ls='--')
    ax.grid(which='minor', axis='both', linewidth=.4, ls=':')
    ax.legend()
    l, b, w, h=ax.get_position().bounds
    #print([l, b, w, h])
    ax.set_position(pos=[l+0.02, b, w-0.02, h-0.03], which='both')

    bandpasslabel=("bandpass: %7.3f Hz - %7.3f Hz" % (args.fHP, args.fLP))
    pmfig.suptitle("%s  %s\n%s\n%s" % 
                   (stZ[0].stats.starttime, bandpasslabel,
                    stationlabel, sourcelabel))
    outbase=args.outbase+"-"+args.network+"-"+args.station
    fig.savefig(outbase+".pdf")
    fig.savefig(outbase+".png")
    if not args.noshow:
        plt.show()

# ============================================================================
if __name__ == "__main__":
    main()

# ----- END OF plotstation.py ----- 
