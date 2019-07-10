"""
Created on Tue Nov  6 16:23:13 2018

@author: saad
"""
import expLib as exp
from datetime import datetime


###################### Vars for all scenarios #################################
DpdkMem = "1024,0"

#Destination MAC (needed for Flow Rules)
outDestMac = "00:00:00:00:30:56"

# RAM value used for Tenant- and OvS VMs
VmRam = "4G" 

# Total number of tenant VMs
totalTenantVMs = 4

# Cpu Cores for Tenant VMs
TenantVmCores = 2 

# Total number of cpu cores
totalCpuCores = 16

InitMessage = "The scenario is getting prepared ..."


def phy2vm2vm2phy_Baseline(cnx_server, isDPDK, nbrCores):
    cpuArray = exp.cpuAllocation(1, nbrCores, True, False, totalTenantVMs, TenantVmCores, totalCpuCores)
    exp.HOST_CPU = cpuArray["hostCpu"]
    OvsCpu = cpuArray["ovsCpu"]
    DpdkCpu = cpuArray["ovsDpdk"]
    cpuDpdkPorts = cpuArray["cpuDpdkPorts"]
    TenantVMsCpuArray = cpuArray["TenantVMsCpuArray"]

    exp.NicType = "mlx"
    exp.isSRIOV = False
    exp.Server_cnx = cnx_server

    exp.scsName = "phy2vm2vm2phy_Baseline"+"_IsDPDK="+str(isDPDK)
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if isDPDK:
            exp.IsDPDK = True
            exp.OVS_PATH = exp.dpdk_path
    else:
            exp.IsDPDK = False
            exp.OVS_PATH = exp.nodpdk_path

    exp.VirtualPorts = [
        ("1", "br0", "tenant-green-1"),
        ("2", "br0", "tenant-green-1"),
        ("4", "br0", "tenant-green-2"),
        ("5", "br0", "tenant-green-2"),
        ("7", "br0", "tenant-green-3"),
        ("8", "br0", "tenant-green-3"),
        ("10", "br0", "tenant-green-4"),
        ("11", "br0", "tenant-green-4")
    ]

    exp.usedVms = [
        ("tenant-green-1", TenantVMsCpuArray[0], VmRam),
        ("tenant-green-2", TenantVMsCpuArray[1], VmRam),
        ("tenant-green-3", TenantVMsCpuArray[2], VmRam),
        ("tenant-green-4", TenantVMsCpuArray[3], VmRam)
    ]

    if isDPDK:
        exp.PhyPorts = [
                ("enp2s0f0", "br0", True, cpuDpdkPorts),
                ("enp2s0f1", "br0", True, cpuDpdkPorts)]
    else:
        exp.PhyPorts = [
                ("enp2s0f0", "br0"),
                ("enp2s0f1", "br0")]

    msg = exp.GetScenarioSummary([], OvsCpu, DpdkCpu, DpdkMem)
    exp.EmailNotify(msg, "is beeing prepared", logTimeStamp)
    exp.Logs(msg, logTimeStamp)

    exp.InitialConfig(isDPDK)

    if isDPDK:
        exp.ConfigOVS(exp.Server_cnx, "br0", " ", OvsCpu, DpdkMem, DpdkCpu)
    else:
        exp.ConfigOVS(exp.Server_cnx, "br0", " ", OvsCpu)

    exp.VirPortConfig()

    '''
    OVS Flow Rules:

    '''
    # Flow Rules (1)
    match = "in_port=enp2s0f0,ip,nw_dst=10.0.0.2"
    action = "vnet1"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    # Flow Rules (2)
    match = "in_port=vnet2"
    action = "enp2s0f1"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    # Flow Rules (3)
    match = "in_port=enp2s0f0,ip,nw_dst=10.0.0.3"
    action = "vnet4"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    # Flow Rules (4)
    match = "in_port=vnet5"
    action = "enp2s0f1"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    # Flow Rules (1)
    match = "in_port=enp2s0f0,ip,nw_dst=10.0.0.4"
    action = "vnet7"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    # Flow Rules (2)
    match = "in_port=vnet8"
    action = "enp2s0f1"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)
    
    # Flow Rules (1)
    match = "in_port=enp2s0f0,ip,nw_dst=10.0.0.5"
    action = "vnet10"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    # Flow Rules (2)
    match = "in_port=vnet11"
    action = "enp2s0f1"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    # show Flow rules of br0
    exp.showFlowRules(exp.Server_cnx, exp.OVS_PATH, "br0")

    exp.startL2Frwd(nbrOvs=1, nicType="e1000", tenantCount=4, vswitchMode="Baseline_4Tenants")
    exp.SetBridging("tenant-green-1", exp.VirPortsMatch["1"], exp.VirPortsMatch["2"])
    exp.SetBridging("tenant-green-2", exp.VirPortsMatch["4"], exp.VirPortsMatch["5"])
    exp.SetBridging("tenant-green-3", exp.VirPortsMatch["7"], exp.VirPortsMatch["8"])
    exp.SetBridging("tenant-green-4", exp.VirPortsMatch["10"], exp.VirPortsMatch["11"])
    exp.EmailNotify(msg, "is ready", logTimeStamp)

    return True


