import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import h5py
import os

def findAscan(data_frame, x=350, y=350):
    # Time-domain lower and upper limits are retrieved
    t0 = data_frame['Time'].attrs['t0']
    tf = data_frame['Time'].attrs['tf']
    # x- and y-axis lower limits, upper limits and step are retrieved
    x0 = int(round(data_frame['Position'].attrs['x0']*1000,0))
    dx = int(round(data_frame['Position'].attrs['dx']*1000,0))
    xf = int(round(data_frame['Position'].attrs['xf']*1000,0))
    y0 = int(round(data_frame['Position'].attrs['y0']*1000,0))
    dy = int(round(data_frame['Position'].attrs['dy']*1000,0))
    yf = int(round(data_frame['Position'].attrs['yf']*1000,0))
    # Amount of steps over each axis is calculated. Operation rounds up the division result as needed
    #qx = int(round((xf - x0) / dx + 1))
    #qy = int(round((yf - y0) / dy + 1))

    x_ = int((x//dx)*dx)
    y_ = int((y//dy)*dy)
    #print(x_,y_)
    index = int(round(((yf-y0)/dy+1)*((x_-x0)/dx) + y_/dy))
    print(index, x_, y_, dx, dy)
    print(x0, xf, y0, yf)

    #TODO: Actualizar x-y-z pol para otros casos.
    realData = data_frame['A-Scan/Re{A-Scan x-pol}'][index][:]          
    #imag_2 = data_frame['A-Scan/Im{A-Scan x-pol}'][index][:]
    #a_scan_x = (np.sqrt(real_2**2+imag_2**2))
    #data_frame['A-Scan/Re{A-Scan x-pol}']
    return [realData, 1e9*np.linspace(t0,tf, len(realData))]


def plot_a_scan_from_merged_file(file, x, y, compareFile=""):
    if(compareFile==""):
        compare = False
    else:
        compare = True

    data_frame = h5py.File(file, 'r')
    rootPath = os.path.dirname(file)
    [realData, time] = findAscan(data_frame, x, y)

    plt.figure(figsize=(13,7))
    plt.plot(time, realData*1000 )
    plt.xlabel("Time [ns]")
    plt.ylabel("Amplitude [mV]")
    plt.grid()
    plt.title("GPR measured A-Scan at (x,y)=("+str(int(x))+","+str(int(y))+")mm")

    imName = "A_Scan_"+str(x)+"_"+str(y)
    plt.savefig(rootPath+"/"+imName+"_measured.png")

    plt.figure(figsize=(13,7))
    plt.plot(time, realData*1000 )
    plt.xlabel("Time [ns]")
    plt.ylabel("Amplitude [mV]")
    plt.grid()
    plt.title("GPR measured A-Scan at (x,y)=("+str(int(x))+","+str(int(y))+")mm")
    plt.xlim([0,12])
    plt.savefig(rootPath+"/"+imName+"_measured_limited.png")

    if(compare):
        sim_data = pd.read_csv(compareFile)
        
        delay = 0
        a_scan_sim = np.array(sim_data["Output(feed_pin1_T1,feed_pin3_T1) [mV]"])[delay:]
        time_sim = np.array(sim_data['Time [ns]'])[delay:]
        time_sim = time_sim - time_sim[0]
        #imag = np.array(a_scan["A-Scan_imag"])
        #dbs = 10*np.log10(np.linalg.norm([real, imag], axis=0))
        plt.figure(figsize=(13,7))
        plt.plot(time_sim, a_scan_sim)
        plt.xlabel("Time [ns]")
        plt.ylabel("Amplitude [mV]")
        plt.title("A-Scan HFSS-simulation")
        plt.grid()
        plt.savefig(rootPath+"/"+"A_Scan_simulation.png")
        # Plot exp+sim
        plt.figure(figsize=(13,7))
        plt.plot(time, realData*1000, label="Measured" )
        plt.plot(time_sim, a_scan_sim, label="Simulation")
        plt.legend()
        plt.xlabel("Time [ns]")
        plt.ylabel("Amplitude [mV]")
        plt.grid()
        plt.title("GPR A-Scan at (x,y)=("+str(int(x))+","+str(int(y))+")mm and HFSS-simulation results")
        plt.savefig(rootPath+"/"+imName+"_measured+simulation.png")
        # Plot exp+sim with restricted domain
        plt.figure(figsize=(13,7))
        plt.plot(time, realData*1000, label="Measured" )
        plt.plot(time_sim, a_scan_sim, label="Simulation")
        plt.legend()
        plt.xlabel("Time [ns]")
        plt.ylabel("Amplitude [mV]")
        plt.grid()
        plt.xlim([0,time_sim[-1]])
        plt.title("GPR A-Scan at (x,y)=("+str(int(x))+","+str(int(y))+")mm and HFSS-simulation results")
        plt.savefig(rootPath+"/"+imName+"_measured+simulation_limited.png")
        #Plot exp+sim with restricted domain and super
        fig, ax1 = plt.subplots(figsize=(13,7))
        ax2 = ax1.twinx()
        ax1.plot(time, realData*1000, color='#1f77b4', label="exp")
        ax2.plot(time_sim, a_scan_sim, color='#ff7f0e', label="sim")

        ax1.set_xlabel('time [ns]')
        ax1.set_ylabel('Measured Amplitude [mV]', color='#1f77b4')
        ax2.set_ylabel('Simulated Amplitude [mV]', color='#ff7f0e')
        plt.xlim([0,12])
        #plt.legend()
        plt.title("GPR A-Scan at (x,y)=("+str(int(x))+","+str(int(y))+")mm and HFSS-simulation results")
        plt.grid()
        plt.savefig(rootPath+"/"+imName+"_measured+simulation_limited+super.png")


if __name__ == '__main__':
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    file = filedialog.askopenfilename(parent=root, initialdir=os.getcwd())
    compare = filedialog.askopenfilename(parent=root, initialdir=os.getcwd())
    root.destroy()
    # B-Scans of the merged file are plotted
    plot_a_scan_from_merged_file(file, 350, 350, compare)
        