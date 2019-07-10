import expLib as exp
from datetime import datetime


DpdkMem = "1024,0"
outDestMac = "00:00:00:00:30:56"
VmRam = "4G" 
totalTenantVMs = 2
totalCpuCores = 16
l2fwdCpuCores = 8
InitMessage = "The scenario is getting prepared ..."


def phy2phy_SRIOV_Dynamic_Container(cnx_server, isDPDK, nbrCores, isIsolated=False, numVMs=1, numCont=1, numTenants=4):
    # sanity checks
    if numVMs > 4:
        print("[ERROR] Currently, only 4 VM instances are available.")
        return False
    elif numCont > 64 // 3:
        print("[ERROR] The maximum number of configurable containers is 21 as the PF's totalvfs is 64.") # not correct
        return False
    elif numCont % numVMs != 0:
        print("[ERROR] Number of containers should be a multiple of number of VMs.")
        return False
    elif numTenants % numCont != 0:
        print("[ERROR] Number of Flow Rules has to be a multiple of the number of Containers.")
        return False
    elif numVMs < 1 or numCont < 1:
        return False
    
    cpuArray = exp.cpuAllocation(numVMs, nbrCores, isIsolated, True, totalTenantVMs, 2, totalCpuCores)    
    exp.HOST_CPU = cpuArray["hostCpu"]
    OvsCpu = cpuArray["ovsCpu"]
    DpdkCpu = cpuArray["ovsDpdk"]
    cpuDpdkPorts = cpuArray["cpuDpdkPorts"]
    OvsVMsCpuArray = cpuArray["OvsVMsCpuArray"]

    # upper bound derived from p2v, results in same offsets for in/out ports 
    num_vfs = str(numTenants * 2 + numCont)
    offset = int(num_vfs) / numCont
    
    exp.NicConfig = ["1", num_vfs]
    exp.NicType = "mlx"
    exp.isSRIOV = True
    exp.Server_cnx = cnx_server

    exp.pf_index = 0
    exp.pfs = []
    exp.vfs = []
    
    exp.scsName = "phy2phy_SRIOV_Dynamic_Container" + "_IsDPDK=" + str(isDPDK) + "_IsIsolated=" + str(isIsolated) + "_numVMs=" + str(numVMs) + "_numCont=" + str(numCont)
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # exp.EmailNotify(InitMessage, "is beeing prepared", logTimeStamp)
    exp.Logs("", logTimeStamp)
    
    exp.isDPDK = isDPDK
    if isDPDK:
        # exp.OVS_PATH = exp.dpdk_path    
        print("Container mode currently does not support DPDK.")
        return

    exp.PhyPorts = [
            ("enp2s0f0", num_vfs),
            ("enp2s0f1", num_vfs)
            ]
    
    exp.InitialConfig()
    # set isContainer only now to make sure that OvS is also stopped on the host (container stopping/cleaning is done in ConfigOVS)
    exp.isContainer = True

    port_1_Vfs = exp.pfs[0][2]
    port_2_Vfs = exp.pfs[1][2]
    
    exp.MyVfs = []
    for i in range(0, numCont):
        vm_idx = int(float(i) / numCont * numVMs) + 1
        print("[*] VM INDEX: " + str(vm_idx))
        vm = "vswitch-vm-container-{}".format(vm_idx) if vm_idx != 1 else "vswitch-vm-container"
        print("    => VM : " + vm)
        exp.MyVfs.append((port_1_Vfs[i*offset], "0", "off", vm, i))
        exp.MyVfs.append((port_2_Vfs[i*offset], "0", "off", vm, i))
    
    exp.usedVms = [("vswitch-vm-container", OvsVMsCpuArray[0], VmRam)]
    for i in range(1, numVMs):
        exp.usedVms.append(("vswitch-vm-container-{}".format(i + 1), OvsVMsCpuArray[i], VmRam))

    if isDPDK:
        pass
    else:
        ovs_ports = []
        for i in range(0, numCont):
            ovs_ports.append([
                        (port_1_Vfs[i*offset], False),
                        (port_2_Vfs[i*offset], False)])

    msg = exp.GetScenarioSummary([a for a in ovs_ports], OvsCpu, DpdkCpu, DpdkMem, isIsolated)
    # exp.EmailNotify(msg, "is beeing prepared", logTimeStamp)
    exp.Logs(msg, logTimeStamp)

    exp.Vfsconfig()
    
    if isDPDK:
        pass
    else:
        for i in range(0, numCont):
            vm_idx = int(float(i) / numCont * numVMs) + 1
            vm = "vswitch-vm-container-{}".format(vm_idx) if vm_idx != 1 else "vswitch-vm-container"
            exp.ConfigOVS(vm, "br0", ovs_ports[i], OvsCpu, ContNum=i, VMNum=vm_idx)
    
    # add flow rules for each container
    for i in range(0, numCont):
        vm_idx = int(float(i) / numCont * numVMs) + 1
        vm = "vswitch-vm-container-{}".format(vm_idx) if vm_idx != 1 else "vswitch-vm-container"
        for f in range(0, numTenants / numCont):
            match = "in_port={},ip,nw_dst=10.0.0.{}".format(exp.VfsMatch[port_1_Vfs[i*offset]], (i * (numTenants / numCont)) + 2 + f)
            action = "mod_dl_dst:{},{}".format(outDestMac, exp.VfsMatch[port_2_Vfs[i*offset]])
            exp.addFlowRule(vm, exp.OVS_PATH, "br0", match, action, ContNum=i)
            exp.showFlowRules(vm, exp.OVS_PATH, "br0", ContNum=i)
    
    print("[*] Offset: {}".format(offset))
    print("[*] in/out MACs: ")
    for i in range(0, numCont):
        print("    Container ID:  {}".format(i))
        print("              IPs: 10.0.0.{}".format(range(i*(numTenants / numCont) + 2, (i+1)*(numTenants / numCont) + 2)))
        print("              {}".format(exp.GetMacByVf(port_1_Vfs[i*offset])))
        print("              {}".format(exp.GetMacByVf(port_2_Vfs[i*offset])))

    # exp.EmailNotify(msg, "is ready", logTimeStamp)
    return True


