#!/usr/bin/env python

# This code makes an inventory object and returns all stations in Antarctica

import cartopy
import cartopy.crs as ccrs
import matplotlib.path as mpath
import matplotlib.pyplot as plt
# Mapping Packages
import numpy as np
from obspy import UTCDateTime, read_inventory
from obspy.clients.fdsn import Client

debug = False

# Final event location
eve_lat = 72.50
eve_lon = -27.30


stas, lats, lons, BAZs, corrs, Vs, Rs,Ts, RAs, TAs, HRs, Ms = [],[],[],[],[],[],[],[],[],[],[],[]

Data_file = open('./92s_RT_Final_Sept16.txt')

for line in Data_file:
        Col = line.split(' , ')
        sta, lat, lon = str(Col[0]),float(Col[1]), float(Col[2])
        if debug:
            print(Col)
        # convert BAZ to the CCW format quiver wants (-1 * BAZ-90)
        BAZ = float(Col[3])
        #RA = float(Col[8])
        corr,V,R,T = float(Col[4]),float(Col[5]),float(Col[6]),float(Col[7])
        #TA = RA + 90.
        HR = np.log10(T/R)
        M = Col[9]

        stas.append(sta),lats.append(lat),lons.append(lon)
        BAZs.append(BAZ),corrs.append(corr), Vs.append(V),Rs.append(R),Ts.append(T)
        #RAs.append(RA), TAs.append(TA)
        HRs.append(HR), Ms.append(M)



DFJ_lons = [-40.153, -13.801]
DFJ_lats = [71.015, 73.606]

LNP_lons = [-26.9716, 79.0708, 153.0283, -84.1053, -26.9716]
LNP_lats = [72.8358, 9.2891, -72.8353, 39.7624, 72.8358]

RNP_lons = [-26.9716, -10.3422, 153.0283, 177.0588, -26.9716]
RNP_lats = [72.8358, 6.2717, -72.8353, 52.2190, 72.8358]

# Make the Plot
fig = plt.figure(1,figsize=(10,10),facecolor='w')


# create the map using the cartopy Orthographic projection, selecting the South Pole



#plt.title('September 16th Fundamental at 10.88 mHz')
# add coastlines, gridlines, fill land color and set limits of plot

# Trick from StackOverflow to improve Resolution of Great Circle Lines
# https://stackoverflow.com/questions/60685245/plot-fine-grained-geodesic-with-cartopy/60724892#60724892

plateCr = ccrs.NorthPolarStereo()
# print(plateCr._threshold) # original threshold=0.5
plateCr._threshold = plateCr._threshold/10.  #set finer threshold
ax1 = plt.axes(projection=plateCr)
######################################################################

ax1.coastlines(resolution='110m', zorder=3) # zorder=3 makes sure that no other plots overlay the coastlines
gl = ax1.gridlines(crs=ccrs.PlateCarree(), color='grey', alpha=0.5, linestyle=':')
# This is necesary to make the latitude lines look circular
gl.n_steps = 90

#gl.yformatter = LATITUDE_FORMATTER
ax1.set_global()
ax1.add_feature(cartopy.feature.LAND, zorder=1,facecolor=cartopy.feature.COLORS['land_alt1'])
# Limit the map to -60 degrees latitude and below.
ax1.set_extent([-180, 180, 90, 38], ccrs.PlateCarree())


# Plot Fjord Strike and PErpedicular to Fjord Strike
ax1.plot(LNP_lons,LNP_lats, linewidth=1, c='xkcd:magenta',transform = ccrs.Geodetic(),zorder=6)
ax1.plot(RNP_lons,RNP_lats, linewidth=1, c='xkcd:green',transform = ccrs.Geodetic(),zorder=7)



# Add a Legend - probably a better way to do this, but we'll just stuff a bunch of fake stations at South Pole
sc2 = ax1.scatter(0,-90,s=150,c='k',edgecolor='k', marker = '^', label = '360 s Surface Vault',transform = ccrs.PlateCarree())
sc2 = ax1.scatter(0,-90,s=150,c='k',edgecolor='k', marker = 'o', label = '360 s Borehole',transform = ccrs.PlateCarree())
sc2 = ax1.scatter(0,-90,s=150,c='k',edgecolor='k', marker = 'H', label = '360 s Cave/Mine',transform = ccrs.PlateCarree())
sc2 = ax1.scatter(0,-90,s=150,c='k',edgecolor='k', marker = 'd', label = '120 s Surface',transform = ccrs.PlateCarree())



for staP in zip(lons,lats,HRs,Ms,stas):
    sc = ax1.scatter(staP[0],staP[1],s=200,c=staP[2],zorder=4, marker=staP[3], edgecolor='k', transform = ccrs.PlateCarree(), cmap='PiYG_r', vmin=-0.8, vmax=0.8 )
    ax1.text(staP[0]+ 0.02*staP[0],staP[1]+1.5,staP[4], c = 'b', transform = ccrs.PlateCarree(), zorder=5)





# Make plot circular

cbar = fig.colorbar(sc, orientation='vertical')
cbar.set_label('LOVE factor',fontsize=16)


theta = np.linspace(0, 2*np.pi, 100)
center, radius = [0.5, 0.5], 0.5
verts = np.vstack([np.sin(theta), np.cos(theta)]).T
circle = mpath.Path(verts * radius + center)
ax1.set_boundary(circle, transform=ax1.transAxes)



ax1.legend(loc=3)


# plt.show()
plt.savefig("./VRT_Figs/global.png")
