import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd


DATA_FILE = "results/results_change_distance/simple_link_var_jun_27.csv"

# plotting parameters
mpl.rcParams.update({'font.sans-serif': 'Helvetica',
                     'font.size': 12})

df = pd.read_csv(DATA_FILE)

distance = df["Distance"]
throughput = df["Average Throughput"]
error = df["Std. Throughput"]
total_time = 1e3 / throughput
error_total_time = total_time * (error / throughput)

# plotting of values
fig, ax = plt.subplots()
ax2 = ax.twinx()

color = 'tab:blue'
ax.errorbar(distance, throughput, yerr=error,
            fmt='-o', capsize=5, color=color)
ax.set_ylabel("Throughput (pairs/s)", color=color)
ax.tick_params(axis='y', colors=color)

color = 'tab:orange'
ax2.errorbar(distance, total_time, yerr=error_total_time,
             fmt='-o', capsize=5, color=color)
ax2.set_ylabel("Time to complete 1000 pairs (sec)", color=color)
ax2.tick_params(axis='y', colors=color)

ax.set_xlabel("Alice-midpoint distance (km)")
ax.grid('on')

fig.tight_layout()
fig.show()
