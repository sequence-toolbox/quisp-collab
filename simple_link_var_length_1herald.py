import numpy as np
import pandas as pd
import time

from sequence.topology.router_net_topo import RouterNetTopo
from sequence.app.request_app import RequestApp
import sequence.utils.log as log


CONFIG_FILE = "config_files/simple_link_bds.json"

# meta params
NO_TRIALS = 1
OUTPUT_FILE = "results/dump_sep_19.csv"
LOGGING = False
LOG_OUTPUT = "results/simple_link_log.csv"
MODULE_TO_LOG = ["timeline", "memory", "bsm", "generation", "request_app"]

# simulation params
PREP_TIME = int(1e12)  # 1 second
COLLECT_TIME = int(10e12)  # 10 seconds

# qc params
QC_FREQ = 1e11
total_distance = 20  # (unit: km)
distances = list(range(11))  # iterate through these (unit: km)

# application params
APP_NODE_NAME = "left"
OTHER_NODE_NAME = "right"
num_memo = 1

# storing data
data_dict = {"Distance": [],
             "Average Throughput": [],
             "Std. Throughput": []}


tick = time.time()

for i, distance in enumerate(distances):
    print(f"Running {NO_TRIALS} trials for distance {distance}km ({i + 1}/{len(distances)})")
    data_dict["Distance"].append(distance)
    throughputs = np.zeros(NO_TRIALS)

    for trial_no in range(NO_TRIALS):
        # establish network
        net_topo = RouterNetTopo(CONFIG_FILE)

        # timeline setup
        tl = net_topo.get_timeline()
        tl.stop_time = PREP_TIME + COLLECT_TIME

        if LOGGING:
            # set log
            if i == 0:
                log.set_logger(__name__, tl, LOG_OUTPUT)
                log.set_logger_level('DEBUG')
                for module in MODULE_TO_LOG:
                    log.track_module(module)
            elif i == 1:
                for module in MODULE_TO_LOG:
                    log.remove_module(module)

        # network configuration
        routers = net_topo.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER)
        bsm_nodes = net_topo.get_nodes_by_type(RouterNetTopo.BSM_NODE)

        for j, node in enumerate(routers + bsm_nodes):
            node.set_seed(j + (trial_no * 3))

        # set quantum channel parameters
        left_distance = distance
        right_distance = total_distance - distance
        for qc in net_topo.get_qchannels():
            qc.frequency = QC_FREQ
            if qc.sender.name == APP_NODE_NAME:
                qc.distance = left_distance * 1e3
            elif qc.sender.name == OTHER_NODE_NAME:
                qc.distance = right_distance * 1e3
            else:
                raise Exception(f"Invalid sender node name '{qc.sender.name}'")

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
