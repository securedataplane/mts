# Securing the Virtual Switch

Following up on the security analysis of Cloud Systems based on Software Defined Networking and of Virtual Switches [1] [2], this repository hosts the 
example implementation of a more secure architecture as proposed by Thimmaraju et al. [3].

## Software Stack
The framework was developed in Python (2) and uses the following technologies:
- Open vSwitch
- SR-IOV
- DPDK 
- libvirt with QEMU
- docker

Currently Mellanox and Solarflare NICs are supported with Mellanox being the more thoroughly tested one.

## The Framework
This code provides means to configure and test different kinds of setups and scenarios. 
Underlying computing and networking resources are automatically managed by this framework. It is composed of the following main components:
- **OvS Utilities:** Set of functions that enable the configuration of OvS. For example, it is used to start/stop OvS, add/delete OvS-bridges or to set flow rules.
- **SR-IOV Utilities:** Enables the configuration of an SR-IOV NIC. For the moment, only Solarflare and Mellanox NICs are supported. It provides utilities to enable/disable SR-IOV, bind/unbind VFs, parse the NIC configuration, etc. 
- **Libvirt Utilities:** Set of functions to manage the guest VMs and the underlying physical resources such as CPU, RAM, and the NIC. For example, it provides functions to start/shutdown VMs, attach/detach VFs, allocate RAM and CPU to guest VMs.
- **Networking Toolkit:** Set of functions offering general-purpose networking operations, e.g bringing interfaces up/down, configuring VLANs, changing the MTU size.

On top of these, a scenario generator provides a pre-defined structure to build and test different designs.
Scenarios may be composed of a combination of the following attributes:
- Mode
    - Baseline: vSwitch running on bare metal, co-located with the host kernel
    - SR-IOV: vSwitch running in a VM, NIC resources shared and isolated on a virtual environment
- Setup
    - FourTenant: 
        - Static number of four tenants and according number of flow rules
        - distributed between 1, 2 or 4 vSwitch instances, each running in a separate VM
        - VFs are assigned in such a way that packets generated for testing can be reused for different Packet Flow Modes (see below) with the same number of OvS instances 
    - Container:
        - testing scalability (different levels of compartmentalization, one-to-one mapping of vSwitches and VMs not longer necessary)
        - vSwitch running in a container inside a VM 
        - number of vSwitch instances, VMs and tenants are dynamically configurable (at the moment limited by number of PCIe devices attachable to a QEMU VM and by the number of possible VFs)
        - in p2v and v2v settings only one respectively two tenant VMs with multiple l2fwd sessions are used
        - v2v implementation untested, DPDK mode not implemented yet
- Packet Flow Topology
    - physical to physical: another machine sends packets to vSwitch host -> vSwitch host NIC IN -> vSwitch flow rules match packets, adjust MAC -> vSwitch host NIC OUT -> back to physical host
    - physical to VM: physical host -> vSwitch host NIC IN -> vSwitch -> VM -> vSwitch -> vSwitch host NIC OUT -> physical
    - VM to VM: physical -> vSwitch host NIC IN -> vSwitch -> VM 1 -> vSwitch -> VM 2 -> vSwitch -> vSwitch host NIC OUT -> physical
- DPDK: enable userland switching
- Isolated CPU: One CPU per VM/vSwitch instance (as opposed to a shared core for the VMs)


## Step-By-Step Overview

The following provides an overview of which steps are necessary to run the framework scripts and what they do.
To begin with, _latency_FourTenants_Measurement.py_ is used as an example. As the framework is highly fine-tuned to our infrastructure setup, additional changes may become necessary.

