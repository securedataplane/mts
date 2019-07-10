#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 10:08:42 2018

@author: saad
"""
############################ File Names ##################################
fIperfBenchmark= "Iperf_Benchmark_Data.csv"
fAbBenchmark= "Ab_Benchmark_Data.csv"
fMemBenchmark= "Mem_Benchmark_Data.csv"

'''
def prepareOutputFiles():
    prefix="Parsed_"
    f = open(prefix+fAbBenchmark, 'a')   
    f.write("Timestamp, concurrency, Document Length, Full Test Time, Complete requests, Failed requests, Requests per second, Transfer rate, mean, 50%, 99% ,topology ,vswitchMode ,DPDK ,Cpu Isolation\n")
    f.close()
        
    f = open(prefix+fMemBenchmark, 'a')   
    f.write("Timestamp, concurrency, The average response time ,standard deviation, Throughput, Total Operations,Test Time,topology ,vswitchMode ,DPDK ,Cpu Isolation \n")
    f.close()
    
    f = open(prefix+fIperfBenchmark, 'a')   
    f.write("Timestamp,  S_Transfer, S_Bandwidth, S_Retr,R_Transfer, R_Bandwidth, Test Time,topology ,vswitchMode, DPDK ,Cpu Isolation \n")
    f.close()
'''
    
def prepareOutputFiles():
    prefix="Parsed_"
    f = open(prefix+fAbBenchmark, 'a')   
    f.write("Timestamp, concurrency, Document Length, Full Test Time (s), Complete requests, Failed requests, Requests per second, Transfer rate (Kbytes/sec), mean (ms), 50% (ms), 99% (ms) ,topology ,vswitchMode ,DPDK ,Cpu Isolation\n")
    f.close()
        
    f = open(prefix+fMemBenchmark, 'a')   
    f.write("Timestamp, concurrency, The average response time (ms) , Throughput(ops/s), Total Operations,Test Time (s),topology ,vswitchMode ,DPDK ,Cpu Isolation \n")
    f.close()
    
    f = open(prefix+fIperfBenchmark, 'a')   
    f.write("Timestamp,  S_Transfer (GBytes), S_Bandwidth (Mbits/sec), S_Retr, R_Transfer(GBytes), R_Bandwidth (Mbits/sec), Test Time (s), topology ,vswitchMode, DPDK ,Cpu Isolation \n")
    f.close()
    
def writeToFile(data,path):
    prefix="Parsed_"
    resultStr=""
    
    l= len(data)
    for entry in data:
        f = open(prefix+path, 'a')
        l=l-1
        if l!=0:
            resultStr=resultStr+str(entry)+","
        else:
            resultStr=resultStr+str(entry)
    f.write(resultStr)
    f.close()
        
        
def preFloat(flw):
    return float("{0:.2f}".format(flw))
#####################################################################
def prepareDataArray(dataPath):
    with open(dataPath) as f:
        dataArray=[]
        lines = f.readlines()
        for l in lines:
            if l!="" and l!="\n" and not l.startswith("Timestamp"):
               d=l.split(",")
               if len(d)>10:
                   dataArray.append(d)
    dataArray
    return dataArray

def cleanDataArray(dataArray, service):
    indx=0
    if len(dataArray) > 0:
        d= len(dataArray[0])
    
    while indx<len(dataArray):
         dp=dataArray[indx]
         desc= dp[d-4:d]
         vmsNbr=0
         
         if "phy2vm2vm2phy" in desc[0]:
             vmsNbr=4
             
         elif "VM2VM" in desc[0]:
             vmsNbr=2
         
         missingData=False
         
         if service!="iperf":
             c= dp[1]
             for i in range(1,vmsNbr):
                 if not dataArray[indx+i][d-4:d]==desc or not dataArray[indx+i][1]==c :
                      missingData=True
                      print ("missing Data ..."+ str(desc)+ "\n")
                      indx=indx+i
                      break
         else:
             for i in range(1,vmsNbr):
                 if not dataArray[indx+i][d-4:d]==desc:
                      missingData=True
                      indx=indx+i
                      break
             
         if missingData==False:
             pdata= dataArray[indx:indx+vmsNbr]
             indx= indx+vmsNbr
             processesData(pdata, service)
             
             
def processesData(data,service):
    if service=="iperf":
        processIperf(data)
    
    elif service=="mem":
        processMem(data)
        
    elif service=="ab":
        processAb(data)
        
                
def processIperf(data):
    results= [] 
    S_Transfer=0 #S_Transfer
    S_Bandwidth=0 #S_Bandwidth
    S_Retr=0 #S_Retr
    R_Transfer=0 #RR_Transfer
    R_Bandwidth=0 #R_Bandwidth
    
    for l in data:
        tmp=l[1]
        S_Transfer=S_Transfer+ float(tmp[0:tmp.index('[')])
        
        tmp=l[2]
        S_Bandwidth=S_Bandwidth+ float(tmp[0:tmp.index('[')])
        
        S_Retr=S_Retr+int(l[3])
        
        tmp=l[4]
        R_Transfer=R_Transfer+ float(tmp[0:tmp.index('[')])
        
        tmp=l[5]
        R_Bandwidth=R_Bandwidth+ float(tmp[0:tmp.index('[')])
    
    results.append(data[0][0])    
    results.append(preFloat(S_Transfer))
    results.append(preFloat(S_Bandwidth))
    results.append(S_Retr)
    results.append(preFloat(R_Transfer))
    results.append(preFloat(R_Bandwidth))
    results.append(int(data[0][6]))
    
    d=len(data[0])
    for info in data[0][d-4:d]:
        results.append(info)
    
    writeToFile(results,fIperfBenchmark)


def processAb(data):
    results= data[0][0:4]
    compReq=0 #Complete requests
    FailReq=0#Failed requests
    ReqPerSec=0#Requests per second
    TransRate=0#Transfer rate (Kbytes)
    SumMean=0 #SumMean
    SumMed=0 # Sum 50%
    SumN=0 #Sum 90%
    
    for l in data:
        compReq=compReq+ int(l[4])
        FailReq=FailReq+int(l[5])
        ReqPerSec= ReqPerSec+ float(l[6])
        trKb=l[7]
        TransRate=TransRate+float(trKb[0:trKb.index('[')])
        SumMean=SumMean+float(l[8])
        SumMed=SumMed+float(l[10])
        SumN=SumN+float(l[11])
    
    
    mean=SumMean/len(data) 
    Med= SumMed/len(data)
    N=SumN/len(data)
    
    results.append(compReq)
    results.append(FailReq)
    results.append(preFloat(ReqPerSec))
    results.append(preFloat(TransRate))
    results.append(preFloat(mean))
    results.append(preFloat(Med))
    results.append(preFloat(N))
    
    d=len(data[0])
    for info in data[0][d-4:d]:
        results.append(info)
    
    writeToFile(results,fAbBenchmark)
    
def processMem(data):
    results= [] 
 
    avrRespTime=0 #The average response time
    Throughput=0 #Throughput
    totalOpt=0 #Total Operations
    
    for l in data:
        avrRespTime=avrRespTime+ int(l[2])
        Throughput= Throughput+ int(l[4])
        totalOpt=totalOpt+int(l[5])
       
    
    results.append(data[0][0])  
    results.append(data[0][1])
    results.append(preFloat(avrRespTime/len(data))/1000)
    results.append(Throughput)
    results.append(totalOpt)
    results.append(data[0][6])
    
    d=len(data[0])
    for info in data[0][d-4:d]:
        results.append(info)
    
    writeToFile(results,fMemBenchmark)    
    
#################################################################
def parser():   
    
    prepareOutputFiles()
    
    dataArray= prepareDataArray(fAbBenchmark)
    dataArray=cleanDataArray(dataArray, "ab")
    
    dataArray= prepareDataArray(fMemBenchmark)
    dataArray=cleanDataArray(dataArray, "mem")
    
    dataArray= prepareDataArray(fIperfBenchmark)
    dataArray=cleanDataArray(dataArray, "iperf")


       
         
         
              
                
