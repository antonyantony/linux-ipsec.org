Title: 2026 TRex  and iperf Testing (Dresden, 19 March)
Date: 2026-03-19
Author: Antony Antony
Summary: TRex and iperf3 Testing: Quick comparison 1500 vs 9000 bytes MTU

## Overview

Performance benchmarks for an IPsec gateway configured with a single Security
Association (SA), tested using iperf, gateway to gateway, Trex as forwarding.

- **TRex** — stateless UDP traffic generator, measuring forwarding throughput
  in Gibps across a range of requested packet rates (pps)
- **iperf3** — measuring TCP and UDP send/receive throughput across a range of
  target bandwidths

Tests were conducted with two MTU sizes: **1500** and **9000** bytes, with 5
repeated runs, each 10 seconds duration, per data point to assess consistency.

## Test Setup

Two different topologies are used depending on the traffic generator.

### iperf3 topology

*west* and *east* are connected back-to-back using Mellanox ConnectX-7 NICs.
iperf3 runs on both hosts directly.

```
west ──────────────────── east
      Mellanox ConnectX-7
       (direct cable)
```

### TRex topology

*sun* is the TRex traffic generator with two ports, one connected to *west*
and one connected to *east*. Traffic enters the IPsec gateway on *west*,
traverses the IPsec tunnel, and exits on *east* back to *sun*.

```
                 ┌─────────────────────┐
                 │         DUT         │
                 │   west ══════ east  │
                 │    (IPsec tunnel)   │
                 └──────┬─────────┬─-──┘
                        │         │
                   port0 │         │ port1
                        └────┬────┘
                             │
                          sun (TRex)
```

A single IPsec SA pair is used throughout all tests.

## TRex UDP Forwarding Results

TRex sends UDP traffic at a fixed requested rate (`tx_pps_req`) and measures
actual forwarded throughput (`fwd_tx_throughput_gibps`) and received throughput
(`fwd_rx_throughput_gibps`) after the IPsec gateway. Each point shows the best
and average of 5 runs.

### MTU 1500

| pps_req | best TX (Gibps) | best RX (Gibps) | avg TX (Gibps) | avg RX (Gibps) |
|--------:|----------------:|----------------:|---------------:|---------------:|
|   270K  |           2.995 |           2.878 |          2.986 |          2.890 |
|   280K  |           3.107 |           2.959 |          3.095 |          2.984 |
|   300K  |           3.318 |           3.176 |          3.314 |          3.216 |
|   310K  |           3.429 |           3.340 |          3.426 |          3.342 |
|   320K  |           3.542 |           3.425 |          3.537 |          3.440 |

![TRex MTU 1500 — best and average TX/RX throughput]({static}/images/20260319-trex-bars-1500.png)

Results are very consistent across runs — best vs average difference is under
0.015 Gibps — indicating stable forwarding with a single SA at MTU 1500.
TX throughput slightly exceeds RX, reflecting a small amount of packet loss
through the gateway.

### MTU 9000 (Jumbo Frames)

| pps_req | best TX (Gibps) | best RX (Gibps) | avg TX (Gibps) | avg RX (Gibps) |
|--------:|----------------:|----------------:|---------------:|---------------:|
|   170K  |          11.389 |          11.342 |         11.367 |         11.354 |
|   180K  |          12.078 |          12.028 |         12.050 |         12.001 |
|   200K  |          13.385 |          13.116 |         13.373 |         13.084 |
|   210K  |          14.042 |          13.115 |         14.038 |         13.125 |
|   220K  |          14.731 |          13.213 |         14.716 |         11.015 |

![TRex MTU 9000 — best and average TX/RX throughput]({static}/images/20260319-trex-bars-9000.png)

With jumbo frames the gateway reaches over 14 Gibps TX at 220K pps. However,
the RX average at 220K drops to 11.015 Gibps (best: 13.213 Gibps), indicating
significant and inconsistent packet loss at the highest load. The 220K pps
point is near the saturation limit for this configuration.

## iperf3 TCP and UDP Results

iperf3 tests vary the target send bandwidth with 5 runs per point.
Plots show TCP and UDP sent/received throughput for best and average runs.

### MTU 1500

![iperf3 MTU 1500 — best and average throughput]({static}/images/20260319-iperf-bw-mtu1500.png)

