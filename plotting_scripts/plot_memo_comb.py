import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

SEQUE_FILE = sys.argv[1]
QUISP_FILE = sys.argv[2]

# plotting parameters
mpl.rcParams.update({'font.sans-serif': 'DejaVu Sans',
                     'font.size': 12})


sequence = pd.read_csv(SEQUE_FILE)
quisp = pd.read_csv(QUISP_FILE)

memo_labels = sequence["Memory Count"]
seq_tput = sequence["Average Throughput"]
seq_stdev = sequence["Std. Throughput"]
qui_tput = quisp["Average Throughput"]
qui_stdev = quisp["Std. Throughput"]

# plotting of bar graph
plt.close()
fig, ax = plt.subplots()
ax2 = ax.twinx()
xtick_loc = np.arange(len(memo_labels))
width = 0.8  # total width of both bars

color = 'tab:blue'
ax.bar(xtick_loc - (width / 4), seq_tput,
       width=width/2, color=color, edgecolor='k', zorder=2)
ax.errorbar(xtick_loc - (width / 4), seq_tput, yerr=seq_stdev,
            color='k', ls='', capsize=5)
ax.set_ylabel("SeQUeNCe avrg. throughput (pairs/s)", color=color)
ax.tick_params(axis='y', colors=color)

color='tab:orange'
ax2.bar(xtick_loc + (width / 4), qui_tput,
        width=width/2, color=color, edgecolor='k', zorder=2)
ax2.errorbar(xtick_loc + (width / 4), qui_tput, yerr=qui_stdev,
             color='k', ls='', capsize=5)
ax2.set_ylabel("QuISP avrg. throughput (pairs/sec)", color=color)
ax2.tick_params(axis='y', colors=color)

ax.set_xticks(ticks=xtick_loc, labels=memo_labels)
ax.set_xlabel("Number of Memories")
ax.grid('on', axis='y')
fig.tight_layout()
fig.savefig('../graphs/comb-var-mem.pdf')
#fig.show()
print(qui_tput / seq_tput)


# plotting of variance
# plt.close()
# plt.plot(memo_labels, error, '-o')
# plt.ylim((0, 17))
# plt.ylim((0, 7.5))
# plt.xlabel("Number of Memories")
# plt.ylabel("Throughput Error")
# plt.grid('on')
#
# plt.tight_layout()
# plt.savefig('../graphs/line-mem-perf.pdf')
# plt.show()