def phy2vm2vm2phy_SRIOV_OneOvs(cnx_server, isDPDK, nbrCores):
    cpuArray = exp.cpuAllocation(1, nbrCores, True, True, totalTenantVMs, TenantVmCores, totalCpuCores)    
    exp.HOST_CPU = cpuArray["hostCpu"]
    OvsCpu = cpuArray["ovsCpu"]
    DpdkCpu = cpuArray["ovsDpdk"]
    cpuDpdkPorts = cpuArray["cpuDpdkPorts"]
    TenantVMsCpuArray = cpuArray["TenantVMsCpuArray"]
    OvsVMsCpuArray = cpuArray["OvsVMsCpuArray"]

    exp.NicConfig = ["1", "10"]       
    exp.NicType = "mlx"
    exp.isSRIOV = True
    exp.Server_cnx = cnx_server

    exp.pf_index = 0
    exp.pfs = []
    exp.vfs = []

    exp.scsName = "phy2vm2vm2phy_SRIOV_OneOvs"+"_IsDPDK=" + str(isDPDK)
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # exp.EmailNotify(InitMessage, "is beeing prepared", logTimeStamp)
    exp.Logs("", logTimeStamp)

    if isDPDK:
        exp.IsDPDK = True
        exp.OVS_PATH = exp.dpdk_path
    else:
        exp.IsDPDK = False
        exp.OVS_PATH = exp.nodpdk_path
            
    exp.PhyPorts = [
           ("enp2s0f0", "10"),
           ("enp2s0f1", "10")
        ]

    exp.InitialConfig()
    port_1_Vfs = exp.pfs[0][2]
    port_2_Vfs = exp.pfs[1][2]

    exp.MyVfs = [
        (port_1_Vfs[0], "0", "off", "vswitch-vm"),
        (port_2_Vfs[0], "0", "off", "vswitch-vm"),
        
        (port_1_Vfs[1], "10", "off", "vswitch-vm"),
        (port_2_Vfs[1], "10", "off", "vswitch-vm"),
        (port_1_Vfs[2], "10", "off", "tenant-green-1"),
        (port_2_Vfs[2], "10", "off", "tenant-green-1"),
        
        (port_1_Vfs[3], "20", "off", "vswitch-vm"),
        (port_2_Vfs[3], "20", "off", "vswitch-vm"),
        (port_1_Vfs[4], "20", "off", "tenant-green-2"),
        (port_2_Vfs[4], "20", "off", "tenant-green-2"),
        

        (port_1_Vfs[6], "30", "off", "vswitch-vm"),
        (port_2_Vfs[6], "30", "off", "vswitch-vm"),
        (port_1_Vfs[7], "30", "off", "tenant-green-3"),
        (port_2_Vfs[7], "30", "off", "tenant-green-3"),
        
        (port_1_Vfs[8], "40", "off", "vswitch-vm"),
        (port_2_Vfs[8], "40", "off", "vswitch-vm"),
        (port_1_Vfs[9], "40", "off", "tenant-green-4"),
        (port_2_Vfs[9], "40", "off", "tenant-green-4")
        ]

    exp.usedVms = [
             ("vswitch-vm", OvsVMsCpuArray[0], VmRam),
             ("tenant-green-1", TenantVMsCpuArray[0], VmRam),
             ("tenant-green-2", TenantVMsCpuArray[1], VmRam),
             ("tenant-green-3", TenantVMsCpuArray[2], VmRam),
             ("tenant-green-4", TenantVMsCpuArray[3], VmRam)]

    if isDPDK:
        OvsVmPorts1 = [
            (port_1_Vfs[0], True, cpuDpdkPorts),
            (port_2_Vfs[0], True, cpuDpdkPorts),
            (port_1_Vfs[1], True, cpuDpdkPorts),
            (port_2_Vfs[1], True, cpuDpdkPorts),
            (port_1_Vfs[3], True, cpuDpdkPorts),
            (port_2_Vfs[3], True, cpuDpdkPorts),
            (port_1_Vfs[6], True, cpuDpdkPorts),
            (port_2_Vfs[6], True, cpuDpdkPorts),
            (port_1_Vfs[8], True, cpuDpdkPorts),
            (port_2_Vfs[8], True, cpuDpdkPorts)]  
    else:
        OvsVmPorts1 = [
            (port_1_Vfs[0], False),
            (port_2_Vfs[0], False),
            (port_1_Vfs[1], False),
            (port_2_Vfs[1], False),
            (port_1_Vfs[3], False),
            (port_2_Vfs[3], False),
            (port_1_Vfs[6], False),
            (port_2_Vfs[6], False),
            (port_1_Vfs[8], False),
            (port_2_Vfs[8], False)]  
     
    msg = exp.GetScenarioSummary([OvsVmPorts1], OvsCpu, DpdkCpu, DpdkMem)
    print(msg)
    # exp.EmailNotify(msg, "is beeing prepared", logTimeStamp)
    exp.Logs(msg, logTimeStamp)    
    exp.Vfsconfig()

    if isDPDK:
        exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu, DpdkMem, DpdkCpu)
    else:
        exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu)

    '''
    OVS Flow Rules for OVS-VM-1:
    '''
    # Flow Rules (1)
    match = "in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.2"
    action = "mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[2])+","+exp.VfsMatch[port_1_Vfs[1]]
    exp.addFlowRule("vswitch-vm", exp.OVS_PATH, "br0", match, action)
    
    # Flow Rules (2)
    match = "in_port="+exp.VfsMatch[port_2_Vfs[1]]
    action = "mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[0]]
    exp.addFlowRule("vswitch-vm", exp.OVS_PATH, "br0", match, action)
    
    # Flow Rules (3)
    match = "in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.3"
    action = "mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[4])+","+exp.VfsMatch[port_1_Vfs[3]]
    exp.addFlowRule("vswitch-vm", exp.OVS_PATH, "br0", match, action)
    
    # Flow Rules (4)
    match = "in_port="+exp.VfsMatch[port_2_Vfs[3]]
    action = "mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[0]]
    exp.addFlowRule("vswitch-vm", exp.OVS_PATH, "br0", match, action)

    # show Flow rules of br0 
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH, "br0")

    # Flow Rules (5)
    match = "in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.4"
    action = "mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[7])+","+exp.VfsMatch[port_1_Vfs[6]]
    exp.addFlowRule("vswitch-vm", exp.OVS_PATH, "br0", match, action)
    
    # Flow Rules (6) 
    match = "in_port="+exp.VfsMatch[port_2_Vfs[6]]
    action = "mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[0]]
    exp.addFlowRule("vswitch-vm", exp.OVS_PATH, "br0", match, action)
    
    # Flow Rules (7)
    match = "in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.5"
    action = "mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[9])+","+exp.VfsMatch[port_1_Vfs[8]]
    exp.addFlowRule("vswitch-vm", exp.OVS_PATH, "br0", match, action)
    
    # Flow Rules (8)
    match = "in_port="+exp.VfsMatch[port_2_Vfs[8]]
    action = "mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[0]]
    exp.addFlowRule("vswitch-vm", exp.OVS_PATH, "br0", match, action)

    exp.showFlowRules("vswitch-vm", exp.OVS_PATH, "br0")

    exp.startL2Frwd(1)

    # exp.EmailNotify(msg, "is ready", logTimeStamp)

    return True


