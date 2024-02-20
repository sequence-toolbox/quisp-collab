import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

DATA_FILE = sys.argv[1]

# plotting parameters
mpl.rcParams.update({'font.sans-serif': 'DejaVu Sans',
                     'font.size': 12})


df = pd.read_csv(DATA_FILE)

memo_labels = df["Memory Count"]
throughput = df["Average Throughput"]
error = df["Std. Throughput"]

# plotting of bar graph
plt.close()
fig, ax = plt.subplots()
ax2 = ax.twinx()
xtick_loc = np.arange(len(memo_labels))
width = 0.8  # total width of both bars

color = 'tab:blue'
ax.bar(xtick_loc - (width / 4), throughput,
       width=width/2, color=color, edgecolor='k', zorder=2)
ax.errorbar(xtick_loc - (width / 4), throughput, yerr=error,
            color='k', ls='', capsize=5)
ax.set_ylabel("Average Throughput (pairs/s)", color=color)
ax.tick_params(axis='y', colors=color)

color='tab:orange'
ax2.bar(xtick_loc + (width / 4), throughput / memo_labels,
        width=width/2, color=color, edgecolor='k', zorder=2)
ax2.errorbar(xtick_loc + (width / 4), throughput / memo_labels, yerr=error / memo_labels,
             color='k', ls='', capsize=5)
ax2.set_ylabel("Throughput per Memory (pairs/sec)", color=color)
ax2.tick_params(axis='y', colors=color)

ax.set_xticks(ticks=xtick_loc, labels=memo_labels)
ax.set_xlabel("Number of Memories")
ax.grid('on', axis='y')
fig.tight_layout()
fig.savefig('../graphs/bar-mem-perf.pdf')
fig.show()


# plotting of variance
plt.close()
plt.plot(memo_labels, error, '-o')
plt.ylim((0, 17))
plt.ylim((0, 7.5))
plt.xlabel("Number of Memories")
plt.ylabel("Throughput Error")
plt.grid('on')

plt.tight_layout()
plt.savefig('../graphs/line-mem-perf.pdf')
plt.show()
