# File:     gem5_ssd_iterative.py
# Author:   Edward Hanson (eth20@duke.edu)
# Desc.:    Iteratively run gem5+SimpleSSD until convergence or timeout

import os
import subprocess
import filecmp
import trace_util

SimpleSSD_Standalone_path = "/root/hostCurUser/SimpleSSD-Standalone/"
SimpleSSD_FullSystem_path = "/root/hostCurUser/SimpleSSD-FullSystem/"
max_iterations = 10

# Build gem5 -- comment out if already done
subprocess.run(["scons", "build/X86_MESI_Two_Level/gem5.opt", "-j", "8"], cwd=SimpleSSD_FullSystem_path, check=True)

iteration = 0
first = True
while True:
    # Check if this is the first iteration
    if os.path.exists(os.path.join(SimpleSSD_Standalone_path, "out/latency.csv")):
        first = False
        subprocess.run(["cp", os.path.join(SimpleSSD_Standalone_path, "out/latency.csv"), os.path.join(SimpleSSD_Standalone_path, "out/prev_latency.csv")], check=True)

    # Run gem5 with or without SimpleSSD feedback
    subprocess.run(["build/X86_MESI_Two_Level/gem5.opt", "--debug-flags=SimpleSSD", "--debug-file=traceForSimpleSSD.txt", "configs/example/ruby_direct_test.py", "--num-cpus=2", "--mem-type=SimpleMemory", "--test-type=SeriesGetMixed", "--percent-writes=100", "--requests=100"], cwd=SimpleSSD_FullSystem_path, check=True)

    # Convert intercepted gem5 transactions to SimpleSSD input
    trace_util.convert_gem5_simplessd(os.path.join(SimpleSSD_FullSystem_path, "m5out/traceForSimpleSSD.txt"), os.path.join(SimpleSSD_Standalone_path, "gem5_trace.txt"))

    # Run SimpleSSD on newly generated trace
    subprocess.run(["./simplessd-standalone", "./config/sample.cfg", "./simplessd/config/sample.cfg", "out/"], cwd=SimpleSSD_Standalone_path, check=True)

    # Check for convergence
    if not first:
        if filecmp.cmp(os.path.join(SimpleSSD_Standalone_path, "out/latency.csv"), os.path.join(SimpleSSD_Standalone_path, "out/prev_latency.csv")):
            print("Converged at iteration {}.".format(iteration))
            break

    # Increment and break upon reaching max iterations
    iteration += 1
    if iteration >= max_iterations:
        print("Did not converge. Max iterations ({}) reached".format(max_iterations))
        break

