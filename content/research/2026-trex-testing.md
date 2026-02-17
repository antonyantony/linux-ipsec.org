Title: 2026 TRex Testing (Frankfurt, 10-12 Feb)
Date: 2026-02-12
Summary: TRex Testing: A Quick Start on Ubuntu 24.04

## Overview
This guide provides a quick start for installing and testing TRex (Cisco's Traffic Generator) on Ubuntu 24.04 (Noble Numbat) LTS

### Prerequisites
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
python3.12 -m venv venv
```

### Activating the Python 3.12 venv

Each time you log in to work with TRex, activate the venv first:

```bash
source /root/venv/bin/activate
# To verify:
type python3.12  # should show /root/venv/bin/python3.12
```

## Installing DOCA-OFED
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

If v3.2.1 is not available for your setup, an earlier release also works:

```bash
wget https://www.mellanox.com/downloads/DOCA/DOCA_v3.0.0/host/doca-host_3.0.0-058000-25.04-ubuntu2504_amd64.deb
dpkg -i doca-host_3.0.0-058000-25.04-ubuntu2504_amd64.deb
apt update
apt -y install doca-ofed
dkms autoinstall
mst start
mst status -v
```

### Downloading TRex

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

## Starting TRex Server
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


## Appendix B: TRex permission issue
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


