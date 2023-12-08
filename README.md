# Redis + DICOM Demo  

## Contents
1.  [Summary](#summary)
2.  [Architecture-High](#arch-high)
3.  [Architecture-Low](#arch-low)
4.  [Features](#features)
5.  [Prerequisites](#prerequisites)
6.  [Installation](#installation)
7.  [Scenario 1](#scenario1)
8.  [Scenario 2](#scenario2)
9.  [Scenario 3](#scenario3)

## Summary <a name="summary"></a>
This is a Jupyter notebook that loads a DICOM data set into Redis.  A JSON object is used to hold DICOM meta data and array of keys for strings holding byte chunks of the DICOM file.  Those JSON objects can subsequently be indexed and searched against the DICOM meta data. The DICOM byte chunks are stored as Redis strings. 

## Architecture - High <a name="arch-high"></a>
![architecture](./images/Dicom_Arch_High.jpg)  

## Architecture - Low <a name="arch-low"></a>
![architecture](./images/Dicom_Arch_Low.jpg)  

## Features <a name="features"></a>
- Loads DICOM data from files to Redis JSON + strings
- Demonstrates fidelity of the Redis by restoring the files from the Redis string binaries.
- Demonstrates Search and Aggregation against the DICOM meta data 

## Prerequisites <a name="prerequisites"></a>
- Docker
- Python
- Jupyter

## Installation <a name="installation"></a>
1. Clone this repo.
2. Follow notebook steps

## Redis Insight Screenshots <a name="insight"></a>
Screenshot of an example JSON object containing DICOM meta-data + byte chunk keys
![insight-json](./images/insight_json.png)  

Screenshot of an example String containing a DICOM byte chunk
![insight-json](./images/insight_string.png) 

## Scenario 1 <a name="scenario1"></a>
Hypothetical Business Problem: Retrieve all the bytes of an image given a known file name
```bash
Exec time: 1.36 ms
Bytes Retrieved: 9844
```

## Scenario 2 <a name="scenario2"></a>
Hypothetical Business Problem: Find a DICOM image with the 'protocolName' of '194' and 'studyDate' in 2019.  Retrieve all file bytes.
```bash
Exec time: 7.64 ms
Image name: J2K_pixelrep_mismatch.dcm
Bytes Retrieved: 138518
```

## Scenario 3 <a name="scenario3"></a>
Hypothetical Business Problem: Find the count of DICOM images by protocol
```bash
Exec time: 1.77 ms
ANGIO Projected from C: 7
T/S/C RF FAST PILOT: 6
1.1 Routine Brain: 4
FAST LOCALIZER: 4
Whole Body Bone: 4
194: 1
```

## Speed Test <a name="speedtest"></a>
There is a Python asyncio app included for allowing scaled file retrievals.  The application allows for configuration of chunk sizes and number of Redis client connections.
### Example
```bash
python3 svs_speed_test.py --chunk_size 30 --connections 1000

*** File Retrieval Test - 30 KB Chunks, 1000 Client Connections ***
test.svs Size: 1579.72 MB
Files loaded: 1

Key: file:test.svs
Exec time: 7924.45 ms
Bytes Retrieved: 1656460030
File integrity check:  Pass

Total time: 7924.45 ms
```