#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
import numpy as np
import csv

# Create and evaluate a dataset from file
class ignition:
    def __init__(self, datafile = "", sp=';', dc=',', hd = 7, ec="utf-8"):
        self.df = pd.read_csv(datafile, sep = sp, decimal = dc, header = hd, encoding = ec)
        print(self.df.head())
        print("Ignition object created")

    def clcols(self, names = []):
        self.df = self.df.drop(columns = names)
        print(self.df.head())
        print("Columns cleared")

    def addtime(self, fq = 1, unit = "s"):        
        sc = {
            "s": 1,
            "ms": 1000,
            "min": 1 / 60,
            "h": 1 / 3600,
            "d": 1 / 86400
        }
        self.df["time"] = np.arange(len(self.df)) / fq * sc.get(unit, 1)
        self.df.insert(0, "time", self.df.pop("time"))

        print(self.df.head())
        print("Time column added")

    def ignplot(self, xcol = 0, ycol = 1, xunit = "bara", yunit = "s", target_x = None, x_lim = None):
        # Zeichnen eines Diagramms mit MatplotLib. Es können auch große Datenmengen verarbeitet werden. 
        # Skalierung muss angepasst werden in Zeile ax1.set_ylim und ax2.set_ylim
        # Zeilen ax1.plot und ax2.plot müssen angepasst werden, um festzulegen, welche Spalten angezeigt werden sollen.

        # Erstelle die erste y-Achse
        fig, ax1 = plt.subplots()

        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['font.serif'] = ['Verdana']
        plt.rcParams['font.size'] = 12

        ax1.set_xlabel(f'time in {xunit}')
        ax1.set_ylabel(f'pressure in {yunit}', color='tab:blue')
        ax1.plot(self.df.iloc[:, xcol], self.df.iloc[:, ycol], color='tab:blue')            # Anpassen um Daten für erste y-Achse festzulegen
        ax1.tick_params(axis='y', labelcolor='tab:blue')
        ax1.grid(True, which='both', linestyle='--', linewidth=0.5)

        #ax1.autoscale()
        #ax1.set_ylim([0, 20])  # y-Achse von 0 bis 50               # Anpassen um Skalierung für erste y-Achse festzulegen

        if x_lim is not None:   # x-Achse skalieren                       
           ax1.set_xlim([0, x_lim])  

        if target_x is not None:  # Zielpunkt rot markieren
            target_y = self.df.loc[self.df.iloc[:, xcol] == target_x].iloc[0, ycol]
            ax1.plot(target_x, target_y, "ro", markersize=8)

        fig.tight_layout()
        plt.show()

    def calcslopes(self, na = 10, ne = 100, xcol = 0, ycol = 1, target = 21):
        results = []
        delta = np.mean(np.diff(self.df.iloc[:, xcol])) #ermittelt Zeitschritte
        for window in range(na, ne +1):
            if window % 2 == 0:
                continue
            slopes = savgol_filter(
                self.df.iloc[:, ycol],
                window_length=window,
                polyorder=1,
                deriv=1,
                delta=delta) 

            max_slope = np.max(slopes)
            max_index = np.argmax(slopes)
            t_max_slope = self.df.iloc[max_index, xcol]
            results.append({
                "window": window,
                "max_slope": max_slope,
                "t_max_slope": t_max_slope
            })
        results_df = pd.DataFrame(results) # results werden erst hinter in ein dataframe geschrieben. Das verkürzt die Rechenzeit

        # Plot results
        fig, ax1 = plt.subplots()

        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['font.serif'] = ['Verdana']
        plt.rcParams['font.size'] = 12

        ax1.set_xlabel('number of values')
        ax1.set_ylabel('(dx/dt)max', color='tab:blue')
        ax1.plot(results_df["window"], results_df["max_slope"], color='tab:blue')            # Anpassen um Daten für erste y-Achse festzulegen
        ax1.tick_params(axis='y', labelcolor='tab:blue')
        ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
        #ax1.autoscale()
        #ax1.set_xlim([0, 6])  # x-Achse von 0 bis 6
        #ax1.set_ylim([0, 20])  # y-Achse von 0 bis 50               # Anpassen um Skalierung für erste y-Achse festzulegen

        fig.tight_layout()

        target_dpdt = round(results_df.loc[results_df["window"] == target, "max_slope"].iat[0], 2)
        target_x = results_df.loc[results_df["window"] == target, "t_max_slope"].iloc[0]
        return results_df, target_dpdt, target_x        

        #print(f'For number of values = {target}: (dp/dt)max = {target_dpdt}. at t = {target_x}')
        #plt.show()