def phy2vm2vm2phy_SRIOV_TwoOvs(cnx_server, isDPDK, nbrCores, isIsolated):    
    cpuArray = exp.cpuAllocation(2, nbrCores, isIsolated, True, totalTenantVMs, TenantVmCores, totalCpuCores)    
    exp.HOST_CPU = cpuArray["hostCpu"]
    OvsCpu = cpuArray["ovsCpu"]
    DpdkCpu = cpuArray["ovsDpdk"]
    cpuDpdkPorts = cpuArray["cpuDpdkPorts"]
    TenantVMsCpuArray = cpuArray["TenantVMsCpuArray"]
    OvsVMsCpuArray = cpuArray["OvsVMsCpuArray"]
    
    exp.NicConfig = ["1", "10"]
    exp.NicType = "mlx"
    exp.isSRIOV = True
    exp.Server_cnx = cnx_server

    exp.pf_index = 0
    exp.pfs = []
    exp.vfs = []

    exp.scsName = "phy2vm2vm2phy_SRIOV_TwoOvs_IsDPDK=" + str(isDPDK) + "_IsIsolated=" + str(isIsolated)
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    exp.EmailNotify(InitMessage, "is beeing prepared", logTimeStamp)
    exp.Logs("", logTimeStamp)

    if isDPDK:
            exp.IsDPDK = True
            exp.OVS_PATH = exp.dpdk_path
    else:
            exp.IsDPDK = False
            exp.OVS_PATH = exp.nodpdk_path
      
    exp.PhyPorts = [
        ("enp2s0f0", "10"),
        ("enp2s0f1", "10")
        ]

    exp.InitialConfig()
    port_1_Vfs = exp.pfs[0][2]
    port_2_Vfs = exp.pfs[1][2]
    
    exp.MyVfs = [
        (port_1_Vfs[0], "0", "off", "vswitch-vm"),
        (port_2_Vfs[0], "0", "off", "vswitch-vm"),

        (port_1_Vfs[1], "10", "off", "vswitch-vm"),
        (port_2_Vfs[1], "10", "off", "vswitch-vm"),
        (port_1_Vfs[2], "10", "off", "tenant-green-1"),
        (port_2_Vfs[2], "10", "off", "tenant-green-1"),

        (port_1_Vfs[3], "20", "off", "vswitch-vm"),
        (port_2_Vfs[3], "20", "off", "vswitch-vm"),
        (port_1_Vfs[4], "20", "off", "tenant-green-2"),
        (port_2_Vfs[4], "20", "off", "tenant-green-2"),

        (port_1_Vfs[5], "0", "off", "vswitch-vm-2"),
        (port_2_Vfs[5], "0", "off", "vswitch-vm-2"),

        (port_1_Vfs[6], "30", "off", "vswitch-vm-2"),
        (port_2_Vfs[6], "30", "off", "vswitch-vm-2"),
        (port_1_Vfs[7], "30", "off", "tenant-green-3"),
        (port_2_Vfs[7], "30", "off", "tenant-green-3"),

        (port_1_Vfs[8], "40", "off", "vswitch-vm-2"),
        (port_2_Vfs[8], "40", "off", "vswitch-vm-2"),
        (port_1_Vfs[9], "40", "off", "tenant-green-4"),
        (port_2_Vfs[9], "40", "off", "tenant-green-4")
        ]

    exp.usedVms =[
        ("vswitch-vm", OvsVMsCpuArray[0], VmRam),
        ("tenant-green-1", TenantVMsCpuArray[0], VmRam),
        ("tenant-green-2", TenantVMsCpuArray[1], VmRam),

        ("vswitch-vm-2", OvsVMsCpuArray[1], VmRam),
        ("tenant-green-3", TenantVMsCpuArray[2], VmRam),
        ("tenant-green-4", TenantVMsCpuArray[3], VmRam)]

    if isDPDK: 
        OvsVmPorts1 = [
            (port_1_Vfs[0], True, cpuDpdkPorts),
            (port_2_Vfs[0], True, cpuDpdkPorts),
            (port_1_Vfs[1], True, cpuDpdkPorts),
            (port_2_Vfs[1], True, cpuDpdkPorts),
            (port_1_Vfs[3], True, cpuDpdkPorts),
            (port_2_Vfs[3], True, cpuDpdkPorts)]  
    
        OvsVmPorts2 = [
            (port_1_Vfs[5], True, cpuDpdkPorts),
            (port_2_Vfs[5], True, cpuDpdkPorts),
            (port_1_Vfs[6], True, cpuDpdkPorts),
            (port_2_Vfs[6], True, cpuDpdkPorts),
            (port_1_Vfs[8], True, cpuDpdkPorts),
            (port_2_Vfs[8], True, cpuDpdkPorts)]
    else:
        OvsVmPorts1 = [
            (port_1_Vfs[0], False),
            (port_2_Vfs[0], False),
            (port_1_Vfs[1], False),
            (port_2_Vfs[1], False),
            (port_1_Vfs[3], False),
            (port_2_Vfs[3], False)]
        
        OvsVmPorts2 = [
            (port_1_Vfs[5], False),
            (port_2_Vfs[5], False),
            (port_1_Vfs[6], False),
            (port_2_Vfs[6], False),
            (port_1_Vfs[8], False),
            (port_2_Vfs[8], False)]

    msg = exp.GetScenarioSummary([OvsVmPorts1, OvsVmPorts2], OvsCpu, DpdkCpu, DpdkMem, isIsolated)
    exp.EmailNotify(msg, "is beeing prepared", logTimeStamp)
    exp.Logs(msg, logTimeStamp)      
    exp.Vfsconfig()

    if isDPDK:
        exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu, DpdkMem, DpdkCpu)
        exp.ConfigOVS("vswitch-vm-2", "br0", OvsVmPorts2, OvsCpu, DpdkMem, DpdkCpu)
    else:    
        exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu)
        exp.ConfigOVS("vswitch-vm-2", "br0", OvsVmPorts2, OvsCpu)

    '''
    OVS Flow Rules for OVS-VM-1:
    '''
    # Flow Rules (1)
    match = "in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.2"
    action = "mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[2])+","+exp.VfsMatch[port_1_Vfs[1]]
    exp.addFlowRule("vswitch-vm", exp.OVS_PATH, "br0", match, action)
    
    # Flow Rules (2)
    match = "in_port="+exp.VfsMatch[port_2_Vfs[1]]
    action = "mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[0]]
    exp.addFlowRule("vswitch-vm", exp.OVS_PATH, "br0", match, action)

    # Flow Rules (3)
    match = "in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.3"
    action = "mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[4])+","+exp.VfsMatch[port_1_Vfs[3]]
    exp.addFlowRule("vswitch-vm", exp.OVS_PATH, "br0", match, action)
    
    # Flow Rules (4)
    match = "in_port="+exp.VfsMatch[port_2_Vfs[3]]
    action = "mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[0]]
    exp.addFlowRule("vswitch-vm", exp.OVS_PATH, "br0", match, action)

    # show Flow rules of br0 
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH, "br0")
    
    '''
    OVS Flow Rules for OVS-VM-2:
    '''
    # Flow Rules (1)
    match = "in_port="+exp.VfsMatch[port_1_Vfs[5]]+",ip,nw_dst=10.0.0.4"
    action = "mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[7])+","+exp.VfsMatch[port_1_Vfs[6]]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)
    
    # Flow Rules (2)
    match = "in_port="+exp.VfsMatch[port_2_Vfs[6]]
    action = "mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[5]]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)
    
    # Flow Rules (3)
    match = "in_port="+exp.VfsMatch[port_1_Vfs[5]]+",ip,nw_dst=10.0.0.5"
    action = "mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[9])+","+exp.VfsMatch[port_1_Vfs[8]]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)
    
    # Flow Rules (4)
    match = "in_port="+exp.VfsMatch[port_2_Vfs[8]]
    action = "mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[5]]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)

    exp.showFlowRules("vswitch-vm-2", exp.OVS_PATH,"br0")
    
    exp.startL2Frwd(2)
    
    exp.EmailNotify(msg, "is ready", logTimeStamp)
        
    return True