- Manual Preparation
    - initial infrastructure setup (for a detailed guide, see _provisioning_)
        - setup and install libvirt and QEMU
        - configure SR-IOV on your host
        - download preprovisioned qcow2 images, providing
            - multiple OvS installations for DPDK/no-DPDK
            - dockered OvS versions
            - preconfigured l2fwd DPDK applications for tenant VMs (MAC addresses need to be adjusted)
    - adjust hardcoded values
        - server IP addresses (and possibly variable names): expLib:38
        - VM IP addresses: expLib:46
        - possibly connection arrays: expLib:93
        - interface names in scenario subroutines: e.g. FourTenantLib:189
        - OvS paths if custom VM images are being used: expLib:138
        - possibly l2fwd application paths for tenant VMs: expLib:1495
        - Destination MAC (of physical host sending packets): ContainerLib:6, FourTenantLib:14
        - number of total cores and cores to be used for l2 forwarding (important for high tenant number setups in container mode): expLib:20, ContainerLib:8, FourTenantLib:26
    - define the scenarios to be tested by adjusting the _topologies_ and _vswitchModes_ lists (throughput_FourTenantLib_Measurement:193)
    - create own pcap files to replay during measurements or adjust MAC addresses in provided pcaps
- the script will then iterate over the configured topologies, vSwitch modes and CPU isolation modes, performing the following steps in each run:
    - call _prepTestbed.prepTestbed()_ with the current configuration
        - starts corresponding subroutine defined in FourTenantLib to prepare the server:
            - starts VMs
            - configures SR-IOV
                - allocating Virtual Functions
                - setting MTU and interrupt moderation
                - assigning VLANs
            - attaches interfaces to VMs
            - starts vSwitches in VMs 
            - configures flow rules
            - in p2v and v2v settings: starts l2fwd applications on tenant VMs
    - initiate measurement in _latency()_
        - **Action required**: configure packet sizes, throughput, host and interface names: latency_FourTenants_Measurement:37
        - prepares traffic files
        - starts packet capturing on TX and RX interfaces
        - starts transmission and stops traffic capturing upon completion
        - computes per packet latency from timestamped packets
        - generates latency plots
    - send results per email



## How to Create a New Scenario

Implementing a new scenario or automating the setup of a user-defined test can be done by using the framework components exposed by expLib (for an example, have a look at ContainerLib).

In general, the following points may become important:
- use expLib.cpuAllocation() to create a resource config array for later use or handle resource allocation otherwise
- use expLib.InitialConfig() to reset the machine's state (set grub config, reboot, clear interfaces, unbind and reconfigure VFs)
- fill in expLib.NicConfig and expLib.PhyPorts with the number of necessary Virtual Functions and used interfaces for SR-IOV
- expLib.MyVfs: array with entries (exp.pfs[i][2][x], VLAN, SPOOFCHECK_BOOL, VM) with i being the index of the interface, x the index of the VF to be used
- call expLib.Vfsconfig() to configure the VFs specified in MyVfs
- use expLib.RunCommand to execute commands on hosts/VMs and to setup/adjust the environment to your needs (for how to address multiple vSwitch instances in containers have a look at e.g. expLib.StartOVS). Or use/ extend readily available auxiliary functions such as:
    - CleanOVSDB
    - AddBridge
    - addFlowRule
    - SetPort
- add cases for your newly defined scenarios to _prepTestbed.py_.


#
## Publications
[1] _Taking Control of SDN-based Cloud Systems via the Data Plane_, Kashyap Thimmaraju, Bhargava Shastry, Tobias Fiebig, Felicitas Hetzelt, Jean-Pierre Seifert, Anja Feldmann and Stefan Schmid. In proc. ACM Symposium on SDN Research, Los Angeles, California, USA, March, 2018.

[2] _Virtual Network Isolation: Are We There Yet?_, Kashyap Thimmaraju, Gábor Rétvári and Stefan Schmid. To appear in the. ACM SIGCOMM 2018 Workshop on Security in Softwarized Networks: Prospects and Challenges (SecSoN 2018), Budapest, Hungary, Aug, 2018. 

[3] _MTS: Bringing Multi-Tenancy to Virtual Networking_, Kashyap Thimmaraju, Saad Hermak, Gabor Retvari and Stefan Schmid. In proc. USENIX Annual Technical Conference '19, Renton, Washington, USA, July, 2019.