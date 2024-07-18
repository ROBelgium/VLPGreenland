#!/usr/bin/env python
# this is <dldata.py>
# ----------------------------------------------------------------------------
# 
# Copyright (c) 2023 by Thomas Forbriger (KIT, GPI, BFO) 
# 
# download data
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
#    22/09/2023   V1.0   Thomas Forbriger
# 
# ============================================================================

import argparse
import textwrap
from obspy.clients.fdsn import Client
from obspy.core import UTCDateTime
from invresponse import dumpresp

# ============================================================================
# define functions

def myparser():
    parser = argparse.ArgumentParser(
            description="Download data",
            formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
            "--datacenter", default="IRIS", 
            metavar="DC",
            help="pass DC as data center name to FDSN webservices client"
            +"\n(default: %(default)s)"
            )
    parser.add_argument(
            "--network", default=None,
            metavar="NC",
            help="use NC as SEED network code in data request"
            +"\n(default: %(default)s)"
            )
    parser.add_argument(
            "--station", default=None,
            metavar="SC",
            help="use SC as SEED station code in data request"
            +"\n(default: %(default)s)"
            )
    parser.add_argument(
            "--location", default="00",
            metavar="SL",
            help="use SL as SEED location code in data request"
            +"\n(default: %(default)s)"
            )
    parser.add_argument(
            "--channel", default="LH?",
            metavar="SC",
            help="use SC as SEED channel code in data request"
            +"\n(default: %(default)s)"
            )
    parser.add_argument(
            "--begin", default="2023/09/16T12:00:00",
            metavar="DT",
            help="request data for time period starting at DT"
            +"\nformat like: 2020-05-17T00:00:00.000"
            +"\n(default: %(default)s)"
            )
    parser.add_argument(
            "--end", default="2023/09/17T12:00:00",
            metavar="DT",
            help="request data for time period ending at DT"
            +"\nformat like: 2020-05-17T00:00:00.000"
            +"\n(default: %(default)s)"
            )
    parser.add_argument(
            "--outbase", default="1d",
            metavar="s",
            type=str,
            help="select a filname base"
            +"\n(default: %(default)s)"
            )
    parser.add_argument(
            "reportlevel", default=None, 
            metavar="level", choices={'I','N','S','C','R'},
            help=textwrap.dedent('''\
            set level of reporting (default: %(default)s)
            this may be any combination of the folloqing characters:
            I: inventory
            N: network
            S: station
            C: channel
            R: response
            '''))
    return parser

# ----------------------------------------------------------------------------
def main():
    parser = myparser()

    args = parser.parse_args()

    client=Client(args.datacenter)
    if args.begin is None:
        starttime=None
    else:
        starttime=UTCDateTime(args.begin)
    if args.end is None:
        endtime=None
    else:
        endtime=UTCDateTime(args.end)

    inv=client.get_stations(network=args.network, 
            station=args.station,
            location=args.location,
            channel=args.channel,
            starttime=starttime,
            endtime=endtime,
            level='response')

    if args.reportlevel.find("I") >= 0:
        print(inv)

    for network in inv:
        ID=network.code
        if args.reportlevel.find("N") >= 0:
            print("\nInventory contents for network %s:" % ID)
            print(network)
        for station in network:
            ID=network.code+"."+station.code
            if args.reportlevel.find("S") >= 0:
                print("\nInventory contents for station %s:" % ID)
                print(station)
            for channel in station:
                timeperiod=("(valid for %s to %s)" % (channel.start_date,
                    channel.end_date))
                ID=(network.code+"."+station.code+"."+
                    channel.location_code+"."+channel.code)
                if args.reportlevel.find("C") >= 0:
                    print("\nInventory contents for channel %s:\n%s" 
                            % (ID, timeperiod))
                    print(channel)
                if args.reportlevel.find("R") >= 0:
                    print("\nInventory response contents for channel %s:\n%s" 
                            % (ID, timeperiod))
                    dumpresp(channel.response)

    st=client.get_waveforms(network=args.network, 
            station=args.station,
            location=args.location,
            channel=args.channel,
            starttime=starttime,
            endtime=endtime)

    for tr in st:
        stid=tr.id
        print(stid)
        trinv=inv.select(network=tr.stats.network,
                         station=tr.stats.station,
                         location=tr.stats.location,
                         channel=tr.stats.channel)
        trfilename=("%s_%s.mseed" % (stid, args.outbase))
        invfilename=("%s_%s.xml" % (stid, args.outbase))
        tr.write(trfilename)
        trinv.write(invfilename, format="STATIONXML")

# ============================================================================
if __name__ == "__main__":
    main()

# ----- END OF dldata.py ----- 
