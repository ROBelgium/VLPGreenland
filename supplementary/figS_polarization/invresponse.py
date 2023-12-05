#!/usr/bin/env python
# this is <invresponse.py>
# ----------------------------------------------------------------------------
# 
# Copyright (c) 2023 by Thomas Forbriger (KIT, GPI, BFO) 
# 
# module to handle inventory data
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
#

import numpy as np
from obspy import read, read_inventory
from obspy.core import AttribDict, UTCDateTime
from obspy.geodetics.base import locations2degrees
import matplotlib.pyplot as plt

def dumpresp(resp):
    """
    resp: obspy response object obtained through get_response function of
    inventory
    """
    print(resp)
    seis_paz=resp.get_paz()
    print(seis_paz)
    print("'"+seis_paz.pz_transfer_function_type+"'")
# factor to scale to units of Hertz (set zo 0, if units are unknown)
    funits=0.
    if seis_paz.pz_transfer_function_type == "LAPLACE (HERTZ)":
        funits=1
    elif seis_paz.pz_transfer_function_type == "LAPLACE (RADIANS/SECOND)":
        funits=0.5/np.pi
    else:
        print("ERROR: unexpected type of response parameters!")
    paz_dict={"zeros": seis_paz.zeros, 
              "poles": seis_paz.poles, 
              "gain": seis_paz.stage_gain}
    print(paz_dict)
    for t in ("zeros", "poles"):
        print("\nlist of %s:" % t)
        for x in paz_dict[t]:
            f=np.abs(x)*funits
            if ((f < 1.e-10) or (f >= 1.)):
                fstring="%10.4f Hz" % f
            else:
                fstring="%10.4f s" % (1./f)
            print(fstring, "at", x*funits, "Hz")

# ----- END OF invresponse.py ----- 
