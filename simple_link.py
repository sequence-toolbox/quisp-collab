import numpy as np
import pandas as pd
import time
from datetime import date

from sequence.topology.router_net_topo import RouterNetTopo
from sequence.app.request_app import RequestApp
import sequence.utils.log as log

today = date.today()

CONFIG_FILE = "config_files/simple_link.json"

# meta params
NO_TRIALS = 50
OUTPUT_FILE = "results/simple_link_"+str(today)+".csv"
LOGGING = False
LOG_OUTPUT = "results/simple_link_log.csv"
MODULE_TO_LOG = ["timeline", "memory", "bsm", "generation", "request_app"]

# simulation params
PREP_TIME = int(1e12)  # 1 second
COLLECT_TIME = int(10e12)  # 10 seconds

# qc params
QC_FREQ = 1e11

# application params
APP_NODE_NAME = "left"
OTHER_NODE_NAME = "right"
num_memories = [1, 2, 4, 8, 16]  # iterate through these

# storing data
data_dict = {"Memory Count": [],
             "Average Throughput": [],
             "Std. Throughput": []}


tick = time.time()

for i, num_memo in enumerate(num_memories):
    print(f"Running {NO_TRIALS} trials for memory count {num_memo} ({i + 1}/{len(num_memories)})")
    data_dict["Memory Count"].append(num_memo)
    throughputs = np.zeros(NO_TRIALS)

    for trial_no in range(NO_TRIALS):
        # establish network
        net_topo = RouterNetTopo(CONFIG_FILE)

        # timeline setup
        tl = net_topo.get_timeline()
        tl.stop_time = PREP_TIME + COLLECT_TIME

        if LOGGING:
            # set log
            if num_memo == num_memories[0]:
                log.set_logger(__name__, tl, LOG_OUTPUT)
                log.set_logger_level('DEBUG')
                for module in MODULE_TO_LOG:
                    log.track_module(module)
            elif num_memo == num_memories[1]:
                for module in MODULE_TO_LOG:
                    log.remove_module(module)

        # network configuration
        routers = net_topo.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER)
        bsm_nodes = net_topo.get_nodes_by_type(RouterNetTopo.BSM_NODE)

        for j, node in enumerate(routers + bsm_nodes):
            node.set_seed(j + (trial_no * 3))

        # set quantum channel parameters
        for qc in net_topo.get_qchannels():
            qc.frequency = QC_FREQ

        # establish app on left node
        start_node = None
        for node in routers:
            if node.name == APP_NODE_NAME:
                start_node = node
                break
        if not start_node:
            raise ValueError(f"Invalid app node name {APP_NODE_NAME}")
        end_node = None
        for node in routers:
            if node.name == OTHER_NODE_NAME:
                end_node = node
                break
        if not start_node:
            raise ValueError(f"Invalid other node name {OTHER_NODE_NAME}")

        app_start = RequestApp(start_node)
        app_end = RequestApp(end_node)

        # initialize and start app
        tl.init()
        app_start.start(OTHER_NODE_NAME, PREP_TIME, PREP_TIME + COLLECT_TIME, num_memo, 1.0)
        tl.run()

        throughputs[trial_no] = app_start.get_throughput()
        print(f"\tCompleted trial {trial_no + 1}/{NO_TRIALS}")

    print("Finished trials.")

    avg_throughput = np.mean(throughputs)
    std_throughput = np.std(throughputs)
    print(f"Average throughput: {avg_throughput} +/- {std_throughput}")

    data_dict["Average Throughput"].append(avg_throughput)
    data_dict["Std. Throughput"].append(std_throughput)

df = pd.DataFrame(data_dict)
df.to_csv(OUTPUT_FILE, index=False)

runtime = time.time() - tick
print("Total runtime:", runtime)
