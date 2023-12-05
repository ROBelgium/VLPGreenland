#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions to handle poles and zeros, and PAZ-dictionaries
(part of CONRAD)

PAZ dictionaries represent transfer functions in the sense of the Laplace
transform of the impulse response function. The poles and the zeros of the
rational function are given by complex values in units of rad/s. Poles and
zeros must either be real or appear in complex conjugate pairs. For a system
to be stable, the real part of the poles must be negative.

For seismometers the gain is understood to be in counts*s/m

For barometers the gain is understood to be in counts/hPa

The dictionary uses three keys:
    zeros
    poles
    gain
"""
#
# Copyright 2021 by Thea Lepage
# Copyright 2023 by Thomas Forbriger
# 
## @package pazfilter
# Functions to handle poles and zeros and PAZ dictionaries
#
# Definitions in file pazfilter.py
#
## @file pazfilter.py
# Functions to handle poles and zeros and PAZ dictionaries
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
#  - 30/11/2023   thof: prepare for publication
#

import numpy as np
import matplotlib.pyplot as plt
from operator import itemgetter
from scipy import signal

# ============================================================================
# functions to treat poles and zeros
# ==================================

# ----------------------------------------------------------------------------
def sosfilter(data,paz,dt):
    """
    Apply sos-filter on data

    Parameters
    ----------
    data : array of data
    paz : paz-dictionary of filter
    dt : sampling interval

    Returns
    -------
    res : filtered data
    """
    z,p,k=signal.bilinear_zpk(paz["zeros"],paz["poles"],paz["gain"],1./dt)
    sos=signal.zpk2sos(z,p,k)
    res=signal.sosfilt(sos,data)
    return res

# ----------------------------------------------------------------------------
# all-pass filter
PAZallpass={"zeros":[], "poles":[], "gain":1.}

# ----------------------------------------------------------------------------
# PAZ for taing the derivative
def PAZderivative():
    PAZ={"zeros": [0.],
         "poles": [],
         "gain":1.}
    return PAZ

# ----------------------------------------------------------------------------
# PAZ for signal integration
def PAZintegrate():
    PAZ={"zeros": [],
         "poles": [0.],
         "gain":1.}
    return PAZ

# ----------------------------------------------------------------------------
# PAZ dictionary for Butterworth high-pass
def PAZBWHP(T0,npoles):
    BWHP={"zeros":np.array([0]*npoles),
          "poles":(2*np.pi/T0)*np.array(signal.buttap(npoles)[1]),
          "gain":1.}
    return BWHP

# ----------------------------------------------------------------------------
# PAZ dictionary for Butterworth low-pass
def PAZBWLP(T0,npoles):
    BWHP={"zeros": [],
          "poles":(2*np.pi/T0)*np.array(signal.buttap(npoles)[1]),
          "gain": np.power(2*np.pi/T0,npoles)}
    return BWHP

# ----------------------------------------------------------------------------
## Reduce common poles and zeros
def reduce_factors(z,p):
    """
    reduce common poles and zeros after sorting
    
    Parameters
    ----------
    z : zeros.
    p : poles.

    Returns
    -------
    zclean : reduced zeros.
    pclean : reduced poles.
    """
    z=sortpz(z)
    p=sortpz(p)
    
    wl=1.e-4 # threshold
    # indexes to reduce
    z_trash=[]
    p_trash=[]
    for k in range(len(z)):
        for j in range(len(p)):  
            if ((np.abs(z[k])-np.abs(p[j]))<wl 
                and (np.real(z[k])-np.real(p[j]))<wl and j not in p_trash):
                # common values are sorted out
                z_trash.append(k)
                p_trash.append(j)
                break
    
    zclean=np.delete(z,z_trash[:])
    pclean=np.delete(p,p_trash[:])
    return(zclean,pclean)

# ----------------------------------------------------------------------------

## Compute inverse of an LTI system (reciprocal transfer function)
def reciprocal(pazdict):
    """
    compute the inverse of an LTI system, i.e. the reciprocal transfer
    function

    pazdict:    a poles and zeros dictionary

    return: reciprocal system (poles and zeros dictionary)
    """
    reciprocal_system={"poles": pazdict["zeros"],
	    "zeros": pazdict["poles"],
	    "gain": 1./pazdict["gain"]}
    return reciprocal_system

# ----------------------------------------------------------------------------

## Concatenate multiple PAZ dictionaries into one
def concatenate(pazdict):
    """
    concatenate multiple paz-dictionaries into one

    Parameters
    ----------
    pazdict : list of poles and zeros dictionaries.

    Returns
    -------
    RES : poles and zeros dictionary.
    """
    z=np.array([])
    p=np.array([])
    k=1
    for i in pazdict:
        z=np.append(z,i["zeros"])
        p=np.append(p,i["poles"])
        k*=i["gain"]
        
    z,p=reduce_factors(z,p)
    
    RES={"zeros":z,
         "poles":p,
         "gain":k}
        
    return RES

# ============================================================================
# functions to report filter properties by plotting a diagram
# ===========================================================

## Plot poles and zeros of a transfer function
def plot_paz(z,p,station):
    """
    plot poles and zeros of analog transfer function

    Parameters
    ----------
    z : zeros.
    p : poles.
    """
    z_Hz=1./(2.*np.pi)*np.array(z)
    p_Hz=1./(2.*np.pi)*np.array(p)
    
    # find largest magnitude of any of the complex values to be used to set
    # axes limits; apply a waterlevel
    axis_limit=np.max(np.abs(list(p_Hz)+list(z_Hz)+[1.e-4]))

    # open new plot an display values
    plt.figure()
    plt.xlim(-1.1*axis_limit,1.1*axis_limit)
    plt.ylim(-1.1*axis_limit,1.1*axis_limit)
    plt.plot(np.real(z_Hz), np.imag(z_Hz), 'ob')
    plt.plot(np.real(p_Hz), np.imag(p_Hz), 'xr')
    plt.legend(['zeros', 'poles'], loc=0)
    plt.grid()
    plt.xlabel("real part in Hz")
    plt.ylabel("imaginary part in Hz")
    plt.title('Pole-zero plot at %s' %station)
    plt.tight_layout()

# ----------------------------------------------------------------------------

## Plot a bode diagram for a transfer function given by a PAZ dictionary
def bode_plot(pazdict):
    """
    plot a bode diagram

    Parameters
    ----------
    pazdict : a poles and zeros dictionary
    """
    sys=signal.ZerosPolesGain(pazdict["zeros"],pazdict["poles"],pazdict["gain"])
    w, mag, phase=signal.bode(sys)
    plt.figure()
    plt.subplot(211)
    plt.semilogx(w/(2*np.pi), mag)    # Bode magnitude plot
    plt.ylabel("gain")
    plt.grid()
    plt.subplot(212)
    plt.semilogx(w/(2*np.pi), phase/(360.))  # Bode phase plot
    plt.ylabel("phase / $2\pi$")
    plt.xlabel("frequency / Hz")
    plt.grid()
    plt.tight_layout()

# ============================================================================
# functions to analyse poles and zeros
# ====================================

## Compute the value of H(s) for s=i*omega=i*2*pi*f
def H(pazdict, f):
    """
    Compute the value of the transfer function H(2*pi*i*f).

    Parameters
    ----------
    pazdict : poles and zeros dictionary
    f : frequency in Hz

    return : complex value
      value of H(s) at s=2*pi*i*f
    """
    s=2.j*np.pi*f
    H=1.
    for z in pazdict["zeros"]:
        H=H*(s-z)
    for p in pazdict["poles"]:
        H=H/(s-p)
    H=H*pazdict["gain"]
    return H

# ----------------------------------------------------------------------------

## Compute damping as a fraction of critical
def damping(pz):
    """ 
    return damping as a fraction of critical for a pole (or zeros) existing in
    a pair of poles (or zeros) for a transfer function H(s)

    pz: pole or zero of a transfer function H(s) - a complex number

    return: damping as a fraction of critical - a real number
    """

    # threshold for value comparison of floating point values
    # if difference is below the threshold, bost are considered equal
    wl=1.e-10

    # set default in case zero or pole is at the origin
    h=1.
    # compute damping if pole or zero is not at origin
    if np.abs(pz) > wl:
        h=-np.real(pz)/np.abs(pz)

    return h

# ----------------------------------------------------------------------------

## Compute eigenfrequency
def eigenfrequency(pz):
    """ 
    return eigenfrequency for a pole (or zeros) existing in
    a transfer function H(s)

    pz: pole or zero of a transfer function H(s) - a complex number

    return: eigenfrequency / Hz - a real number
    """
    f0=np.abs(pz)/(2.*np.pi)
    return f0

# ----------------------------------------------------------------------------

## Pretty print a complex number
def printcomplex(z, u):
    """
    print a complex number in a nice way

    z: complex number
    u: units
    """

    # sign of imaginary part
    if np.imag(z) < 0.:
        isign="-"
    else:
        isign="+"
    print("  (%10.5f %s i%10.5f) %s" 
            % (np.real(z), isign, np.abs(np.imag(z)), u))

# ----------------------------------------------------------------------------

## Pretty print a complex number
def complex_to_str(z, u):
    """
    return a string representing a complex number in a nice way

    z : complex number
    u : units

    return : str
    """

    # sign of imaginary part
    if np.imag(z) < 0.:
        isign="-"
    else:
        isign="+"
    retval=("(%10.5f %s i%10.5f) %s" % (np.real(z), isign, 
                                       np.abs(np.imag(z)), u))
    return retval

# ----------------------------------------------------------------------------

## Sort a list of poles or zeros
def sortpz(pz):
    """
    sort a list of poles and zeros by increasing frequency

    Parameters
    ----------
    pz : list of poles or zeros of a transfer function H(s) - complex numbers

    Returns
    -------
    retval : sorted list
    """
    # setup a sort list
    # we sort by absolute value and real value (in case of absolute value
    # being equal)
    pzlist=[]
    for ipz in pz:
        pzlist.append((ipz, np.abs(ipz), np.abs(np.real(ipz))))

    # sort the list
    pzsorted=sorted(pzlist, key=itemgetter(1,2))
   
    # extract complex number of poles as a return value 
    retval=[]
    for ipz in pzsorted:
        retval.append(ipz[0])
    
    return retval

# ----------------------------------------------------------------------------

## return a pretty string representation of a list of poles or zeros
def pz_to_str(pz):
    """
    return a pretty string representation of a list of poles or zeros
    of a transfer function H(s) by specifying eigenfrequncy and damping

    pz : list of complex
        poles or zeros of a transfer function H(s) - complex numbers
    return : list of strings
    """
   
    retval=list()
    # threshold for value comparison of floating point values
    # if difference is below the threshold, bost are considered equal
    wl=1.e-10

    # skip if list is empty
    if len(pz) > 0:
        # sort list
        spz=sortpz(pz)

        # iterate through list
        k=0
        while k < len(spz):
            # compute eigenfrequency and damping
            f0=eigenfrequency(spz[k])
            h=damping(spz[k])
            # if damping is not 1, i.e. pz-value is not on real axis, we
            # expect a pair of complex conjugate values
            expectpair=(np.abs(1.-h) > wl)
            # is there a partner for this value
            if ((expectpair) and ((k+1) >=len(spz))):
                print("ERROR in printpz: values do not appear in pairs!")
                exit(3)
            # check if partner matches and print
            if ((expectpair) 
                    and (np.abs(f0-eigenfrequency(spz[k+1])) < wl)
                    and (np.abs(np.imag(spz[k]+spz[k+1])) < wl)):
                # report second order system
                if (f0 > wl):
                    retval.append("pair at   f0=%10.5fHz   T0=%10.5fs   h=%10.5f" %
                            (f0, 1./f0, h))
                else:
                    retval.append("pair at   f0=%10.5fHz" % f0)
                # skip the next entry
                k=k+1
            else:
                # report first order system
                if (f0 > wl):
                    retval.append("single at f0=%10.5fHz   T0=%10.5fs" %
                            (f0, 1./f0))
                else:
                    retval.append("single at f0=%10.5fHz" % f0)

            # proceed to next entry
            k=k+1

    return retval

# ----------------------------------------------------------------------------

## Pretty print a list of poles or zeros
def printpz(pz):
    """
    print a list of poles or zeros of a transfer function H(s) specifying
    eigenfrequncy and damping

    pz: list of poles or zeros of a transfer function H(s) - complex numbers
    """

    listofpz=pz_to_str(pz)
    for l in listofpz:
        print("  %s" % l)

# ----------------------------------------------------------------------------

## create a pretty print report of a poles and zeros dictionary
def pazdict_to_str(pazdict):
    """
    create a pretty print report of a poles and zeros dictionary

    Parameters
    ----------
    pazdict : dictionary
        PAZ dictionary defining an LTI system transfer function

    return : list of strings
    """

    retval=list()
    # extract poles and zeros
    sz=sortpz(pazdict["zeros"])
    sp=sortpz(pazdict["poles"])
    sk=pazdict["gain"]

    # print summary values
    retval.append("number of zeros:  %d" % len(sz))
    retval.append("number of poles:  %d" % len(sp))
    retval.append("numerator factor: %f" % sk)

    # dump complex zeros and poles
    if len(sz) > 0:
        retval.append("")
        retval.append("complex zeros (numerator zeros):")
        for z in sz:
            retval.append(complex_to_str(z, "rad/s"))

    if len(sp) > 0:
        retval.append("")
        retval.append("complex poles (denominator zeros):")
        for p in sp:
            retval.append(complex_to_str(p, "rad/s"))

    # dump complex zeros and poles as eigenfrequency and damping
    if len(sz) > 0:
        retval.append("")
        retval.append("zeros (numerator zeros):")
        retval=retval+pz_to_str(sz)

    if len(sp) > 0:
        retval.append("")
        retval.append("poles (denominator zeros):")
        retval=retval+pz_to_str(sp)

    return retval

# ----------------------------------------------------------------------------

## Pretty print a poles and zeros (PAZ) dictionary
def printsys(pazdict):
    """
    print parameters of a transfer function H(s)

    Parameters
    ----------
    pazdict : dictionary
        PAZ dictionary defining an LTI system transfer function
    """

    listofstrings=pazdict_to_str(pazdict)
    for l in listofstrings:
        print("  %s" % l)

# ----- END OF pazfilter.py ----- 
