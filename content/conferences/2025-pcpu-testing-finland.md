Title: 2025 Linux IPsec pCPU testing, (Madrid 20 - 26 July)
Date: 2025-08-15
Summary: Test performance improvements using pPCPU [RFC9611](https://www.rfc-editor.org/rfc/rfc9611.html) with the Linux Kernel and strongSwan pCPU implementation.

The testing started as part of IETF 123 Hackathon and continued since then.

## Test setup

<pre>
| sunset |-----| west |====| east |----| sunrise |
</pre>
### Test hosts : 4 hosts

- Supermicro H13SSW Motherboard
- AMD EPYC 9135 16-Core Processor
- NIC: Mellanox Technologies MT28800 ConnectX-5 Ex
- NIC: Broadcom BCM57508 NetXtreme-E (sunrise)

## Test Results

### TREX pCPU UDP Results (2025-07-28)

In this test west and and east are IPsec gateways and the sunset is running [TRex ](https://trex-tgn.cisco.com/trex/doc/ trex_appendix_mellanox.html) traffic generator. It will send on one port and while receving the traffic on the second port, on the same host.

![TREX pCPU UDP Results]({static}/images/20250728-trex-pcpu-udp.png)
*Figure: UDP performance with pCPU (2025-07-28)*

<pre>
 +------| sunset |--------+
 |                        |
 +--| west |====| east |--+
</pre>


### TREX Loop Test Results (2025-08-15)

This test uses a loopback (also called cross-connect) setup with only one host, sunset. It checks how fast the TRex traffic generator can send and receive data without involving Linux packet forwarding. The results show the maximum speed you can expect before adding IPsec gateways.

![TREX Loop Test Results]({static}/images/20250815-trex-loop-test.png)
*Figure: Loop test results (2025-08-15)*

<pre>
 +-----| sunset |-------+
 |                      |
 +----------------------+
</pre>

###  Linux contention in xfrm_state_find ()
This is a known limitation of the Linux XFRM (IPsec) implementation. We hope to resolve this issue and hope to fix the contention in a future update.
![Flamegraph xfrm_state_find]({static}/images/20250727-dcache_miss_flamegraph-xfrm_state_find.svg)
*Figure: Falmegraph xfrm_state_find

Look at the function xfrm_state_find(), [Flamegraph](https://www.brendangregg.com/FlameGraphs/cpuflamegraphs.html)
