Title: 2025 Linux IPsec pCPU testing, (Finland 20 - 26 July)
Date: 2025-08-15
Summary: Test performance improvements using pPCPU [RFC9611](https://www.rfc-editor.org/rfc/rfc9611.html) with the Linux Kernel and strongSwan pCPU implementation.

The testing started as part of IETF 123 Hackathon and continued since then.

## Test setup

The initial test setup have four hosts or servers. Here, *west* and *east* function as IPsec gateways, also known as black servers. Meanwhile, *sunseti* and *sunrise* act as traffic generators or receivers, referred to as red servers.

<pre>
| sunset |-----| west |====| east |----| sunrise |
</pre>

Figure: Initial topology

### Test hosts specification : 4 hosts

- Supermicro H13SSW Motherboard
- AMD EPYC 9135 16-Core Processor (a.k.a. Bergamo, or Zen 5)
- NIC: Mellanox MT28800 ConnectX-5 Ex (100Gbps NIc)
- NIC: Broadcom BCM57508 NetXtreme-E (only on sunrise, 100Gbps NIc)

## Test Results

### TREX pCPU UDP Results (2025-07-28)

In this test, west and east are IPsec gateways, and sunset is running [TRex](https://trex-tgn.cisco.com/trex/doc/trex_appendix_mellanox.html) traffic generator. It sends on one port while receiving the traffic on the second port, on the same host.

![TREX pCPU UDP Results]({static}/images/20250728-trex-pcpu-udp.png)
*Figure: UDP performance with pCPU (2025-07-28)*

Each flow is 3.3Gbps. The [TRex](https://trex-tgn.cisco.com) on sunset sends the traffic to west, which is an IPsec gateway that encrypts the traffic and forwards it to the second IPsec gateway, east. East decrypts the IPsec and sends it back to sunset. Sunset receives it on the second interface. The results clearly show total IPsec throughput increases linearly with the number of flows. Each flow is pinned to each CPU. Adding CPU increases the IPsec throughput as expected in [RFC9611](https://www.rfc-editor.org/rfc/rfc9611.html).

<pre>
 +-<<<---| sunset |-------+
 |                        |
 +--| west |====| east |--+
</pre>
Figure: TRex IPsec test topology


### TREX Loop Test Results (2025-08-15)

This test uses a loopback (also called cross-connect) setup with only one host, sunset. It checks how fast the [TRex](https://trex-tgn.cisco.com) traffic generator can send and receive data without involving Linux packet forwarding. The results show the maximum speed you can expect before adding IPsec gateways.

![TREX Loop Test Results]({static}/images/20250815-trex-loop-test.png)
*Figure: Loop test results (2025-08-15)*

<pre>
 +--<<<---| sunset |-------+
 |                         |
 +-------------------------+
</pre>
Figure: TRex loopback test topology

## Future work: Linux contention analysis
We use the Linux profiling tool [perf](https://perfwiki.github.io/main) to identify contention points. The following examples from IPsec sender.

### [xfrm_state_find()]({static}/images/20250727-dcache_miss_flamegraph-xfrm_state_find.svg?x=405.3&y=341) contention.

When using pCPU i.e. multiple CPU looking up state, even with states cached on policy there is CPU contention. You can see this in perf output as well as in Flamegrah clearly.
This is a known limitation of the Linux XFRM (IPsec) implementation. We hope to resolve this issue and hope to fix the contention in a future update.
![Flamegraph xfrm_state_find()]({static}/images/20250727-dcache_miss_flamegraph-xfrm_state_find.svg)
*Figure: Falmegraph xfrm_state_find*

The function [xfrm_state_find()]({static}/images/20250727-dcache_miss_flamegraph-xfrm_state_find.svg?x=405.3&y=341). For more details on Flamegraphs, refer to [Brendan Gregg's page](https://www.brendangregg.com/FlameGraphs/cpuflamegraphs.html). Is called on each sending cpu on 

### [_raw_spin_lock_bh()]({static}/images/20250727-dcache_miss_flamegraph-xfrm_state_find.svg?x=543.5&y=373) contention. 

This contention appears on sending side and _raw_spin_lock_bh() called in transmit path. 

#### Example of perf commandline.
This records perf counters on CPU 1, which we identified as sending CPU on west.
<pre>
perf record -b -e cycles,L1-dcache-load-misses,L1-icache-load-misses:k -g -C 5 --call-graph dwarf
perf report -g
</pre>

## Scripts to Tune the System

- [set-irq-affinity.sh]({static}/202507-madrid-pcpu-testing/set-irq-affinity.sh)
   This script optimizes packet processing by preventing `skb_free` from being handled by a different CPU when using a Mellanox ConnectX NIC. By configuring RSS (Receive Side Scaling), it ensures that the same CPU manages  both packet processing and freeing, particularly enhancing performance when pCPU affinity is enabled, and multiple CPUs are in use. Execute this script on each network interface, for red and black interface.

- [Flow pinning on black interface]({static}/202507-madrid-pcpu-testing/west/west-black.sh)
   Use this script to pin ESP-in-UDP traffic flows across different CPUs on a Linux system, based on UDP soruce port.. Run this script on the IPsec gateway ,east and west, black NICs.

- [Flow pinning on red interface]({static}/202507-madrid-pcpu-testing/west/west-red-udp.sh)
   This script is intended to distribute red traffic across several CPUs, allowing efficient pCPU utilization for sending. It should be run on the IPsec gateway, specifically on the west in your scenario. For bi-directional traffic, execute this on both IPsec gateways for the black interface.

## For future work
Ensure CPUs used for networking, IPsec data path, are isolated from general-purpose tasks (`isolcpus` kernel boot option). - Use high-resolution network and CPU measurements (`nstat`, `mpstat -P ALL 1`, etc.).  Monitor for dropped packets and IRQ balancing using `ethtool -S` and `irqbalance` status.

### check if Ethernet is pausing.
<pre>
ethtool --include-statistics -a  black
Pause parameters for black:
Autonegotiate:	off
RX:		on
TX:		on
Statistics:
  tx_pause_frames: 0
  rx_pause_frames: 10542401
</pre>
