# This module generates our meteograms.

import matplotlib.pyplot as plt
from wrf import getvar, ll_to_xy, to_np
import numpy as np
import os

def plot_meteogram(wrf_file, airport, coords, output_path, forecast_times, wrfhours, run_time):
    x, y = ll_to_xy(wrf_file, coords[0], coords[1])
    hours = np.arange(1, wrfhours + 1)
    times = [forecast_times[t].strftime('%H UTC') for t in hours]
    u_wind = [to_np(getvar(wrf_file, "U10", timeidx=t)[y, x]) for t in hours]
    v_wind = [to_np(getvar(wrf_file, "V10", timeidx=t)[y, x]) for t in hours]
    temperatures = []
    dewpoints = []
    pressures = []
    for t in hours:
        t_data = getvar(wrf_file, "T2", timeidx=t)[y, x].values
        td_data = getvar(wrf_file, "td2", timeidx=t)[y, x].values
        pressure_data = getvar(wrf_file, "AFWA_MSLP", timeidx=t)[y, x].values
        t_f = (t_data - 273.15) * 9/5 + 32
        td_f = to_np(td_data) * 9/5 + 32
        pressure_mb = to_np(pressure_data) / 100
        temperatures.append(t_f)
        dewpoints.append(td_f)
        pressures.append(pressure_mb)
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(hours, temperatures, color='red', label='Temperature (°F)')
    ax1.plot(hours, dewpoints, color='green', label='Dewpoint (°F)')
    ax1.barbs(hours, ax1.get_ylim()[0] * 1.07, u_wind, v_wind, length=6, barb_increments={'half': 2.57222, 'full': 5.14444, 'flag': 25.7222}) 
    ax1.set_ylabel('Temperature / Dewpoint (°F)')
    ax1.set_xlabel('Forecast Hour') 
    ax1.set_xticks(hours)
    ax1.set_xticklabels(times, rotation=45)
    ax2 = ax1.twinx()
    ax2.plot(hours, pressures, color='blue', label='Pressure (mb)')
    ax2.set_ylabel('Pressure (mb)')
    lines_ax1, labels_ax1 = ax1.get_legend_handles_labels()
    lines_ax2, labels_ax2 = ax2.get_legend_handles_labels()
    all_lines = lines_ax1 + lines_ax2
    all_labels = labels_ax1 + labels_ax2
    ax1.legend(all_lines, all_labels, loc="upper left")
    plt.title(f"UGA-WRF Meteogram for {airport.upper()} starting at {forecast_times[1]} UTC - Init: {forecast_times[0]}")
    plt.grid(True)
    plt.tight_layout()
    plt.annotate(f"UGA-WRF Run {run_time}", xy=(0.01, 0.01), xycoords='figure fraction', fontsize=8, color='black')
    os.makedirs(output_path, exist_ok=True)
    plt.savefig(os.path.join(output_path, "meteogram.png"))
    plt.close()