def phy2vm2vm2phy_SRIOV_Dynamic_Container(cnx_server, isDPDK, nbrCores, isIsolated, numVMs=1, numCont=1, numTenants=4): 
    # sanity checks
    if numVMs > 4:
        print("[ERROR] Currently, only 4 VM instances are available.")
        return False
    elif numCont > 24:
        print("[ERROR] The maximum number of configurable containers is 24 as the PF's totalvfs is 64.")
        return False
    elif numCont % numVMs != 0:
        print("[ERROR] Number of containers should be a multiple of number of VMs.")
        return False
    elif numTenants % numCont != 0:
        print("[ERROR] Number of Tenants has to be a multiple of the number of Containers.")
        return False
    elif numVMs < 1 or numCont < 1:
        return False
    
    # 2 cores per l2fwd session, all running on one tenant VM
    exp.isContainer = True
    cpuArray = exp.cpuAllocation(numVMs, nbrCores, isIsolated, True, 1, l2fwdCpuCores, totalCpuCores)    
    exp.isContainer = False
    exp.HOST_CPU = cpuArray["hostCpu"]
    OvsCpu = cpuArray["ovsCpu"]
    DpdkCpu = cpuArray["ovsDpdk"]
    cpuDpdkPorts = cpuArray["cpuDpdkPorts"]
    TenantVMsCpuArray = cpuArray["TenantVMsCpuArray"]
    OvsVMsCpuArray = cpuArray["OvsVMsCpuArray"]

    # upper bound derived from p2v, results in same offsets for in/out ports 
    num_vfs = str(numTenants * 2 + numCont)
    offset = int(num_vfs) / numCont

    exp.NicConfig = ["1", num_vfs]
    exp.NicType = "mlx"
    exp.isSRIOV = True
    exp.Server_cnx = cnx_server

    exp.pf_index = 0
    exp.pfs = []
    exp.vfs = []
    
    exp.scsName= "phy2vm2vm2phy_SRIOV_Dynamic_Container" + "_IsDPDK=" + str(isDPDK) + "_IsIsolated=" + str(isIsolated) + "_numVMs=" + str(numVMs) + "_numCont=" + str(numCont)
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # exp.EmailNotify(InitMessage, "is beeing prepared", logTimeStamp)
    exp.Logs("", logTimeStamp)
    
    exp.IsDPDK = isDPDK
    if isDPDK:
        # exp.OVS_PATH = exp.dpdk_path
        print("Container mode currently does not support DPDK.")
        return
      
    exp.PhyPorts= [
           ("enp2s0f0", num_vfs),
           ("enp2s0f1", num_vfs)
          ]
    
    exp.InitialConfig()
    # set isContainer only now to make sure that OvS is also stopped on the host (container stopping/cleaning is done in ConfigOVS)
    exp.isContainer = True

    port_1_Vfs = exp.pfs[0][2]
    port_2_Vfs = exp.pfs[1][2]

    exp.MyVfs = []
    for i in range(0, numCont):
        vm_idx = int(float(i) / numCont * numVMs) + 1
        print("[*] VM INDEX: " + str(vm_idx))
        vm = "vswitch-vm-container-{}".format(vm_idx) if vm_idx != 1 else "vswitch-vm-container"
        tenant_vm = "tenant-green-1"
        
        print("    => VM : " + vm)
        # in/out VF per container
        exp.MyVfs.append((port_1_Vfs[i*offset], "0", "off", vm, i))
        exp.MyVfs.append((port_2_Vfs[i*offset], "0", "off", vm, i))
        for f in range(0, numTenants / numCont):
            vlan = str(((numTenants / numCont)*i + f + 1) * 10)

            # tenant specific gateway VFs
            exp.MyVfs.append((port_1_Vfs[i*offset + f*2 + 1], vlan, "off", vm, i))
            exp.MyVfs.append((port_2_Vfs[i*offset + f*2 + 1], vlan, "off", vm, i))

            exp.MyVfs.append((port_1_Vfs[i*offset + f*2 + 2], vlan, "off", tenant_vm))
            exp.MyVfs.append((port_2_Vfs[i*offset + f*2 + 2], vlan, "off", tenant_vm))

    exp.usedVms = [("vswitch-vm-container", OvsVMsCpuArray[0], VmRam)]
    for i in range(1, numVMs):
        exp.usedVms.append(("vswitch-vm-container-{}".format(i + 1), OvsVMsCpuArray[i], VmRam))

    # allocate some base memory for the VM and 1GB + some overhead per tenant, as each l2fwd application needs at least one 1GB hugepage
    exp.usedVms.append(("tenant-green-{}".format(1), TenantVMsCpuArray[0], str(488281 + 1074219 * numTenants)))
    
    if isDPDK:
        return
    else:
        ovs_ports = []
        for i in range(0, numCont):
            p = [(port_1_Vfs[i*offset], False),
                 (port_2_Vfs[i*offset], False)]
            for f in range(0, numTenants / numCont):
                p.append((port_1_Vfs[i*offset + f*2 + 1], False))
                p.append((port_2_Vfs[i*offset + f*2 + 1], False))
            ovs_ports.append(p)
        
    msg= exp.GetScenarioSummary([a for a in ovs_ports], OvsCpu, DpdkCpu, DpdkMem, isIsolated)
    # exp.EmailNotify(msg, "is beeing prepared", logTimeStamp)
    exp.Logs(msg, logTimeStamp)      
    exp.Vfsconfig()
    
    if isDPDK:
        return
    else:    
        for i in range(0, numCont):
            vm_idx = int(float(i) / numCont * numVMs) + 1
            vm = "vswitch-vm-container-{}".format(vm_idx) if vm_idx != 1 else "vswitch-vm-container"
            exp.ConfigOVS(vm, "br0", ovs_ports[i], OvsCpu, ContNum=i, VMNum=vm_idx)
    
    # add flow rules for each container
    for i in range(0, numCont):
        vm_idx = int(float(i) / numCont * numVMs) + 1
        vm = "vswitch-vm-container-{}".format(vm_idx) if vm_idx != 1 else "vswitch-vm-container"
        
        for f in range(0, numTenants / numCont):
            match = "in_port={},ip,nw_dst=10.0.0.{}".format(exp.VfsMatch[port_1_Vfs[i*offset]], (numTenants / numCont)*i + f + 2)
            action = "mod_dl_dst:{},{}".format(exp.GetMacByVf(port_1_Vfs[i*offset + f*2 + 2]), exp.VfsMatch[port_1_Vfs[i*offset + f*2 + 1]])
            exp.addFlowRule(vm, exp.OVS_PATH, "br0", match, action, ContNum=i)
            
            match = "in_port={}".format(exp.VfsMatch[port_2_Vfs[i*offset + f*2 + 1]])
            action = "mod_dl_dst:{},{}".format(outDestMac, exp.VfsMatch[port_2_Vfs[i*offset]])
            exp.addFlowRule(vm, exp.OVS_PATH, "br0", match, action, ContNum=i)
            
            # adjust MAC address in l2fwd binary on tenant vm
            tenant = "tenant-green-1"
            mac = exp.GetMacByVf(port_2_Vfs[i*offset + f*2 + 1])
            exp.patchMAC(tenant, "./container/l2fwd-container-{}".format((numTenants / numCont)*i + 1), mac)

        exp.showFlowRules(vm, exp.OVS_PATH, "br0", ContNum=i)

    exp.startL2Frwd(numCont, vswitchMode="p2v_container", tenantCount=numCont)
    
    print("[*] Offset: {}".format(offset))
    print("[*] in/out MACs: ")
    for i in range(0, numCont):
        print("    Container ID:  {}".format(i))
        print("              IPs: 10.0.0.{}".format(range(i*(numTenants / numCont) + 2, (i+1)*(numTenants / numCont) + 2)))
        print("              {}".format(exp.GetMacByVf(port_1_Vfs[i*offset])))
        print("              {}".format(exp.GetMacByVf(port_2_Vfs[i*offset])))

    # exp.EmailNotify(msg, "is ready", logTimeStamp)
    return True
    