def phy2vm2vm2phy_SRIOV_FourOvs(cnx_server, isDPDK, nbrCores, isIsolated):
    cpuArray = exp.cpuAllocation(4, nbrCores, isIsolated, True, totalTenantVMs, TenantVmCores, totalCpuCores)    
    exp.HOST_CPU = cpuArray["hostCpu"];
    OvsCpu = cpuArray["ovsCpu"];
    DpdkCpu = cpuArray["ovsDpdk"];
    cpuDpdkPorts = cpuArray["cpuDpdkPorts"];
    TenantVMsCpuArray = cpuArray["TenantVMsCpuArray"];
    OvsVMsCpuArray = cpuArray["OvsVMsCpuArray"];
    
    exp.NicConfig = ["1","12"]    
    exp.NicType = "mlx"
    exp.isSRIOV = True
    exp.Server_cnx = cnx_server

    exp.pf_index = 0
    exp.pfs = []
    exp.vfs = []
    
    exp.scsName = "phy2vm2vm2phy_SRIOV_FourOvs_IsDPDK=" + str(isDPDK) + "_IsIsolated=" + str(isIsolated)
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    exp.EmailNotify(InitMessage, "is beeing prepared", logTimeStamp)
    exp.Logs("", logTimeStamp)
    
    if isDPDK:
        exp.IsDPDK = True
        exp.OVS_PATH = exp.dpdk_path
    else:
        exp.IsDPDK = False
        exp.OVS_PATH = exp.nodpdk_path
      
    exp.PhyPorts= [
        ("enp2s0f0", "12"),
        ("enp2s0f1", "12")
        ]
    
    exp.InitialConfig()
    port_1_Vfs = exp.pfs[0][2]
    port_2_Vfs = exp.pfs[1][2]
    
    exp.MyVfs= [
        (port_1_Vfs[0], "0", "off", "vswitch-vm"),
        (port_2_Vfs[0], "0", "off", "vswitch-vm"),  

        (port_1_Vfs[1], "10", "off", "vswitch-vm"),
        (port_2_Vfs[1], "10", "off", "vswitch-vm"),
        (port_1_Vfs[2], "10", "off", "tenant-green-1"),
        (port_2_Vfs[2], "10", "off", "tenant-green-1"),
        
        (port_1_Vfs[3], "0", "off", "vswitch-vm-2"),
        (port_2_Vfs[3], "0", "off", "vswitch-vm-2"),

        (port_1_Vfs[4], "20", "off", "vswitch-vm-2"),
        (port_2_Vfs[4], "20", "off", "vswitch-vm-2"),
        (port_1_Vfs[5], "20", "off", "tenant-green-2"),
        (port_2_Vfs[5], "20", "off", "tenant-green-2"),
        
        (port_1_Vfs[6], "0", "off", "vswitch-vm-3"),
        (port_2_Vfs[6], "0", "off", "vswitch-vm-3"),

        (port_1_Vfs[7], "30", "off", "vswitch-vm-3"),
        (port_2_Vfs[7], "30", "off", "vswitch-vm-3"),
        (port_1_Vfs[8], "30", "off", "tenant-green-3"),
        (port_2_Vfs[8], "30", "off", "tenant-green-3"),

        (port_1_Vfs[9], "0", "off", "vswitch-vm-4"),
        (port_2_Vfs[9], "0", "off", "vswitch-vm-4"),       
            
        (port_1_Vfs[10], "40", "off", "vswitch-vm-4"),
        (port_2_Vfs[10], "40", "off", "vswitch-vm-4"),
        (port_1_Vfs[11], "40", "off", "tenant-green-4"),
        (port_2_Vfs[11], "40", "off", "tenant-green-4")
        ]
    
    exp.usedVms=[
        ("vswitch-vm", OvsVMsCpuArray[0], VmRam),
        ("vswitch-vm-2", OvsVMsCpuArray[1], VmRam),
        ("vswitch-vm-3", OvsVMsCpuArray[2], VmRam),
        ("vswitch-vm-4", OvsVMsCpuArray[3], VmRam),
        ("tenant-green-1", TenantVMsCpuArray[0], VmRam),
        ("tenant-green-2", TenantVMsCpuArray[1], VmRam),
        ("tenant-green-3", TenantVMsCpuArray[2], VmRam),
        ("tenant-green-4", TenantVMsCpuArray[3], VmRam)]
    
    if isDPDK:
        OvsVmPorts1 = [
            (port_1_Vfs[0], True, cpuDpdkPorts),
            (port_2_Vfs[0], True, cpuDpdkPorts),
            (port_1_Vfs[1], True, cpuDpdkPorts),
            (port_2_Vfs[1], True, cpuDpdkPorts)]  

        OvsVmPorts2 = [
            (port_1_Vfs[3], True, cpuDpdkPorts),
            (port_2_Vfs[3], True, cpuDpdkPorts),
            (port_1_Vfs[4], True, cpuDpdkPorts),
            (port_2_Vfs[4], True, cpuDpdkPorts)]  
        
        OvsVmPorts3 = [
            (port_1_Vfs[6], True, cpuDpdkPorts),
            (port_2_Vfs[6], True, cpuDpdkPorts),
            (port_1_Vfs[7], True, cpuDpdkPorts),
            (port_2_Vfs[7], True, cpuDpdkPorts)]  

        OvsVmPorts4 = [
            (port_1_Vfs[9], True, cpuDpdkPorts),
            (port_2_Vfs[9], True, cpuDpdkPorts),
            (port_1_Vfs[10], True, cpuDpdkPorts),
            (port_2_Vfs[10], True, cpuDpdkPorts)]  
    else:
        OvsVmPorts1 = [
            (port_1_Vfs[0], False),
            (port_2_Vfs[0], False),
            (port_1_Vfs[1], False),
            (port_2_Vfs[1], False)]  

        OvsVmPorts2 = [
            (port_1_Vfs[3], False),
            (port_2_Vfs[3], False),
            (port_1_Vfs[4], False),
            (port_2_Vfs[4], False)]  
            
        OvsVmPorts3 = [
            (port_1_Vfs[6], False),
            (port_2_Vfs[6], False),
            (port_1_Vfs[7], False),
            (port_2_Vfs[7], False)]  

        OvsVmPorts4 = [
            (port_1_Vfs[9], False),
            (port_2_Vfs[9], False),
            (port_1_Vfs[10], False),
            (port_2_Vfs[10], False)]
        
    msg = exp.GetScenarioSummary([OvsVmPorts1, OvsVmPorts2, OvsVmPorts3, OvsVmPorts4], OvsCpu, DpdkCpu, DpdkMem, isIsolated)
    exp.EmailNotify(msg, "is beeing prepared", logTimeStamp)
    exp.Logs(msg, logTimeStamp)      
    exp.Vfsconfig()
    
    if isDPDK:
        exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu, DpdkMem, DpdkCpu)
        exp.ConfigOVS("vswitch-vm-2", "br0", OvsVmPorts2, OvsCpu, DpdkMem, DpdkCpu)
        exp.ConfigOVS("vswitch-vm-3", "br0", OvsVmPorts3, OvsCpu, DpdkMem, DpdkCpu)
        exp.ConfigOVS("vswitch-vm-4", "br0", OvsVmPorts4, OvsCpu, DpdkMem, DpdkCpu) 
    else:    
        exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu)
        exp.ConfigOVS("vswitch-vm-2", "br0", OvsVmPorts2, OvsCpu)
        exp.ConfigOVS("vswitch-vm-3", "br0", OvsVmPorts3, OvsCpu)
        exp.ConfigOVS("vswitch-vm-4", "br0", OvsVmPorts4, OvsCpu)
    
    '''
    OVS Flow Rules for OVS-VM-1:
    '''
    # Flow Rules (1)
    match = "in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.2"
    action = "mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[2])+","+exp.VfsMatch[port_1_Vfs[1]]
    exp.addFlowRule("vswitch-vm", exp.OVS_PATH, "br0", match, action)
    
    # Flow Rules (2)
    match = "in_port="+exp.VfsMatch[port_2_Vfs[1]]
    action = "mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[0]]
    exp.addFlowRule("vswitch-vm", exp.OVS_PATH, "br0", match, action)
    
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
        
    '''
    OVS Flow Rules for OVS-VM-2:
    '''
    #Flow Rules (3)
    match = "in_port="+exp.VfsMatch[port_1_Vfs[3]]+",ip,nw_dst=10.0.0.3"
    action = "mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[5])+","+exp.VfsMatch[port_1_Vfs[4]]
    exp.addFlowRule("vswitch-vm-2", exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (4)
    match = "in_port="+exp.VfsMatch[port_2_Vfs[4]]
    action = "mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[3]]
    exp.addFlowRule("vswitch-vm-2", exp.OVS_PATH, "br0", match, action)

    exp.showFlowRules("vswitch-vm-2", exp.OVS_PATH,"br0")
    
    '''
    OVS Flow Rules for OVS-VM-3:
    '''
    #Flow Rules (1)
    match = "in_port="+exp.VfsMatch[port_1_Vfs[6]]+",ip,nw_dst=10.0.0.4"
    action = "mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[8])+","+exp.VfsMatch[port_1_Vfs[7]]
    exp.addFlowRule("vswitch-vm-3", exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    match = "in_port="+exp.VfsMatch[port_2_Vfs[7]]
    action = "mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[6]]
    exp.addFlowRule("vswitch-vm-3", exp.OVS_PATH, "br0", match, action)

    exp.showFlowRules("vswitch-vm-3", exp.OVS_PATH,"br0")
    
    '''
    OVS Flow Rules for OVS-VM-4:
    '''
    
    #Flow Rules (3)
    match = "in_port="+exp.VfsMatch[port_1_Vfs[9]]+",ip,nw_dst=10.0.0.5"
    action = "mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[11])+","+exp.VfsMatch[port_1_Vfs[10]]
    exp.addFlowRule("vswitch-vm-4", exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (4)
    match = "in_port="+exp.VfsMatch[port_2_Vfs[10]]
    action = "mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[9]]
    exp.addFlowRule("vswitch-vm-4", exp.OVS_PATH, "br0", match, action)

    exp.showFlowRules("vswitch-vm-4", exp.OVS_PATH,"br0")
    
    exp.startL2Frwd(4)
    
    exp.EmailNotify(msg, "is ready", logTimeStamp)
        
    return True


def phy2phy_Baseline(cnx_server, isDPDK, nbrCores):    
    cpuArray = exp.cpuAllocation(1, nbrCores, True, False, totalTenantVMs, TenantVmCores, totalCpuCores)    
    exp.HOST_CPU = cpuArray["hostCpu"];
    OvsCpu = cpuArray["ovsCpu"];
    DpdkCpu = cpuArray["ovsDpdk"];
    cpuDpdkPorts = cpuArray["cpuDpdkPorts"];
    DpdkMem = str((nbrCores -1)*1024) # for multiple cores need to allocate proportional memory
    
    exp.NicType = "mlx"
    exp.isSRIOV = False
    exp.Server_cnx = cnx_server
    
    exp.scsName = "phy2phy_Baseline"+"_IsDPDK="+str(isDPDK)
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    if isDPDK:
        exp.IsDPDK= True
        exp.OVS_PATH= exp.dpdk_path
    else:
        exp.IsDPDK= False
        exp.OVS_PATH= exp.nodpdk_path
         
    if isDPDK:
        exp.PhyPorts= [
            ("enp2s0f0", "br0", True, cpuDpdkPorts),
            ("enp2s0f1", "br0", True, cpuDpdkPorts)]
    else:
        exp.PhyPorts= [
            ("enp2s0f0", "br0"),
            ("enp2s0f1", "br0")]
        
    
    msg = exp.GetScenarioSummary([], OvsCpu, DpdkCpu, DpdkMem)
    exp.EmailNotify(msg, "is beeing prepared", logTimeStamp)
    exp.Logs(msg, logTimeStamp)       
    exp.InitialConfig(isDPDK)
    
    if isDPDK: 
        exp.ConfigOVS(exp.Server_cnx, "br0", " ", OvsCpu, DpdkMem, DpdkCpu)
    else:
        exp.ConfigOVS(exp.Server_cnx, "br0", " ", OvsCpu)
  
    exp.VirPortConfig()

    '''
    OVS Flow Rules:

    '''
    # Flow Rules (1)
    match = "in_port=enp2s0f0,ip,nw_dst=10.0.0.2"
    action = "enp2s0f1"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)
    
    # Flow Rules (2)
    match = "in_port=enp2s0f0,ip,nw_dst=10.0.0.3"
    action = "enp2s0f1"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)
    
    # Flow Rules (3)
    match = "in_port=enp2s0f0,ip,nw_dst=10.0.0.4"
    action = "enp2s0f1"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)
    
    # Flow Rules (4)
    match = "in_port=enp2s0f0,ip,nw_dst=10.0.0.5"
    action = "enp2s0f1"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    exp.showFlowRules(exp.Server_cnx, exp.OVS_PATH, "br0")
    
    exp.EmailNotify(msg, "is ready", logTimeStamp)

    return True



