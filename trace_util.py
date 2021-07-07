# File:      trace_util.py
# Author:    Edward Hanson (eth20@duke.edu)
# Desc:      Utility functions to inject and extract traces from SimpleSSD

import math

def convert_gem5_simplessd(fin_path, fout_path):
    fin = open(fin_path, "r")

    simplessd_trace = ""
    for line in fin:
        line = line.split(":")
        tick = int(line[0])
        rw = line[2].strip()
        block_addr = int(line[3])
        size = int(line[4])

        time = float(tick / 1000000000)
        nanoseconds, seconds = math.modf(time)
        nanoseconds = int(nanoseconds * 1e9)
        seconds = int(seconds)

        simplessd_trace += "0,0 0 0 {}.{} 0 D {} {} + {}\n".format(seconds, nanoseconds, rw, block_addr, 4)

    fin.close()
    fout = open(fout_path, "w")
    fout.write(simplessd_trace)
    fout.close()
        
def extract_trace(file_path):
    f = open(file_path, "r")

    # reported in ps
    times = []
    latencies = []
    instructions = []
    locations = []
    
    for line in f:
        line = line.split()

        time = int(line[0][:-1])
        source = line[1][:-1]
        
        # ignore setup, warning, and info lines
        if time == 0 or "warn" in source or "info" in source:
            continue

        if "(" in line[-1] and ")" in line[-1]:
            times.append(time)
            latencies.append(int(line[-1][1:-1]))
            instructions.append(line[2])
            locations.append(source)
            print("{}: {} | {} | {}".format(time, source, line[2], int(line[-1][1:-1])))
            continue

def extract_latency_trace(file_path):
    f = open(file_path, "r")

    # reported in ps
    ids = []
    offsets = []
    lengths = []
    latencies = []

    for line in f:
        line = line.split(',')
        ids.append(int(line[0]))
        offsets.append(int(line[1]))
        lengths.append(int(line[2]))
        latencies.append(int(line[3]))

    print(latencies)
        
def main():
    convert_gem5_simplessd(fin_path="/root/hostCurUser/SimpleSSD-FullSystem/m5out/traceForSimpleSSD.txt", fout_path="gem5_trace.txt")
    #extract_trace("out/debug.txt")
    #extract_latency_trace("out/latency.csv")
    
if __name__ == "__main__":
    main()