- **TCP** throughput saturates around 4.5 Gbps regardless of the target
  bandwidth, reflecting the single-SA single-CPU limit at this MTU.
- **UDP sent** keeps climbing toward the target, but **UDP received** drops off
  at higher loads, indicating increasing packet loss beyond a ~5–6 Gbps target.

### MTU 9000 (Jumbo Frames)

![iperf3 MTU 9000 — best and average throughput]({static}/images/20260319-iperf-bw-mtu9000.png)

With MTU 9000, TCP scales well with the target bandwidth, reaching up to
~17 Gbps before becoming inconsistent. The average degrades from 13 Gbps
target onwards, suggesting the single-SA forwarding limit is being reached.
UDP with MTU 9000 shows a large gap between sent and received — sent climbs
freely but received saturates around 9–10 Gbps, indicating significant packet
loss at higher rates.

#### iperf3 TCP MTU 9000 — numbers

| target | best TX (Gbps) | best RX (Gbps) | avg TX (Gbps) | avg RX (Gbps) |
|-------:|---------------:|---------------:|--------------:|--------------:|
|    8G  |          8.000 |          7.999 |         7.999 |         7.998 |
|    9G  |          9.000 |          8.999 |         8.999 |         8.998 |
|   10G  |         10.000 |         10.000 |         9.999 |         9.999 |
|   11G  |         11.000 |         10.998 |        10.997 |        10.996 |
|   12G  |         12.000 |         12.000 |        11.998 |        11.997 |
|   13G  |         12.999 |         12.999 |        12.541 |        12.540 |
|   14G  |         13.999 |         13.998 |        13.333 |        13.331 |
|   15G  |         15.000 |         14.999 |        14.186 |        14.185 |
|   16G  |         15.999 |         15.999 |        14.120 |        14.119 |
|   17G  |         16.999 |         16.999 |        16.254 |        16.253 |
|   18G  |         13.600 |         13.600 |        13.099 |        13.098 |
|   19G  |         17.379 |         17.378 |        14.112 |        14.112 |
|   20G  |         16.660 |         16.656 |        15.179 |        15.177 |

#### iperf3 UDP MTU 9000 — numbers

| target | best TX (Gbps) | best RX (Gbps) | avg TX (Gbps) | avg RX (Gbps) |
|-------:|---------------:|---------------:|--------------:|--------------:|
|    8G  |          7.466 |          6.706 |         4.239 |         3.733 |
|    9G  |          8.999 |          7.300 |         5.709 |         4.817 |
|   10G  |          9.999 |          7.476 |         6.170 |         4.632 |
|   11G  |         11.000 |          7.201 |         5.983 |         4.210 |
|   12G  |         11.999 |          8.569 |        10.555 |         7.376 |
|   13G  |         13.000 |          8.773 |         8.165 |         5.538 |
|   14G  |         13.999 |          9.019 |        13.932 |         9.022 |
|   15G  |         14.992 |          9.245 |        14.857 |         9.187 |
|   16G  |         15.755 |          9.333 |        15.021 |         9.140 |
|   17G  |         15.910 |          9.338 |        15.053 |         9.175 |
|   18G  |         17.977 |         10.374 |        16.628 |         9.844 |
|   19G  |         17.787 |         10.137 |        16.285 |         9.595 |
|   20G  |         19.998 |         10.269 |        15.167 |         8.201 |

UDP RX saturates around 9–10 Gbps regardless of how high the sender pushes,
confirming the single-SA forwarding limit for UDP at MTU 9000.

## Summary

| Test      | MTU  | Peak RX (best)  | Notes                              |
|-----------|------|-----------------|------------------------------------|
| TRex UDP  | 1500 |     3.42 Gibps  | Stable, < 0.02 Gibps variance      |
| TRex UDP  | 9000 |    13.21 Gibps  | Loss starts at 220K pps            |
| iperf TCP | 1500 |     ~4.5 Gbps   | CPU-bound saturation               |
| iperf UDP | 1500 |     ~5.5 Gbps   | Loss above 6 Gbps target           |
| iperf TCP | 9000 |    ~17.4 Gbps   | Inconsistent above 13 Gbps target  |
| iperf UDP | 9000 |    ~10.4 Gbps   | RX saturates ~9–10 Gbps            |

With a single SA, all IPsec processing is handled by one CPU.
Jumbo frames (MTU 9000) substantially improve throughput by reducing per-packet
overhead, but the single-SA single-CPU bottleneck remains the limiting factor.