#############################################################################
        
def phy2phy_SRIOV_OneOvs(cnx_server, isDPDK, nbrCores):
    cpuArray = exp.cpuAllocation(1, nbrCores, True, True, totalTenantVMs, TenantVmCores, totalCpuCores)    
    exp.HOST_CPU = cpuArray["hostCpu"];
    OvsCpu = cpuArray["ovsCpu"];
    DpdkCpu = cpuArray["ovsDpdk"];
    cpuDpdkPorts = cpuArray["cpuDpdkPorts"];
    OvsVMsCpuArray = cpuArray["OvsVMsCpuArray"];
    
    exp.NicConfig = ["1","9"]    
    exp.NicType = "mlx"
    exp.isSRIOV = True
    exp.Server_cnx = cnx_server

    exp.pf_index = 0
    exp.pfs = []
    exp.vfs = []
    
    exp.scsName = "phy2phy_SRIOV_OneOvs_IsDPDK=" + str(isDPDK)
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # exp.EmailNotify(InitMessage, "is beeing prepared", logTimeStamp)
    exp.Logs("", logTimeStamp)
    
    if isDPDK:
        exp.IsDPDK= True
        exp.OVS_PATH= exp.dpdk_path
    else:
        exp.IsDPDK= False
        exp.OVS_PATH= exp.nodpdk_path
            
    exp.PhyPorts= [
        ("enp2s0f0", "9"),
        ("enp2s0f1", "9")
        ]
    
    exp.InitialConfig()
    port_1_Vfs = exp.pfs[0][2]
    port_2_Vfs = exp.pfs[1][2]

    exp.MyVfs= [
        (port_1_Vfs[0], "0", "off", "vswitch-vm"),
        (port_2_Vfs[0], "0", "off", "vswitch-vm")
        ]
    
    exp.usedVms=[("vswitch-vm", OvsVMsCpuArray[0], VmRam)]
        
    if isDPDK:
        OvsVmPorts1= [
            (port_1_Vfs[0], True, cpuDpdkPorts),
            (port_2_Vfs[0], True, cpuDpdkPorts)]  
    else:
        OvsVmPorts1= [
            (port_1_Vfs[0], False),
            (port_2_Vfs[0], False)]  

    msg = exp.GetScenarioSummary([OvsVmPorts1], OvsCpu, DpdkCpu, DpdkMem)
    # exp.EmailNotify(msg, "is beeing prepared", logTimeStamp)
    exp.Logs(msg, logTimeStamp)       
    exp.Vfsconfig()
    
    if isDPDK:
        exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu, DpdkMem, DpdkCpu)    
    else:    
        exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu)
    
    '''
    OVS Flow Rules for OVS-VM-1:
    '''
    
    # Flow Rules (1)
    match = "in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.2"
    action = "mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[0]]
    exp.addFlowRule("vswitch-vm", exp.OVS_PATH, "br0", match, action)
    
    match = "in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.3"
    action = "mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[0]]
    exp.addFlowRule("vswitch-vm", exp.OVS_PATH, "br0", match, action)
    
    match = "in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.4"
    action = "mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[0]]
    exp.addFlowRule("vswitch-vm", exp.OVS_PATH, "br0", match, action)
    
    match = "in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.5"
    action = "mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[0]]
    exp.addFlowRule("vswitch-vm", exp.OVS_PATH, "br0", match, action)
    
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
    
    # exp.EmailNotify(msg, "is ready", logTimeStamp)

    return True

    
