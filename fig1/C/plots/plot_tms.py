#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy as np
ext="_6hrs"
#ext=""
fil="../sim/gglo/gglo_box_%(vol)dM%(ext)s/spletaD%(tms)d"
info={}
info[0]=["Tide gauge: Dickson fjord",1]
#info[2]=["Tide gauge: Rohrs fjord",2]
info[1]=["Gauge 1",3]
info[2]=["Tide gauge: Ella $\O$",4]
info[3]=["Gauge 2",5]

ratio=0.05
#fig = plt.figure()
for z in [0,1,2]:
    fig, ax = plt.subplots(4,sharex=True)
    for d in [0,1,2,3]:
        for vol in [20]:
            tms=info[d][1]
            inn=fil %vars()
            arr=np.loadtxt(inn)
            x,y=arr[:,0],arr[:,1]*1000
            print("x",x)
            ax[d].plot(x,y) #,label=str(vol)+"M")
        if z==1:
            ax[d].set_xlim([5000,5500])
        elif z==2:
            ax[d].set_xlim([2000,2500])
        else:
            ax[d].plot([5000,5000],[min(y[:]),max(y[:])],'r-')
            ax[d].plot([5500,5500],[min(y[:]),max(y[:])],'r-')
            ax[d].plot([2000,2000],[min(y[:]),max(y[:])],'r-')
            ax[d].plot([2500,2500],[min(y[:]),max(y[:])],'r-')
        #plt.xlabel("Time [s]")
        #plt.ylabel("Surface elevation [m]")
        #ax[d].set_aspect(abs((x[0]-x[-1])/(y[0]-y[-1]))*ratio)
        title=info[d][0]
        ax[d].set_title(title, fontsize=10)
        ax[d].set_ylabel("[m]")
        #plt.show()
        
    #ax[tms].legend()
    for a in ax.flat:
        a.set(xlabel="Time [s]",ylabel="[m]")
        a.label_outer()
    fig.tight_layout()
    #plt.show()
    plt.savefig("tide_gauges_20M_z%(z)d%(ext)s.png" %vars())