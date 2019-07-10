#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 11 22:12:05 2018

@author: saad

"""
'''
Scenarios: 
        + Single tenant: 
            + phy2vm2vm2phy_Baseline_NoDPDK 
            + phy2vm2vm2phy_Baseline_DPDK
            + phy2vm2vm2phy_SRIOV_NoDPDK
            + phy2vm2vm2phy_SRIOV_DPDK
            + phy2phy_Baseline_NoDPDK
            + phy2phy_Baseline_DPDK
            + phy2phy_SRIOV_NoDPDK
            + phy2phy_SRIOV_DPDK
        
        
        +multi tenant:
            + phy2vm2vm2phy_Baseline_MultiTenant_NoDPDK
            + phy2vm2vm2phy_Baseline_MultiTenant_DPDK 
            + phy2vm2vm2phy_SRIOV_MultiTenant_NoDPDK
            + phy2vm2vm2phy_SRIOV_MultiTenant_DPDK   
            + phy2vm2vm2phy_SRIOV_MultiOvs_NoDPDK    
            + phy2vm2vm2phy_SRIOV_MultiOvs_DPDK      
            
            + phy2phy_Baseline_MultiTenant_NoDPDK
            + phy2phy_Baseline_MultiTenant_DPDK
            + phy2phy_SRIOV_MultiTenant_NoDPDK
            + phy2phy_SRIOV_MultiTenant_DPDK
            + phy2phy_SRIOV_MultiOvs_NoDPDK
            + phy2phy_SRIOV_MultiOvs_DPDK            
'''

import expLib as exp
import smtplib
from datetime import datetime
import os
import errno
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


###########################################################################################
####################################---Scenario Specific Data---###########################
###########################################################################################
# Server CPU
MaxCpu= 8

#cpu isolation
IsCpusIsolated=True

#Destination MAC (needed for Flow Rules)
outDestMac="00:00:00:00:30:56"


#cpu_array=[Host	 ,Vswitch VM	,Tenant VM	,ovs-vswitchd	,dpdk-vswitch ,dpdk-tenant, OVS-VM count, Tenents per OVS]
CpuData= []

################################ single tenant ################################
CpuData.append(["phy2phy",      "Baseline_NoDPDK",                      [2	,0	,0	,0	,0	,0, 0 ,0]])
CpuData.append(["phy2phy",      "Baseline_DPDK",                        [2	,0	,0	,0	,1	,0, 0 ,0]])

CpuData.append(["phy2phy",      "SRIOV_NoDPDK",                         [1	,2	,0	,0	,0	,0, 1, 0]])
CpuData.append(["phy2phy",      "SRIOV_DPDK",                           [1	,1	,0	,0	,1	,0, 1, 0]])

#-------------------------------------------------------------------------------------------------------

CpuData.append(["phy2vm2vm2phy", "Baseline_NoDPDK",                     [2	,0	,2	,0	,0	,0, 0, 1]])
CpuData.append(["phy2vm2vm2phy", "Baseline_DPDK",                       [2	,0	,2	,0	,1	,0, 0, 1]])

CpuData.append(["phy2vm2vm2phy", "SRIOV_NoDPDK",                        [1	,2	,2	,0	,0	,0, 1, 1]])
CpuData.append(["phy2vm2vm2phy", "SRIOV_DPDK",                          [1	,1	,2	,0	,1	,0, 1, 1]])

################################ Multi tenant ################################

CpuData.append(["phy2phy",      "Baseline_MultiTenant_NoDPDK",          [2	,0	,0	,0	,0	,0, 0 ,0]])
CpuData.append(["phy2phy",      "Baseline_MultiTenant_DPDK",            [2	,0	,0	,0	,1	,0, 0 ,0]])

CpuData.append(["phy2phy",      "SRIOV_MultiTenant_NoDPDK",             [1	,2	,0	,0	,0	,0, 1, 0]])
CpuData.append(["phy2phy",      "SRIOV_MultiTenant_DPDK",               [1	,1	,0	,0	,1	,0, 1, 0]])

CpuData.append(["phy2phy",      "SRIOV_MultiOvs_NoDPDK",                [1	,2	,0	,0	,0	,0, 2, 0]])
CpuData.append(["phy2phy",      "SRIOV_MultiOvs_DPDK",                  [1	,1	,0	,0	,1	,0, 2, 0]])

#-------------------------------------------------------------------------------------------------------

CpuData.append(["phy2vm2vm2phy", "Baseline_MultiTenant_NoDPDK",         [2	,0	,2	,0	,0	,0, 0, 2]])
CpuData.append(["phy2vm2vm2phy", "Baseline_MultiTenant_DPDK",           [2	,0	,2	,0	,1	,0, 0, 2]])

CpuData.append(["phy2vm2vm2phy", "SRIOV_MultiTenant_NoDPDK",            [1	,2	,2	,0	,0	,0, 1, 2]])
CpuData.append(["phy2vm2vm2phy", "SRIOV_MultiTenant_DPDK",              [1	,1	,2	,0	,1	,0, 1, 2]])

CpuData.append(["phy2vm2vm2phy", "SRIOV_MultiOvs_NoDPDK",               [1	,2	,2	,0	,0	,0, 2, 1]])
CpuData.append(["phy2vm2vm2phy", "SRIOV_MultiOvs_DPDK",                 [1	,1	,2	,0	,1	,0, 2, 1]])


###########################################################################################
####################################---Helper Functions---#################################
###########################################################################################

def Logs(Summary,cpuArray, time):
    
    exp.CmdLogPath= "./ExpLib_logs/"+time+"/"+exp.scsName+"_"+exp.Server_cnx[0]+"_"+str(cpuArray)+"_.txt"
    exp.SummaryPath= "./ExpLib_logs/"+time+"/summary.txt"
    
    if not os.path.exists(os.path.dirname(exp.SummaryPath)):
        try:
            os.makedirs(os.path.dirname(exp.SummaryPath))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
                
    with open(exp.SummaryPath, "w") as f:
        f.write(Summary)
        f.close()
                
def CpuArrayFinder(ScsName, dpdk_vswitch_cores):
    for d in CpuData:
        if d[0]==ScsName and d[1]==dpdk_vswitch_cores:
            return d[2]



#cpu_array=[Host	 ,Vswitch VM	,Tenant VM	,ovs-vswitchd	,dpdk-vswitch ,dpdk-tenant, OVS-VM count, Tenents per OVS]
def CpuAllocation(config):
    exp.HOST_CPU=str(config[0])
    ovsVmCpuListArray=[]
    tenantVmCpuListArray=[]

    if config[1]!=0:
        
        if config[6]==1:
        
            ovsHostCpuCount= config[0]
            ovsVmCpuCount= config[1] +config[3] +config[4] 
            tenantVmCpuCount=  config[2] +config[5] 
    
            ovsVmCpuList = range(ovsHostCpuCount,ovsVmCpuCount+ovsHostCpuCount)
            ovsVmCpuListArray.append(ovsVmCpuList)
            
            start= ovsVmCpuCount+ovsHostCpuCount
            end=ovsVmCpuCount+ovsHostCpuCount
            for i in range(config[7]):
                start=end
                end=end + tenantVmCpuCount
                tenantVmCpuList = range(start,end)
                tenantVmCpuListArray.append(tenantVmCpuList)
            
            vSwitchdCpuList= range(config[1]+config[3])
            dpdkVswitchCpu= range(config[1]+config[3], config[1]+config[3]+config[4])
    
            vSwitchdCpuStr= ','.join(str(c) for c in vSwitchdCpuList)  
            OvsCpu=[vSwitchdCpuStr, vSwitchdCpuStr]
            
            DpdkCpu=[ovsVmCpuCount,dpdkVswitchCpu]
            
        else:
            ovsHostCpuCount= config[0]
            ovsVmCpuCount= config[1] +config[3] +config[4] 
            tenantVmCpuCount=  config[2] +config[5] 
            
            if IsCpusIsolated:
                ovsVmCpuCount= ovsVmCpuCount-1
                start=ovsHostCpuCount
                end=ovsHostCpuCount
                for i in range(config[6]):
                    start=end
                    end=end + ovsVmCpuCount
                    ovsVmCpuList = range(start,end)
                    ovsVmCpuListArray.append(ovsVmCpuList)
                
            else:       
                start=ovsHostCpuCount
                end=ovsHostCpuCount+ ovsVmCpuCount
                for i in range(config[6]):
                    ovsVmCpuList = range(start,end)
                    ovsVmCpuListArray.append(ovsVmCpuList)
                    
            Tstart=end
            Tend=end
            for i in range(config[6]):
               Tstart= Tend
               Tend=  Tend + tenantVmCpuCount
               tenantVmCpuList = range(Tstart,Tend)
               tenantVmCpuListArray.append(tenantVmCpuList)
                             
            if IsCpusIsolated:
                 dpdkVswitchCpu= range(ovsVmCpuCount)
                 if config[1]+config[3]>1:
                     vSwitchdCpuList= range(config[1]+config[3]-1)
                 else:
                     vSwitchdCpuList= range(config[1]+config[3])
            else:
                 dpdkVswitchCpu= range(config[1]+config[3], config[1]+config[3]+config[4])
                 vSwitchdCpuList= range(config[1]+config[3])
                
            vSwitchdCpuStr= ','.join(str(c) for c in vSwitchdCpuList)  
            OvsCpu=[vSwitchdCpuStr, vSwitchdCpuStr]   
            DpdkCpu=[ovsVmCpuCount,dpdkVswitchCpu]
            
    else:
        ovsCpuCount= config[3] +config[4] 
        
        if ovsCpuCount>0: 
            ovsHostCpuCount= config[0] -1
        else:
            ovsHostCpuCount= config[0]
                    
        tenantVmCpuCount=  config[2] +config[5] 
        
        vSwitchdCpuList= range(ovsHostCpuCount)
        dpdkVswitchCpu= range(ovsHostCpuCount, ovsHostCpuCount +config[4])
          
        ovsVmCpuList=[]
        ovsVmCpuListArray.append(ovsVmCpuList)
        
        start= ovsCpuCount+ovsHostCpuCount
        end=ovsCpuCount+ovsHostCpuCount
        for i in range(config[7]):
            start=end
            end=end + tenantVmCpuCount
            tenantVmCpuList = range(start,end)
            tenantVmCpuListArray.append(tenantVmCpuList)
                                  
        vSwitchdCpuStr= ','.join(str(c) for c in vSwitchdCpuList)  
        OvsCpu=[vSwitchdCpuStr, vSwitchdCpuStr]
        
        DpdkCpu=[MaxCpu ,dpdkVswitchCpu]
        
    return [ovsVmCpuListArray, tenantVmCpuListArray, OvsCpu, DpdkCpu]
        

def EmailNotify(body, state, time, attachmentPath=""):
            
    subject = time+": "+exp.scsName+" "+state+" on "+exp.Server_cnx[0]
    
    # Sign In
    gmail_sender = 'XXX'
    gmail_passwd = 'XXX'
    
    #Receivers
    receivers = "XXX"
    
    subject = time+": "+exp.scsName+" "+state+" on "+exp.Server_cnx[0]
    
    msg = MIMEMultipart()
    msg['From'] = gmail_sender
    msg['To'] = receivers
    msg['Subject'] = subject
    
    
    msg.attach(MIMEText(body))
    
    if(attachmentPath!=""):    
        attachment  =open(attachmentPath,'rb')    
        part = MIMEBase('application','octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',"attachment; filename= "+attachmentPath)
        msg.attach(part)
    
    text = msg.as_string()
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login(gmail_sender,gmail_passwd)
    
    try:
        server.sendmail(gmail_sender, receivers.split(","), text)
    except:
        print ('error sending mail')
    
    server.quit()   
    
def GetScenarioSummary(OvsVmPorts, OvsCpu, DpdkCpu, DpdkMem):    
    
    SummaryMsg="Scenario Name: "+exp.scsName+"\n"
    SummaryMsg= SummaryMsg+ "Nic : "+ str(exp.NicType)+"\n"
    SummaryMsg= SummaryMsg+ "Is OVS running with DPDK : "+str(exp.IsDPDK)+"\n"
    SummaryMsg= SummaryMsg+ "Is SR-IOV enabled : "+str(exp.isSRIOV)+"\n"
    SummaryMsg= SummaryMsg+ "CPU Isolation : "+str(IsCpusIsolated)+"\n"
    SummaryMsg= SummaryMsg+ " \n \n"
    
    SummaryMsg= SummaryMsg+ "Physical Ports config: \n"
    if exp.isSRIOV:
        for p in exp.PhyPorts: 
             SummaryMsg= SummaryMsg+ "     +port "+p[0]+" has "+p[1]+" configured Vfs \n"
    else:
        if exp.IsDPDK:
            for p in exp.PhyPorts:
                SummaryMsg= SummaryMsg+ "     +port "+p[0]+"  assigned to:"+p[1]+" as a DPDK port on Core"+p[3]+" \n"
        else:
            for p in exp.PhyPorts:    
                SummaryMsg= SummaryMsg+ "     +port "+p[0]+"  assigned to:"+p[1]+" \n"
     
    
    SummaryMsg= SummaryMsg+ " \n \n"    
            
    if exp.isSRIOV:
        SummaryMsg= SummaryMsg+ "Vfs config: \n"
        for vf in exp.MyVfs:
            SummaryMsg= SummaryMsg+ "     +"+vf[0]+"   Vlan: "+vf[1]+" Spoofchk: "+vf[2]+"  asssigned to "+vf[3]+"\n"
    
    else:
        if len(exp.VirtualPorts)!=0:
            SummaryMsg= SummaryMsg+ "Virtual ports config: \n"
            for vp in exp.VirtualPorts:
                SummaryMsg= SummaryMsg+ "     +Mac Id: "+vp[0]+"   assigned to bridge: "+vp[1]+"  assigned to: "+vp[2]+"\n"
                
            
    SummaryMsg= SummaryMsg+ " \n \n" 
    
    if len(exp.usedVms)!=0:
        SummaryMsg= SummaryMsg+ "VMs config: \n"
        for vm in exp.usedVms:
            SummaryMsg= SummaryMsg+ "     +"+vm[0]+"  Running on cores:"+str(vm[1])+"  RAM: "+vm[2]+"\n"
            
    SummaryMsg= SummaryMsg+ " \n \n" 
    
    SummaryMsg= SummaryMsg+ "OVS CPU Config: \n" 
    SummaryMsg= SummaryMsg+ "     +OVSDb:  "+OvsCpu[0]+" \n"
    SummaryMsg= SummaryMsg+ "     +Vswitchd:  "+OvsCpu[1]+" \n"
    
    if exp.IsDPDK:
        SummaryMsg= SummaryMsg+ "     +OVS-DPDK:  "+str(DpdkCpu[1])+" \n"
        SummaryMsg= SummaryMsg+ "     +DPDK Memory:  "+DpdkMem+" \n"
            
    SummaryMsg= SummaryMsg+ " \n \n" 
        
    if exp.isSRIOV and len(OvsVmPorts)!=0:
        SummaryMsg= SummaryMsg+ "OVS VM(s) Config: \n"
        indx=1
        for pl in OvsVmPorts: 
            SummaryMsg= SummaryMsg+ "OVS-VM "+str(indx)+" Config: \n"
            indx=indx+1
            for vmp in pl:
                if vmp[1]==True:
                    SummaryMsg= SummaryMsg+ "     +vf "+vmp[0]+"  is a DPDK port Running on cores:"+vmp[2]+"\n"
                else:
                    SummaryMsg= SummaryMsg+ "     +vf "+vmp[0]+"\n"
                    
    return SummaryMsg  


###########################################################################################
####################################---Scenarios---########################################
###########################################################################################
    
###########################################################################################
####################################---Single Tenant VM---#################################
###########################################################################################
    
def phy2vm2vm2phy_SRIOV_DPDK(cnx_server, config, dpdkMemory="1024,0"):
        
    #----------------------------------------#
    exp.NicType= "mlx"
    exp.isSRIOV= True
    exp.IsDPDK= True
    exp.OVS_PATH= exp.dpdk_path
    exp.Server_cnx= cnx_server
    exp.scsName= "phy2vm2vm2phy_SRIOV_DPDK"
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    #----------------------------------------#
    cpu_config= CpuAllocation(config)
    
    exp.PhyPorts= [
           ("enp3s0f0", "8"),
           ("enp3s0f1", "8")
          ]
    
    exp.MyVfs= [
            ("enp3s0f2", "0", "off", "vswitch-vm"),
            ("enp3s1f2", "0", "off", "vswitch-vm"),
            ("enp3s1f3", "10", "off", "vswitch-vm"),
            ("enp3s0f3", "10", "off", "vswitch-vm"),
            ("enp3s0f4", "10", "off", "tenant-green-1"),
            ("enp3s1f4", "10", "off", "tenant-green-1")]
    
    exp.usedVms=[
             ("vswitch-vm", cpu_config[0][0], "4G"),
             ("tenant-green-1", cpu_config[1][0], "4G")]
    
    #----------------- OVS-VM_1------------------
    OvsCpu= cpu_config[2]
    DpdkCpu= cpu_config[3]
    DpdkMem= dpdkMemory
    
    if len(DpdkCpu[1]) >1:
    
        OvsVmPorts1= [
                ("enp3s0f2", True, str(DpdkCpu[1][0])),
                ("enp3s1f2", True, str(DpdkCpu[1][0])),
                ("enp3s1f3", True, str(DpdkCpu[1][1])),
                ("enp3s0f3", True, str(DpdkCpu[1][1]))]   
    else:
        OvsVmPorts1= [
                ("enp3s0f2", True, str(DpdkCpu[1][0])),
                ("enp3s1f2", True, str(DpdkCpu[1][0])),
                ("enp3s1f3", True, str(DpdkCpu[1][0])),
                ("enp3s0f3", True, str(DpdkCpu[1][0]))]
        
    
    msg= GetScenarioSummary([OvsVmPorts1], OvsCpu, DpdkCpu, DpdkMem)
    EmailNotify(msg, "is beeing prepared", logTimeStamp)
    Logs(msg,config, logTimeStamp)
    #----------------------------------------#
    exp.InitialConfig()
    exp.Vfsconfig()
    exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu, DpdkMem, DpdkCpu)
    
    '''
    OVS Flow Rules:
    + (1) in: enp3s0f2 with ip:10.0.0.2--> out= enp3s0f3, change Mac to enp3s0f4 mac
    + (2) in: enp3s1f3    --> out= enp3s1f2,  change Mac to 00:00:00:00:30:56 

    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f2"]+",ip,nw_dst=10.0.0.2"
    action="mod_dl_dst:"+exp.GetMacByVf("enp3s0f4")+","+exp.VfsMatch["enp3s0f3"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s1f3"]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch["enp3s1f2"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
    
    #Start DPDK App in The tenantVM
    #exp.StartDpdkApp("tenant-green-1")
    
    EmailNotify(msg, "is ready", logTimeStamp)
    return True


def phy2vm2vm2phy_SRIOV_NoDPDK(cnx_server, config):
    #----------------------------------------#
    exp.NicType= "mlx"
    exp.isSRIOV= True
    exp.IsDPDK= False
    exp.OVS_PATH= exp.nodpdk_path
    exp.Server_cnx= cnx_server
    exp.scsName= "phy2vm2vm2phy_SRIOV_NoDPDK"
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    #----------------------------------------#
    cpu_config= CpuAllocation(config)
    
    exp.PhyPorts= [
           ("enp3s0f0", "8"),
           ("enp3s0f1", "8")
          ]
    
    exp.MyVfs= [
            ("enp3s0f2", "0", "off", "vswitch-vm"),
            ("enp3s1f2", "0", "off", "vswitch-vm"),
            ("enp3s1f3", "10", "off", "vswitch-vm"),
            ("enp3s0f3", "10", "off", "vswitch-vm"),
            ("enp3s0f4", "10", "off", "tenant-green-1"),
            ("enp3s1f4", "10", "off","tenant-green-1")]
    
    exp.usedVms=[
             ("vswitch-vm", cpu_config[0][0], "4G"),
             ("tenant-green-1", cpu_config[1][0], "4G")]
    
    #----------------- OVS-VM_1------------------
    OvsCpu= cpu_config[2]
    OvsVmPorts1= [
            ("enp3s0f2", False),
            ("enp3s1f2", False),
            ("enp3s1f3", False),
            ("enp3s0f3", False)]   
    
    
    msg= GetScenarioSummary([OvsVmPorts1], OvsCpu, [], "")
    EmailNotify(msg, "is beeing prepared", logTimeStamp)
    Logs(msg,config, logTimeStamp)
    #----------------------------------------#
    exp.InitialConfig()
    exp.Vfsconfig()
    exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu)
    
    '''
    OVS Flow Rules:
    + (1) in: enp3s0f2 with ip:10.0.0.2 --> out= enp3s0f3, change Mac to enp3s0f4 mac
    + (2) in: enp3s1f3    --> out= enp3s1f2,  change Mac to 00:00:00:00:30:56 

    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f2"]+",ip,nw_dst=10.0.0.2"
    action="mod_dl_dst:"+exp.GetMacByVf("enp3s0f4")+","+exp.VfsMatch["enp3s0f3"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s1f3"]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch["enp3s1f2"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
    
    #Start DPDK App in The tenantVM
    #exp.StartDpdkApp("tenant-green-1")
    
    EmailNotify(msg, "is ready", logTimeStamp)
    return True
    

def phy2vm2vm2phy_Baseline_NoDPDK(cnx_server, config):
    # ----------------------------------------#
    exp.NicType = "mlx"
    exp.isSRIOV = False
    exp.IsDPDK = False
    exp.OVS_PATH = exp.nodpdk_path
    exp.Server_cnx = cnx_server
    exp.scsName= "phy2vm2vm2phy_Baseline_NoDPDK"
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


    # ----------------------------------------#
    cpu_config= CpuAllocation(config)
    
    exp.PhyPorts = [
        ("enp3s0f0", "br0"),
        ("enp3s0f1", "br0")
    ]

    exp.VirtualPorts = [
        ("1", "br0", "tenant-green-1"),
        ("2", "br0", "tenant-green-1")
    ]

    exp.usedVms = [
        ("tenant-green-1", cpu_config[1][0], "4G")]

    OvsCpu = cpu_config[2]
    
    
    msg= GetScenarioSummary([], OvsCpu, [], "")
    EmailNotify(msg, "is beeing prepared", logTimeStamp)
    Logs(msg,config, logTimeStamp)
    # ----------------------------------------#
    exp.InitialConfig()
    exp.ConfigOVS(exp.Server_cnx, "br0", " ", OvsCpu)
    exp.VirPortConfig()

    '''
    OVS Flow Rules:
        + (1) in: enp3s0f0 with ip: 10.0.0.2 --> out= vnet1
        + (2) in: vnet2    --> out= enp3s0f1

    '''
    # Flow Rules (1)
    # ---------------------------------------------------------
    match = "in_port=enp3s0f0,ip,nw_dst=10.0.0.2"
    action = "vnet1"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    # Flow Rules (2)
    # ---------------------------------------------------------
    match = "in_port=vnet2"
    action = "enp3s0f1"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    # show Flow rules of br0
    exp.showFlowRules(exp.Server_cnx, exp.OVS_PATH, "br0")
    
    #Tenant-Vm Bridge
    #exp.SetBridging("tenant-green-1", exp.VirPortsMatch["1"], exp.VirPortsMatch["2"])
    
    EmailNotify(msg, "is ready", logTimeStamp)
    return True

# Not tested !!!
def phy2vm2vm2phy_Baseline_DPDK(cnx_server, config, dpdkMemory="1024,0"):
    # ----------------------------------------#
    exp.NicType = "mlx"
    exp.isSRIOV = False
    exp.IsDPDK = True
    exp.OVS_PATH = exp.dpdk_path
    exp.Server_cnx = cnx_server
    exp.scsName= "phy2vm2vm2phy_Baseline_DPDK"
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # ----------------------------------------#
    cpu_config= CpuAllocation(config)
        
    exp.VirtualPorts = [
        ("1", "br0", "tenant-green-1"),
        ("2", "br0", "tenant-green-1")
    ]
    
    exp.usedVms = [
        ("tenant-green-1", cpu_config[1][0], "4G")]

    OvsCpu = cpu_config[2]
    DpdkCpu= cpu_config[3]
    DpdkMem= dpdkMemory
    
                 
    if len(DpdkCpu[1]) >1:   
              exp.PhyPorts= [
                      ("enp3s0f0", "br0", True,  str(DpdkCpu[1][0])),
                      ("enp3s0f1", "br0", True,  str(DpdkCpu[1][0]))]

                                                                             
    else:
              exp.PhyPorts= [
                      ("enp3s0f0", "br0", True,  str(DpdkCpu[1][0])),
                      ("enp3s0f1", "br0", True,  str(DpdkCpu[1][0]))]

                            
    msg= GetScenarioSummary([], OvsCpu, DpdkCpu, DpdkMem)
    EmailNotify(msg, "is beeing prepared", logTimeStamp) 
    Logs(msg,config, logTimeStamp)
    # ----------------------------------------#
    exp.InitialConfig(True)
    exp.ConfigOVS(exp.Server_cnx, "br0", " ", OvsCpu, DpdkMem, DpdkCpu)
    exp.VirPortConfig()

    '''
    OVS Flow Rules:
        + (1) in: enp3s0f0 with ip:10.0.0.2 --> out= vnet1
        + (2) in: vnet2    --> out= enp3s0f1

    '''
    # Flow Rules (1)
    # ---------------------------------------------------------
    match = "in_port=enp3s0f0,ip,nw_dst=10.0.0.2"
    action = "vnet1"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    # Flow Rules (2)
    # ---------------------------------------------------------
    match = "in_port=vnet2"
    action = "enp3s0f1"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    # show Flow rules of br0
    exp.showFlowRules(exp.Server_cnx, exp.OVS_PATH, "br0")
        
    #Start DPDK App

    #Change it To DPDK App
    
    EmailNotify(msg, "is ready", logTimeStamp)
    return True


def phy2phy_SRIOV_DPDK(cnx_server, config, dpdkMemory="1024,0"):
        #----------------------------------------#
    exp.NicType= "mlx"
    exp.isSRIOV= True
    exp.IsDPDK= True
    exp.OVS_PATH= exp.dpdk_path
    exp.Server_cnx= cnx_server
    exp.scsName= "phy2phy_SRIOV_DPDK"
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


    #----------------------------------------#
    cpu_config= CpuAllocation(config)
    
    exp.PhyPorts= [
           ("enp3s0f0", "8"),
           ("enp3s0f1", "8")
          ]
    
    exp.MyVfs= [
            ("enp3s0f2", "0", "off", "vswitch-vm"),
            ("enp3s1f2", "0", "off", "vswitch-vm")]
    
    exp.usedVms=[
             ("vswitch-vm", cpu_config[0][0], "4G")]
    
    #----------------- OVS-VM_1------------------
    OvsCpu= cpu_config[2]
    DpdkCpu= cpu_config[3]
    DpdkMem= dpdkMemory
    
    if len(DpdkCpu[1]) >1:    
        OvsVmPorts1= [
                ("enp3s0f2", True, str(DpdkCpu[1][0])),
                ("enp3s1f2", True, str(DpdkCpu[1][1]))]   
        
    else:
        OvsVmPorts1= [
                ("enp3s0f2", True, str(DpdkCpu[1][0])),
                ("enp3s1f2", True, str(DpdkCpu[1][0]))]  
     
    msg= GetScenarioSummary([OvsVmPorts1], OvsCpu, DpdkCpu, DpdkMem)
    EmailNotify(msg, "is beeing prepared", logTimeStamp)
    Logs(msg,config, logTimeStamp)
    #-------------------------------------------
    
    exp.InitialConfig()
    exp.Vfsconfig()
    exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu, DpdkMem, DpdkCpu)
    
    '''
    OVS Flow Rules:
    + (1) in: enp3s0f2 with ip:10.0.0.2 --> out= enp3s1f2, change Mac to 00:00:00:00:30:56

    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f2"]+",ip,nw_dst=10.0.0.2"
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch["enp3s1f2"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
    
    EmailNotify(msg, "is ready", logTimeStamp)
    return True


def phy2phy_SRIOV_NoDPDK(cnx_server, config):
    #----------------------------------------#
    exp.NicType= "mlx"
    exp.isSRIOV= True
    exp.IsDPDK= False
    exp.OVS_PATH= exp.nodpdk_path
    exp.Server_cnx= cnx_server
    exp.scsName= "phy2phy_SRIOV_NoDPDK"
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    
    #----------------------------------------#
    cpu_config= CpuAllocation(config)
    
    exp.PhyPorts= [
           ("enp3s0f0", "8"),
           ("enp3s0f1", "8")
          ]
    
    exp.MyVfs= [
            ("enp3s0f2", "0", "off", "vswitch-vm"),
            ("enp3s1f2", "0", "off", "vswitch-vm")]
    
    exp.usedVms=[
             ("vswitch-vm", cpu_config[0][0], "4G")]
    
    #----------------- OVS-VM_1------------------
    OvsCpu1= cpu_config[2]
    OvsVmPorts1= [
            ("enp3s0f2", False),
            ("enp3s1f2", False)]   

    
    msg= GetScenarioSummary([OvsVmPorts1], OvsCpu1, [], "")
    EmailNotify(msg, "is beeing prepared", logTimeStamp)
    Logs(msg,config, logTimeStamp)
    
    exp.InitialConfig()
    exp.Vfsconfig()
    exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu1)
    
    '''
    OVS Flow Rules:
    + (1) in: enp3s0f2 with ip:10.0.0.2 --> out= enp3s1f2, change Mac to 00:00:00:00:30:56

    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f2"]+",ip,nw_dst=10.0.0.2"
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch["enp3s1f2"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
    
    EmailNotify(msg, "is ready", logTimeStamp)
    return True


def phy2phy_Baseline_NoDPDK(cnx_server, config):
     #----------------------------------------#
     exp.NicType= "mlx"
     exp.isSRIOV= False
     exp.IsDPDK= False
     exp.OVS_PATH= exp.nodpdk_path
     exp.Server_cnx= cnx_server
     exp.scsName= "phy2phy_Baseline_NoDPDK"
     logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
     
     #----------------------------------------#
     cpu_config= CpuAllocation(config)
     
     exp.PhyPorts= [
             ("enp3s0f0", "br0"),
             ("enp3s0f1", "br0")  
             ]
     
     exp.VirtualPorts=[]
     
     #no Vm is used in this topology
     exp.usedVms=[]
     
     #no Vfs ir virtual portes are needed in this topology
     Ports=[]
     
     OvsCpu= cpu_config[2]
     
     
     msg= GetScenarioSummary([], OvsCpu, [], "")
     EmailNotify(msg, "is beeing prepared", logTimeStamp)
     Logs(msg,config, logTimeStamp)
     #----------------------------------------#
     
     exp.InitialConfig()
     exp.ConfigOVS(exp.Server_cnx, "br0",  Ports, OvsCpu)
     
     '''
     OVS Flow Rules:
         + (1) in: enp3s0f0 with ip:10.0.0.2 --> out= enp3s0f1
     '''
     #Flow Rules (1)
     #---------------------------------------------------------   
     match="in_port=enp3s0f0,ip,nw_dst=10.0.0.2"
     action="enp3s0f1"
     exp.addFlowRule(exp.Server_cnx , exp.OVS_PATH, "br0", match, action) 


     #show Flow rules of br0 
     exp.showFlowRules(exp.Server_cnx, exp.OVS_PATH, "br0")
     
     EmailNotify(msg, "is ready", logTimeStamp)
     return True

# Not tested !!!
def phy2phy_Baseline_DPDK(cnx_server, config, dpdkMemory="1024,0"):
     #----------------------------------------#
     exp.NicType= "mlx"
     exp.isSRIOV= False
     exp.IsDPDK= True
     exp.OVS_PATH= exp.dpdk_path
     exp.Server_cnx= cnx_server
     exp.scsName= "phy2phy_Baseline_DPDK"
     logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
     
     #----------------------------------------#
     cpu_config= CpuAllocation(config)
          
     exp.VirtualPorts=[]
     
     #no Vm is used in this topology
     exp.usedVms=[]
     
     #no Vfs ir virtual portes are needed in this topology
     Ports=[]
     
     OvsCpu= cpu_config[2]
     DpdkCpu= cpu_config[3]
     DpdkMem= dpdkMemory
             
     if len(DpdkCpu[1]) >1:   
              exp.PhyPorts= [
                      ("enp3s0f0", "br0", True,  str(DpdkCpu[1][0])),
                      ("enp3s0f1", "br0", True,  str(DpdkCpu[1][1]))]

     else:
              exp.PhyPorts= [
                      ("enp3s0f0", "br0", True,  str(DpdkCpu[1][0])),
                      ("enp3s0f1", "br0", True,  str(DpdkCpu[1][0]))]
              
      
     msg= GetScenarioSummary([], OvsCpu, DpdkCpu, DpdkMem)
     EmailNotify(msg, "is beeing prepared", logTimeStamp)
     Logs(msg,config, logTimeStamp)
     
     #----------------------------------------#
     
     exp.InitialConfig(True)
     exp.ConfigOVS(exp.Server_cnx, "br0",  Ports, OvsCpu, DpdkMem, DpdkCpu)
      
     '''
     OVS Flow Rules:
         + (1) in: enp3s0f0 with ip:10.0.0.2 --> out= enp3s0f1
     '''
     #Flow Rules (1)
     #---------------------------------------------------------   
     match="in_port=enp3s0f0,ip,nw_dst=10.0.0.2"
     action="enp3s0f1"
     exp.addFlowRule(exp.Server_cnx , exp.OVS_PATH, "br0", match, action) 

     #show Flow rules of br0 
     exp.showFlowRules(exp.Server_cnx, exp.OVS_PATH, "br0")
     
     EmailNotify(msg, "is ready", logTimeStamp)
     return True


###########################################################################################
####################################---Multi Tenant VMs---#################################
###########################################################################################
    
def phy2vm2vm2phy_SRIOV_MultiOvs_DPDK(cnx_server, config, dpdkMemory="1024,0"):
        
    #----------------------------------------#
    exp.NicType= "mlx"
    exp.isSRIOV= True
    exp.IsDPDK= True
    exp.OVS_PATH= exp.dpdk_path
    exp.Server_cnx= cnx_server
    exp.scsName= "phy2vm2vm2phy_SRIOV_MultiOvs_DPDK"
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    #----------------------------------------#
    cpu_config= CpuAllocation(config)
    
    exp.PhyPorts= [
           ("enp3s0f0", "8"),
           ("enp3s0f1", "8")
          ]
    
    exp.MyVfs= [
            ("enp3s0f2", "0", "off", "vswitch-vm"),
            ("enp3s1f2", "0", "off", "vswitch-vm"),
            ("enp3s1f3", "10", "off", "vswitch-vm"),
            ("enp3s0f3", "10", "off", "vswitch-vm"),
            ("enp3s0f4", "10", "off", "tenant-green-1"),
            ("enp3s1f4", "10", "off", "tenant-green-1"),
            
            ("enp3s0f5", "0", "off", "vswitch-vm-2"),
            ("enp3s1f5", "0", "off", "vswitch-vm-2"),   
            ("enp3s1f6", "20", "off", "vswitch-vm-2"),
            ("enp3s0f6", "20", "off", "vswitch-vm-2"),
            ("enp3s0f7", "20", "off", "tenant-green-2"),
            ("enp3s1f7", "20", "off", "tenant-green-2")
            ]
    
    exp.usedVms=[
             ("vswitch-vm", cpu_config[0][0], "4G"),
             ("tenant-green-1", cpu_config[1][0], "4G"),
             
             ("vswitch-vm-2", cpu_config[0][1], "4G"),
             ("tenant-green-2", cpu_config[1][1], "4G")]
   
        
    OvsCpu= cpu_config[2]
    DpdkCpu= cpu_config[3]
    DpdkMem= dpdkMemory
    #----------------- OVS-VM_1------------------    
    if len(DpdkCpu[1]) >1:
    
        OvsVmPorts1= [
                ("enp3s0f2", True, str(DpdkCpu[1][0])),
                ("enp3s1f2", True, str(DpdkCpu[1][0])),
                ("enp3s1f3", True, str(DpdkCpu[1][1])),
                ("enp3s0f3", True, str(DpdkCpu[1][1]))]   
    else:
        OvsVmPorts1= [
                ("enp3s0f2", True, str(DpdkCpu[1][0])),
                ("enp3s1f2", True, str(DpdkCpu[1][0])),
                ("enp3s1f3", True, str(DpdkCpu[1][0])),
                ("enp3s0f3", True, str(DpdkCpu[1][0]))]   

    #----------------- OVS-VM_2------------------    
    if len(DpdkCpu[1]) >1:
    
        OvsVmPorts2= [
                ("enp3s0f5", True, str(DpdkCpu[1][0])),
                ("enp3s1f5", True, str(DpdkCpu[1][0])),
                ("enp3s1f6", True, str(DpdkCpu[1][1])),
                ("enp3s0f6", True, str(DpdkCpu[1][1]))]   
    else:
        OvsVmPorts2= [
                ("enp3s0f5", True, str(DpdkCpu[1][0])),
                ("enp3s1f5", True, str(DpdkCpu[1][0])),
                ("enp3s1f6", True, str(DpdkCpu[1][0])),
                ("enp3s0f6", True, str(DpdkCpu[1][0]))]       
        
    msg= GetScenarioSummary([OvsVmPorts1, OvsVmPorts2], OvsCpu, DpdkCpu, DpdkMem)
    EmailNotify(msg, "is beeing prepared", logTimeStamp)
    Logs(msg,config, logTimeStamp)
     
    #----------------------------------------#
    exp.InitialConfig()
    exp.Vfsconfig()
    exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu, DpdkMem, DpdkCpu)
    
    if IsCpusIsolated:
        exp.ConfigOVS("vswitch-vm-2", "br0", OvsVmPorts2, OvsCpu, DpdkMem, DpdkCpu)
    else:
        exp.ConfigOVS("vswitch-vm-2", "br0", OvsVmPorts2, OvsCpu, DpdkMem, [2,[0]])
        
    
    '''
    OVS Flow Rules for OVS-VM-1:
    + (1) in: enp3s0f2 with ip: 10.0.0.2 --> out= enp3s0f3, change Mac to enp3s0f4 mac
    + (2) in: enp3s1f3    --> out= enp3s1f2, change Mac to 00:00:00:00:30:56

    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f2"]+",ip,nw_dst=10.0.0.2"
    action="mod_dl_dst:"+exp.GetMacByVf("enp3s0f4")+","+exp.VfsMatch["enp3s0f3"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s1f3"]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch["enp3s1f2"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
    
    '''
    OVS Flow Rules for OVS-VM-2:
    + (1) in: enp3s0f5 with ip:10.0.0.3--> out= enp3s0f6, change Mac to enp3s0f7 mac
    + (2) in: enp3s1f6    --> out= enp3s1f5, change Mac to 00:00:00:00:30:56

    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f5"]+",ip,nw_dst=10.0.0.3"
    action="mod_dl_dst:"+exp.GetMacByVf("enp3s0f7")+","+exp.VfsMatch["enp3s0f6"]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s1f6"]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch["enp3s1f5"]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm-2", exp.OVS_PATH,"br0")
    
    
    #Start DPDK App in The tenantVM 1
    #exp.StartDpdkApp("tenant-green-1")
    
    #Start DPDK App in The tenantVM 2
    #exp.StartDpdkApp("tenant-green-2")
    
    EmailNotify(msg, "is ready", logTimeStamp)
    return True


def phy2vm2vm2phy_SRIOV_MultiOvs_NoDPDK(cnx_server, config):
        
    #----------------------------------------#
    exp.NicType= "mlx"
    exp.isSRIOV= True
    exp.IsDPDK= False
    exp.OVS_PATH= exp.nodpdk_path
    exp.Server_cnx= cnx_server
    exp.scsName= "phy2vm2vm2phy_SRIOV_MultiOvs_NoDPDK"
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    #----------------------------------------#
    cpu_config= CpuAllocation(config)
    
    exp.PhyPorts= [
           ("enp3s0f0", "8"),
           ("enp3s0f1", "8")
          ]
    
    exp.MyVfs= [
            ("enp3s0f2", "0", "off", "vswitch-vm"),
            ("enp3s1f2", "0", "off", "vswitch-vm"),
            ("enp3s1f3", "10", "off", "vswitch-vm"),
            ("enp3s0f3", "10", "off", "vswitch-vm"),
            ("enp3s0f4", "10", "off", "tenant-green-1"),
            ("enp3s1f4", "10", "off", "tenant-green-1"),
            
            ("enp3s0f5", "0", "off", "vswitch-vm-2"),
            ("enp3s1f5", "0", "off", "vswitch-vm-2"),   
            ("enp3s1f6", "20", "off", "vswitch-vm-2"),
            ("enp3s0f6", "20", "off", "vswitch-vm-2"),
            ("enp3s0f7", "20", "off", "tenant-green-2"),
            ("enp3s1f7", "20", "off", "tenant-green-2")
            ]
    
    exp.usedVms=[
             ("vswitch-vm", cpu_config[0][0], "4G"),
             ("tenant-green-1", cpu_config[1][0], "4G"),
             
             ("vswitch-vm-2", cpu_config[0][1], "4G"),
             ("tenant-green-2", cpu_config[1][1], "4G")]
   
        
    OvsCpu= cpu_config[2]
    #----------------- OVS-VM_1------------------    
    OvsVmPorts1= [
                ("enp3s0f2", False),
                ("enp3s1f2", False),
                ("enp3s1f3", False),
                ("enp3s0f3", False)]  

    #----------------- OVS-VM_2------------------  
    OvsVmPorts2= [
                ("enp3s0f5", False),
                ("enp3s1f5", False),
                ("enp3s1f6", False),
                ("enp3s0f6", False)]   
    
    
    msg= GetScenarioSummary([OvsVmPorts1, OvsVmPorts2], OvsCpu, [], "")
    EmailNotify(msg, "is beeing prepared", logTimeStamp)
    Logs(msg,config, logTimeStamp)
     
    #----------------------------------------#
    exp.InitialConfig()
    exp.Vfsconfig()
    exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu)
    exp.ConfigOVS("vswitch-vm-2", "br0", OvsVmPorts2, OvsCpu)
    
    '''
    OVS Flow Rules for OVS-VM-1:
    + (1) in: enp3s0f2 with ip: 10.0.0.2 --> out= enp3s0f3, change Mac to enp3s0f4 mac
    + (2) in: enp3s1f3    --> out= enp3s1f2, change Mac to 00:00:00:00:30:56

    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f2"]+",ip,nw_dst=10.0.0.2"
    action="mod_dl_dst:"+exp.GetMacByVf("enp3s0f4")+","+exp.VfsMatch["enp3s0f3"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s1f3"]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch["enp3s1f2"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
    
    '''
    OVS Flow Rules for OVS-VM-2:
    + (1) in: enp3s0f5 with ip: 10.0.0.3 --> out= enp3s0f6, change Mac to enp3s0f7 mac
    + (2) in: enp3s1f6    --> out= enp3s1f5, change Mac to 00:00:00:00:30:56

    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f5"]+",ip,nw_dst=10.0.0.3"
    action="mod_dl_dst:"+exp.GetMacByVf("enp3s0f7")+","+exp.VfsMatch["enp3s0f6"]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s1f6"]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch["enp3s1f5"]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm-2", exp.OVS_PATH,"br0")
    
    #Start DPDK App in The tenantVM 1
    #exp.StartDpdkApp("tenant-green-1")
    
    #Start DPDK App in The tenantVM 2
    #exp.StartDpdkApp("tenant-green-2")
    
    EmailNotify(msg, "is ready", logTimeStamp)
    return True

  
def phy2vm2vm2phy_Baseline_MultiTenant_NoDPDK(cnx_server, config):
    # ----------------------------------------#
    exp.NicType = "mlx"
    exp.isSRIOV = False
    exp.IsDPDK = False
    exp.OVS_PATH = exp.nodpdk_path
    exp.Server_cnx = cnx_server
    exp.scsName= "phy2vm2vm2phy_Baseline_MultiTenant_NoDPDK"
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


    # ----------------------------------------#
    cpu_config= CpuAllocation(config)
    
    exp.PhyPorts = [
        ("enp3s0f0", "br0"),
        ("enp3s0f1", "br0")
    ]

    exp.VirtualPorts = [
        ("1", "br0", "tenant-green-1"),
        ("2", "br0", "tenant-green-1"),
        ("4", "br0", "tenant-green-2"),
        ("5", "br0", "tenant-green-2")
    ]

    exp.usedVms = [
        ("tenant-green-1", cpu_config[1][0], "4G"),
        ("tenant-green-2", cpu_config[1][1], "4G")]

    OvsCpu = cpu_config[2]
    
    
    msg= GetScenarioSummary([], OvsCpu, [], "")
    EmailNotify(msg, "is beeing prepared", logTimeStamp)
    Logs(msg,config, logTimeStamp)
    # ----------------------------------------#
    exp.InitialConfig()
    exp.ConfigOVS(exp.Server_cnx, "br0", " ", OvsCpu)
    exp.VirPortConfig()

    '''
    OVS Flow Rules for Tenant-1:
        + (1) in: enp3s0f0 with dest-IP 10.0.0.2: --> out= vnet1
        + (2) in: vnet2    --> out= enp3s0f1

    '''
    # Flow Rules (1)
    # ---------------------------------------------------------
    match = "in_port=enp3s0f0,ip,nw_dst=10.0.0.2"
    action = "vnet1"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    # Flow Rules (2)
    # ---------------------------------------------------------
    match = "in_port=vnet2"
    action = "enp3s0f1"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)
    
    '''
    OVS Flow Rules for Tenant-2:
        + (1) in: enp3s0f0 with dest-IP 10.0.0.3: --> out= vnet4
        + (2) in: vnet5    --> out= enp3s0f1
    '''
    # Flow Rules (1)
    # ---------------------------------------------------------
    match = "in_port=enp3s0f0,ip,nw_dst=10.0.0.3"
    action = "vnet4"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    # Flow Rules (2)
    # ---------------------------------------------------------
    match = "in_port=vnet5"
    action = "enp3s0f1"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    # show Flow rules of br0
    exp.showFlowRules(exp.Server_cnx, exp.OVS_PATH, "br0")
    
    #Tenant-Vm Bridge
    #exp.SetBridging("tenant-green-1", exp.VirPortsMatch["1"], exp.VirPortsMatch["2"])
    
    #exp.SetBridging("tenant-green-2", exp.VirPortsMatch["4"], exp.VirPortsMatch["5"])
    
    EmailNotify(msg, "is ready", logTimeStamp)
    return True

# Not tested !!!
def phy2vm2vm2phy_Baseline_MultiTenant_DPDK(cnx_server, config, dpdkMemory="1024,0"):
    # ----------------------------------------#
    exp.NicType = "mlx"
    exp.isSRIOV = False
    exp.IsDPDK = True
    exp.OVS_PATH = exp.dpdk_path
    exp.Server_cnx = cnx_server
    exp.scsName= "phy2vm2vm2phy_Baseline_MultiTenant_DPDK"
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # ----------------------------------------#
    cpu_config= CpuAllocation(config)
    
    exp.VirtualPorts = [
        ("1", "br0", "tenant-green-1"),
        ("2", "br0", "tenant-green-1"),       
        ("4", "br0", "tenant-green-2"),
        ("5", "br0", "tenant-green-2")
    ]

    exp.usedVms = [
        ("tenant-green-1", cpu_config[1][0], "4G"),
        ("tenant-green-2", cpu_config[1][1], "4G")]

    OvsCpu = cpu_config[2]
    DpdkCpu= cpu_config[3]
    DpdkMem= dpdkMemory
                 
    if len(DpdkCpu[1]) >1:   
              exp.PhyPorts= [
                      ("enp3s0f0", "br0", True,  str(DpdkCpu[1][0])),
                      ("enp3s0f1", "br0", True,  str(DpdkCpu[1][1]))]
    
    else:
              exp.PhyPorts= [
                      ("enp3s0f0", "br0", True,  str(DpdkCpu[1][0])),
                      ("enp3s0f1", "br0", True,  str(DpdkCpu[1][0]))]

    msg= GetScenarioSummary([], OvsCpu, DpdkCpu, DpdkMem)
    EmailNotify(msg, "is beeing prepared", logTimeStamp) 
    Logs(msg,config, logTimeStamp)
    # ----------------------------------------#
    
    exp.InitialConfig(True)
    exp.ConfigOVS(exp.Server_cnx, "br0", " ", OvsCpu, DpdkMem, DpdkCpu)
    exp.VirPortConfig()

    '''
    OVS Flow Rules for Tenant-1:
        + (1) in: enp3s0f0 , dest IP 10.0.0.2: --> out= vnet1
        + (2) in: vnet2    --> out= enp3s0f1

    '''
    # Flow Rules (1)
    # ---------------------------------------------------------
    match = "in_port=enp3s0f0,ip,nw_dst=10.0.0.2"
    action = "vnet1"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    # Flow Rules (2)
    # ---------------------------------------------------------
    match = "in_port=vnet2"
    action = "enp3s0f1"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)
    
    '''
    OVS Flow Rules for Tenant-2:
        + (1) in: enp3s0f0 from IP 10.0.0.3: --> out= vnet4
        + (2) in: vnet5    --> out= enp3s0f1

    '''
    # Flow Rules (1)
    # ---------------------------------------------------------
    match = "in_port=enp3s0f0,ip,nw_dst=10.0.0.3"
    action = "vnet4"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    # Flow Rules (2)
    # ---------------------------------------------------------
    match = "in_port=vnet5"
    action = "enp3s0f1"
    exp.addFlowRule(exp.Server_cnx, exp.OVS_PATH, "br0", match, action)

    # show Flow rules of br0
    exp.showFlowRules(exp.Server_cnx, exp.OVS_PATH, "br0")
    
    #Start DPDK App on both Tenant VMs

    
    EmailNotify(msg, "is ready", logTimeStamp)
    return True


def phy2vm2vm2phy_SRIOV_MultiTenant_DPDK(cnx_server, config, dpdkMemory="1024,0"):
        
    #----------------------------------------#
    exp.NicType= "mlx"
    exp.isSRIOV= True
    exp.IsDPDK= True
    exp.OVS_PATH= exp.dpdk_path
    exp.Server_cnx= cnx_server
    exp.scsName= "phy2vm2vm2phy_SRIOV_MultiTenant_DPDK"
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    #----------------------------------------#
    cpu_config= CpuAllocation(config)
    
    exp.PhyPorts= [
           ("enp3s0f0", "8"),
           ("enp3s0f1", "8")
          ]
    
    exp.MyVfs= [
            ("enp3s0f2", "0", "off", "vswitch-vm"),
            ("enp3s1f2", "0", "off", "vswitch-vm"),
            ("enp3s1f3", "10", "off", "vswitch-vm"),
            ("enp3s0f3", "10", "off", "vswitch-vm"),
            ("enp3s0f4", "10", "off", "tenant-green-1"),
            ("enp3s1f4", "10", "off", "tenant-green-1"),
            
            ("enp3s1f5", "20", "off", "vswitch-vm"),
            ("enp3s0f5", "20", "off", "vswitch-vm"),
            ("enp3s0f6", "20", "off", "tenant-green-2"),
            ("enp3s1f6", "20", "off", "tenant-green-2")]
    
    exp.usedVms=[
             ("vswitch-vm", cpu_config[0][0], "4G"),
             ("tenant-green-1", cpu_config[1][0], "4G"),
             ("tenant-green-2", cpu_config[1][1], "4G")]
    
    #----------------- OVS-VM_1------------------
    OvsCpu= cpu_config[2]
    DpdkCpu= cpu_config[3]
    DpdkMem= dpdkMemory
    
    if len(DpdkCpu[1]) >1:
    
        OvsVmPorts1= [
                ("enp3s0f2", True, str(DpdkCpu[1][0])),
                ("enp3s1f2", True, str(DpdkCpu[1][0])),
                ("enp3s1f3", True, str(DpdkCpu[1][0])),
                ("enp3s0f3", True, str(DpdkCpu[1][1])),
                ("enp3s1f5", True, str(DpdkCpu[1][1])),
                ("enp3s0f5", True, str(DpdkCpu[1][1]))]   
    else:
        OvsVmPorts1= [
                ("enp3s0f2", True, str(DpdkCpu[1][0])),
                ("enp3s1f2", True, str(DpdkCpu[1][0])),
                ("enp3s1f3", True, str(DpdkCpu[1][0])),
                ("enp3s0f3", True, str(DpdkCpu[1][0])),
                ("enp3s1f5", True, str(DpdkCpu[1][0])),
                ("enp3s0f5", True, str(DpdkCpu[1][0]))]
        
    
    msg= GetScenarioSummary([OvsVmPorts1], OvsCpu, DpdkCpu, DpdkMem)
    EmailNotify(msg, "is beeing prepared", logTimeStamp)
    Logs(msg,config, logTimeStamp)
    #----------------------------------------#
    exp.InitialConfig()
    exp.Vfsconfig()
    exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu, DpdkMem, DpdkCpu)
    
    '''
    OVS Flow Rules for tenant-1 :
    + (1) in: enp3s0f2 ,dest IP 10.0.0.2 --> out= enp3s0f3, change Mac to enp3s0f4 mac
    + (2) in: enp3s1f3    --> out= enp3s1f2,  change Mac to 00:00:00:00:30:56 

    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f2"]+",ip,nw_dst=10.0.0.2"
    action="mod_dl_dst:"+exp.GetMacByVf("enp3s0f4")+","+exp.VfsMatch["enp3s0f3"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s1f3"]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch["enp3s1f2"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    
    '''
    OVS Flow Rules for tenant-2 :
    + (1) in: enp3s0f2 ,dest IP 10.0.0.3 --> out= enp3s0f5, change Mac to enp3s0f6 mac
    + (2) in: enp3s1f5    --> out= enp3s1f2,  change Mac to 00:00:00:00:30:56 

    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f2"]+",ip,nw_dst=10.0.0.3"
    action="mod_dl_dst:"+exp.GetMacByVf("enp3s0f6")+","+exp.VfsMatch["enp3s0f5"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s1f5"]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch["enp3s1f2"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
    
    #Start DPDK App in The tenantVM
    #exp.StartDpdkApp("tenant-green-1")
    
    EmailNotify(msg, "is ready", logTimeStamp)
    return True


def phy2vm2vm2phy_SRIOV_MultiTenant_NoDPDK(cnx_server, config):
    #----------------------------------------#
    exp.NicType= "mlx"
    exp.isSRIOV= True
    exp.IsDPDK= False
    exp.OVS_PATH= exp.nodpdk_path
    exp.Server_cnx= cnx_server
    exp.scsName= "phy2vm2vm2phy_SRIOV_MultiTenant_NoDPDK"
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    #----------------------------------------#
    cpu_config= CpuAllocation(config)
    
    exp.PhyPorts= [
           ("enp3s0f0", "8"),
           ("enp3s0f1", "8")
          ]
    
    exp.MyVfs= [
            ("enp3s0f2", "0", "off", "vswitch-vm"),
            ("enp3s1f2", "0", "off", "vswitch-vm"),
            ("enp3s1f3", "10", "off", "vswitch-vm"),
            ("enp3s0f3", "10", "off", "vswitch-vm"),
            ("enp3s0f4", "10", "off", "tenant-green-1"),
            ("enp3s1f4", "10", "off", "tenant-green-1"),
            
            ("enp3s1f5", "20", "off", "vswitch-vm"),
            ("enp3s0f5", "20", "off", "vswitch-vm"),
            ("enp3s0f6", "20", "off", "tenant-green-2"),
            ("enp3s1f6", "20", "off", "tenant-green-2")]
    
    exp.usedVms=[
             ("vswitch-vm", cpu_config[0][0], "4G"),
             ("tenant-green-1", cpu_config[1][0], "4G"),
             ("tenant-green-2", cpu_config[1][1], "4G")]
    
    #----------------- OVS-VM_1------------------
    OvsCpu= cpu_config[2]
    OvsVmPorts1= [
            ("enp3s0f2", False),
            ("enp3s1f2", False),
            ("enp3s1f3", False),
            ("enp3s0f3", False),
            ("enp3s1f5", False),
            ("enp3s0f5", False)]   
    
    
    msg= GetScenarioSummary([OvsVmPorts1], OvsCpu, [], "")
    EmailNotify(msg, "is beeing prepared", logTimeStamp)
    Logs(msg,config, logTimeStamp)
    #----------------------------------------#
    exp.InitialConfig()
    exp.Vfsconfig()
    exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu)
    
    '''
    OVS Flow Rules for tenant-1 :
    + (1) in: enp3s0f2 ,dest IP 10.0.0.2 --> out= enp3s0f3, change Mac to enp3s0f4 mac
    + (2) in: enp3s1f3    --> out= enp3s1f2,  change Mac to 00:00:00:00:30:56 

    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f2"]+",ip,nw_dst=10.0.0.2"
    action="mod_dl_dst:"+exp.GetMacByVf("enp3s0f4")+","+exp.VfsMatch["enp3s0f3"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s1f3"]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch["enp3s1f2"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    
    '''
    OVS Flow Rules for tenant-2 :
    + (1) in: enp3s0f2 ,dest IP 10.0.0.3 --> out= enp3s0f5, change Mac to enp3s0f6 mac
    + (2) in: enp3s1f5    --> out= enp3s1f2,  change Mac to 00:00:00:00:30:56 

    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f2"]+",ip,nw_dst=10.0.0.3"
    action="mod_dl_dst:"+exp.GetMacByVf("enp3s0f6")+","+exp.VfsMatch["enp3s0f5"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s1f5"]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch["enp3s1f2"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
    
    #Start DPDK App in The tenantVM
    #exp.StartDpdkApp("tenant-green-1")
    
    EmailNotify(msg, "is ready", logTimeStamp)
    return True



def phy2phy_SRIOV_MultiOvs_NoDPDK(cnx_server, config):
    #----------------------------------------#
    exp.NicType= "mlx"
    exp.isSRIOV= True
    exp.IsDPDK= False
    exp.OVS_PATH= exp.nodpdk_path
    exp.Server_cnx= cnx_server
    exp.scsName= "phy2phy_SRIOV_MultiOvs_NoDPDK"
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    #----------------------------------------#
    cpu_config= CpuAllocation(config)
    
    exp.PhyPorts= [
           ("enp3s0f0", "8"),
           ("enp3s0f1", "8")
          ]
    
    exp.MyVfs= [
            ("enp3s0f2", "0", "off", "vswitch-vm"),
            ("enp3s1f2", "0", "off", "vswitch-vm"),
            
            ("enp3s0f5", "0", "off", "vswitch-vm-2"),
            ("enp3s1f5", "0", "off", "vswitch-vm-2")]
    
    exp.usedVms=[
             ("vswitch-vm", cpu_config[0][0], "4G"),
             ("vswitch-vm-2", cpu_config[0][1], "4G")]
 
    OvsCpu= cpu_config[2]
    #----------------- OVS-VM_1------------------
    OvsVmPorts1= [
            ("enp3s0f2", False),
            ("enp3s1f2", False)]   
    
    #----------------- OVS-VM_2------------------
    OvsVmPorts2= [
            ("enp3s0f5", False),
            ("enp3s1f5", False)]
    
    msg= GetScenarioSummary([OvsVmPorts1, OvsVmPorts2], OvsCpu, [], "")
    EmailNotify(msg, "is beeing prepared", logTimeStamp )
    Logs(msg,config, logTimeStamp)

    exp.InitialConfig()
    exp.Vfsconfig()
    exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu)
    exp.ConfigOVS("vswitch-vm-2", "br0", OvsVmPorts2, OvsCpu)
    
    '''
    OVS Flow Rules for OVS-VM-1:
    + (1) in: enp3s0f2 with ip: 10.0.0.2 --> out= enp3s1f2, change Mac to 00:00:00:00:30:56

    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f2"]+",ip,nw_dst=10.0.0.2"
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch["enp3s1f2"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
    
    '''
    OVS Flow Rules for OVS-VM-2:
    + (1) in: enp3s0f5 with ip: 10.0.0.3 --> out= enp3s1f5, change Mac to 00:00:00:00:30:56

    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f5"]+",ip,nw_dst=10.0.0.3"
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch["enp3s1f5"]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)
    
    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm-2", exp.OVS_PATH,"br0")
    
    EmailNotify(msg, "is ready", logTimeStamp)
    return True


def phy2phy_SRIOV_MultiOvs_DPDK(cnx_server, config, dpdkMemory="1024,0"):
        #----------------------------------------#
    exp.NicType= "mlx"
    exp.isSRIOV= True
    exp.IsDPDK= True
    exp.OVS_PATH= exp.dpdk_path
    exp.Server_cnx= cnx_server
    exp.scsName= "phy2phy_SRIOV_MultiOvs_DPDK"
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    #----------------------------------------#
    cpu_config= CpuAllocation(config)
    
    exp.PhyPorts= [
           ("enp3s0f0", "8"),
           ("enp3s0f1", "8")
          ]
    
    exp.MyVfs= [
            ("enp3s0f2", "0", "off", "vswitch-vm"),
            ("enp3s1f2", "0", "off", "vswitch-vm"),
            
            ("enp3s0f5", "0", "off", "vswitch-vm-2"),
            ("enp3s1f5", "0", "off", "vswitch-vm-2")]
    
    exp.usedVms=[
             ("vswitch-vm", cpu_config[0][0], "4G"),
             ("vswitch-vm-2", cpu_config[0][1], "4G")]
    
    OvsCpu= cpu_config[2]
    DpdkCpu= cpu_config[3]
    DpdkMem= dpdkMemory
    
    #----------------- OVS-VM_1------------------   
    if len(DpdkCpu[1]) >1:    
        OvsVmPorts1= [
                ("enp3s0f2", True, str(DpdkCpu[1][0])),
                ("enp3s1f2", True, str(DpdkCpu[1][1]))]   
        
    else:
        OvsVmPorts1= [
                ("enp3s0f2", True, str(DpdkCpu[1][0])),
                ("enp3s1f2", True, str(DpdkCpu[1][0]))]   

    #----------------- OVS-VM_2------------------   
    if len(DpdkCpu[1]) >1:    
        OvsVmPorts2= [
                ("enp3s0f5", True, str(DpdkCpu[1][0])),
                ("enp3s1f5", True, str(DpdkCpu[1][1]))]   
        
    else:
        OvsVmPorts2= [
                ("enp3s0f5", True, str(DpdkCpu[1][0])),
                ("enp3s1f5", True, str(DpdkCpu[1][0]))]   
        
    msg= GetScenarioSummary([], OvsCpu, DpdkCpu, DpdkMem)
    EmailNotify(msg, "is beeing prepared", logTimeStamp)
    Logs(msg,config, logTimeStamp)
     
    #-------------------------------------------
    exp.InitialConfig()
    exp.Vfsconfig()
    exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu, DpdkMem, DpdkCpu)
    
    if IsCpusIsolated:    
        exp.ConfigOVS("vswitch-vm-2", "br0", OvsVmPorts2, OvsCpu, DpdkMem, DpdkCpu)
    else:
        exp.ConfigOVS("vswitch-vm-2", "br0", OvsVmPorts2, OvsCpu, DpdkMem, [2,[0]])
        
    
    '''
    OVS Flow Rules:
    + (1) in: enp3s0f2 with ip:10.0.0.2--> out= enp3s1f2, change Mac to 00:00:00:00:30:56

    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f2"]+",ip,nw_dst=10.0.0.2"
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch["enp3s1f2"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
    
    '''
    OVS Flow Rules for OVS-VM-2:
    + (1) in: enp3s0f3 with ip:10.0.0.3--> out= enp3s1f3, change Mac to 00:00:00:00:30:56

    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f5"]+",ip,nw_dst=10.0.0.3"
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch["enp3s1f5"]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)
    
    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm-2", exp.OVS_PATH,"br0")
    
    EmailNotify(msg, "is ready", logTimeStamp)
    return True


def phy2phy_Baseline_MultiTenant_NoDPDK(cnx_server, config):
     #----------------------------------------#
     exp.NicType= "mlx"
     exp.isSRIOV= False
     exp.IsDPDK= False
     exp.OVS_PATH= exp.nodpdk_path
     exp.Server_cnx= cnx_server
     exp.scsName= "phy2phy_Baseline_MultiTenant_NoDPDK"
     logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
     
     #----------------------------------------#
     cpu_config= CpuAllocation(config)
     
     exp.PhyPorts= [
             ("enp3s0f0", "br0"),
             ("enp3s0f1", "br0")  
             ]
     
     exp.VirtualPorts=[]
     
     #no Vm is used in this topology
     exp.usedVms=[]
     
     #no Vfs ir virtual portes are needed in this topology
     Ports=[]
     
     OvsCpu= cpu_config[2]
     
     
     msg= GetScenarioSummary([], OvsCpu, [], "")
     EmailNotify(msg, "is beeing prepared", logTimeStamp)
     Logs(msg,config, logTimeStamp)
     #----------------------------------------#
     
     exp.InitialConfig()
     exp.ConfigOVS(exp.Server_cnx, "br0",  Ports, OvsCpu)
     
     '''
     OVS Flow Rules:
         + (1) in: enp3s0f0 with ip 10.0.0.2 --> out= enp3s0f1
         + (2) in: enp3s0f0 with ip 10.0.0.3 --> out= enp3s0f1
     '''
     #Flow Rules (1)
     #---------------------------------------------------------   
     match="in_port=enp3s0f0,ip,nw_dst=10.0.0.2"
     action="enp3s0f1"
     exp.addFlowRule(exp.Server_cnx , exp.OVS_PATH, "br0", match, action) 
     
     #Flow Rules (2)
     #---------------------------------------------------------   
     match="in_port=enp3s0f0,ip,nw_dst=10.0.0.3"
     action="enp3s0f1"
     exp.addFlowRule(exp.Server_cnx , exp.OVS_PATH, "br0", match, action) 


     #show Flow rules of br0 
     exp.showFlowRules(exp.Server_cnx, exp.OVS_PATH, "br0")
     
     EmailNotify(msg, "is ready", logTimeStamp)
     return True

# Not tested !!!
def phy2phy_Baseline_MultiTenant_DPDK(cnx_server, config, dpdkMemory="1024,0"):
     #----------------------------------------#
     exp.NicType= "mlx"
     exp.isSRIOV= False
     exp.IsDPDK= True
     exp.OVS_PATH= exp.dpdk_path
     exp.Server_cnx= cnx_server
     exp.scsName= "phy2phy_Baseline_MultiTenant_DPDK"
     logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
     
     #----------------------------------------#
     cpu_config= CpuAllocation(config)
          
     exp.VirtualPorts=[]
     
     #no Vm is used in this topology
     exp.usedVms=[]
     
     #no Vfs ir virtual portes are needed in this topology
     Ports=[]
     
     OvsCpu= cpu_config[2]
     DpdkCpu= cpu_config[3]
     DpdkMem= dpdkMemory
             
     if len(DpdkCpu[1]) >1:   
              exp.PhyPorts= [
                      ("enp3s0f0", "br0", True,  str(DpdkCpu[1][0])),
                      ("enp3s0f1", "br0", True,  str(DpdkCpu[1][1]))]

     else:
              exp.PhyPorts= [
                      ("enp3s0f0", "br0", True,  str(DpdkCpu[1][0])),
                      ("enp3s0f1", "br0", True,  str(DpdkCpu[1][0]))]
              
      
     msg= GetScenarioSummary([], OvsCpu, DpdkCpu, DpdkMem)
     EmailNotify(msg, "is beeing prepared", logTimeStamp)
     Logs(msg,config, logTimeStamp)
     
     #----------------------------------------#
     
     exp.InitialConfig(True)
     exp.ConfigOVS(exp.Server_cnx, "br0",  Ports, OvsCpu, DpdkMem, DpdkCpu)
      
     '''
     OVS Flow Rules:
         + (1) in: enp3s0f0 with ip 10.0.0.2 --> out= enp3s0f1
         + (2) in: enp3s0f0 with ip 10.0.0.3 --> out= enp3s0f1
     '''
     #Flow Rules (1)
     #---------------------------------------------------------   
     match="in_port=enp3s0f0,ip,nw_dst=10.0.0.2"
     action="enp3s0f1"
     exp.addFlowRule(exp.Server_cnx , exp.OVS_PATH, "br0", match, action) 
     
     #Flow Rules (2)
     #---------------------------------------------------------   
     match="in_port=enp3s0f0,ip,nw_dst=10.0.0.3"
     action="enp3s0f1"
     exp.addFlowRule(exp.Server_cnx , exp.OVS_PATH, "br0", match, action) 

     #show Flow rules of br0 
     exp.showFlowRules(exp.Server_cnx, exp.OVS_PATH, "br0")
     
     EmailNotify(msg, "is ready", logTimeStamp)
     return True
 
            
def phy2phy_SRIOV_MultiTenant_DPDK(cnx_server, config, dpdkMemory="1024,0"):
        #----------------------------------------#
    exp.NicType= "mlx"
    exp.isSRIOV= True
    exp.IsDPDK= True
    exp.OVS_PATH= exp.dpdk_path
    exp.Server_cnx= cnx_server
    exp.scsName= "phy2phy_SRIOV_MultiTenant_DPDK"
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


    #----------------------------------------#
    cpu_config= CpuAllocation(config)
    
    exp.PhyPorts= [
           ("enp3s0f0", "8"),
           ("enp3s0f1", "8")
          ]
    
    exp.MyVfs= [
            ("enp3s0f2", "0", "off", "vswitch-vm"),
            ("enp3s1f2", "0", "off", "vswitch-vm")]
    
    exp.usedVms=[
             ("vswitch-vm", cpu_config[0][0], "4G")]
    
    #----------------- OVS-VM_1------------------
    OvsCpu= cpu_config[2]
    DpdkCpu= cpu_config[3]
    DpdkMem= dpdkMemory
    
    if len(DpdkCpu[1]) >1:    
        OvsVmPorts1= [
                ("enp3s0f2", True, str(DpdkCpu[1][0])),
                ("enp3s1f2", True, str(DpdkCpu[1][1]))]   
        
    else:
        OvsVmPorts1= [
                ("enp3s0f2", True, str(DpdkCpu[1][0])),
                ("enp3s1f2", True, str(DpdkCpu[1][0]))]  
     
    msg= GetScenarioSummary([OvsVmPorts1], OvsCpu, DpdkCpu, DpdkMem)
    EmailNotify(msg, "is beeing prepared", logTimeStamp)
    Logs(msg,config, logTimeStamp)
    #-------------------------------------------
    
    exp.InitialConfig()
    exp.Vfsconfig()
    exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu, DpdkMem, DpdkCpu)
    
    '''
    OVS Flow Rules:
    + (1) in: enp3s0f2  with ip:10.0.0.2--> out= enp3s1f2, change Mac to 00:00:00:00:30:56
    + (2) in: enp3s0f2  with ip:10.0.0.3--> out= enp3s1f2, change Mac to 00:00:00:00:30:56

    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f2"]+",ip,nw_dst=10.0.0.2"
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch["enp3s1f2"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
        #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f2"]+",ip,nw_dst=10.0.0.3"
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch["enp3s1f2"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
    
    EmailNotify(msg, "is ready", logTimeStamp)
    return True


def phy2phy_SRIOV_MultiTenant_NoDPDK(cnx_server, config):
    #----------------------------------------#
    exp.NicType= "mlx"
    exp.isSRIOV= True
    exp.IsDPDK= False
    exp.OVS_PATH= exp.nodpdk_path
    exp.Server_cnx= cnx_server
    exp.scsName= "phy2phy_SRIOV_MultiTenant_NoDPDK"
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    
    #----------------------------------------#
    cpu_config= CpuAllocation(config)
    
    exp.PhyPorts= [
           ("enp3s0f0", "8"),
           ("enp3s0f1", "8")
          ]
    
    exp.MyVfs= [
            ("enp3s0f2", "0", "off", "vswitch-vm"),
            ("enp3s1f2", "0", "off", "vswitch-vm")]
    
    exp.usedVms=[
             ("vswitch-vm", cpu_config[0][0], "4G")]
    
    #----------------- OVS-VM_1------------------
    OvsCpu1= cpu_config[2]
    OvsVmPorts1= [
            ("enp3s0f2", False),
            ("enp3s1f2", False)]   

    
    msg= GetScenarioSummary([OvsVmPorts1], OvsCpu1, [], "")
    EmailNotify(msg, "is beeing prepared", logTimeStamp)
    Logs(msg,config, logTimeStamp)
    
    exp.InitialConfig()
    exp.Vfsconfig()
    exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu1)
    
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f2"]+",ip,nw_dst=10.0.0.2"
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch["enp3s1f2"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
        #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f2"]+",ip,nw_dst=10.0.0.3"
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch["enp3s1f2"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
    
    EmailNotify(msg, "is ready", logTimeStamp)
    return True



###########################################################################################
###################---Custom Scenarios (No CPU array is needed)---#########################
###########################################################################################        
    
def phy2vm2vm2phy_SRIOV_MultiOvs_DPDK_Custom(cnx_server, dpdkMemory="1024,0"):
        
    #----------------------------------------#
    exp.NicType= "mlx"
    exp.isSRIOV= True
    exp.IsDPDK= True
    exp.OVS_PATH= exp.dpdk_path
    exp.Server_cnx= cnx_server
    exp.scsName= "phy2vm2vm2phy_SRIOV_MultiOvs_DPDK_Custom"
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    #----------------------------------------#
    exp.HOST_CPU="custom"
    
    exp.PhyPorts= [
           ("enp3s0f0", "8"),
           ("enp3s0f1", "8")
          ]
    
    exp.MyVfs= [
            ("enp3s0f2", "0", "off", "vswitch-vm"),
            ("enp3s1f2", "0", "off", "vswitch-vm"),
            ("enp3s1f3", "10", "off", "vswitch-vm"),
            ("enp3s0f3", "10", "off", "vswitch-vm"),
            ("enp3s0f4", "10", "off", "tenant-green-1"),
            ("enp3s1f4", "10", "off", "tenant-green-1"),
            
            ("enp3s0f5", "0", "off", "vswitch-vm-2"),
            ("enp3s1f5", "0", "off", "vswitch-vm-2"),   
            ("enp3s1f6", "20", "off", "vswitch-vm-2"),
            ("enp3s0f6", "20", "off", "vswitch-vm-2"),
            ("enp3s0f7", "20", "off", "tenant-green-2"),
            ("enp3s1f7", "20", "off", "tenant-green-2")
            ]
    
    exp.usedVms=[
             ("vswitch-vm", [4,5], "4G"),
             ("tenant-green-1", [0,1], "4G"),
             
             ("vswitch-vm-2", [6,7], "4G"),
             ("tenant-green-2",[2,3], "4G")]
   
        
    OvsCpu= ["0","0"]
    DpdkCpu=[2,[1]]
    DpdkMem= dpdkMemory
    #----------------- OVS-VM_1------------------    

    OvsVmPorts1= [
                ("enp3s0f2", True, str(DpdkCpu[1][0])),
                ("enp3s1f2", True, str(DpdkCpu[1][0])),
                ("enp3s1f3", True, str(DpdkCpu[1][0])),
                ("enp3s0f3", True, str(DpdkCpu[1][0]))]   

    #----------------- OVS-VM_2------------------    

    OvsVmPorts2= [
                ("enp3s0f5", True, str(DpdkCpu[1][0])),
                ("enp3s1f5", True, str(DpdkCpu[1][0])),
                ("enp3s1f6", True, str(DpdkCpu[1][0])),
                ("enp3s0f6", True, str(DpdkCpu[1][0]))]       
        
    msg= GetScenarioSummary([OvsVmPorts1, OvsVmPorts2], OvsCpu, DpdkCpu, DpdkMem)
    EmailNotify(msg, "is beeing prepared", logTimeStamp)
    # Logs(msg,config, logTimeStamp)
     
    #----------------------------------------#
    exp.InitialConfig()
    exp.Vfsconfig()
    exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu, DpdkMem, DpdkCpu)
    exp.ConfigOVS("vswitch-vm-2", "br0", OvsVmPorts2, OvsCpu, DpdkMem, DpdkCpu)
    
    '''
    OVS Flow Rules for OVS-VM-1:
    + (1) in: enp3s0f2 with ip: 10.0.0.2--> out= enp3s0f3, change Mac to enp3s0f4 mac
    + (2) in: enp3s1f3    --> out= enp3s1f2, change Mac to 00:00:00:00:30:16

    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f2"]+",ip,nw_dst=10.0.0.2"
    action="mod_dl_dst:"+exp.GetMacByVf("enp3s0f4")+","+exp.VfsMatch["enp3s0f3"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s1f3"]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch["enp3s1f2"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
    
    '''
    OVS Flow Rules for OVS-VM-2:
    + (1) in: enp3s0f5 with ip: 10.0.0.3 --> out= enp3s0f6, change Mac to enp3s0f7 mac
    + (2) in: enp3s1f6    --> out= enp3s1f5, change Mac to 00:00:00:00:30:16

    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f5"]+",ip,nw_dst=10.0.0.3"
    action="mod_dl_dst:"+exp.GetMacByVf("enp3s0f7")+","+exp.VfsMatch["enp3s0f6"]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s1f6"]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch["enp3s1f5"]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm-2", exp.OVS_PATH,"br0")
    
    
    #Start DPDK App in The tenantVM 1
    #exp.StartDpdkApp("tenant-green-1")
    
    #Start DPDK App in The tenantVM 2
    #exp.StartDpdkApp("tenant-green-2")
    
    EmailNotify(msg, "is ready", logTimeStamp)
    return True  


def phy2vm2vm2phy_SRIOV_MultiOvs_NoDPDK_Custom(cnx_server):
        
    #----------------------------------------#
    exp.NicType= "mlx"
    exp.isSRIOV= True
    exp.IsDPDK= False
    exp.OVS_PATH= exp.nodpdk_path
    exp.Server_cnx= cnx_server
    exp.scsName= "phy2vm2vm2phy_SRIOV_NoDPDK_MultiOvs_Custom"
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    #----------------------------------------#
    exp.HOST_CPU="custom"
    
    exp.PhyPorts= [
           ("enp3s0f0", "8"),
           ("enp3s0f1", "8")
          ]
    
    exp.MyVfs= [
            ("enp3s0f2", "0", "off", "vswitch-vm"),
            ("enp3s1f2", "0", "off", "vswitch-vm"),
            ("enp3s1f3", "10", "off", "vswitch-vm"),
            ("enp3s0f3", "10", "off", "vswitch-vm"),
            ("enp3s0f4", "10", "off", "tenant-green-1"),
            ("enp3s1f4", "10", "off", "tenant-green-1"),
            
            ("enp3s0f5", "0", "off", "vswitch-vm-2"),
            ("enp3s1f5", "0", "off", "vswitch-vm-2"),   
            ("enp3s1f6", "20", "off", "vswitch-vm-2"),
            ("enp3s0f6", "20", "off", "vswitch-vm-2"),
            ("enp3s0f7", "20", "off", "tenant-green-2"),
            ("enp3s1f7", "20", "off", "tenant-green-2")
            ]
    
    exp.usedVms=[
             ("vswitch-vm", [4, 5], "4G"),
             ("tenant-green-1", [0, 1], "4G"),

             ("vswitch-vm-2", [6, 7], "4G"),
             ("tenant-green-2",[2, 3], "4G")]


    OvsCpu= ["0,1","0,1"]
    #----------------- OVS-VM_1------------------    
    OvsVmPorts1= [
                ("enp3s0f2", False),
                ("enp3s1f2", False),
                ("enp3s1f3", False),
                ("enp3s0f3", False)]  

    #----------------- OVS-VM_2------------------  
    OvsVmPorts2= [
                ("enp3s0f5", False),
                ("enp3s1f5", False),
                ("enp3s1f6", False),
                ("enp3s0f6", False)]       
        
    msg= GetScenarioSummary([OvsVmPorts1, OvsVmPorts2], OvsCpu, [], "")
    EmailNotify(msg, "is beeing prepared", logTimeStamp)
    # Logs(msg,config, logTimeStamp)
     
    #----------------------------------------#
    exp.InitialConfig()
    exp.Vfsconfig()
    exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu, [], "")
    exp.ConfigOVS("vswitch-vm-2", "br0", OvsVmPorts2, OvsCpu, [], "")
    
    '''
    OVS Flow Rules for OVS-VM-1:
    + (1) in: enp3s0f2 with ip: 10.0.0.2 --> out= enp3s0f3, change Mac to enp3s0f4 mac
    + (2) in: enp3s1f3    --> out= enp3s1f2, change Mac to 00:00:00:00:30:56

    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f2"]+",ip,nw_dst=10.0.0.2"
    action="mod_dl_dst:"+exp.GetMacByVf("enp3s0f4")+","+exp.VfsMatch["enp3s0f3"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s1f3"]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch["enp3s1f2"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
    
    '''
    OVS Flow Rules for OVS-VM-2:
    + (1) in: enp3s0f5 with ip: 10.0.0.3 --> out= enp3s0f6, change Mac to enp3s0f7 mac
    + (2) in: enp3s1f6    --> out= enp3s1f5, change Mac to 00:00:00:00:30:56

    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f5"]+",ip,nw_dst=10.0.0.3"
    action="mod_dl_dst:"+exp.GetMacByVf("enp3s0f7")+","+exp.VfsMatch["enp3s0f6"]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s1f6"]
    action="mod_dl_dst:"+outDestMac+","+exp.VfsMatch["enp3s1f5"]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm-2", exp.OVS_PATH,"br0")
    
    
    #Start DPDK App in The tenantVM 1
    #exp.StartDpdkApp("tenant-green-1")
    
    #Start DPDK App in The tenantVM 2
    #exp.StartDpdkApp("tenant-green-2")
    
    EmailNotify(msg, "is ready", logTimeStamp)
    return True      




########################################### Benchmark Scenarios ########################################
    
BenIntrMac= "00:0f:53:5b:b7:e1"
BenIntr="ens2f1"
BenServer= exp.cnx_dosse

def bench_phy2vm2vm2phy_SRIOV_MultiTenant_NoDPDK(cnx_server, config):
    #----------------------------------------#
    exp.NicType= "mlx"
    exp.isSRIOV= True
    exp.IsDPDK= False
    exp.OVS_PATH= exp.nodpdk_path
    exp.Server_cnx= cnx_server
    exp.scsName= "bench_phy2vm2vm2phy_SRIOV_MultiTenant_NoDPDK"
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    #----------------------------------------#
    cpu_config= CpuAllocation(config)
    
    exp.PhyPorts= [
           ("enp3s0f0", "8")
          ]
    
    exp.MyVfs= [
            ("enp3s0f2", "0", "off", "vswitch-vm"),
            ("enp3s0f3", "0", "off", "vswitch-vm"),            
            ("enp3s0f4", "10", "off", "vswitch-vm"),
            ("enp3s0f5", "20", "off", "vswitch-vm"),
            
            
            ("enp3s0f6", "10", "off", "tenant-green-1"),
            ("enp3s0f7", "20", "off", "tenant-green-2")]
    
    exp.usedVms=[
             ("vswitch-vm", cpu_config[0][0], "4G"),
             ("tenant-green-1", cpu_config[1][0], "4G"),
             ("tenant-green-2", cpu_config[1][1], "4G")]
    
    #----------------- OVS-VM_1------------------
    OvsCpu= cpu_config[2]
    OvsVmPorts1= [
            ("enp3s0f2", False),
            ("enp3s0f3", False),
            ("enp3s0f4", False),
            ("enp3s0f5", False)]   
    
    
    msg= GetScenarioSummary([OvsVmPorts1], OvsCpu, [], "")
    EmailNotify(msg, "is beeing prepared", logTimeStamp)
    Logs(msg,config, logTimeStamp)
    #----------------------------------------#
    exp.RebootServer(BenServer, wait=False)
    exp.InitialConfig()
    exp.Vfsconfig()
    exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu)
    
    '''
    OVS Flow Rules for tenant-1 :
    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f2"]+",ip,nw_dst=10.0.0.2"
    action="mod_dl_dst:"+exp.GetMacByVf("enp3s0f6")+","+exp.VfsMatch["enp3s0f4"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f4"]
    action="mod_dl_dst:"+BenIntrMac+","+exp.VfsMatch["enp3s0f3"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
       
    '''
    OVS Flow Rules for tenant-2 :
    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f2"]+",ip,nw_dst=10.0.0.3"
    action="mod_dl_dst:"+exp.GetMacByVf("enp3s0f7")+","+exp.VfsMatch["enp3s0f5"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f5"]
    action="mod_dl_dst:"+BenIntrMac+","+exp.VfsMatch["enp3s0f3"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
    
    ###############################################
    exp.setCnxLimit(BenServer, 4096)
    exp.SetInt(BenServer,BenIntr,"up")
    exp.SetIpInt(BenServer, BenIntr, "10.0.0.1/24")
    exp.SetArpEntry(BenServer,"10.0.0.3", exp.GetMacByVf("enp3s0f2"), BenIntr)
    exp.SetArpEntry(BenServer,"10.0.0.2", exp.GetMacByVf("enp3s0f2"), BenIntr)
    
    ###############################################
    
    exp.SetIpInt(exp.getVmCnx("tenant-green-1"), "ens8", "10.0.0.2/24")
    exp.SetIpInt(exp.getVmCnx("tenant-green-2"), "ens8", "10.0.0.3/24")
    
    exp.SetArpEntry(exp.getVmCnx("tenant-green-1"),"10.0.0.1", exp.GetMacByVf("enp3s0f4"), exp.VfsMatch["enp3s0f6"])
    exp.SetArpEntry(exp.getVmCnx("tenant-green-2"),"10.0.0.1", exp.GetMacByVf("enp3s0f5"), exp.VfsMatch["enp3s0f7"])
     
    ################################################

    EmailNotify(msg, "is ready", logTimeStamp)
    return True

def bench_phy2vm2vm2phy_SRIOV_MultiOvs_NoDPDK(cnx_server, config):
        
    #----------------------------------------#
    exp.NicType= "mlx"
    exp.isSRIOV= True
    exp.IsDPDK= False
    exp.OVS_PATH= exp.nodpdk_path
    exp.Server_cnx= cnx_server
    exp.scsName= "bench_phy2vm2vm2phy_SRIOV_MultiOvs_NoDPDK"
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    #----------------------------------------#
    cpu_config= CpuAllocation(config)
    
    exp.PhyPorts= [
           ("enp3s0f0", "8")
          ]
    
    exp.MyVfs= [
            ("enp3s0f2", "0", "off", "vswitch-vm"),
            ("enp3s0f3", "0", "off", "vswitch-vm"),            
            ("enp3s0f4","10", "off", "vswitch-vm"),
            ("enp3s0f5","10", "off", "tenant-green-1"),
            
            ("enp3s0f6", "0", "off", "vswitch-vm-2"),
            ("enp3s0f7", "0", "off", "vswitch-vm-2"),              
            ("enp3s1",  "20", "off", "vswitch-vm-2"),
            ("enp3s1f1","20", "off", "tenant-green-2")
            ]
    
    exp.usedVms=[
             ("vswitch-vm", cpu_config[0][0], "4G"),
             ("tenant-green-1", cpu_config[1][0], "4G"),
             
             ("vswitch-vm-2", cpu_config[0][1], "4G"),
             ("tenant-green-2", cpu_config[1][1], "4G")]
   
        
    OvsCpu= cpu_config[2]
    #----------------- OVS-VM_1------------------    
    OvsVmPorts1= [
                ("enp3s0f2", False),
                ("enp3s0f3", False),
                ("enp3s0f4", False)]  

    #----------------- OVS-VM_2------------------  
    OvsVmPorts2= [
                ("enp3s0f6", False),
                ("enp3s0f7", False),
                ("enp3s1", False)]   
    
    
    msg= GetScenarioSummary([OvsVmPorts1, OvsVmPorts2], OvsCpu, [], "")
    EmailNotify(msg, "is beeing prepared", logTimeStamp)
    Logs(msg,config, logTimeStamp)
     
    #----------------------------------------#
    exp.RebootServer(BenServer, wait=False)
    exp.InitialConfig()
    exp.Vfsconfig()
    exp.ConfigOVS("vswitch-vm", "br0", OvsVmPorts1, OvsCpu)
    exp.ConfigOVS("vswitch-vm-2", "br0", OvsVmPorts2, OvsCpu)
    
    '''
    OVS Flow Rules for OVS-VM-1:
        
    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f2"]+",ip,nw_dst=10.0.0.2"
    action="mod_dl_dst:"+exp.GetMacByVf("enp3s0f5")+","+exp.VfsMatch["enp3s0f4"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f4"]
    action="mod_dl_dst:"+BenIntrMac+","+exp.VfsMatch["enp3s0f3"]
    exp.addFlowRule("vswitch-vm" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm", exp.OVS_PATH,"br0")
    
    '''
    OVS Flow Rules for OVS-VM-2:
        
    '''
    #Flow Rules (1)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s0f6"]+",ip,nw_dst=10.0.0.3"
    action="mod_dl_dst:"+exp.GetMacByVf("enp3s1f1")+","+exp.VfsMatch["enp3s1"]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)
    
    #Flow Rules (2)
    #---------------------------------------------------------    
    match="in_port="+exp.VfsMatch["enp3s1"]
    action="mod_dl_dst:"+BenIntrMac+","+exp.VfsMatch["enp3s0f7"]
    exp.addFlowRule("vswitch-vm-2" , exp.OVS_PATH, "br0", match, action)

    #show Flow rules of br0 
    exp.showFlowRules("vswitch-vm-2", exp.OVS_PATH,"br0")
    
    ###############################################
    exp.setCnxLimit(BenServer, 4096)
    exp.SetInt(BenServer,BenIntr,"up")
    exp.SetIpInt(BenServer, BenIntr, "10.0.0.1/24")
    exp.SetArpEntry(BenServer,"10.0.0.2", exp.GetMacByVf("enp3s0f2"), BenIntr)
    exp.SetArpEntry(BenServer,"10.0.0.3", exp.GetMacByVf("enp3s0f6"), BenIntr)
    
    ###############################################
    
    exp.SetIpInt(exp.getVmCnx("tenant-green-1"), "ens8", "10.0.0.2/24")
    exp.SetIpInt(exp.getVmCnx("tenant-green-2"), "ens8", "10.0.0.3/24")
    
    exp.SetArpEntry(exp.getVmCnx("tenant-green-1"),"10.0.0.1", exp.GetMacByVf("enp3s0f4"), exp.VfsMatch["enp3s0f5"])
    exp.SetArpEntry(exp.getVmCnx("tenant-green-2"),"10.0.0.1", exp.GetMacByVf("enp3s1"), exp.VfsMatch["enp3s1f1"])
     
    ################################################
    
        
    EmailNotify(msg, "is ready", logTimeStamp)
    return True



def bench_phy2vm2vm2phy_Baseline_MultiTenant_NoDPDK(cnx_server, config):
    # ----------------------------------------#
    exp.NicType = "mlx"
    exp.isSRIOV = False
    exp.IsDPDK = False
    exp.OVS_PATH = exp.nodpdk_path
    exp.Server_cnx = cnx_server
    exp.scsName= "bench_phy2vm2vm2phy_Baseline_MultiTenant_NoDPDK"
    logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


    # ----------------------------------------#
    cpu_config= CpuAllocation(config)
    
    exp.PhyPorts = [
        ("enp3s0f0", "br0")
    ]

    exp.VirtualPorts = [
        ("1", "br0", "tenant-green-1"),
        ("3", "br0", "tenant-green-2")
    ]

    exp.usedVms = [
        ("tenant-green-1", cpu_config[1][0], "4G"),
        ("tenant-green-2", cpu_config[1][1], "4G")]

    OvsCpu = cpu_config[2]
    
    
    msg= GetScenarioSummary([], OvsCpu, [], "")
    EmailNotify(msg, "is beeing prepared", logTimeStamp)
    Logs(msg,config, logTimeStamp)
    # ----------------------------------------#
    exp.RebootServer(BenServer, wait=False)
    exp.InitialConfig()
    exp.ConfigOVS(exp.Server_cnx, "br0", " ", OvsCpu)
    exp.VirPortConfig()

    '''
    OVS Flow Rules for Tenant-1:
    '''
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
    
    '''
    OVS Flow Rules for Tenant-2:
    '''
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

    # show Flow rules of br0
    exp.showFlowRules(exp.Server_cnx, exp.OVS_PATH, "br0")
    
    ###############################################
    exp.setCnxLimit(BenServer, 4096)
    exp.SetInt(BenServer,BenIntr,"up")
    exp.SetIpInt(BenServer, BenIntr, "10.0.0.1/24")
    exp.SetArpEntry(BenServer,"10.0.0.2", exp.GenerateMacID("1"), BenIntr)
    exp.SetArpEntry(BenServer,"10.0.0.3", exp.GenerateMacID("3"), BenIntr)
    
    ###############################################
    
    exp.SetIpInt(exp.getVmCnx("tenant-green-1"), "ens8", "10.0.0.2/24")
    exp.SetIpInt(exp.getVmCnx("tenant-green-2"), "ens8", "10.0.0.3/24")
    
    exp.SetArpEntry(exp.getVmCnx("tenant-green-1"),"10.0.0.1", BenIntrMac, "ens8")
    exp.SetArpEntry(exp.getVmCnx("tenant-green-2"),"10.0.0.1", BenIntrMac, "ens8")
     
    ################################################

    
    EmailNotify(msg, "is ready", logTimeStamp)
    return True


