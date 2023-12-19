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
info[2]=["Tsunami simulations, surface elevations at tide gauge near by Ella $\O$",4]
info[3]=["Gauge 2",5]

ratio=0.05
#fig = plt.figure()
fig,ax = plt.subplots(2) #,sharex=True)
for z in [0,1]:   
    #for d in [2]:
    d=2
    #for vol in [20]:
    vol=20
    tms=info[d][1]
    inn=fil %vars()
    arr=np.loadtxt(inn)
    x,y=arr[:,0],arr[:,1]*1000
    print("x",x)
    ax[z].plot(x,y) #,label=str(vol)+"M")
    if z==1:
        ax[z].set_xlim(600,3600)
        ax[z].set_aspect(150)
        ax[z].set_xlabel("Time [s]")
        
    elif z==0:
        title=info[d][0]
        ax[z].set_title(title, fontsize=10)
        ax[z].set_aspect(1700)
        ax[z].plot([600,600],[min(y[:]),max(y[:])],'r-')
        ax[z].plot([3600,3600],[min(y[:]),max(y[:])],'r-')
        #ax[z].xaxis.set_tick_params(labelbottom=True)
        #ax[z].set_xticks(range(0,30000,500))
    # else:
    #     ax[z].plot([5000,5000],[min(y[:]),max(y[:])],'r-')
    #     ax[z].plot([5500,5500],[min(y[:]),max(y[:])],'r-')
    #     ax[z].plot([2000,2000],[min(y[:]),max(y[:])],'r-')

    #     ax[z].plot([2500,2500],[min(y[:]),max(y[:])],'r-')
    #plt.xlabel("Time [s]")
    #plt.ylabel("Surface elevation [m]")
    #ax[d].set_aspect(abs((x[0]-x[-1])/(y[0]-y[-1]))*ratio)

    ax[z].set_ylabel("[m]")
    ax[z].set_ylim(-2.2,2.2)
    #plt.show()
    
    #ax[tms].legend()
    
    #ax[z].set(xlabel="Time [s]",ylabel="[m]")
    #ax[z].label_outer()
fig.tight_layout()
plt.subplots_adjust(hspace=-0.4)
#plt.show()
#for a in ax.flat:
#    a.xaxis.set_tick_params(labelbottom=True)

plt.savefig(f"tsunami_EllaO_20M{ext}.png",format='png')
plt.savefig(f"tsunami_EllaO_20M{ext}.pdf",format='pdf')
plt.savefig(f"tsunami_EllaO_20M{ext}.svg",format='svg')
