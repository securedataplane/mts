#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 10:30:56 2018

@author: saad
"""
import expLib as exp
from datetime import datetime

###############################################################################
DpdkMem="1024,0"

#Destination MAC (needed for Flow Rules)
outDestMac="00:00:00:00:30:56"

# RAM value used for Tenant- and OvS VMs
VmRam="4G" 

#Cpu Cores for Tenant VMs
TenantVmCores= 2 

# Total number of cpu cores
totalCpuCores=16

#message
InitMessage="The scenario is getting prepared ..."
###############################################################################
                           # SR-IOV Scenarios       
###############################################################################
    
def vm2vm_SRIOV_OneOvs(cnx_server, isDPDK, nbrCores):
    
    cpuArray= exp.cpuAllocation(1, nbrCores, True, True, 4, TenantVmCores, totalCpuCores)    
    exp.HOST_CPU=cpuArray["hostCpu"]
    OvsCpu= cpuArray["ovsCpu"]
    DpdkCpu=cpuArray["ovsDpdk"]
    cpuDpdkPorts= cpuArray["cpuDpdkPorts"]
    TenantVMsCpuArray= cpuArray["TenantVMsCpuArray"]
    OvsVMsCpuArray= cpuArray["OvsVMsCpuArray"]
    
    exp.NicConfig=["1","10"]    
    exp.NicType= "mlx"
    exp.isSRIOV= True
    exp.Server_cnx= cnx_server
    
    exp.pf_index=0
    exp.pfs=[]
    exp.vfs=[]
    
    exp.scsName= "vm2vm_SRIOV_OneOvs"+"_IsDPDK="+str(isDPDK)
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    exp.EmailNotify(InitMessage, "is beeing prepared", logTimeStamp)
    exp.Logs("", logTimeStamp) 
    
    
    if isDPDK:
            exp.IsDPDK= True
            exp.OVS_PATH= exp.dpdk_path
    else:
            exp.IsDPDK= False
            exp.OVS_PATH= exp.nodpdk_path
        
    #----------------------------------------#
      
    exp.PhyPorts= [
           ("enp3s0f0", "10"),
           ("enp3s0f1", "10")
          ]
    
    exp.InitialConfig()
    port_1_Vfs=exp.pfs[0][2]
    port_2_Vfs=exp.pfs[1][2]
    
    exp.MyVfs= [
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
    
    exp.usedVms=[
             ("vswitch-vm", OvsVMsCpuArray[0], VmRam),
             ("tenant-green-1", TenantVMsCpuArray[0], VmRam),
             ("tenant-green-2", TenantVMsCpuArray[1], VmRam),
             ("tenant-green-3", TenantVMsCpuArray[2], VmRam),
             ("tenant-green-4", TenantVMsCpuArray[3], VmRam)]
    
    
    if isDPDK:
        
            #----------------- OVS-VM_1------------------    
            OvsVmPorts1= [
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
        
            #----------------- OVS-VM_1------------------    
            OvsVmPorts1= [
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
    
    msg= exp.GetScenarioSummary([OvsVmPorts1], OvsCpu, DpdkCpu, DpdkMem)
    exp.EmailNotify(msg, "is beeing prepared", logTimeStamp)
    exp.Logs(msg, logTimeStamp)             
    #----------------------------------------#
    exp.Vfsconfig()
    
    if isDPDK:
         exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu, DpdkMem, DpdkCpu)
    
    else:    
        exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu)
    
    '''
    OVS Flow Rules for OVS-VM-1:
    '''
    ################################# Tenant_1 ##############################
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.2"
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[2])+","+exp.VfsMatch[port_1_Vfs[1]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_2_Vfs[1]]
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[4])+","+exp.VfsMatch[port_1_Vfs[3]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    
    #Flow Rules (3)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_2_Vfs[3]]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[0]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    ################################# Tenant_2 ##############################
    
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.4"
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[7])+","+exp.VfsMatch[port_1_Vfs[6]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_2_Vfs[6]]
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[9])+","+exp.VfsMatch[port_1_Vfs[8]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    
    #Flow Rules (3)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_2_Vfs[8]]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[0]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
    
    exp.startL2Frwd(1)
    
    exp.EmailNotify(msg, "is ready", logTimeStamp)
           
    return True


###############################################################################
def vm2vm_SRIOV_TwoOvs(cnx_server, isDPDK, nbrCores, isIsolated):
    
    cpuArray= exp.cpuAllocation(2, nbrCores, isIsolated, True, 4,TenantVmCores, totalCpuCores)    
    exp.HOST_CPU=cpuArray["hostCpu"];
    OvsCpu= cpuArray["ovsCpu"];
    DpdkCpu=cpuArray["ovsDpdk"];
    cpuDpdkPorts= cpuArray["cpuDpdkPorts"];
    TenantVMsCpuArray= cpuArray["TenantVMsCpuArray"];
    OvsVMsCpuArray= cpuArray["OvsVMsCpuArray"];
    
    exp.NicConfig=["1","10"]    
    exp.NicType= "mlx"
    exp.isSRIOV= True
    exp.Server_cnx= cnx_server

    exp.pf_index=0
    exp.pfs=[]
    exp.vfs=[]
    
    exp.scsName= "vm2vm_SRIOV_TwoOvs"+"_IsDPDK="+str(isDPDK)+"_IsIsolated="+str(isIsolated)
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    exp.EmailNotify(InitMessage, "is beeing prepared", logTimeStamp)
    exp.Logs("", logTimeStamp)
    
    
    if isDPDK:
            exp.IsDPDK= True
            exp.OVS_PATH= exp.dpdk_path
    else:
            exp.IsDPDK= False
            exp.OVS_PATH= exp.nodpdk_path

    #----------------------------------------#
      
    exp.PhyPorts= [
           ("enp3s0f0", "10"),
           ("enp3s0f1", "10")
          ]
    
    exp.InitialConfig()
    port_1_Vfs=exp.pfs[0][2]
    port_2_Vfs=exp.pfs[1][2]
    
    exp.MyVfs= [
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
    
    exp.usedVms=[
             ("vswitch-vm", OvsVMsCpuArray[0], VmRam),
             ("tenant-green-1", TenantVMsCpuArray[0], VmRam),
             ("tenant-green-2", TenantVMsCpuArray[1], VmRam),
             
             ("vswitch-vm-2", OvsVMsCpuArray[1], VmRam),
             ("tenant-green-3", TenantVMsCpuArray[2], VmRam),
             ("tenant-green-4", TenantVMsCpuArray[3], VmRam)]
    
    
    if isDPDK:
        
            #----------------- OVS-VM_1------------------    
            OvsVmPorts1= [
                        (port_1_Vfs[0], True, cpuDpdkPorts),
                        (port_2_Vfs[0], True, cpuDpdkPorts),
                        (port_1_Vfs[1], True, cpuDpdkPorts),
                        (port_2_Vfs[1], True, cpuDpdkPorts),
                        (port_1_Vfs[3], True, cpuDpdkPorts),
                        (port_2_Vfs[3], True, cpuDpdkPorts)]  
        
            #----------------- OVS-VM_2------------------  
            OvsVmPorts2= [
                        (port_1_Vfs[5], True, cpuDpdkPorts),
                        (port_2_Vfs[5], True, cpuDpdkPorts),
                        (port_1_Vfs[6], True, cpuDpdkPorts),
                        (port_2_Vfs[6], True, cpuDpdkPorts),
                        (port_1_Vfs[8], True, cpuDpdkPorts),
                        (port_2_Vfs[8], True, cpuDpdkPorts)]  
        

    else:
        
            #----------------- OVS-VM_1------------------    
            OvsVmPorts1= [
                        (port_1_Vfs[0], False),
                        (port_2_Vfs[0], False),
                        (port_1_Vfs[1], False),
                        (port_2_Vfs[1], False),
                        (port_1_Vfs[3], False),
                        (port_2_Vfs[3], False)]  
        
            #----------------- OVS-VM_2------------------  
            OvsVmPorts2= [
                        (port_1_Vfs[5], False),
                        (port_2_Vfs[5], False),
                        (port_1_Vfs[6], False),
                        (port_2_Vfs[6], False),
                        (port_1_Vfs[8], False),
                        (port_2_Vfs[8], False)] 
        
    msg= exp.GetScenarioSummary([OvsVmPorts1, OvsVmPorts2], OvsCpu, DpdkCpu, DpdkMem, isIsolated)
    exp.EmailNotify(msg, "is beeing prepared", logTimeStamp)
    exp.Logs(msg, logTimeStamp)      
    #----------------------------------------#
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
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.2"
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[2])+","+exp.VfsMatch[port_1_Vfs[1]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_2_Vfs[1]]
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[4])+","+exp.VfsMatch[port_1_Vfs[3]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    
    #Flow Rules (3)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_2_Vfs[3]]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[0]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
    
    '''
    OVS Flow Rules for OVS-VM-2:
    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[5]]+",ip,nw_dst=10.0.0.4"
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[7])+","+exp.VfsMatch[port_1_Vfs[6]]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_2_Vfs[6]]
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[9])+","+exp.VfsMatch[port_1_Vfs[8]]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)
    
    
    #Flow Rules (3)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_2_Vfs[8]]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_2_Vfs[5]]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm-2", exp.OVS_PATH,"br0")
    
    exp.startL2Frwd(2)
    
    exp.EmailNotify(msg, "is ready", logTimeStamp)
           
    return True
###############################################################################
                           # Baseline        
###############################################################################

def vm2vm_Baseline(cnx_server, isDPDK, nbrCores):
    
    cpuArray= exp.cpuAllocation(1, nbrCores, True, False, 4, TenantVmCores, totalCpuCores)
    exp.HOST_CPU=cpuArray["hostCpu"]
    OvsCpu= cpuArray["ovsCpu"]
    DpdkCpu=cpuArray["ovsDpdk"]
    cpuDpdkPorts= cpuArray["cpuDpdkPorts"]
    TenantVMsCpuArray= cpuArray["TenantVMsCpuArray"]
    
    exp.NicType= "mlx"
    exp.isSRIOV= False
    exp.Server_cnx= cnx_server

    exp.scsName= "vm2vm_Baseline"+"_IsDPDK="+str(isDPDK)
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    if isDPDK:
            exp.IsDPDK= True
            exp.OVS_PATH= exp.dpdk_path
    else:
            exp.IsDPDK= False
            exp.OVS_PATH= exp.nodpdk_path
        
    
    # ----------------------------------------#
        
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
            ("tenant-green-4", TenantVMsCpuArray[3], VmRam)]


    if isDPDK:
              exp.PhyPorts= [
                      ("enp3s0f0", "br0", True, cpuDpdkPorts),
                      ("enp3s0f1", "br0", True, cpuDpdkPorts)]
    else:
              exp.PhyPorts= [
                      ("enp3s0f0", "br0"),
                      ("enp3s0f1", "br0")]
        
    
    msg= exp.GetScenarioSummary([], OvsCpu, DpdkCpu, DpdkMem)
    exp.EmailNotify(msg, "is beeing prepared", logTimeStamp)
    exp.Logs(msg, logTimeStamp)    
    # ----------------------------------------#
    exp.InitialConfig(isDPDK)
    
    if isDPDK: 
        exp.ConfigOVS(exp.Server_cnx, "br0", " ", OvsCpu, DpdkMem, DpdkCpu)
    else:
        exp.ConfigOVS(exp.Server_cnx, "br0", " ", OvsCpu)

  
    exp.VirPortConfig()

    '''
    OVS Flow Rules T1 --> T2:
        
    '''
    # Flow Rules (1)
    # ---------------------------------------------------------
    match = "in_port=enp3s0f0,ip,nw_dst=10.0.0.2"
    action = "vnet1"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    # Flow Rules (2)
    # ---------------------------------------------------------
    match = "in_port=vnet2"
    action = "vnet4"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)
    
    # Flow Rules (3)
    # ---------------------------------------------------------
    match = "in_port=vnet5"
    action = "enp3s0f1"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)
    
    '''
    OVS Flow Rules T3 --> T4:
        
    '''
    # Flow Rules (1)
    # ---------------------------------------------------------
    match = "in_port=enp3s0f0,ip,nw_dst=10.0.0.4"
    action = "vnet7"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    # Flow Rules (2)
    # ---------------------------------------------------------
    match = "in_port=vnet8"
    action = "vnet10"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)
    
    # Flow Rules (3)
    # ---------------------------------------------------------
    match = "in_port=vnet11"
    action = "enp3s0f1"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)
    
   
    # show Flow rules of br0
    exp.showFlowRules(exp.Server_cnx, exp.OVS_PATH, "br0")

    # exp.startL2Frwd(nbrOvs=1 ,nicType="e1000", tenantCount=4, vswitchMode="Baseline_4Tenants")
    exp.SetBridging("tenant-green-1", exp.VirPortsMatch["1"], exp.VirPortsMatch["2"])
    exp.SetBridging("tenant-green-2", exp.VirPortsMatch["4"], exp.VirPortsMatch["5"])
    exp.SetBridging("tenant-green-3", exp.VirPortsMatch["7"], exp.VirPortsMatch["8"])
    exp.SetBridging("tenant-green-4", exp.VirPortsMatch["10"], exp.VirPortsMatch["11"])

    exp.EmailNotify(msg, "is ready", logTimeStamp)
        
    return True

##############################################################################