## Test Notes

Packet captures and test commands recorded during the test session:

```
9000 MTU UDP test
06:03:55.677864 IP 192.1.2.45 > 192.1.2.23: ESP(spi=0xcdfb55ce,seq=0xd6a4), length 8956
06:03:55.677869 IP 192.1.2.45 > 192.1.2.23: ESP(spi=0xcdfb55ce,seq=0xd6a5), length 8956
06:03:55.677876 IP 192.1.2.45 > 192.1.2.23: ESP(spi=0xcdfb55ce,seq=0xd6a6), length 8956

NO ESP fragment
Neither CPUs are 100%

MTU 1500 UDP
06:32:01.137179 IP 192.1.2.45 > 192.1.2.23: ESP(spi=0xcd9ae971,seq=0x10de0), length 1456
06:32:01.137181 IP 192.1.2.45 > 192.1.2.23: ESP(spi=0xcd9ae971,seq=0x10de1), length 1456
06:32:01.137183 IP 192.1.2.45 > 192.1.2.23: ESP(spi=0xcd9ae971,seq=0x10de2), length 1456
06:32:01.137185 IP 192.1.2.45 > 192.1.2.23: ESP(spi=0xcd9ae971,seq=0x10de3), length 1456

with tcp
06:55:05.916940 IP 192.1.2.45 > 192.1.2.23: ESP(spi=0xc129b223,seq=0x23a), length 1480
06:55:05.916945 IP 192.1.2.45 > 192.1.2.23: ESP(spi=0xc129b223,seq=0x23b), length 1480
06:55:05.916937 IP 192.0.2.254.5201 > 192.0.1.254.55136: Flags [.], ack 3507262502, win 31043, options [nop,nop,TS val 3598111131 ecr 1625372311], length 0
06:55:05.916948 IP 192.1.2.45 > 192.1.2.23: ESP(spi=0xc129b223,seq=0x23c), length 1480
06:55:05.916952 IP 192.1.2.45 > 192.1.2.23: ESP(spi=0xc129b223,seq=0x23d), length 1480
06:55:05.916955 IP 192.1.2.45 > 192.1.2.23: ESP(spi=0xc129b223,seq=0x23e), length 1480
06:55:05.916957 IP 192.1.2.45 > 192.1.2.23: ESP(spi=0xc129b223,seq=0x23f), length 1480
06:55:05.916960 IP 192.1.2.45 > 192.1.2.23: ESP(spi=0xc129b223,seq=0x240), length 1480

Trex UDP 1500
./u1.py --pps 0.27M --pps 0.28M  --pps 0.3M --pps 0.31M --pps 0.32M  --frame-size 1460 --duration 10 --results-file $SUBDIR/trex-1500.json

07:14:42.153127 10:70:fd:87:53:30 > 10:70:fd:87:52:f0, ethertype IPv4 (0x0800), length 1514: 192.1.2.45 > 192.1.2.23: ESP(spi=0xca8130f4,seq=0x35e83), length 1480
07:14:42.153129 10:70:fd:87:53:30 > 10:70:fd:87:52:f0, ethertype IPv4 (0x0800), length 1514: 192.1.2.45 > 192.1.2.23: ESP(spi=0xca8130f4,seq=0x35e84), length 1480
07:14:42.153131 10:70:fd:87:53:30 > 10:70:fd:87:52:f0, ethertype IPv4 (0x0800), length 1514: 192.1.2.45 > 192.1.2.23: ESP(spi=0xca8130f4,seq=0x35e85), length 1480
07:14:42.153136 10:70:fd:87:53:30 > 10:70:fd:87:52:f0, ethertype IPv4 (0x0800), length 1514: 192.1.2.45 > 192.1.2.23: ESP(spi=0xca8130f4,seq=0x35e86), length 1480
07:14:42.153137 10:70:fd:87:53:30 > 10:70:fd:87:52:f0, ethertype IPv4 (0x0800), length 1514: 192.1.2.45 > 192.1.2.23: ESP(spi=0xca8130f4,seq=0x35e87), length 1480

iperf command line used
iperf3 -i 2 -c 192.0.2.254 $UDP -b $TP -t ${D} --json > ${PROTO}-${MTU}-${TP}-${i}.json;

```