def phy2phy_SRIOV_TwoOvs(cnx_server, isDPDK, nbrCores, isIsolated):    
    cpuArray = exp.cpuAllocation(2, nbrCores, isIsolated, True, totalTenantVMs, TenantVmCores, totalCpuCores)    
    exp.HOST_CPU = cpuArray["hostCpu"];
    OvsCpu = cpuArray["ovsCpu"];
    DpdkCpu = cpuArray["ovsDpdk"];
    cpuDpdkPorts = cpuArray["cpuDpdkPorts"];
    OvsVMsCpuArray = cpuArray["OvsVMsCpuArray"];
    
    exp.NicConfig = ["1","10"]    
    exp.NicType = "mlx"
    exp.isSRIOV = True
    exp.Server_cnx = cnx_server

    exp.pf_index = 0
    exp.pfs = []
    exp.vfs = []
    
    exp.scsName = "phy2phy_SRIOV_TwoOvs"+"_IsDPDK="+str(isDPDK)+"_IsIsolated="+str(isIsolated)
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    exp.EmailNotify(InitMessage, "is beeing prepared", logTimeStamp)
    exp.Logs("", logTimeStamp)
    
    if isDPDK:
        exp.IsDPDK= True
        exp.OVS_PATH= exp.dpdk_path
    else:
        exp.IsDPDK= False
        exp.OVS_PATH= exp.nodpdk_path

      
    exp.PhyPorts= [
           ("enp2s0f0", "10"),
           ("enp2s0f1", "10")
          ]
    
    exp.InitialConfig()
    port_1_Vfs=exp.pfs[0][2]
    port_2_Vfs=exp.pfs[1][2]
    
    exp.MyVfs= [
        (port_1_Vfs[0], "0", "off", "vswitch-vm"),
        (port_2_Vfs[0], "0", "off", "vswitch-vm"),
                    
        (port_1_Vfs[5], "0", "off", "vswitch-vm-2"),
        (port_2_Vfs[5], "0", "off", "vswitch-vm-2")
        ]
    
    exp.usedVms=[
        ("vswitch-vm", OvsVMsCpuArray[0], VmRam),
        ("vswitch-vm-2", OvsVMsCpuArray[1], VmRam)]
    
    
    if isDPDK:        
        OvsVmPorts1= [
            (port_1_Vfs[0], True, cpuDpdkPorts),
            (port_2_Vfs[0], True, cpuDpdkPorts)]  
    
        OvsVmPorts2= [
            (port_1_Vfs[5], True, cpuDpdkPorts),
            (port_2_Vfs[5], True, cpuDpdkPorts)]  
    else:        
        OvsVmPorts1= [
            (port_1_Vfs[0], False),
            (port_2_Vfs[0], False)]  
        
        OvsVmPorts2= [
            (port_1_Vfs[5], False),
            (port_2_Vfs[5], False)]
    
    msg = exp.GetScenarioSummary([OvsVmPorts1, OvsVmPorts2], OvsCpu, DpdkCpu, DpdkMem, isIsolated)
    exp.EmailNotify(msg, "is beeing prepared", logTimeStamp)
    exp.Logs(msg, logTimeStamp)       
    exp.Vfsconfig()
    
    if isDPDK:
        exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu, DpdkMem, DpdkCpu)
        exp.ConfigOVS("vswitch-vm-2", "br0", OvsVmPorts2, OvsCpu, DpdkMem, DpdkCpu)    
    else:    
        exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu)
        exp.ConfigOVS("vswitch-vm-2", "br0", OvsVmPorts2, OvsCpu)
    
    '''
    OVS Flow Rules for OVS-VM-1:
    '''
    #Flow Rules (1)
    match = "in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.2"
    action = "mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[0]]
    exp.addFlowRule("vswitch-vm", exp.OVS_PATH, "br0", match, action)

    match = "in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.3"
    action = "mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[0]]
    exp.addFlowRule("vswitch-vm", exp.OVS_PATH, "br0", match, action)
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
    
    '''
    OVS Flow Rules for OVS-VM-2:

    note that the VF offset (5) is chosen to be unnecessarily big in order to 
    match in/out port assignment between p2p and p2v for the same number of OvS VMs/instances 
    (same offsets -> same MACs -> same pcaps can be used for measurements)

    '''
    
    #Flow Rules (1) 
    match = "in_port="+exp.VfsMatch[port_1_Vfs[5]]+",ip,nw_dst=10.0.0.4"
    action = "mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[5]]
    exp.addFlowRule("vswitch-vm-2", exp.OVS_PATH, "br0", match, action)
    
    match = "in_port="+exp.VfsMatch[port_1_Vfs[5]]+",ip,nw_dst=10.0.0.5"
    action = "mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[5]]
    exp.addFlowRule("vswitch-vm-2", exp.OVS_PATH, "br0", match, action)
    exp.showFlowRules("vswitch-vm-2", exp.OVS_PATH,"br0")
    
    exp.EmailNotify(msg, "is ready", logTimeStamp)

    return True
    
    
