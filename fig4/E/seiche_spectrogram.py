import matplotlib.pyplot as plt
import numpy as np
import obspy
from obspy.signal.tf_misfit import cwt
from scipy import signal
from scipy.signal import butter, lfilter


def butter_bandpass(lowcut, highcut, fs, order=5):
    return butter(order, [lowcut, highcut], fs=fs, btype='band')

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y


if __name__ == "__main__":

    datat = np.loadtxt('./eta1-Gauge_Landslide_interp.txt')

    fs = 1
    
    t = datat[:,0]
    d = datat[:,1]

    t = t/(3600*24)

    window = signal.tukey(36001,0.1)
    
    #plt.plot(t,d)
    #plt.show()

    f_min = 5e-3
    f_max = 30e-3

    f_min1 = 1e-3
    f_max1 = 40e-3
    
    df = butter_bandpass_filter(d*window, f_min1, f_max1, fs, order=3)


    scalogram = cwt(df, 1/fs, 120, f_min, f_max, nf=350)

    x, y = np.meshgrid(
        t,
        np.logspace(np.log10(f_min), np.log10(f_max), scalogram.shape[0]))

    fig = plt.figure(figsize=(25/24,6)) #figsize=(5,6) for larger figure
    ax0 = fig.add_subplot(111)
    im=ax0.pcolormesh(x, y*1000, np.log10(np.abs(scalogram)), cmap='inferno',vmin=-4.0, vmax=1.0) 
    fig.colorbar(im, ax=ax0,label="log10(amplitude)")
    ax0.set_xlabel("Time [days]")
    ax0.set_ylabel("Frequency [mHz]")
    ax0.set_title("Synthetic gauge")

    ax0.set_ylim(f_min*1000, f_max*1000)
    plt.savefig("SyntheticGauge_Scaled_Spectro.png", dpi=150, bbox_inches='tight')

    # plt.show()