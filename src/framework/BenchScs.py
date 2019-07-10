#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 23 15:24:30 2018

@author: saad
"""

import expLib as exp
from datetime import datetime

BenIntrMac= "00:0f:53:5b:89:f1"
BenIntr="ens2f1"
BenServer= exp.cnx_spree

###################### Vars for all scenarios #################################
DpdkMem="1024,0"

#Destination MAC (needed for Flow Rules)
outDestMac="00:00:00:00:30:56"
outDestMac=BenIntrMac
# RAM value used for Tenant- and OvS VMs
VmRam="4G" 

# Total number of tenant VMs
totalTenantVMs=4

#Cpu Cores for Tenant VMs
TenantVmCores= 2 

# Total number of cpu cores
totalCpuCores=16

#message
InitMessage="The scenario is getting prepared ..."

###############################################################################
###########################  phy2vm2vm2phy  ###################################
###############################################################################

def phy2vm2vm2phy_Baseline(cnx_server, isDPDK, nbrCores):
    
    cpuArray= exp.cpuAllocation(1, nbrCores, True, False, totalTenantVMs,TenantVmCores, totalCpuCores)
    exp.HOST_CPU=cpuArray["hostCpu"]
    OvsCpu= cpuArray["ovsCpu"]
    DpdkCpu=cpuArray["ovsDpdk"]
    cpuDpdkPorts= cpuArray["cpuDpdkPorts"]
    TenantVMsCpuArray= cpuArray["TenantVMsCpuArray"]
    
    exp.NicType= "mlx"
    exp.isSRIOV= False
    exp.Server_cnx= cnx_server
    
    exp.scsName= "Benchmark: phy2vm2vm2phy_Baseline"+"_IsDPDK="+str(isDPDK)
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
        ("3", "br0", "tenant-green-2"), 
        ("5", "br0", "tenant-green-3"),
        ("7", "br0", "tenant-green-4")
    ]
    
    exp.usedVms = [
            ("tenant-green-1", TenantVMsCpuArray[0], VmRam),
            ("tenant-green-2", TenantVMsCpuArray[1], VmRam),
            ("tenant-green-3", TenantVMsCpuArray[2], VmRam),
            ("tenant-green-4", TenantVMsCpuArray[3], VmRam)
            ]


    if isDPDK:
              exp.PhyPorts= [
                      ("enp3s0f0", "br0", True, cpuDpdkPorts)]
    else:
              exp.PhyPorts= [
                      ("enp3s0f0", "br0")]
        
    
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
    OVS Flow Rules:

    '''
    ################################# tenant 1 ###############################
    # Flow Rules (1)
    # ---------------------------------------------------------
    match = "in_port=enp3s0f0,ip,nw_dst=10.0.0.2"
    action = "vnet1"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    # Flow Rules (2)
    # ---------------------------------------------------------
    match = "in_port=vnet1"
    action = "enp3s0f0"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)
    
    ################################# tenant 2 ###############################
    # Flow Rules (1)
    # ---------------------------------------------------------
    match = "in_port=enp3s0f0,ip,nw_dst=10.0.0.3"
    action = "vnet3"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    # Flow Rules (2)
    # ---------------------------------------------------------
    match = "in_port=vnet3"
    action = "enp3s0f0"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)
    
    ################################# tenant 3 ###############################
    # Flow Rules (1)
    # ---------------------------------------------------------
    match = "in_port=enp3s0f0,ip,nw_dst=10.0.0.4"
    action = "vnet5"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    # Flow Rules (2)
    # ---------------------------------------------------------
    match = "in_port=vnet5"
    action = "enp3s0f0"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)
    
    ################################# tenant 4 ###############################
    # Flow Rules (1)
    # ---------------------------------------------------------
    match = "in_port=enp3s0f0,ip,nw_dst=10.0.0.5"
    action = "vnet7"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    # Flow Rules (2)
    # ---------------------------------------------------------
    match = "in_port=vnet7"
    action = "enp3s0f0"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)
    

    
    # show Flow rules of br0
    exp.showFlowRules(exp.Server_cnx, exp.OVS_PATH, "br0")
    
    ##################################################### 
    exp.SetInt(BenServer,BenIntr,"up")
    exp.SetIpInt(BenServer, BenIntr, "10.0.0.1/24")
    exp.SetArpEntry(BenServer,"10.0.0.2", exp.GenerateMacID("1"), BenIntr)
    exp.SetArpEntry(BenServer,"10.0.0.3", exp.GenerateMacID("3"), BenIntr)
    exp.SetArpEntry(BenServer,"10.0.0.4", exp.GenerateMacID("5"), BenIntr)
    exp.SetArpEntry(BenServer,"10.0.0.5", exp.GenerateMacID("7"), BenIntr)
    
    exp.SetIpInt(exp.getVmCnx("tenant-green-1"), "ens8", "10.0.0.2/24")
    exp.SetIpInt(exp.getVmCnx("tenant-green-2"), "ens8", "10.0.0.3/24")
    exp.SetIpInt(exp.getVmCnx("tenant-green-3"), "ens8", "10.0.0.4/24")
    exp.SetIpInt(exp.getVmCnx("tenant-green-4"), "ens8", "10.0.0.5/24")
    
    exp.SetArpEntry(exp.getVmCnx("tenant-green-1"),"10.0.0.1", BenIntrMac, "ens8")
    exp.SetArpEntry(exp.getVmCnx("tenant-green-2"),"10.0.0.1", BenIntrMac, "ens8")
    exp.SetArpEntry(exp.getVmCnx("tenant-green-3"),"10.0.0.1", BenIntrMac, "ens8")
    exp.SetArpEntry(exp.getVmCnx("tenant-green-4"),"10.0.0.1", BenIntrMac, "ens8")
    
    exp.EmailNotify(msg, "is ready", logTimeStamp)
     
    return True
###############################################################################
def phy2vm2vm2phy_SRIOV_OneOvs(cnx_server, isDPDK, nbrCores):

    cpuArray= exp.cpuAllocation(1, nbrCores, True, True, totalTenantVMs,TenantVmCores, totalCpuCores)    
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
    
    exp.scsName= "benchmark: phy2vm2vm2phy_SRIOV_OneOvs"+"_IsDPDK="+str(isDPDK)
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
           ("enp3s0f0", "10")
          ]
    
    exp.InitialConfig()
    port_1_Vfs=exp.pfs[0][2]
    

    
    exp.MyVfs= [
            (port_1_Vfs[0], "0", "off", "vswitch-vm"),
            (port_1_Vfs[1], "0", "off", "vswitch-vm"),
            
            (port_1_Vfs[2], "10", "off", "vswitch-vm"),
            (port_1_Vfs[3], "10", "off", "tenant-green-1"),
            
            
            (port_1_Vfs[4], "20", "off", "vswitch-vm"),
            (port_1_Vfs[5], "20", "off", "tenant-green-2"),
            

            (port_1_Vfs[6], "30", "off", "vswitch-vm"),
            (port_1_Vfs[7], "30", "off", "tenant-green-3"),
            
            (port_1_Vfs[8], "40", "off", "vswitch-vm"),
            (port_1_Vfs[9], "40", "off", "tenant-green-4")
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
                        (port_1_Vfs[1], True, cpuDpdkPorts),
                        (port_1_Vfs[2], True, cpuDpdkPorts),
                        (port_1_Vfs[4], True, cpuDpdkPorts),
                        (port_1_Vfs[6], True, cpuDpdkPorts),
                        (port_1_Vfs[8], True, cpuDpdkPorts)
                        ]  
        
    else:
        
            #----------------- OVS-VM_1------------------    
            OvsVmPorts1= [
                        (port_1_Vfs[0], False),
                        (port_1_Vfs[1], False),
                        (port_1_Vfs[2], False),
                        (port_1_Vfs[4], False),
                        (port_1_Vfs[6], False),
                        (port_1_Vfs[8], False)]  
        
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
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.2"
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[3])+","+exp.VfsMatch[port_1_Vfs[2]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[2]]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_1_Vfs[1]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (3)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.3"
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[5])+","+exp.VfsMatch[port_1_Vfs[4]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (4)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[4]]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_1_Vfs[1]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)

    #Flow Rules (5)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.4"
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[7])+","+exp.VfsMatch[port_1_Vfs[6]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (6) 
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[6]]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_1_Vfs[1]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (7)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.5"
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[9])+","+exp.VfsMatch[port_1_Vfs[8]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (8)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[8]]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_1_Vfs[1]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
    
    ####################### Bench COnfig ################################
    inVF= port_1_Vfs[0]
    exp.SetInt(BenServer,BenIntr,"up")
    exp.SetIpInt(BenServer, BenIntr, "10.0.0.1/24")
    exp.SetArpEntry(BenServer,"10.0.0.2", exp.GetMacByVf(inVF), BenIntr)
    exp.SetArpEntry(BenServer,"10.0.0.3", exp.GetMacByVf(inVF), BenIntr)
    exp.SetArpEntry(BenServer,"10.0.0.4", exp.GetMacByVf(inVF), BenIntr)
    exp.SetArpEntry(BenServer,"10.0.0.5", exp.GetMacByVf(inVF), BenIntr)
    
    exp.SetIpInt(exp.getVmCnx("tenant-green-1"), "ens8", "10.0.0.2/24")
    exp.SetIpInt(exp.getVmCnx("tenant-green-2"), "ens8", "10.0.0.3/24")
    exp.SetIpInt(exp.getVmCnx("tenant-green-3"), "ens8", "10.0.0.4/24")
    exp.SetIpInt(exp.getVmCnx("tenant-green-4"), "ens8", "10.0.0.5/24")
    
    
    exp.SetArpEntry(exp.getVmCnx("tenant-green-1"),"10.0.0.1", exp.GetMacByVf(port_1_Vfs[2]), exp.VfsMatch[port_1_Vfs[3]])
    exp.SetArpEntry(exp.getVmCnx("tenant-green-2"),"10.0.0.1", exp.GetMacByVf(port_1_Vfs[4]), exp.VfsMatch[port_1_Vfs[5]])
    exp.SetArpEntry(exp.getVmCnx("tenant-green-3"),"10.0.0.1", exp.GetMacByVf(port_1_Vfs[6]), exp.VfsMatch[port_1_Vfs[7]])
    exp.SetArpEntry(exp.getVmCnx("tenant-green-4"),"10.0.0.1", exp.GetMacByVf(port_1_Vfs[8]), exp.VfsMatch[port_1_Vfs[9]])
    
    exp.EmailNotify(msg, "is ready", logTimeStamp)
        
    return True
##############################################################################

def phy2vm2vm2phy_SRIOV_TwoOvs(cnx_server, isDPDK, nbrCores, isIsolated):
    
    cpuArray= exp.cpuAllocation(2, nbrCores, isIsolated, True, totalTenantVMs,TenantVmCores, totalCpuCores)    
    exp.HOST_CPU=cpuArray["hostCpu"];
    OvsCpu= cpuArray["ovsCpu"];
    DpdkCpu=cpuArray["ovsDpdk"];
    cpuDpdkPorts= cpuArray["cpuDpdkPorts"];
    TenantVMsCpuArray= cpuArray["TenantVMsCpuArray"];
    OvsVMsCpuArray= cpuArray["OvsVMsCpuArray"];
    
    exp.NicConfig=["1","12"]    
    exp.NicType= "mlx"
    exp.isSRIOV= True
    exp.Server_cnx= cnx_server

    exp.pf_index=0
    exp.pfs=[]
    exp.vfs=[]
    
    exp.scsName= "benchmark: phy2vm2vm2phy_SRIOV_TwoOvs"+"_IsDPDK="+str(isDPDK)+"_IsIsolated="+str(isIsolated)
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
           ("enp3s0f0", "12")
          ]
    
    exp.InitialConfig()
    port_1_Vfs=exp.pfs[0][2]
    
    exp.MyVfs= [
            (port_1_Vfs[0], "0", "off", "vswitch-vm"),
            (port_1_Vfs[1], "0", "off", "vswitch-vm"),
            
            (port_1_Vfs[2], "10", "off", "vswitch-vm"),
            (port_1_Vfs[3], "10", "off", "tenant-green-1"),
            
            
            (port_1_Vfs[4], "20", "off", "vswitch-vm"),
            (port_1_Vfs[5], "20", "off", "tenant-green-2"),
            
            
            (port_1_Vfs[6], "0", "off", "vswitch-vm-2"),
            (port_1_Vfs[7], "0", "off", "vswitch-vm-2"),
            
            (port_1_Vfs[8], "30", "off", "vswitch-vm-2"),
            (port_1_Vfs[9], "30", "off", "tenant-green-3"),
            
            
            (port_1_Vfs[10], "40", "off", "vswitch-vm-2"),
            (port_1_Vfs[11], "40", "off", "tenant-green-4")
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
                        (port_1_Vfs[1], True, cpuDpdkPorts),
                        (port_1_Vfs[2], True, cpuDpdkPorts),
                        (port_1_Vfs[4], True, cpuDpdkPorts)]  
        
            #----------------- OVS-VM_2------------------  
            OvsVmPorts2= [
                        (port_1_Vfs[0], True, cpuDpdkPorts),
                        (port_1_Vfs[1], True, cpuDpdkPorts),
                        (port_1_Vfs[2], True, cpuDpdkPorts),
                        (port_1_Vfs[4], True, cpuDpdkPorts)]  
        

    else:
        
            #----------------- OVS-VM_1------------------    
            OvsVmPorts1= [
                        (port_1_Vfs[6], False),
                        (port_1_Vfs[7], False),
                        (port_1_Vfs[8], False),
                        (port_1_Vfs[10], False)]  
        
            #----------------- OVS-VM_2------------------  
            OvsVmPorts2= [
                        (port_1_Vfs[6], False),
                        (port_1_Vfs[7], False),
                        (port_1_Vfs[8], False),
                        (port_1_Vfs[10], False)] 
        
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
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[3])+","+exp.VfsMatch[port_1_Vfs[2]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[2]]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_1_Vfs[1]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (3)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.3"
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[5])+","+exp.VfsMatch[port_1_Vfs[4]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (4)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[4]]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_1_Vfs[1]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
    
    '''
    OVS Flow Rules for OVS-VM-2:
    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[6]]+",ip,nw_dst=10.0.0.4"
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[9])+","+exp.VfsMatch[port_1_Vfs[8]]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[8]]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_1_Vfs[7]]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (3)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[6]]+",ip,nw_dst=10.0.0.5"
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[11])+","+exp.VfsMatch[port_1_Vfs[10]]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (4)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[10]]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_1_Vfs[7]]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm-2", exp.OVS_PATH,"br0")
    
    ####################### Bench COnfig ################################
    inVF1= port_1_Vfs[0]
    inVF2= port_1_Vfs[6]
    exp.SetInt(BenServer,BenIntr,"up")
    exp.SetIpInt(BenServer, BenIntr, "10.0.0.1/24")
    exp.SetArpEntry(BenServer,"10.0.0.2", exp.GetMacByVf(inVF1), BenIntr)
    exp.SetArpEntry(BenServer,"10.0.0.3", exp.GetMacByVf(inVF1), BenIntr)
    exp.SetArpEntry(BenServer,"10.0.0.4", exp.GetMacByVf(inVF2), BenIntr)
    exp.SetArpEntry(BenServer,"10.0.0.5", exp.GetMacByVf(inVF2), BenIntr)
    
    exp.SetIpInt(exp.getVmCnx("tenant-green-1"), "ens8", "10.0.0.2/24")
    exp.SetIpInt(exp.getVmCnx("tenant-green-2"), "ens8", "10.0.0.3/24")
    exp.SetIpInt(exp.getVmCnx("tenant-green-3"), "ens8", "10.0.0.4/24")
    exp.SetIpInt(exp.getVmCnx("tenant-green-4"), "ens8", "10.0.0.5/24")
    
    
    exp.SetArpEntry(exp.getVmCnx("tenant-green-1"),"10.0.0.1", exp.GetMacByVf(port_1_Vfs[2]), exp.VfsMatch[port_1_Vfs[3]])
    exp.SetArpEntry(exp.getVmCnx("tenant-green-2"),"10.0.0.1", exp.GetMacByVf(port_1_Vfs[4]), exp.VfsMatch[port_1_Vfs[5]])
    exp.SetArpEntry(exp.getVmCnx("tenant-green-3"),"10.0.0.1", exp.GetMacByVf(port_1_Vfs[8]), exp.VfsMatch[port_1_Vfs[9]])
    exp.SetArpEntry(exp.getVmCnx("tenant-green-4"),"10.0.0.1", exp.GetMacByVf(port_1_Vfs[10]), exp.VfsMatch[port_1_Vfs[11]])
    
    
    exp.EmailNotify(msg, "is ready", logTimeStamp)
        
    return True

##############################################################################
        
def phy2vm2vm2phy_SRIOV_FourOvs(cnx_server, isDPDK, nbrCores, isIsolated):
    
    cpuArray= exp.cpuAllocation(4, nbrCores, isIsolated, True, totalTenantVMs,TenantVmCores, totalCpuCores)    
    exp.HOST_CPU=cpuArray["hostCpu"];
    OvsCpu= cpuArray["ovsCpu"];
    DpdkCpu=cpuArray["ovsDpdk"];
    cpuDpdkPorts= cpuArray["cpuDpdkPorts"];
    TenantVMsCpuArray= cpuArray["TenantVMsCpuArray"];
    OvsVMsCpuArray= cpuArray["OvsVMsCpuArray"];
    
    exp.NicConfig=["1","16"]    
    exp.NicType= "mlx"
    exp.isSRIOV= True
    exp.Server_cnx= cnx_server

    exp.pf_index=0
    exp.pfs=[]
    exp.vfs=[]
    
    exp.scsName= "Benchmark: phy2vm2vm2phy_SRIOV_FourOvs"+"_IsDPDK="+str(isDPDK)+"_IsIsolated="+str(isIsolated)
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
           ("enp3s0f0", "16")
          ]
    
    exp.InitialConfig()
    port_1_Vfs=exp.pfs[0][2]
    
    exp.MyVfs= [
            (port_1_Vfs[0], "0", "off", "vswitch-vm"),
            (port_1_Vfs[1], "0", "off", "vswitch-vm"), 
            
            (port_1_Vfs[2], "10", "off", "vswitch-vm"),
            (port_1_Vfs[3], "10", "off", "tenant-green-1"),
            
            
            (port_1_Vfs[4], "0", "off", "vswitch-vm-2"),
            (port_1_Vfs[5], "0", "off", "vswitch-vm-2"),
            
            (port_1_Vfs[6], "20", "off", "vswitch-vm-2"),
            (port_1_Vfs[7], "20", "off", "tenant-green-2"),
           
            
            (port_1_Vfs[8], "0", "off", "vswitch-vm-3"),
            (port_1_Vfs[9], "0", "off", "vswitch-vm-3"),
            
            (port_1_Vfs[10], "30", "off", "vswitch-vm-3"),
            (port_1_Vfs[11], "30", "off", "tenant-green-3"),
            
 
            (port_1_Vfs[12], "0", "off", "vswitch-vm-4"),
            (port_1_Vfs[13], "0", "off", "vswitch-vm-4"),   
            
            (port_1_Vfs[14], "40", "off", "vswitch-vm-4"),
            (port_1_Vfs[15], "40", "off", "tenant-green-4")
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
    
            OvsVmPorts1= [
                        (port_1_Vfs[0], True, cpuDpdkPorts),
                        (port_1_Vfs[1], True, cpuDpdkPorts),
                        (port_1_Vfs[2], True, cpuDpdkPorts)]  

            OvsVmPorts2= [
                        (port_1_Vfs[4], True, cpuDpdkPorts),
                        (port_1_Vfs[5], True, cpuDpdkPorts),
                        (port_1_Vfs[6], True, cpuDpdkPorts)]  
            
            OvsVmPorts3= [
                        (port_1_Vfs[8], True, cpuDpdkPorts),
                        (port_1_Vfs[9], True, cpuDpdkPorts),
                        (port_1_Vfs[10], True, cpuDpdkPorts)]  

            OvsVmPorts4= [
                        (port_1_Vfs[12], True, cpuDpdkPorts),
                        (port_1_Vfs[13], True, cpuDpdkPorts),
                        (port_1_Vfs[14], True, cpuDpdkPorts)]  
    else:
        
            OvsVmPorts1= [
                        (port_1_Vfs[0], False),
                        (port_1_Vfs[1], False),
                        (port_1_Vfs[2], False)]  

            OvsVmPorts2= [
                        (port_1_Vfs[4], False),
                        (port_1_Vfs[5], False),
                        (port_1_Vfs[6], False)]  
            
            OvsVmPorts3= [
                        (port_1_Vfs[8], False),
                        (port_1_Vfs[9], False),
                        (port_1_Vfs[10], False)]  

            OvsVmPorts4= [
                        (port_1_Vfs[12], False),
                        (port_1_Vfs[13], False),
                        (port_1_Vfs[14], False)]
        
    msg= exp.GetScenarioSummary([OvsVmPorts1, OvsVmPorts2, OvsVmPorts3, OvsVmPorts4], OvsCpu, DpdkCpu, DpdkMem, isIsolated)
    exp.EmailNotify(msg, "is beeing prepared", logTimeStamp)
    exp.Logs(msg, logTimeStamp)      
    #----------------------------------------#
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
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.2"
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[3])+","+exp.VfsMatch[port_1_Vfs[2]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[2]]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_1_Vfs[1]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    
    '''
    OVS Flow Rules for OVS-VM-2:
    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[4]]+",ip,nw_dst=10.0.0.3"
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[7])+","+exp.VfsMatch[port_1_Vfs[6]]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[6]]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_1_Vfs[5]]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm-2", exp.OVS_PATH,"br0")
    
    '''
    OVS Flow Rules for OVS-VM-3:
    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[8]]+",ip,nw_dst=10.0.0.4"
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[11])+","+exp.VfsMatch[port_1_Vfs[10]]
    exp.addFlowRule("vswitch-vm-3" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[10]]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_1_Vfs[9]]
    exp.addFlowRule("vswitch-vm-3" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm-3", exp.OVS_PATH,"br0")
    
    '''
    OVS Flow Rules for OVS-VM-4:
    '''
    
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[12]]+",ip,nw_dst=10.0.0.5"
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[15])+","+exp.VfsMatch[port_1_Vfs[14]]
    exp.addFlowRule("vswitch-vm-4" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[14]]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_1_Vfs[13]]
    exp.addFlowRule("vswitch-vm-4" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm-4", exp.OVS_PATH,"br0")
    
    ####################### Bench COnfig ################################
    inVF1= port_1_Vfs[0]
    inVF2= port_1_Vfs[4]
    inVF3= port_1_Vfs[8]
    inVF4= port_1_Vfs[12]
    
    exp.SetInt(BenServer,BenIntr,"up")
    exp.SetIpInt(BenServer, BenIntr, "10.0.0.1/24")
    exp.SetArpEntry(BenServer,"10.0.0.2", exp.GetMacByVf(inVF1), BenIntr)
    exp.SetArpEntry(BenServer,"10.0.0.3", exp.GetMacByVf(inVF2), BenIntr)
    exp.SetArpEntry(BenServer,"10.0.0.4", exp.GetMacByVf(inVF3), BenIntr)
    exp.SetArpEntry(BenServer,"10.0.0.5", exp.GetMacByVf(inVF4), BenIntr)
    
    exp.SetIpInt(exp.getVmCnx("tenant-green-1"), "ens8", "10.0.0.2/24")
    exp.SetIpInt(exp.getVmCnx("tenant-green-2"), "ens8", "10.0.0.3/24")
    exp.SetIpInt(exp.getVmCnx("tenant-green-3"), "ens8", "10.0.0.4/24")
    exp.SetIpInt(exp.getVmCnx("tenant-green-4"), "ens8", "10.0.0.5/24")
    
    exp.SetArpEntry(exp.getVmCnx("tenant-green-1"),"10.0.0.1", exp.GetMacByVf(port_1_Vfs[2]), exp.VfsMatch[port_1_Vfs[3]])
    exp.SetArpEntry(exp.getVmCnx("tenant-green-2"),"10.0.0.1", exp.GetMacByVf(port_1_Vfs[6]), exp.VfsMatch[port_1_Vfs[7]])
    exp.SetArpEntry(exp.getVmCnx("tenant-green-3"),"10.0.0.1", exp.GetMacByVf(port_1_Vfs[10]), exp.VfsMatch[port_1_Vfs[11]])
    exp.SetArpEntry(exp.getVmCnx("tenant-green-4"),"10.0.0.1", exp.GetMacByVf(port_1_Vfs[14]), exp.VfsMatch[port_1_Vfs[15]])
    
    exp.EmailNotify(msg, "is ready", logTimeStamp)
        
    return True




###############################################################################
###############################  vm2vm  #######################################
###############################################################################
    
def vm2vm_Baseline(cnx_server, isDPDK, nbrCores):
    
    cpuArray= exp.cpuAllocation(1, nbrCores, True, False, totalTenantVMs,TenantVmCores, totalCpuCores)
    exp.HOST_CPU=cpuArray["hostCpu"]
    OvsCpu= cpuArray["ovsCpu"]
    DpdkCpu=cpuArray["ovsDpdk"]
    cpuDpdkPorts= cpuArray["cpuDpdkPorts"]
    TenantVMsCpuArray= cpuArray["TenantVMsCpuArray"]
    
    exp.NicType= "mlx"
    exp.isSRIOV= False
    exp.Server_cnx= cnx_server
    
    exp.scsName= "Benchmark: vm2vm_Baseline"+"_IsDPDK="+str(isDPDK)
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
        
        ("6", "br0", "tenant-green-3"),
        ("7", "br0", "tenant-green-3"),
        
        ("9", "br0", "tenant-green-4")
    ]
    
    exp.usedVms = [
            ("tenant-green-1", TenantVMsCpuArray[0], VmRam),
            ("tenant-green-2", TenantVMsCpuArray[1], VmRam),
            ("tenant-green-3", TenantVMsCpuArray[2], VmRam),
            ("tenant-green-4", TenantVMsCpuArray[3], VmRam)
            ]


    if isDPDK:
              exp.PhyPorts= [
                      ("enp3s0f0", "br0", True, cpuDpdkPorts)]
    else:
              exp.PhyPorts= [
                      ("enp3s0f0", "br0")]
        
    
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
    OVS Flow Rules:

    '''
    ############################# Tenant 2 ###################################
    # Flow Rules (1)
    # ---------------------------------------------------------
    match = "in_port=enp3s0f0,ip,nw_dst=10.0.0.3"
    action = "vnet1"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    # Flow Rules (2)
    # ---------------------------------------------------------
    match = "in_port=vnet2"
    action = "vnet4"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)
    
    # Flow Rules (3)
    # ---------------------------------------------------------
    match = "in_port=vnet4"
    action = "enp3s0f0"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)
    
    ############################# Tenant 4 ###################################
    # Flow Rules (1)
    # ---------------------------------------------------------
    match = "in_port=enp3s0f0,ip,nw_dst=10.0.0.5"
    action = "vnet6"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    # Flow Rules (2)
    # ---------------------------------------------------------
    match = "in_port=vnet7"
    action = "vnet9"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)
    
    # Flow Rules (3)
    # ---------------------------------------------------------
    match = "in_port=vnet9"
    action = "enp3s0f0"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    
    # show Flow rules of br0
    exp.showFlowRules(exp.Server_cnx, exp.OVS_PATH, "br0")
    
    ##################################################### 
    exp.SetInt(BenServer,BenIntr,"up")
    exp.SetIpInt(BenServer, BenIntr, "10.0.0.1/24")
    exp.SetArpEntry(BenServer,"10.0.0.3", exp.GenerateMacID("4"), BenIntr)
    exp.SetArpEntry(BenServer,"10.0.0.5", exp.GenerateMacID("9"), BenIntr)
    
    exp.SetIpInt(exp.getVmCnx("tenant-green-2"), "ens8", "10.0.0.3/24")
    exp.SetIpInt(exp.getVmCnx("tenant-green-4"), "ens8", "10.0.0.5/24")
    
    #exp.startL2fwdDpdk(exp.getVmCnx("tenant-green-1"), vswitchMode="vm2vm_Bench_Baseline", nicType="e1000", tenantNumber="1")
    #exp.startL2fwdDpdk(exp.getVmCnx("tenant-green-3"), vswitchMode="vm2vm_Bench_Baseline", nicType="e1000", tenantNumber="3")
    
    exp.SetBridging("tenant-green-1", "ens8", "ens9")
    exp.SetBridging("tenant-green-3", "ens8", "ens9")
    
    
    exp.SetArpEntry(exp.getVmCnx("tenant-green-2"),"10.0.0.1", BenIntrMac, "ens8")
    exp.SetArpEntry(exp.getVmCnx("tenant-green-4"),"10.0.0.1", BenIntrMac, "ens8")
    
    exp.EmailNotify(msg, "is ready", logTimeStamp)
     
    return True
###############################################################################
def vm2vm_SRIOV_OneOvs(cnx_server, isDPDK, nbrCores):

    cpuArray= exp.cpuAllocation(1, nbrCores, True, True, totalTenantVMs,TenantVmCores, totalCpuCores)    
    exp.HOST_CPU=cpuArray["hostCpu"];
    OvsCpu= cpuArray["ovsCpu"];
    DpdkCpu=cpuArray["ovsDpdk"];
    cpuDpdkPorts= cpuArray["cpuDpdkPorts"];
    TenantVMsCpuArray= cpuArray["TenantVMsCpuArray"];
    OvsVMsCpuArray= cpuArray["OvsVMsCpuArray"];
        
    exp.NicConfig=["1","12"]       
    exp.NicType= "mlx"
    exp.isSRIOV= True
    exp.Server_cnx= cnx_server
    
    exp.pf_index=0
    exp.pfs=[]
    exp.vfs=[]
    
    exp.scsName= "benchmark: vm2vm_SRIOV_OneOvs"+"_IsDPDK="+str(isDPDK)
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
           ("enp3s0f0", "12")
          ]
    
    exp.InitialConfig()
    port_1_Vfs=exp.pfs[0][2]
    

    
    exp.MyVfs= [
            (port_1_Vfs[0], "0", "off", "vswitch-vm"),
            (port_1_Vfs[1], "0", "off", "vswitch-vm"),
            
            (port_1_Vfs[2], "10", "off", "vswitch-vm"),
            (port_1_Vfs[3], "10", "off", "tenant-green-1"),
            (port_1_Vfs[10], "10", "off", "tenant-green-1"),
            
            
            (port_1_Vfs[4], "20", "off", "vswitch-vm"),
            (port_1_Vfs[5], "20", "off", "tenant-green-2"),
            

            (port_1_Vfs[6], "30", "off", "vswitch-vm"),
            (port_1_Vfs[7], "30", "off", "tenant-green-3"),
            (port_1_Vfs[11], "10", "off", "tenant-green-3"),
            
            (port_1_Vfs[8], "40", "off", "vswitch-vm"),
            (port_1_Vfs[9], "40", "off", "tenant-green-4")
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
                        (port_1_Vfs[1], True, cpuDpdkPorts),
                        (port_1_Vfs[2], True, cpuDpdkPorts),
                        (port_1_Vfs[4], True, cpuDpdkPorts),
                        (port_1_Vfs[6], True, cpuDpdkPorts),
                        (port_1_Vfs[8], True, cpuDpdkPorts)
                        ]  
        
    else:
        
            #----------------- OVS-VM_1------------------    
            OvsVmPorts1= [
                        (port_1_Vfs[0], False),
                        (port_1_Vfs[1], False),
                        (port_1_Vfs[2], False),
                        (port_1_Vfs[4], False),
                        (port_1_Vfs[6], False),
                        (port_1_Vfs[8], False)]  
        
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
    ############################# Tenant 1 ###################################
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.3"
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[3])+","+exp.VfsMatch[port_1_Vfs[2]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[2]]
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[5])+","+exp.VfsMatch[port_1_Vfs[4]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (3)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[4]]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_1_Vfs[1]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    ############################# Tenant 3 ###################################
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.5"
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[7])+","+exp.VfsMatch[port_1_Vfs[6]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[6]]
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[9])+","+exp.VfsMatch[port_1_Vfs[8]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (3)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[8]]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_1_Vfs[1]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
    
    ####################### Bench COnfig ################################
    inVF= port_1_Vfs[0]
    exp.SetInt(BenServer,BenIntr,"up")
    exp.SetIpInt(BenServer, BenIntr, "10.0.0.1/24")
    
    exp.SetArpEntry(BenServer,"10.0.0.3", exp.GetMacByVf(inVF), BenIntr)
    exp.SetArpEntry(BenServer,"10.0.0.5", exp.GetMacByVf(inVF), BenIntr)
    
   
    exp.SetIpInt(exp.getVmCnx("tenant-green-2"), "ens8", "10.0.0.3/24")
    exp.SetIpInt(exp.getVmCnx("tenant-green-4"), "ens8", "10.0.0.5/24")
    
    
    exp.SetArpEntry(exp.getVmCnx("tenant-green-2"),"10.0.0.1", exp.GetMacByVf(port_1_Vfs[4]), exp.VfsMatch[port_1_Vfs[5]])
    exp.SetArpEntry(exp.getVmCnx("tenant-green-4"),"10.0.0.1", exp.GetMacByVf(port_1_Vfs[8]), exp.VfsMatch[port_1_Vfs[9]])
    
    exp.startL2fwdDpdk(exp.getVmCnx("tenant-green-1"), vswitchMode="vm2vm_SRIOV_1Ovs", nicType="mlx", tenantNumber="1")
    exp.startL2fwdDpdk(exp.getVmCnx("tenant-green-3"), vswitchMode="vm2vm_SRIOV_1Ovs", nicType="mlx", tenantNumber="3")
        
    exp.EmailNotify(msg, "is ready", logTimeStamp)
        
    return True
##############################################################################

def vm2vm_SRIOV_TwoOvs(cnx_server, isDPDK, nbrCores, isIsolated):
    
    cpuArray= exp.cpuAllocation(2, nbrCores, isIsolated, True, totalTenantVMs,TenantVmCores, totalCpuCores)    
    exp.HOST_CPU=cpuArray["hostCpu"];
    OvsCpu= cpuArray["ovsCpu"];
    DpdkCpu=cpuArray["ovsDpdk"];
    cpuDpdkPorts= cpuArray["cpuDpdkPorts"];
    TenantVMsCpuArray= cpuArray["TenantVMsCpuArray"];
    OvsVMsCpuArray= cpuArray["OvsVMsCpuArray"];
    
    exp.NicConfig=["1","14"]    
    exp.NicType= "mlx"
    exp.isSRIOV= True
    exp.Server_cnx= cnx_server

    exp.pf_index=0
    exp.pfs=[]
    exp.vfs=[]
    
    exp.scsName= "benchmark: vm2vm_SRIOV_TwoOvs"+"_IsDPDK="+str(isDPDK)+"_IsIsolated="+str(isIsolated)
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
           ("enp3s0f0", "14")
          ]
    
    exp.InitialConfig()
    port_1_Vfs=exp.pfs[0][2]
    
    exp.MyVfs= [
            (port_1_Vfs[0], "0", "off", "vswitch-vm"),
            (port_1_Vfs[1], "0", "off", "vswitch-vm"),
            
            (port_1_Vfs[2], "10", "off", "vswitch-vm"),
            (port_1_Vfs[3], "10", "off", "tenant-green-1"),
            (port_1_Vfs[12], "10", "off", "tenant-green-1"),
            
            
            (port_1_Vfs[4], "20", "off", "vswitch-vm"),
            (port_1_Vfs[5], "20", "off", "tenant-green-2"),
            
            
            (port_1_Vfs[6], "0", "off", "vswitch-vm-2"),
            (port_1_Vfs[7], "0", "off", "vswitch-vm-2"),
            
            (port_1_Vfs[8], "30", "off", "vswitch-vm-2"),
            (port_1_Vfs[9], "30", "off", "tenant-green-3"),
            (port_1_Vfs[13], "30", "off", "tenant-green-3"),
            
            
            (port_1_Vfs[10], "40", "off", "vswitch-vm-2"),
            (port_1_Vfs[11], "40", "off", "tenant-green-4")
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
                        (port_1_Vfs[1], True, cpuDpdkPorts),
                        (port_1_Vfs[2], True, cpuDpdkPorts),
                        (port_1_Vfs[4], True, cpuDpdkPorts)]  
        
            #----------------- OVS-VM_2------------------  
            OvsVmPorts2= [
                        (port_1_Vfs[0], True, cpuDpdkPorts),
                        (port_1_Vfs[1], True, cpuDpdkPorts),
                        (port_1_Vfs[2], True, cpuDpdkPorts),
                        (port_1_Vfs[4], True, cpuDpdkPorts)]  
        

    else:
        
            #----------------- OVS-VM_1------------------    
            OvsVmPorts1= [
                        (port_1_Vfs[6], False),
                        (port_1_Vfs[7], False),
                        (port_1_Vfs[8], False),
                        (port_1_Vfs[10], False)]  
        
            #----------------- OVS-VM_2------------------  
            OvsVmPorts2= [
                        (port_1_Vfs[6], False),
                        (port_1_Vfs[7], False),
                        (port_1_Vfs[8], False),
                        (port_1_Vfs[10], False)] 
        
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
    match="in_port="+exp.VfsMatch[port_1_Vfs[0]]+",ip,nw_dst=10.0.0.3"
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[3])+","+exp.VfsMatch[port_1_Vfs[2]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[2]]
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[5])+","+exp.VfsMatch[port_1_Vfs[4]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (3)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[4]]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_1_Vfs[1]]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
    
    '''
    OVS Flow Rules for OVS-VM-2:
    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[6]]+",ip,nw_dst=10.0.0.5"
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[9])+","+exp.VfsMatch[port_1_Vfs[8]]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[8]]
    action="mod_dl_dst:"+exp.GetMacByVf(port_1_Vfs[11])+","+exp.VfsMatch[port_1_Vfs[10]]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (3)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch[port_1_Vfs[10]]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch[port_1_Vfs[7]]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm-2", exp.OVS_PATH,"br0")
    
    ####################### Bench COnfig ################################
    inVF1= port_1_Vfs[0]
    inVF2= port_1_Vfs[6]
    exp.SetInt(BenServer,BenIntr,"up")
    exp.SetIpInt(BenServer, BenIntr, "10.0.0.1/24")
    exp.SetArpEntry(BenServer,"10.0.0.3", exp.GetMacByVf(inVF1), BenIntr)
    exp.SetArpEntry(BenServer,"10.0.0.5", exp.GetMacByVf(inVF2), BenIntr)
    
    exp.SetIpInt(exp.getVmCnx("tenant-green-2"), "ens8", "10.0.0.3/24")
    exp.SetIpInt(exp.getVmCnx("tenant-green-4"), "ens8", "10.0.0.5/24")
    
    exp.SetArpEntry(exp.getVmCnx("tenant-green-2"),"10.0.0.1", exp.GetMacByVf(port_1_Vfs[4]), exp.VfsMatch[port_1_Vfs[5]])
    exp.SetArpEntry(exp.getVmCnx("tenant-green-4"),"10.0.0.1", exp.GetMacByVf(port_1_Vfs[10]), exp.VfsMatch[port_1_Vfs[11]])
    
    exp.startL2fwdDpdk(exp.getVmCnx("tenant-green-1"), vswitchMode="vm2vm_SRIOV_2Ovs", nicType="mlx", tenantNumber="1")
    exp.startL2fwdDpdk(exp.getVmCnx("tenant-green-3"), vswitchMode="vm2vm_SRIOV_2Ovs", nicType="mlx", tenantNumber="3")
    
    
    exp.EmailNotify(msg, "is ready", logTimeStamp)
        
    return True
