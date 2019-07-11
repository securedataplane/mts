# Provisioning an MTS System

To set-up a secure virtual switch system or reproduce the results of the ATC'19 paper we have uploaded 2 (libvirt) VMs that can be downloaded and installed on your test server.

## Hardware Requirements

To deploy MTS, the server needs to support the following:

1. CPU type: INTEL Haswell Based processors or higher
2. PCIe Bus speed: 8GT/s; Gen3 PCIe
3. Processor bus speed: up to 9.60 GT/s
4. Memory Type: DDR3/DDR4
5. PCIe slots: At least One Half length/full height/double width/x8 slot
6. Support for PCI-SIG Single Root I/O Virtualization (SR-IOV)
7. Support for Vt-D or generically “Virtualization Technology”
8. Support for ARI or Alternative Routing-ID Interpretation

In addition the BIOS should have the following features:
1. ARI Support
2. Memory and I/O virtualization Enable
3. SR-IOV Support
4. Vt-D Support

## Our System Configuration

We had a total of four servers with the below configuration. However two servers had an 8 core Intel(R) Xeon(R) CPU E5-2609 instead of the 16 core Intel(R) Xeon(R) CPU E5-2683. The systems with the 8 cores were used for packet generation, packet collection, data storage and data visualization. The 16 core servers ran MTS.

### Supermicro SuperServer 5018R-WR

 1. Single socket R3 (LGA 2011) Intel(R) Xeon(R) CPU E5-2683 v4 @ 2.10GHz C612 chipset
 2. 4x 3.5" Hot-swap SATA3 drive bays
 3. 1x Slim DVD-ROM drive bay
 4. 64 GB DDR4 RAM
 5. 2x PCI-E 3.0 x16 FHFL, 1x PCI-E 3.0 x8 LPHL (3x AOC slots total)
 6. Intel® i350-AM2 Dual port GbE LAN
 7. Integrated IPMI 2.0 and KVM with Dedicated LAN
 8. I/O ports: 1x VGA, 2x COM, 2x USB 3.0, 2x USB 2.0
 9. 500W Redundant Power Supplies Platinum Level (94%+)
 10. CPU Heatsink #SNK-P0047PS
 11. Riser Card RSC-R1UW-2E16
 12. Riser Card RSC-R1UW-E8R
 13. 2x PCI-E 3.0 x16 FHFL, 1x PCI-E 3.0 x8 LPHL
 14. 3x AOC slots total
 15. Toshiba Enterprise HDD 1TB 3,5" SATA3 7200rpm, 64MB Cache, SATA3 6Gbps

### Network Cards

For our secure architecture, we experimented with network cards from Netronome, SolarFlare and Mellanox. All of them were dual port 10 Gbps SFP+ NICs.

- Netronome
- Solarflare SFN8522 Dual Port 10GbE
- Mellanox MCX4121A-XCAT dual-port SFP+ (ConnectX-4 Lx EN) 10GbE dual-port SFP+

The card that finally worked for all security levels was the Mellanox ConnectX-4 NIC, which is what we used for the measurements. The SolarFlare NIC did not support running OvS-DPDK on the VFs in the vswitch-vm and using the VFs of the Netronome NIC was not straightforward due to the several modes in operates in.

We used the MLNX_OFED_LINUX-4.3-1.0.1.0-ubuntu16.04-x86_64.iso driver for the Mellanox NIC.

### Operating System

A standard Ubuntu 16.04.4 LTS server OS was installed with a Linux kernel version 4.4.0-116-generic.

### Fine-Tuning

We had to tune the system for network performance as a default system does not have high throughput. Here's what we did:

- Disabled HyperThreading in the BIOS
- Grub file customization
	- Isolated CPUs for the Host OS via the isolcpus cmdline parameter
	- 1 GB huge pages
	- Enabled IOMMU and PassThrough

## VMs

We used two types of VMs which ran the same OS and CPU topology of the Host.

 - Virtual switch VM (vswitch-vm)
	 - The VM that runs the virtual switch, in this case Open vSwitch (OvS).
 - Tenant VM (tenant-vm)
	 - The VM that runs the workload, e.g., DPDK l2fwd, apache's webserver or memcached's key-value store.

The VMs can be downloaded at the following URL:

 - https://tubcloud.tu-berlin.de/s/saRTeBAamso7wfm

The credential for the VMs are the following:

 - vswitch-vm
	 - username: dahme
	 - password: securedataplane
 - tenant-vm
	 - username: tenant
	 - password: securedataplane

Place your public key in the authorized_keys file to login without the password via ssh.

The VMs can be cloned to create multiple similar vswitch-vms and tenant-vms.

By default huge pages and IOMMU are not enabled in these VMs. They can be configured by copying the 1gb huge page file from `~/grubFiles/` to `/etc/default/grub` and then rebooting the VM. Note that the Host OS also needs to have IOMMU enabled for this.

### vswitch-vm
We used OvS as the virtual switch and that can be found in `/usr/local/src/openvswitch-2.9.0` and a dpdk compiled version in `/usr/local/src/ovs-dpdk/openvswitch-2.9.0/`. By default the 