# untested
def vm2vm_SRIOV_Dynamic_Container(cnx_server, isDPDK, nbrCores, isIsolated, numVMs=1, numCont=1, numTenants=4):
    # sanity checks
    if numVMs > 4:
        print("[ERROR] Currently, only 4 VM instances are available.")
        return False
    elif numCont > 2:
        print("[ERROR] The number of possible OVS containers is limited by the number of available cores: 2 cores per l2fwd session, 2 sessions per OVS instance => limit=3")
        return False
    elif numCont % numVMs != 0:
        print("[ERROR] Number of containers should be a multiple of number of VMs.")
        return False
    elif numTenants % numCont != 0:
        print("[ERROR] Number of Flow Rules has to be a multiple of the number of Containers.")
        return False
    elif numVMs < 1 or numCont < 1:
        return False

    exp.isContainer = True
    cpuArray = exp.cpuAllocation(2, nbrCores, isIsolated, True, 2, l2fwdCpuCores, totalCpuCores)    
    exp.isContainer = False
    exp.HOST_CPU = cpuArray["hostCpu"]
    OvsCpu = cpuArray["ovsCpu"]
    DpdkCpu = cpuArray["ovsDpdk"]
    cpuDpdkPorts = cpuArray["cpuDpdkPorts"]
    TenantVMsCpuArray = cpuArray["TenantVMsCpuArray"]
    OvsVMsCpuArray = cpuArray["OvsVMsCpuArray"]
    num_vfs = str(numCont * 3)
    
    exp.NicConfig = ["1", num_vfs]
    exp.NicType = "mlx"
    exp.isSRIOV = True
    exp.Server_cnx= cnx_server

    exp.pf_index = 0
    exp.pfs = []
    exp.vfs = []
    
    exp.scsName = "vm2vm_SRIOV_Dynamic_Container"+"_IsDPDK="+str(isDPDK)+"_IsIsolated="+str(isIsolated)
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # exp.EmailNotify(InitMessage, "is beeing prepared", logTimeStamp)
    exp.Logs("", logTimeStamp)
    
    exp.IsDPDK = isDPDK
    if isDPDK:
        exp.OVS_PATH = exp.dpdk_path
    else:
        exp.OVS_PATH = exp.nodpdk_path

    exp.PhyPorts= [
           ("enp2s0f0", num_vfs),
           ("enp2s0f1", num_vfs)
          ]
    
    exp.InitialConfig()
    exp.isContainer = True

    port_1_Vfs = exp.pfs[0][2]
    port_2_Vfs = exp.pfs[1][2]

    exp.MyVfs = []
    for i in range(0, numCont):
        vm_idx = int(float(i) / numCont * numVMs) + 1
        print("[*] VM INDEX: " + str(vm_idx))
        vm = "vswitch-vm-container-{}".format(vm_idx) if vm_idx != 1 else "vswitch-vm-container"
        print("    => VM : " + vm)
        exp.MyVfs.append((port_1_Vfs[i*5], "0", "off", vm, i))
        exp.MyVfs.append((port_2_Vfs[i*5], "0", "off", vm, i))
        for l in range(0, 2):
            vlan = str((i*2 + l + 1)*10)
            # tenant_vm = "tenant-green-{}".format(i*2 + l + 1)
            tenant_vm = "tenant-green-{}".format(l + 1)
            exp.MyVfs.append((port_1_Vfs[i*5 + l*2 + 1], vlan, "off", vm, i))
            exp.MyVfs.append((port_2_Vfs[i*5 + l*2 + 1], vlan, "off", vm, i))
            exp.MyVfs.append((port_1_Vfs[i*5 + l*2 + 2], vlan, "off", tenant_vm))
            exp.MyVfs.append((port_2_Vfs[i*5 + l*2 + 2], vlan, "off", tenant_vm))
    
    exp.usedVms = [("vswitch-vm-container", OvsVMsCpuArray[0], VmRam)]
    for i in range(1, numVMs):
        exp.usedVms.append(("vswitch-vm-container-{}".format(i + 1), OvsVMsCpuArray[i], VmRam))
    for i in range(0, 2):
        exp.usedVms.append(("tenant-green-{}".format(i + 1), TenantVMsCpuArray[i], str(2929688 * numCont)))
    
    if isDPDK:
        ovs_ports = []
        for i in range(0, numCont):
            ovs_ports.append([
                        (port_1_Vfs[i*5], True, cpuDpdkPorts),
                        (port_2_Vfs[i*5], True, cpuDpdkPorts),
                        (port_1_Vfs[i*5 + 1], True, cpuDpdkPorts),
                        (port_2_Vfs[i*5 + 1], True, cpuDpdkPorts),
                        (port_1_Vfs[i*5 + 3], True, cpuDpdkPorts),
                        (port_2_Vfs[i*5 + 3], True, cpuDpdkPorts)])  
    else:
        ovs_ports = []
        for i in range(0, numCont):
            ovs_ports.append([
                        (port_1_Vfs[i*5], False),
                        (port_2_Vfs[i*5], False),
                        (port_1_Vfs[i*5 + 1], False),
                        (port_2_Vfs[i*5 + 1], False),
                        (port_1_Vfs[i*5 + 3], False),
                        (port_2_Vfs[i*5 + 3], False)])
        
    msg= exp.GetScenarioSummary([a for a in ovs_ports], OvsCpu, DpdkCpu, DpdkMem, isIsolated)
    # exp.EmailNotify(msg, "is beeing prepared", logTimeStamp)
    exp.Logs(msg, logTimeStamp)      
    exp.Vfsconfig()
    
    if isDPDK:
         for i in range(0, numCont):
            vm_idx = int(float(i) / numCont * numVMs) + 1
            vm = "vswitch-vm-container-{}".format(vm_idx) if vm_idx != 1 else "vswitch-vm-container"
            exp.ConfigOVS(vm, "br0", ovs_ports[i], OvsCpu, DpdkMem, DpdkCpu, ContNum=i, VMNum=vm_idx)
    else:
        for i in range(0, numCont):
            vm_idx = int(float(i) / numCont * numVMs) + 1
            vm = "vswitch-vm-container-{}".format(vm_idx) if vm_idx != 1 else "vswitch-vm-container"
            exp.ConfigOVS(vm, "br0", ovs_ports[i], OvsCpu, ContNum=i, VMNum=vm_idx)

    for i in range(0, numCont):
        vm_idx = int(float(i) / numCont * numVMs) + 1
        vm = "vswitch-vm-container-{}".format(vm_idx) if vm_idx != 1 else "vswitch-vm-container"
   
        match="in_port={},ip,nw_dst=10.0.0.{}".format(exp.VfsMatch[port_1_Vfs[i*5]], (i+1)*2)
        action="mod_dl_dst:{},{}".format(exp.GetMacByVf(port_1_Vfs[i*5 + 2]), exp.VfsMatch[port_1_Vfs[i*5 + 1]])
        exp.addFlowRule(vm, exp.OVS_PATH, "br0", match, action)

        match="in_port={}".format(exp.VfsMatch[port_2_Vfs[i*5 + 1]])
        action="mod_dl_dst:{},{}".format(exp.GetMacByVf(port_1_Vfs[i*5 + 4]), exp.VfsMatch[port_1_Vfs[i*5 + 3]])
        exp.addFlowRule(vm, exp.OVS_PATH, "br0", match, action)

        match="in_port={}".format(exp.VfsMatch[port_2_Vfs[i*5 + 3]])
        action="mod_dl_dst:{},{}".format(outDestMac, exp.VfsMatch[port_2_Vfs[i*5]])
        exp.addFlowRule(vm, exp.OVS_PATH, "br0", match, action)

        exp.showFlowRules(vm, exp.OVS_PATH,"br0")
        
        tenant = "tenant-green-{}".format(1)
        mac = exp.GetMacByVf(port_2_Vfs[i*5 + 1])
        exp.patchMAC(tenant, "./container/l2fwd-FourOvsVm-container-{}".format(i + 1), mac)
        tenant = "tenant-green-{}".format(2)
        mac = exp.GetMacByVf(port_2_Vfs[i*5 + 3])
        exp.patchMAC(tenant, "./container/l2fwd-FourOvsVm-container-{}".format(i + 1), mac)
        
    exp.startL2Frwd(numCont, vswitchMode="v2v_container", tenantCount=numCont)
    
    # exp.EmailNotify(msg, "is ready", logTimeStamp)
    return True