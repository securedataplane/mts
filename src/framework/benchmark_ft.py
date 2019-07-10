#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 29 09:59:18 2018

@author: saad
"""
import expLib as exp
import multiprocessing
import scsLib as scs
import BenchParser as benp
import os 
from datetime import datetime
import BenchScs as ben
import time

############################# Benchmark vars ##################################
#DUT
DutServer=exp.cnx_plane

#Benchmark Server
benServer= exp.cnx_spree

#Tenants Ips
Tenant1_ip= "10.0.0.2"
Tenant2_ip= "10.0.0.3"
Tenant3_ip= "10.0.0.4"
Tenant4_ip= "10.0.0.5"

Tenants=["tenant-green-1",
         "tenant-green-2",
         "tenant-green-3",
         "tenant-green-4"]

#concurrency Levels
concurrencyList=[1000]

#iperf vars
IperfTime="100"

#ab vars
AbTime="100"

#memcashed vars
MemPort="11211"
MemTime="100"

prefix="Parsed_"

#files to store data
dir_path = os.path.dirname(os.path.realpath(__file__))
fIperfBenchmark= "Iperf_Benchmark_Data.csv"
fAbBenchmark= "Ab_Benchmark_Data.csv"
fMemBenchmark= "Mem_Benchmark_Data.csv"


topologies = ["phy2vm2vm2phy", "VM2VM"]

vswitchModes = ["Baseline",
                "SRIOV_OneOvs",
                "SRIOV_TwoOvs",
                "SRIOV_FourOvs",
                "Baseline_NoDPDK_2Core",
                "Baseline_NoDPDK_4Core"]

cpuIsolation = [True]
DPDK = [False]

########################################### Benchmark Scenarios#############################################

def prepTestbed(cnx, topology, vswitchMode, isDPDK, isolateCPUs):
    print "prepTestbed" + "topology: " + topology + ", vswitchMode: " + vswitchMode + ", isolateCPUs: " + str(isolateCPUs)
    
    if isDPDK and not isolateCPUs:
        return False
        
    if topology== "phy2vm2vm2phy":
        
        if vswitchMode== "Baseline" or vswitchMode == "Baseline_NoDPDK_2Core" or vswitchMode == "Baseline_NoDPDK_4Core" and isolateCPUs and not isDPDK:
            exp.RebootServer(benServer, wait=True)
            ben.phy2vm2vm2phy_Baseline(cnx_server= cnx, isDPDK=False, nbrCores=getNbrCores(vswitchMode, isolateCPUs))
                     
        elif vswitchMode == "SRIOV_OneOvs" and isolateCPUs:
            exp.RebootServer(benServer, wait=True)
            ben.phy2vm2vm2phy_SRIOV_OneOvs(cnx_server= cnx, isDPDK=isDPDK, nbrCores=1)
        
        elif vswitchMode == "SRIOV_TwoOvs":
            exp.RebootServer(benServer, wait=True)
            ben.phy2vm2vm2phy_SRIOV_TwoOvs(cnx_server= cnx, isDPDK=isDPDK, nbrCores=1, isIsolated=isolateCPUs)
            
        elif vswitchMode == "SRIOV_FourOvs":
            exp.RebootServer(benServer, wait=True)
            ben.phy2vm2vm2phy_SRIOV_FourOvs(cnx_server= cnx, isDPDK=isDPDK, nbrCores=1, isIsolated=isolateCPUs)
            
        else:
            return False
    
    
    elif topology== "VM2VM" and vswitchMode != "SRIOV_FourOvs":
        
        if vswitchMode== "Baseline" or vswitchMode == "Baseline_NoDPDK_2Core" or vswitchMode == "Baseline_NoDPDK_4Core" and isolateCPUs and not isDPDK:
            ben.vm2vm_Baseline(cnx_server= cnx, isDPDK=False, nbrCores=getNbrCores(vswitchMode, isolateCPUs))
                  
        elif vswitchMode == "SRIOV_OneOvs"  and isolateCPUs:
            exp.RebootServer(benServer, wait=True)
            ben.vm2vm_SRIOV_OneOvs(cnx_server= cnx, isDPDK=isDPDK, nbrCores=1)
        
        elif vswitchMode == "SRIOV_TwoOvs":
            exp.RebootServer(benServer, wait=True)
            ben.vm2vm_SRIOV_TwoOvs(cnx_server= cnx, isDPDK=isDPDK, nbrCores=1, isIsolated=isolateCPUs)
            
        else:
            return False
    
    else:
       return False
                               
#############################################################################################################
########################################## Helper Functions #################################################
#############################################################################################################
def getNbrCores(vswitchMode="Baseline_NoDPDK", cpuIsolation=False):
    print "getNbrCores()"
    if cpuIsolation is False:
        print "cpuIsolation False:"
        if vswitchMode == "Baseline_NoDPDK" or vswitchMode == "SRIOV_NoDPDK_OneOvs" or \
                vswitchMode == "SRIOV_NoDPDK_TwoOvs" or vswitchMode == "SRIOV_NoDPDK_FourOvs" or\
                vswitchMode == "Baseline":
            # print "1 core for shared and NoDPDK vswitchMode"
            return 1
        elif vswitchMode == "Baseline_DPDK" or \
                vswitchMode == "SRIOV_DPDK_OneOvs" or \
                vswitchMode == "SRIOV_DPDK_TwoOvs" or \
                vswitchMode == "SRIOV_DPDK_FourOvs" or \
                vswitchMode == "Baseline_NoDPDK_2Cores" or \
                vswitchMode == "Baseline_NoDPDK_4Cores":
            print "No DPDK, Baseline_NoDPDK_2Cores and Baseline_NoDPDK_4Cores when cpuIsolation is False."
        else:
            print "Unknown vswitchMode"
            exit()
    elif cpuIsolation is True:
        print "cpuIsolation True:"
        if vswitchMode == "Baseline_NoDPDK" or vswitchMode == "Baseline_DPDK" or vswitchMode == "Baseline":
            return 1
        elif vswitchMode == "Baseline_NoDPDK_2Core":
            return 2
        elif vswitchMode == "Baseline_DPDK_2Core":
            return 3
        elif vswitchMode == "Baseline_NoDPDK_4Core":
            return 4
        elif vswitchMode == "Baseline_DPDK_4Core":
            return 5
        elif vswitchMode == "SRIOV_NoDPDK_OneOvs" or vswitchMode == "SRIOV_DPDK_OneOvs":
            return 1
        elif vswitchMode == "SRIOV_NoDPDK_TwoOvs" or vswitchMode == "SRIOV_DPDK_TwoOvs":
            return 1
        elif vswitchMode == "SRIOV_NoDPDK_FourOvs" or vswitchMode == "SRIOV_DPDK_FourOvs":
            return 1
        else:
            print "Unknown vswitchMode"
            exit()

def prepareOutputFiles():
    f = open(fAbBenchmark, 'a')   
    f.write("Timestamp, concurrency, Document Length, Full Test Time (s), Complete requests, Failed requests, Requests per second, Transfer rate (Kbytes/sec), mean (ms), standard deviation, 50% (ms), 99% (ms), Tenant ,topology ,vswitchMode ,DPDK ,Cpu Isolation\n")
    f.close()
        
    f = open(fMemBenchmark, 'a')   
    f.write("Timestamp, concurrency, The average response time (us) ,standard deviation, Throughput(ops/s), Total Operations,Test Time (s), Tenant,topology ,vswitchMode ,DPDK ,Cpu Isolation \n")
    f.close()
    
    f = open(fIperfBenchmark, 'a')   
    f.write("Timestamp,  S_Transfer (GBytes), S_Bandwidth (Mbits/sec), S_Retr, R_Transfer(GBytes), R_Bandwidth (Mbits/sec), Test Time (s), Tenant,topology ,vswitchMode, DPDK ,Cpu Isolation \n")
    f.close()

def prepareMemServersList(topo):
    MemServers=""  
    if topo=="phy2vm2vm2phy":
        MemServers= Tenant1_ip+":"+MemPort+","\
           +Tenant2_ip+":"+MemPort+","\
           +Tenant3_ip+":"+MemPort+","\
           +Tenant4_ip+":"+MemPort
    elif topo=="VM2VM":
        MemServers= Tenant2_ip+":"+MemPort+","\
                   +Tenant4_ip+":"+MemPort                 
    return MemServers    

def getTimeStamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def descToCsv(scsDisc):
    return  scsDisc[0]+" ,"+scsDisc[1]+" ,"+str(scsDisc[2])+" ,"+str(scsDisc[3])

def descTotext(scsDisc):
    return "Topology: "+scsDisc[0]+" vswitch Mode: "+scsDisc[1]+" DPDK: "+str(scsDisc[2])+" ,Cpu Isolation: "+str(scsDisc[3])
        
def startIperfServer(cnx):
    print "starting Iperf Server on: "+cnx[0]+"\n"
    ssh = exp.SSHConnect(cnx)    
    cmd="iperf3  -s -D"
    exp.RunCommand(ssh, cmd)
    time.sleep(5)
    ssh.close()


def stopIperfServer(cnx):
    print "stoping Iperf Server on: "+cnx[0]+"\n"
    ssh = exp.SSHConnect(cnx)
    lines =exp.RunCommand(ssh ,"ps aux| grep iperf")
    for l in lines:
        if " iperf3 -s -D" in l:
            tmp=l
            tmp=tmp.split()
            exp.RunCommand(ssh ,"kill -9 "+tmp[1])
            time.sleep(5)
            break
    ssh.close()
    

def startStopVMService(cnx ,service ,state):
    print state+" "+service+" Server on: "+cnx[0]+"\n"    
    if service=="iperf" and state=="start":
        startIperfServer(cnx)
    elif service=="iperf" and state=="stop":
        stopIperfServer(cnx)
    
    else:
        ssh = exp.SSHConnect(cnx)
        exp.RunCommand(ssh ,"service "+service+" "+state)
        time.sleep(5)
        ssh.close()
    
    
def StopVmServices(cnx):
    startStopVMService(cnx ,"apache2" ,"stop")
    startStopVMService(cnx ,"memcached" ,"stop")
    startStopVMService(cnx ,"iperf" ,"stop")
    

def StopVMsServices():
    for t in Tenants:
        cnx=exp.getVmCnx(t)
        StopVmServices(cnx)
        

def startVMsService(service):
    for t in Tenants:
        cnx=exp.getVmCnx(t)
        startStopVMService(cnx,service,"start")
     

def emailFinalData(timeStamp):
    scs.EmailNotify(body="Apache Server Benchmarking Final Data", state="_Apache Server Benchmarking Final Data_", time=timeStamp, attachmentPath=dir_path+"/"+prefix+fAbBenchmark)
    scs.EmailNotify(body="Memcached Benchmarking Final Data", state="_Memcached Benchmarking Final Data_", time=timeStamp, attachmentPath=dir_path+"/"+prefix+fMemBenchmark)
    scs.EmailNotify(body="Iperf Benchmarking Final Data", state="_Iperf Benchmarking Final Data_", time=timeStamp, attachmentPath=dir_path+"/"+prefix+fIperfBenchmark)

     

#############################################################################################################
########################################## Main Benchmark ###################################################
#############################################################################################################    
def doBenchMark():
    rept=5
    print ("Benchmarking started ...") 

    for d in DPDK:
        for c in cpuIsolation:
            for t in topologies:
                for v in vswitchModes:
                    desc= [t,v,d,c]
                    
                    #preparing the testbed
                    result= prepTestbed(DutServer ,t ,v ,d ,c)
                    if result==False:
                       print  "Scenario ignored: "+descTotext(desc)+"\n"
                    else:
                        
                        #do Iperf Benchmark
                        StopVMsServices()
                        startVMsService("iperf")
                        for rp in range(rept):
                            doIperfBenchMark(desc)
                        
                        #do Apache Server Benchmark
                        StopVMsServices()
                        startVMsService("apache2")
                        for rp2 in range(rept):
                            doAbBenchMark(desc)
                
                        #do Memcached Benchmark
                        StopVMsServices()
                        startVMsService("memcached")
                        for rp3 in range(rept):
                            doMemBenchmark(desc)
                        
                    
#############################################################################################################
########################################## Iperf benchmark ##############################################
#############################################################################################################
def doIperfBenchMark(scsDisc):
    print ("Iperf Benchmarking started ...")
    logTimeStamp = getTimeStamp()
    scs.EmailNotify(body="Iperf Benchmarking started", state="_Iperf Benchmarking started_", time=logTimeStamp)
   
    runFullIperfBenchmark(scsDisc)
    
    logTimeStamp = getTimeStamp()
    scs.EmailNotify(body="Iperf Benchmarking Done", state="_Iperf Benchmarking Done_", time=logTimeStamp, attachmentPath=dir_path+"/"+fIperfBenchmark)

                                      
def runIperfBenchmark(testTime, tenant, tenantIp, cpu, scsDisc):
    results=[]
    timeStamp=getTimeStamp()
    resultStr=""
    
    ssh = exp.SSHConnect(benServer)    
    cmd="iperf3  -c "+tenantIp+" -A "+str(cpu)+" -t "+str(testTime)+" -f m"
    lines=exp.RunCommand(ssh, cmd)
    ssh.close()
    
    for l in lines:
        #print l
        if not l=="\n":
            tmp=l
            tmp=tmp.split()
            
            if "sender" in l:
                results.append(tmp[4]+"["+tmp[5]+"]")  #Transfer
                results.append(tmp[6]+"["+tmp[7]+"]") #Bandwidth
                results.append(tmp[8]) #Retr
                 
            elif "receiver" in l:
                results.append(tmp[4]+"["+tmp[5]+"]") #Transfer
                results.append(tmp[6]+"["+tmp[7]+"]")  #Bandwidth
            
    # writting output to a file    
    f = open(fIperfBenchmark, 'a')  
    for r in results:
        resultStr=resultStr+r+" "
    f.write(timeStamp+", "+resultStr.replace(" ",", ")+""+str(testTime)+" ,"+str(tenant)+" ,"+descToCsv(scsDisc)+"\n")
    f.close()
                                             
def runFullIperfBenchmark(scsDisc):
    print ("Starting Iperf Benchmarking for "+descTotext(scsDisc)+" \n")
    if scsDisc[0] == "phy2vm2vm2phy":
        
        p1 = multiprocessing.Process(target=runIperfBenchmark, args=(AbTime ,1 ,Tenant1_ip , 1, scsDisc,))
        p1.start()
        p2 = multiprocessing.Process(target=runIperfBenchmark, args=(AbTime ,2 ,Tenant2_ip , 2, scsDisc,))
        p2.start()
        p3 = multiprocessing.Process(target=runIperfBenchmark, args=(AbTime ,3 ,Tenant3_ip , 3, scsDisc,))
        p3.start()
        p4 = multiprocessing.Process(target=runIperfBenchmark, args=(AbTime ,4 ,Tenant4_ip , 4, scsDisc,))
        p4.start()
            
        while(True):
            if (p1.is_alive()==False and p2.is_alive()==False and p3.is_alive()==False and p4.is_alive()==False):
                break
                
            
    elif scsDisc[0] == "VM2VM":
        p2 = multiprocessing.Process(target=runIperfBenchmark, args=(AbTime ,2 ,Tenant2_ip , 2, scsDisc,))
        p2.start()
        p4 = multiprocessing.Process(target=runIperfBenchmark, args=(AbTime ,4 ,Tenant4_ip , 4, scsDisc,))
        p4.start()
            
        while(True):
            if ( p2.is_alive()==False and p4.is_alive()==False):
                break
                
    time.sleep(150)
    print ("Iperf Benchmarking Done for "+descTotext(scsDisc)+" \n")

#############################################################################################################
########################################## Apache benchmark #################################################
#############################################################################################################      
def doAbBenchMark(scsDisc):
    print ("Apache Server Benchmarking started ...")
    logTimeStamp = getTimeStamp()
    scs.EmailNotify(body="Apache Server Benchmarking started", state="_Apache Benchmarking started_", time=logTimeStamp)
   
    runFullAbBenchmark(scsDisc)
    
    logTimeStamp = getTimeStamp()
    scs.EmailNotify(body="Apache Server Benchmarking Done", state="_Apache Benchmarking Done_", time=logTimeStamp, attachmentPath=dir_path+"/"+fAbBenchmark)

                                      
def runAbBenchmark(testTime, concurrency, tenant, tenantIp, cpu, scsDisc):
    results=[]
    RequestsCount="60000000"
    resultStr=""
    timeStamp=getTimeStamp()
    #LinkUnderTest= "http://"+tenantIp+":80/test.html"
    LinkUnderTest= "http://"+tenantIp+":80/"
        
    ssh = exp.SSHConnect(benServer)    
    cmd="taskset  --cpu-list "+str(cpu)+" ab -t "+str(testTime)+" -n "+RequestsCount+" -c "+str(concurrency)+" "+LinkUnderTest
    
    lines=exp.RunCommand(ssh, cmd)
     
    ssh.close()
    
    for l in lines:
        if not l=="\n":
            #print l
            tmp=l
            tmp=tmp.split()
            
            if "Document Length:" in l:
                results.append(tmp[2]) #Time taken for tests  
                
            elif "Time taken for tests:" in l:
                results.append(tmp[4]) #Time taken for tests    
                
            elif "Complete requests:" in l:
                results.append(tmp[2]) #requests   
                
            elif "Failed requests:" in l:
                results.append(tmp[2]) #Failed requests
            
            elif "Requests per second:" in l:
                results.append(tmp[3]) #Requests per second
            
            elif "Transfer rate:" in l:
                results.append(tmp[2]+tmp[3]) #Transfer rate
            
            elif tmp[0]=="Total:":
                results.append(tmp[2]) #mean
                results.append(tmp[3]) #standard deviation
            
            elif tmp[0]=="50%" and len(tmp)==2:
                results.append(tmp[1]) #50%
                
            elif tmp[0]=="99%" and len(tmp)==2:
                results.append(tmp[1]) #99%       
    
     
    # writting output to a file    
    f = open(fAbBenchmark, 'a')  
    for r in results:
        resultStr=resultStr+r+" "
    f.write(timeStamp+" ,"+str(concurrency)+", "+resultStr.replace(" ",", ")+""+str(tenant)+" ,"+scsDisc[0]+" ,"+scsDisc[1]+" ,"+str(scsDisc[2])+" ,"+str(scsDisc[3])+"\n")
    f.close()                   

                     
def runFullAbBenchmark(scsDisc):
    print ("Starting Apache Benchmarking for Topology: "+scsDisc[0]+" vswitch Mode: "+scsDisc[1]+" DPDK: "+str(scsDisc[2])+" ,Cpu Isolation: "+str(scsDisc[3])+" \n")
    for c in concurrencyList:
        if scsDisc[0] == "phy2vm2vm2phy":
            
            p1 = multiprocessing.Process(target=runAbBenchmark, args=(AbTime ,c ,1 ,Tenant1_ip , 1, scsDisc,))
            p1.start()
            p2 = multiprocessing.Process(target=runAbBenchmark, args=(AbTime ,c ,2 ,Tenant2_ip , 2, scsDisc,))
            p2.start()
            p3 = multiprocessing.Process(target=runAbBenchmark, args=(AbTime ,c ,3 ,Tenant3_ip , 3, scsDisc,))
            p3.start()
            p4 = multiprocessing.Process(target=runAbBenchmark, args=(AbTime ,c ,4 ,Tenant4_ip , 4, scsDisc,))
            p4.start()
            while(True):
                if (p1.is_alive()==False and p2.is_alive()==False and p3.is_alive()==False and p4.is_alive()==False):
                    break
                
        elif scsDisc[0] == "VM2VM":
                
            p2 = multiprocessing.Process(target=runAbBenchmark, args=(AbTime ,c ,2 ,Tenant2_ip , 2, scsDisc,))
            p2.start()
            
            p4 = multiprocessing.Process(target=runAbBenchmark, args=(AbTime ,c ,4 ,Tenant4_ip , 4, scsDisc,))
            p4.start()
            while(True):
                if (p2.is_alive()==False and  p4.is_alive()==False):
                    break
                
    time.sleep(150)
    print ("Apache Benchmarking Done for Topology: "+scsDisc[0]+" vswitch Mode: "+scsDisc[1]+" DPDK: "+str(scsDisc[2])+" ,Cpu Isolation: "+str(scsDisc[3])+" \n")
     
#############################################################################################################
########################################## Memcached benchmark ##############################################
#############################################################################################################   

def doMemBenchmark(scsDisc):
    print ("Memcached Benchmarking started ...")
    logTimeStamp = getTimeStamp()
    scs.EmailNotify(body="Memcached Benchmarking started", state="_Memcached Benchmarking started_", time=logTimeStamp)
    
    runFullMemBenchmark(scsDisc)
    
    logTimeStamp = getTimeStamp()
    scs.EmailNotify(body="Memcached Benchmarking Done", state="_Memcached Benchmarking Done_", time=logTimeStamp, attachmentPath=dir_path+"/"+fMemBenchmark)
    
    
def runMemBenchmark(testTime ,concurrency, tenant, tenantIp, cpu, scsDisc):
    results=[] 
    resultStr=""
    timeStamp=getTimeStamp()
    startReading=False
    MemCachedServer= tenantIp+":"+MemPort
    ssh = exp.SSHConnect(benServer)    
    cmd="cd ~/memcachedBench/libmemcached-1.0.15/clients/; taskset  --cpu-list "+str(cpu)+" ./memaslap -s "+MemCachedServer+" -t "+str(testTime)+"s  -c "+str(concurrency)+" -S 2d"
    
    lines=exp.RunCommand(ssh, cmd)
    ssh.close()
    
    for l in lines:
        if not l=="\n":
            #print l
            tmp=l
            tmp=tmp.split()
            
            if tmp[0]=="Total" and tmp[1]=="Statistics":
               startReading=True
            
            if startReading and tmp[0]=="Avg:":
                results.append(tmp[1]) #50%
                
            if startReading and tmp[0]=="Std:":
                results.append(tmp[1]) #50%   
                
            if tmp[0]=="Run" and tmp[1]=="time:" and tmp[3]=="Ops:":
               results.append(tmp[6]) # Throughput
               results.append(tmp[4]) # Total Operations
               results.append(tmp[2]) # Test Time
    
    # writting output to a file    
    f = open(fMemBenchmark, 'a')  
    for r in results:
        resultStr=resultStr+r+" "
    f.write(timeStamp+" ,"+str(concurrency)+", "+resultStr.replace(" ",", ")+" "+str(tenant)+" ,"+scsDisc[0]+" ,"+scsDisc[1]+" ,"+str(scsDisc[2])+" ,"+str(scsDisc[3])+"\n")
    f.close()    


def runFullMemBenchmark(scsDisc):
    print ("Starting Memcached Benchmarking for "+descTotext(scsDisc)+" \n")
    for c in concurrencyList:
        
        if scsDisc[0] == "phy2vm2vm2phy":
            
            p1 = multiprocessing.Process(target=runMemBenchmark, args=(MemTime ,c ,1 ,Tenant1_ip , 1, scsDisc,))
            p1.start()
            p2 = multiprocessing.Process(target=runMemBenchmark, args=(MemTime ,c ,2 ,Tenant2_ip , 2, scsDisc,))
            p2.start()
            p3 = multiprocessing.Process(target=runMemBenchmark, args=(MemTime ,c ,3 ,Tenant3_ip , 3, scsDisc,))
            p3.start()
            p4 = multiprocessing.Process(target=runMemBenchmark, args=(MemTime ,c ,4 ,Tenant4_ip , 4, scsDisc,))
            p4.start()
            while(True):
                if (p1.is_alive()==False and p2.is_alive()==False and p3.is_alive()==False and p4.is_alive()==False):
                    break
                
        elif  scsDisc[0] == "VM2VM":

            p2 = multiprocessing.Process(target=runMemBenchmark, args=(MemTime ,c ,2 ,Tenant2_ip , 2, scsDisc,))
            p2.start()
            
            p4 = multiprocessing.Process(target=runMemBenchmark, args=(MemTime ,c ,4 ,Tenant4_ip , 4, scsDisc,))
            p4.start()
            while(True):
                if (p2.is_alive()==False and  p4.is_alive()==False):
                    break
                
    time.sleep(150)
    print ("Memcached Benchmarking Done for  "+descTotext(scsDisc)+" \n")

    
############################################## Start Benchmarking #################################################  
#get the Date 5 times
'''
for i in range(5):  
   prepareOutputFiles()
   doBenchMark()

scsDisc=["VM2VM", "Baseline", True, True]
for i in range(5):
    runFullMemBenchmark(scsDisc)
    time.sleep(150)
#runFullAbBenchmark(scsDisc)
#runFullMemBenchmark(scsDisc)

benp.parser()
timeStamp=getTimeStamp()
emailFinalData(timeStamp)
'''

prepareOutputFiles()
doBenchMark()
benp.parser()
timeStamp=getTimeStamp()
emailFinalData(timeStamp)
###################################################################################################################

