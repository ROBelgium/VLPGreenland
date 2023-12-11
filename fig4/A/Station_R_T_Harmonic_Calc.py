#!/usr/bin/env python
from obspy.clients.fdsn import Client
from obspy.core import UTCDateTime
import matplotlib.pyplot as plt
import numpy as np
from obspy.geodetics.base import gps2dist_azimuth
from scipy.signal import hilbert
from obspy.signal.cross_correlation import correlate, xcorr_max


import matplotlib as mpl
mpl.rc('font', family='serif')
mpl.rc('font', serif='Times')
#mpl.rc('text', usetex=True)
mpl.rc('font', size=18)


'''
We want to grab 3 component data for a Window starting, Delay hours after
the event time for a given station.

We remove the response and rotate all data to the radial and transverse components

We bandpass filter around the 10.88 mHz mode

We do a Hilbert Transform to see how Rayleigh wave this looks

We do some pointwise thing to track H/V over time, using the peak of each oscillation

We report:

- Correlation between vertical and HT Radial Components
- Mean H/V Ratio
- Plot of H/V evolution


'''

################################################################################
# User set variables

debug = 'True'
sta = 'TLY'
loc = '00'

# bandpass params

# Fundamental

Filt_min = 1/100.
Filt_max = 1/83.6

# 2nd Harmonic

#Filt_min = 1/50
#Filt_max = 1/41.8

# Hours of data we want to grab prior to the Landslide
Pre_win = 5

# Hours before event when we will plot data
Plot_start = 3

# Time after the event where we want to start the window
Winstart_Del = 3
# hours of Window
Win_Length = 5

# Hours after the event where we kill this
Analysis_End = 96



############ ###################################################################
# Fixed Variables


# network
client = Client("IRIS")

#September 16th event
Event_time = UTCDateTime('2023-09-16T12:35:04')

# October 11th event
#Event_time = UTCDateTime('2023-10-11T16:50:46.00')



eve_lat = 72.50
eve_lon = -27.30

stime = Event_time - Pre_win*60*60
etime = Event_time + Analysis_End*60*60



# Start of the actual code

###############################################################################
inv = client.get_stations(network='IU,II,IC,G,MN,AB,GE,CN,DK', station=sta, starttime=stime,
                          endtime=etime, level="response",
                          location=loc, channel='LH*')


st = client.get_waveforms(network='IU,II,IC,G,MN,GE,CN,DK', station=sta, location=loc,
                          channel='LH*', starttime=stime,
                          endtime=etime)


# detrend and merge
st.detrend('linear')
st.merge(fill_value=0)

#st.sort(['channel'])




# Remove response to units of ground velocity, filter, trim
st.remove_response(inventory=inv)
st.filter('bandpass', freqmin=Filt_min, freqmax=Filt_max)
st.trim(Event_time-Plot_start*60*60,etime)

# Now we get the BAZ and window

coors = inv.get_coordinates(st[0].stats.network+'.' + st[0].stats.station + '.' + st[0].stats.location + '.LHZ')
s_lat = coors['latitude']
s_lon = coors['longitude']

# Now we get dist and the BAZ to the Event
dist,BAZ, BAZ_INV = gps2dist_azimuth(s_lat,s_lon,eve_lat,eve_lon)
print(sta, 'Distance to Greenland Event ', dist/1000 )
print('Back Azimuth is:',BAZ)

#
#if st[0].stats.network == 'CH':
    #st.select(channel='LHE')[0].trim(Event_time-Plot_start*60*60,etime-1)
    #st.select(channel='LHZ')[0].trim(Event_time-Plot_start*60*60,etime-1)

if debug:
    print(st)
    print(inv)

# Now we need to rotate everything to radial
# Now we rotate the seismometer first from arbitary orientation to N and
st.rotate('->ZNE', inventory=inv)
st.rotate('NE->RT',back_azimuth=BAZ)

st2 = st.copy()
st2.trim(Event_time+Winstart_Del*60*60, Event_time+(Winstart_Del+Win_Length)*60*60)

# Grab the Traces we want

TR_Z, TR_Z_Calc = st.select(channel='LHZ')[0],st2.select(channel='LHZ')[0]
TR_R, TR_R_Calc = st.select(channel='LHR')[0], st2.select(channel='LHR')[0]
TR_T, TR_T_Calc = st.select(channel='LHT')[0], st2.select(channel='LHT')[0]

Vert_Amp = np.std(TR_Z_Calc.data)*1E9
Rad_Amp = np.std(TR_R_Calc.data)*1E9
Trans_Amp = np.std(TR_T_Calc.data)*1E9




# Now we do our Hilber Transforms
# Take the Hilbert Transforms that we want
# Keep in mind these will no longer be trace objects

TR_RHT, TR_RHT_Calc = np.imag(hilbert(TR_R.data)), np.imag(hilbert(TR_R_Calc.data))

# Now we do our correlations

cc_Ray =  correlate(TR_Z_Calc.data,TR_RHT_Calc,0)
shift_Ray, value_Ray = xcorr_max(cc_Ray)
value_Ray = np.round(value_Ray, decimals=2)
print(sta, 'HT Radial to Vertical Correlation is ', value_Ray)

# Straight correlation of radial and transverse

#cc_Ray =  correlate(TR_T_Calc.data,TR_R_Calc,0)
#shift_Ray, value_Ray = xcorr_max(cc_Ray)
#value_Ray = np.round(value_Ray, decimals=2)
#print(sta, 'Radial to Transverse ', value_Ray)


######### Figure of How Rayleigh Wave this is #################################

# Creating figure and moving subplots to have no space between them
fig = plt.figure(1, figsize=(20,16))
plt.clf()

# Vertical vs HT Radial

plt.plot(TR_Z.times()/(60*60),(TR_Z.data*1000000.),linewidth=1,c='k',alpha=1.0, label= sta + ' Vertical: ' + str(value_Ray))
plt.plot(TR_R.times()/(60*60),(TR_RHT*1000000.)+0.1,linewidth=1,c='g',linestyle='dashed', label='Radial', alpha=0.5)
plt.plot(TR_T.times()/(60*60),(TR_T.data*1000000.)-0.1,linewidth=2,color='xkcd:hot pink', label='Transverse', alpha=0.3)

# Event time: black
plt.axvspan(Plot_start,Plot_start+0.1, color='k', alpha = 0.5)
# analysis window: "c1"
plt.axvspan(Plot_start+Winstart_Del,Plot_start+Winstart_Del+Win_Length, color='C1', alpha = 0.5)


plt.ylabel('Ground\nVelocity ($\mu$m/s)', fontsize=24)
plt.xlabel('Time (Hr)', fontsize = 24)
plt.legend()

########################################################################
plt.savefig(Anthony_LoveMap_Final.eps)

plt.show()

print('Rob Here is your stuff:', sta, ',', s_lat, ',', s_lon, ',', BAZ, ',', value_Ray, ',', Vert_Amp, ',', Rad_Amp, ',', Trans_Amp)


# Now let's do some sliding window analysis
