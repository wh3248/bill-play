import os
import numpy as np
import struct

def main():
    run_id = "3ac91b62-106e-11ef-aab0-8a4bb6883123"
    run_id = "3f573cec-121a-11ef-b5d6-5a3e7dd68100"
    index = 10
    path = "runs/{run_id}/SLIM_SandTank_test_cgrid.{index:08d}.vtk".format(run_id=run_id, index=index)
    print(path)
    (point_results, cell1_results, cell2_results) = read_vtk(path)
    high = -1000
    low = 1000
    data = cell1_results
    for i in range(0, len(data)):
        v = data[i]
        high = max(high, v)
        low = min(low, v)
    print("LOW/HIGH", low, high)
    return
    run_id = "3ac91b62-106e-11ef-aab0-8a4bb6883123"
    for run_id in os.listdir("runs"):
        if not run_id == "." and not run_id == "..":
            print("*** RUNID",run_id)
            (low, high) = find_range(run_id)
            print(run_id, "Range", low, high)
    return

def find_range(run_id):
    low = 10000
    high = -1000
    for index in range(1, 11):
        path = "runs/{run_id}/SLIM_SandTank_test_cgrid.{index:08d}.vtk".format(run_id=run_id, index=index)
        (point_results, cell1_results, cell2_results) = read_vtk(path)
        #print(path)
        for i in range(0, cell1_results.size):
            v = cell1_results[i]
            low = min(low, v)
            high = max(high, v)
            break
        print(low, high)
    return (low, high)

def read_vtk(path):
    result = []
    point_results = []
    cell1_results = []
    cell2_results = []

    with open(path, "rb") as fp:
        contents = fp.read()
        position = 0
        nxyz = None
        for _ in range(0, 16):
            (line, position) = read_line(contents, position)
            parts = line.split(" ")
            print(line)
            if parts[0] == "DIMENSIONS":
                ixlim = int(parts[10])-1
                iylim = int(parts[22])-1
                izlim = int(parts[33])-1
                nxyzp1 = (ixlim + 1) * (iylim + 1) * (izlim + 1)
                nxyz = (ixlim) * (iylim) * (izlim)
            if parts[0] == "POINTS":
                if nxyz is None:
                    nxyz = int(parts[10])
                    nxyzp1 = int(parts[10])
                break
        (data, position) = read_float_array(contents, position, 3*nxyzp1)
        point_results = data
        for _ in range(0, 15):
            (line, position) = read_line(contents, position)
            print(line)
            parts = line.split(" ")
            if parts[0] == "LOOKUP_TABLE":
                break
        (data, position) = read_float_array(contents, position, nxyz)
        cell1_results = data
        result = data
        (data, position) = read_float_array(contents, position, nxyz)
        #print(data)
        cell2_results = data
        return (point_results, cell1_results, cell2_results)
    
def read_line(contents, position):
    result = ""
    while contents[position] != 10:
        result = result + chr(contents[position])
        position = position + 1
    if contents[position] == 10:
        position = position + 1
    return (result, position)

def read_float_array(contents, position, size):
    float_dt = np.dtype(np.float32)
    float_dt = float_dt.newbyteorder('>')
    float_bytes = 4
    result = []
    for i in range(0, size):
        [v] = struct.unpack(">f", contents[position:position + float_bytes])
        result.append(v)
        position = position + float_bytes
    return (result, position)
    value = np.frombuffer(contents[position:position + size*float_bytes], dtype=float_dt)
    position = position + float_bytes * size
    return (value, position)
main()