def phy2phy_SRIOV_FourOvs(cnx_server, isDPDK, nbrCores, isIsolated):
    cpuArray = exp.cpuAllocation(4, nbrCores, isIsolated, True, totalTenantVMs, TenantVmCores, totalCpuCores)    
    exp.HOST_CPU = cpuArray["hostCpu"]
    OvsCpu = cpuArray["ovsCpu"]
    DpdkCpu = cpuArray["ovsDpdk"]
    cpuDpdkPorts= cpuArray["cpuDpdkPorts"]
    OvsVMsCpuArray= cpuArray["OvsVMsCpuArray"]
    
    exp.NicConfig = ["1","12"]
    exp.NicType = "mlx"
    exp.isSRIOV = True
    exp.Server_cnx = cnx_server

    exp.pf_index = 0
    exp.pfs = []
    exp.vfs = []
    
    exp.scsName = "phy2phy_SRIOV_FourOvs_IsDPDK=" + str(isDPDK) + "_IsIsolated=" + str(isIsolated)
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    exp.EmailNotify(InitMessage, "is beeing prepared", logTimeStamp)
    exp.Logs("", logTimeStamp)
    
    if isDPDK:
        exp.IsDPDK= True
        exp.OVS_PATH= exp.dpdk_path
    else:
        exp.IsDPDK= False
        exp.OVS_PATH= exp.nodpdk_path
              
    exp.PhyPorts = [
        ("enp2s0f0", "12"),
        ("enp2s0f1", "12")
        ]
    
    exp.InitialConfig()
    port_1_Vfs = exp.pfs[0][2]
    port_2_Vfs = exp.pfs[1][2]
    
    exp.MyVfs = [
        (port_1_Vfs[0], "0", "off", "vswitch-vm"),
        (port_2_Vfs[0], "0", "off", "vswitch-vm"),      

        
        (port_1_Vfs[3], "0", "off", "vswitch-vm-2"),
        (port_2_Vfs[3], "0", "off", "vswitch-vm-2"),

        
        (port_1_Vfs[6], "0", "off", "vswitch-vm-3"),
        (port_2_Vfs[6], "0", "off", "vswitch-vm-3"),


        (port_1_Vfs[9], "0", "off", "vswitch-vm-4"),
        (port_2_Vfs[9], "0", "off", "vswitch-vm-4")       

        ]
    
    exp.usedVms = [
        ("vswitch-vm", OvsVMsCpuArray[0], VmRam),
        ("vswitch-vm-2", OvsVMsCpuArray[1], VmRam),
        ("vswitch-vm-3", OvsVMsCpuArray[2], VmRam),
        ("vswitch-vm-4", OvsVMsCpuArray[3], VmRam)]

    if isDPDK:    
        OvsVmPorts1= [
            (port_1_Vfs[0], True, cpuDpdkPorts),
            (port_2_Vfs[0], True, cpuDpdkPorts)]  

        OvsVmPorts2= [
            (port_1_Vfs[3], True, cpuDpdkPorts),
            (port_2_Vfs[3], True, cpuDpdkPorts)]  
        
        OvsVmPorts3= [
            (port_1_Vfs[6], True, cpuDpdkPorts),
            (port_2_Vfs[6], True, cpuDpdkPorts)]  

        OvsVmPorts4= [
            (port_1_Vfs[9], True, cpuDpdkPorts),
            (port_2_Vfs[9], True, cpuDpdkPorts)]  
    else:
        OvsVmPorts1= [
            (port_1_Vfs[0], False),
            (port_2_Vfs[0], False)]  

        OvsVmPorts2= [
            (port_1_Vfs[3], False),
            (port_2_Vfs[3], False)]  
        
        OvsVmPorts3= [
            (port_1_Vfs[6], False),
            (port_2_Vfs[6], False)]  

        OvsVmPorts4= [
            (port_1_Vfs[9], False),
            (port_2_Vfs[9], False)]
    
    msg = exp.GetScenarioSummary([OvsVmPorts1, OvsVmPorts2, OvsVmPorts3, OvsVmPorts4], OvsCpu, DpdkCpu, DpdkMem, isIsolated)
    exp.EmailNotify(msg, "is beeing prepared", logTimeStamp)
    exp.Logs(msg, logTimeStamp)       
    exp.Vfsconfig()
    
    if isDPDK:
        exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu, DpdkMem, DpdkCpu)
        exp.ConfigOVS("vswitch-vm-2", "br0", OvsVmPorts2, OvsCpu, DpdkMem, DpdkCpu)
        exp.ConfigOVS("vswitch-vm-3", "br0", OvsVmPorts3, OvsCpu, DpdkMem, DpdkCpu)
        exp.ConfigOVS("vswitch-vm-4", "br0", OvsVmPorts4, OvsCpu, DpdkMem, DpdkCpu)
    else:    
        exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu)
        exp.ConfigOVS("vswitch-vm-2", "br0", OvsVmPorts2, OvsCpu)
        exp.ConfigOVS("vswitch-vm-3", "br0", OvsVmPorts3, OvsCpu)
        exp.ConfigOVS("vswitch-vm-4", "br0", OvsVmPorts4, OvsCpu)
    
    '''
    OVS Flow Rules for OVS-VM-1:
    
    Note that the VF offset (3) is chosen to be unnecessarily big in order to 
    match in/out port assignment between p2p and p2v for the same number of OvS VMs/instances 
    (same offsets -> same MACs -> same pcaps can be used for measurements) 
    
    '''


    #Flow Rules (1)
    match = "in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.2"
    action = "mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[0]]
    exp.addFlowRule("vswitch-vm", exp.OVS_PATH, "br0", match, action)
        
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
    
    '''
    OVS Flow Rules for OVS-VM-2:
    '''
    #Flow Rules (3)
    match = "in_port="+exp.VfsMatch[port_1_Vfs[3]]+",ip,nw_dst=10.0.0.3"
    action = "mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[3]]
    exp.addFlowRule("vswitch-vm-2", exp.OVS_PATH, "br0", match, action)
    
    exp.showFlowRules("vswitch-vm-2", exp.OVS_PATH,"br0")
    
    '''
    OVS Flow Rules for OVS-VM-3:
    '''
    #Flow Rules (1)
    match = "in_port="+exp.VfsMatch[port_1_Vfs[6]]+",ip,nw_dst=10.0.0.4"
    action = "mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[6]]
    exp.addFlowRule("vswitch-vm-3", exp.OVS_PATH, "br0", match, action)
    
    exp.showFlowRules("vswitch-vm-3", exp.OVS_PATH,"br0")
    
    '''
    OVS Flow Rules for OVS-VM-4:
    '''
    
    #Flow Rules (3)
    match = "in_port="+exp.VfsMatch[port_1_Vfs[9]]+",ip,nw_dst=10.0.0.5"
    action = "mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[9]]
    exp.addFlowRule("vswitch-vm-4", exp.OVS_PATH, "br0", match, action)
    
    exp.showFlowRules("vswitch-vm-4", exp.OVS_PATH,"br0")
    
    exp.EmailNotify(msg, "is ready", logTimeStamp)

    return True


