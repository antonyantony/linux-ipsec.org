Title: 2026 TRex Testing (Frankfurt, 10-12 Feb)
Date: 2026-02-12
Summary: TRex Testing: A Quick Start on Ubuntu 24.04

## Overview
This guide provides a quick start for installing and testing TRex (Cisco's Traffic Generator) on Ubuntu 24.04 (Noble Numbat) LTS

## Prerequisites
Before installing TRex, ensure your system meets the following requirements:

- **Operating System:** Ubuntu 24.04 LTS
- **Python:** Python 3.12 (TRex v3.08 is tied to this version)
- **CPU:** Multi-core processor with NICs bound to the cores you are using
- **Network:** Tested with Mellanox ConnectX-5 or ConnectX-7
- **DOCA-OFED:** Must match your OS distribution — https://developer.nvidia.com/networking/doca

## Installation

### Installing Python 3.12
TRex v3.08 (current as of Feb 2026) requires Python 3.12, which is older than
what ships with Ubuntu 24.04.

Download the Python 3.12 source tarball:

`wget https://www.python.org/ftp/python/3.12.9/Python-3.12.9.tgz`

Extract it, run `configure`, and install.

```bash
tar -zxf Python-3.12.9.tgz
cd  Python-3.12.9
./configure --enable-optimizations
make -j 3 install
```

To always use Python 3.12 with TRex, create a virtual environment (one-time setup). After that, activate this venv every time you work with TRex.

Run this from `/root` or another persistent location:

```bash
apt install python3.12-venv
python3.12 -m venv venv
```

### Activating the Python 3.12 venv

Each time you log in to work with TRex, activate the venv first:

```bash
source /root/venv/bin/activate
# To verify:
type python3.12  # should show /root/venv/bin/python3.12
```

### Installing DOCA-OFED
For setups using Mellanox ConnectX NICs, DOCA-OFED is required to ensure proper driver and DPDK support. Configuration details are provided at the end of this document.

Navigate to the [DOCA downloads page](https://developer.nvidia.com/doca-downloads) and select the local package for your OS.

```bash
wget https://www.mellanox.com/downloads/DOCA/DOCA_v3.2.1/host/doca-host_3.2.1-044000-25.10-ubuntu2404_amd64.deb
dpkg -i doca-host_3.2.1-044000-25.10-ubuntu2404_amd64.deb
apt-get update
apt-get -y install doca-ofed
dkms autoinstall
mst start
mst status -v
```

### Installing TRex 3.08

```bash
wget --no-check-certificate --no-cache https://trex-tgn.cisco.com/trex/release/latest
mv latest trex-v3.08.tgz
tar xvf trex-v3.08.tgz
mv v3.08 /var/tmp/trex-v3.08  # you may need to chmod 777 first
cd /var/tmp/trex-v3.08/
rm  so/x86_64/libstdc++.so.6
sysctl -w vm.nr_hugepages=2048  # add this to /etc/sysctl.d to make it permanent.
chmod -R 777 /var/tmp/trex-v3.08/
```
At the time of writing, `latest` pointed to v3.08.

### Starting TRex Server
TRex is installed under `/var/tmp/trex-v3.08` on the sunset host. The server runs in the foreground, so start it inside a `screen` session — that way you can reattach later with `screen -x` to check its output.

Activate the venv first, then launch `screen` and start TRex inside it:

```bash
source /root/venv/bin/activate
screen bash
sysctl -w vm.nr_hugepages=2048
cd /var/tmp/trex-v3.08
./t-rex-64 -i --no-scapy --cfg /etc/trex_cfg.yaml -c 8
```

The server takes a few seconds to initialize.

### Running a TRex Test Script

From a second terminal (also inside the Python 3.12 venv), run one of the test scripts. For example:

```bash
cd /root/ietf-123-pcpu/tests-trex
./u1.py
./u1.py --src-ip 192.0.1.253 --dst-ip 192.0.2.253 --pps 1M --frame-size 1518 --flows 2 --duration 10 --flows-end 2 --runs 2
```

`u1.py` is a simple UDP sender/receiver that measures throughput and packet loss. It stores results in JSON, which are later processed with Pandas and plotted using Matplotlib.

## Appendix A: Mellanox DOCA-OFED Diagnostics
This section is only needed if you are troubleshooting your Mellanox NIC setup. If TRex starts and traffic flows, you can skip this.

After installing DOCA-OFED, run `mst start` once. To verify that your NICs are detected, check the output of `mst status -v`:
```
 mst status -v
MST modules:
------------
    MST PCI module is not loaded
    MST PCI configuration module loaded
    -E- Unknown argument "--v"
root@sunset:~/ietf-123-pcpu/tests-trex# mst status -v
MST modules:
------------
    MST PCI module is not loaded
    MST PCI configuration module loaded
PCI devices:
------------
DEVICE_TYPE             MST                           PCI       RDMA                                               NET                                     NUMA
ConnectX5(rev:0)        /dev/mst/mt4121_pciconf0.1    01:00.1   mlx5_1          net-redwest                             0

ConnectX5(rev:0)        /dev/mst/mt4121_pciconf0      01:00.0   mlx5_0          net-redeast                             0
```


## Appendix B: TRex scapy permission issue
```
./t-rex-64 -i -c 4 --cfg /etc/trex_cfg.yaml

    Error: current path is not readable by user "nobody" (starting at /root).
    Two possible solutions:

    1. (Recommended)
        Copy TRex to some public location (/tmp or /scratch, assuming it has proper permissions (chmod 777 etc.))

    2. (Not recommended)
        Change permissions of current path. (Starting from directory /root).
        chmod 777 /root -R

Could not start scapy daemon server, which is needed by GUI to create packets.
If you don't need it, use --no-scapy-server flag.
ERROR encountered while configuring TRex system
```


## Appendix C: TRex v3.08 MTU setting

Trex v3.08 seems to need larger mtu set on Mellanox CX cards. The OFED/DPDK should newer than 25.07.

```
./t-rex-64 -i --no-scapy
The ports are bound/configured.
Starting  TRex v3.08 please wait  ...
 set driver name net_mlx5
 driver capability  : TCP_UDP_OFFLOAD  TSO  LRO
 set dpdk queues mode to DROP_QUE_FILTER
 Number of ports found: 2
zmq publisher at: tcp://*:4500
mlx5_net: port 0 failed to set MTU to 65518
ETHDEV: Port0 dev_configure = -22
EAL: Error - exiting with code: 1
Cannot configure device: err=-22, port=0
```

```
ofed_info -s
OFED-internal-25.10-1.7.1:
```
workaround:
`port_mtu: 9000`

## Appendix D: Trex Config file

cat /etc/trex_cfg.yaml

```
- version         : 2
  port_limit      : 2
  interfaces:       ["02:00.0", "02:00.1"]

  platform:
    master_thread_id: 0
    latency_thread_id: 1
    dual_if:
      - socket: 0
        threads: [2,3,4,5,6,7]

  port_info       :  # Port IPs.
          - ip         : 192.0.1.250
            default_gw : 192.0.1.254
          - ip         : 192.0.2.250
            default_gw : 192.0.2.254
  port_mtu: 9000
```

## Appendix E: Trex with scapy
`pip install scapy` This may give you permission issues.

```
pip install scapy
Collecting scapy
  Downloading scapy-2.7.0-py3-none-any.whl.metadata (5.8 kB)
Downloading scapy-2.7.0-py3-none-any.whl (2.6 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.6/2.6 MB 19.1 MB/s eta 0:00:00
Installing collected packages: scapy
Successfully installed scapy-2.7.0
(venv-3.12-202260217) root@sun:/var/tmp/trex-v3.08# ./t-rex-64 -i
Starting Scapy server... Scapy server failed to run
Output: b'taskset: failed to execute /root/venv/bin/python3: Permission denied\n'
Could not start scapy daemon server, which is needed by GUI to create packets.
If you don't need it, use --no-scapy-server flag.
ERROR encountered while configuring TRex system
```

```
chmod 755 /root/venv/bin/python3
chmod 755 /root/venv/bin/python3.12
chmod 755 /root/venv/bin/python3
chmod 755 /root/venv/bin/python3.12

```
