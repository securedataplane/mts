#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  2 12:49:23 2018

@author: saad
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


################### File Names ################################
fIperfBenchmark= "Parsed_Iperf_Benchmark_Data.csv"
fAbBenchmark= "Parsed_Ab_Benchmark_Data.csv"
fMemBenchmark= "Parsed_Mem_Benchmark_Data.csv"

############################# Helper Functions #########################
def getValue(strVal):
    if "." in strVal:
        flw= float(strVal)
        return float("{0:.2f}".format(flw))
    else:
        return int(strVal)
        
        
def getEmptyDic():
    dic= {}
    dic["cpuIsolation_without_DPDK"]=[]
    dic["cpuIsolation_with_DPDK"]= []
    dic["cpuShared_without_DPDK"]= []
    return dic

def calStd(valList):
    a=np.array(valList)
    return float("{0:.2f}".format(np.std(a)))

def calMean(valList):
    a=np.array(valList)
    return float("{0:.2f}".format(np.mean(a)))

############################## Ploter #################################
'''
def ploter(data, scsNames, titel, yLabel):
    
    ind = np.arange(len(scsNames))
    width = 0.20
    
    means=data["cpuIsolation_without_DPDK_MEAN"]
    stds=data["cpuIsolation_without_DPDK_STD"]      
    plt.bar(ind, means, width, label='cpu_Isolation=True & DPDK=False', yerr=stds)
    
    means=data["cpuIsolation_with_DPDK_MEAN"]
    stds=data["cpuIsolation_with_DPDK_STD"]
    plt.bar(ind + width, means, width, label='cpu_Isolation=True & DPDK=True', yerr=stds)
    
    means=data["cpuShared_without_DPDK_MEAN"]
    stds=data["cpuShared_without_DPDK_STD"]
    plt.bar(ind + 2*width, means, width, label='cpu_Isolation=False & DPDK=False', yerr=stds)
    
    plt.ylabel(yLabel)
    plt.title(titel)
    
    plt.xticks(ind + width , scsNames)
    plt.legend(loc=9, bbox_to_anchor=(0.5, -0.1), ncol=3)
    
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)
    plt.show()
    plt.draw()
    fig.savefig(titel+'.png')
    
'''      
def ploter(data, scsNames, titel, yLabel):
    # colors
    colors = ['#3D9970', '#FF9136', '#FFC51B', '#66c2a5', '#3D9970', '#FF9136', '#FFC51B']
    p1 = mpatches.Patch(color= colors[0], label='Baseline')
    p2 = mpatches.Patch(color= colors[1], label='1 OvS VM')
    p3 = mpatches.Patch(color= colors[2], label='2 OvS VMs')
    p4 = mpatches.Patch(color= colors[3], label='4 OvS VMs')
       
    #Spaces and Bar sizes
    ind = (0, 1, 2, 3, 5, 6, 7)
    width = 1.0
    
    fig, (ax1, ax2,ax3) = plt.subplots(1,3,sharey=True, sharex=True,figsize=(10,5)) 
    
    means=data["cpuShared_without_DPDK_MEAN"]
    stds=data["cpuShared_without_DPDK_STD"]
    ax1.bar(ind, means, width, color=colors, edgecolor='black', yerr=stds)
    ax1.set_title("Shared Core (No DPDK)",fontsize=20)
    ax1.xaxis.set_tick_params(labelsize=15)
    ax1.yaxis.set_tick_params(labelsize=12)
    
    means=data["cpuIsolation_without_DPDK_MEAN"]
    stds=data["cpuIsolation_without_DPDK_STD"]
    ax2.bar(ind, means, width, color=colors, edgecolor='black', yerr=stds)
    ax2.set_title("Isolated Core (No DPDK)",fontsize=20)
    ax2.xaxis.set_tick_params(labelsize=15)
    ax2.yaxis.set_tick_params(labelsize=12)
    
    means=data["cpuIsolation_with_DPDK_MEAN"]
    stds=data["cpuIsolation_with_DPDK_STD"]
    ax3.bar(ind, means, width, color=colors, edgecolor='black', yerr=stds)
    ax3.set_title("Isolated Core (DPDK)",fontsize=20)
    ax3.xaxis.set_tick_params(labelsize=15)
    ax3.yaxis.set_tick_params(labelsize=12)
    
    plt.xticks((1.5,6) ,("phy2vm2vm2phy","vm2vm"))
    
    ax1.set_ylabel(yLabel,fontsize=15)
   
    plt.legend(loc=7, bbox_to_anchor=(0.5, -0.1), ncol=4,handles=[p1,p2,p3,p4],fontsize=20)
    
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)
    plt.show()
    plt.draw()
    fig.savefig(titel+'.png')

def ploterMemAb(Abdata, Memdata, AbyLabel, MemyLabel, titel):
    # colors
    colors = ['#3D9970', '#FF9136', '#FFC51B', '#66c2a5', '#3D9970', '#FF9136', '#FFC51B']
    p1 = mpatches.Patch(color= colors[0], label='Baseline')
    p2 = mpatches.Patch(color= colors[1], label='1 OvS VM')
    p3 = mpatches.Patch(color= colors[2], label='2 OvS VMs')
    p4 = mpatches.Patch(color= colors[3], label='4 OvS VMs')
       
    #Spaces and Bar sizes
    ind = (0, 1, 2, 3, 5, 6, 7)
    width = 1.0
    
    fig, (ax1, ax2) = plt.subplots(1,2,sharey=False, sharex=True,figsize=(10,5)) 
    
    means=Abdata["cpuShared_without_DPDK_MEAN"]
    stds=Abdata["cpuShared_without_DPDK_STD"]
    ax1.bar(ind, means, width, color=colors, edgecolor='black', yerr=stds)
    ax1.set_title("Apache \n Shared Core (No DPDK)",fontsize=20)
    ax1.xaxis.set_tick_params(labelsize=15)
    ax1.yaxis.set_tick_params(labelsize=12)
    
    means= Memdata["cpuIsolation_without_DPDK_MEAN"]
    stds= Memdata["cpuIsolation_without_DPDK_STD"]
    ax2.bar(ind, means, width, color=colors, edgecolor='black', yerr=stds)
    ax2.set_title("Memcached \n Shared Core (No DPDK)",fontsize=20)
    ax2.xaxis.set_tick_params(labelsize=15)
    ax2.yaxis.set_tick_params(labelsize=12)
    
    plt.xticks((1.5,6) ,("phy2vm2vm2phy","vm2vm"))
    
    ax1.set_ylabel(AbyLabel,fontsize=15)
    ax2.set_ylabel(MemyLabel,fontsize=15)
   
    plt.legend(loc=7, bbox_to_anchor=(0.5, -0.1), ncol=4,handles=[p1,p2,p3,p4],fontsize=20)
    
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)
    plt.show()
    plt.draw()
    fig.savefig(titel+'.png')
############################## Data Porcessing ################################
#get Scenarios's Names
def getScsNames(Scs):
    scsNames=()
    for s in Scs:
        n= s[0]+"\n"+s[1]
        scsNames=scsNames+(n,)
    return scsNames


# get available Topologies and vSwitch Modes
def getScs(dataPath):
    Scs=[]
    with open(dataPath) as f:
        lines = f.readlines()
        for l in lines:
            if l!="" and l!="\n" and not l.startswith("Timestamp"):
               d=l.split(",")
               if d[len(d)-4:len(d)-2] not in Scs:
                   Scs.append(d[len(d)-4:len(d)-2])
    finalScs = Scs
    finalScs = []
    for s in Scs:
        fs = []
        for f in s:
            fs.append(f.rstrip())
        finalScs.append(fs)
    return finalScs

      
def getData(Scs, dataPath, param):
    Scs= getScsData(Scs, dataPath, param)
    data={}
    
    cpuIsolation_without_DPDK_MEAN= ()
    cpuIsolation_with_DPDK_MEAN= ()
    cpuShared_without_DPDK_MEAN= ()
    
    cpuIsolation_without_DPDK_STD= ()
    cpuIsolation_with_DPDK_STD= ()
    cpuShared_without_DPDK_STD= ()
    
    for s in Scs:
        cpuIsolation_without_DPDK_STD= cpuIsolation_without_DPDK_STD+ (calStd(s[2]["cpuIsolation_without_DPDK"]),)
        cpuIsolation_with_DPDK_STD= cpuIsolation_with_DPDK_STD+ (calStd(s[2]["cpuIsolation_with_DPDK"]),)
        cpuShared_without_DPDK_STD= cpuShared_without_DPDK_STD+ (calStd(s[2]["cpuShared_without_DPDK"]),)
        
        cpuIsolation_without_DPDK_MEAN= cpuIsolation_without_DPDK_MEAN+ (calMean(s[2]["cpuIsolation_without_DPDK"]),)
        cpuIsolation_with_DPDK_MEAN= cpuIsolation_with_DPDK_MEAN+ (calMean(s[2]["cpuIsolation_with_DPDK"]),)
        cpuShared_without_DPDK_MEAN= cpuShared_without_DPDK_MEAN+ (calMean(s[2]["cpuShared_without_DPDK"]),)
        
        
    data["cpuIsolation_without_DPDK_STD"]= cpuIsolation_without_DPDK_STD
    data["cpuIsolation_with_DPDK_STD"]= cpuIsolation_with_DPDK_STD
    data["cpuShared_without_DPDK_STD"]= cpuShared_without_DPDK_STD
    
    data["cpuIsolation_without_DPDK_MEAN"]= cpuIsolation_without_DPDK_MEAN
    data["cpuIsolation_with_DPDK_MEAN"]= cpuIsolation_with_DPDK_MEAN
    data["cpuShared_without_DPDK_MEAN"]= cpuShared_without_DPDK_MEAN
    
    return data
    
def getScsData(ScenariosArray, dataPath, param):
    
    Scs= ScenariosArray
    index= getIndex(dataPath, param)
    
    with open(dataPath) as f:
        lines = f.readlines()
        for s in Scs:
            s.append(getEmptyDic())
            
            for l in lines:
                if l!="" and l!="\n" and not l.startswith("Timestamp"):
                    d=l.split(",")
                    xStripped = []
                    for i in d:
                        xStripped.append(i.rstrip())
                    d = xStripped
                    if d[len(d)-4:len(d)-2] == s[0:2] and "True" in d[len(d)-1] and "False" in d[len(d)-2]:
                        s[2]["cpuIsolation_without_DPDK"].append(getValue(d[index]))

                    elif d[len(d)-4:len(d)-2] == s[0:2] and "True" in d[len(d)-1] and "True" in d[len(d)-2]:
                        s[2]["cpuIsolation_with_DPDK"].append(getValue(d[index]))

                    elif d[len(d)-4:len(d)-2] == s[0:2] and "False" in d[len(d)-1] and "False" in d[len(d)-2]:
                        s[2]["cpuShared_without_DPDK"].append(getValue(d[index]))
    for s in Scs:
        if "Baseline" in s[1] or "SRIOV_OneOvs" in s[1]:
            s[2]["cpuShared_without_DPDK"]= s[2]["cpuIsolation_without_DPDK"]
    
    Scs= reorderArray(Scs)
    
    return Scs
      
def getIndex(dataPath, param):
    #get Index
    index=999999
    
    with open(dataPath) as f:
        lines = f.readlines()
        for l in lines:
            if l!="" and l!="\n" and l.startswith("Timestamp"):
               d=l.split(",")
               for e in d:
                   if param in e:
                       index= d.index(e)
                       break
               break
    return index
    
    
def reorderArray(arrayData):   
    orderedArray= [['phy2vm2vm2phy','Baseline'],
            ['phy2vm2vm2phy','SRIOV_OneOvs'],
            ['phy2vm2vm2phy','SRIOV_TwoOvs'],
            ['phy2vm2vm2phy','SRIOV_FourOvs'],
            ['VM2VM','Baseline'],
            ['VM2VM','SRIOV_OneOvs'],
            ['VM2VM','SRIOV_TwoOvs'],
            ['phy2vm2vm2phy', 'Baseline_NoDPDK_2Core'],
            ['phy2vm2vm2phy', 'Baseline_NoDPDK_4Core'],
            ['VM2VM', 'Baseline_NoDPDK_2Core'],
            ['VM2VM', 'Baseline_NoDPDK_4Core'],
            ['phy2vm2vm2phy', 'Baseline_DPDK_2Core'],
            ['phy2vm2vm2phy', 'Baseline_DPDK_4Core'],
            ['VM2VM', 'Baseline_DPDK_2Core'],
            ['VM2VM', 'Baseline_DPDK_4Core']]
    
    indx=0
    for d  in orderedArray:
        for entry in arrayData:
            if d[0] == entry[0] and d[1] == entry[1]:
                orderedArray[indx]= entry
        
        indx=indx+1
    
    return orderedArray
################################## Examples ##################################                       

'''
# Ab benchmark                  
Scs= getScs(fAbBenchmark)
data= getData(Scs, fAbBenchmark, "Requests per second")
names=getScsNames(Scs)
ploter(data, names, "Ab Benchmark: Requests per second", "Requests per second")

Scs= getScs(fAbBenchmark)
data= getData(Scs, fAbBenchmark, "50%")
names=getScsNames(Scs)
ploter(data, names, "Ab Benchmark: 50% (ms)", "50% (ms)")

Scs= getScs(fAbBenchmark)
data= getData(Scs, fAbBenchmark, "99%")
names=getScsNames(Scs)
ploter(data, names, "Ab Benchmark: 99% (ms)", "99% (ms)")

# Iperf benchmark
Scs= getScs(fIperfBenchmark)
data= getData(Scs, fIperfBenchmark, "S_Bandwidth")
names=getScsNames(Scs)
ploter(data, names, "Iperf Benchmark: Sender Bandwidth (Mbits Per sec)", "Bandwidth (Mbits/sec)")   
  
# Iperf benchmark                     
Scs= getScs(fMemBenchmark)
data= getData(Scs, fMemBenchmark, "The average response time")
names=getScsNames(Scs)
ploter(data, names, "Memcached Benchmark: The average response time (us)", "The average response time (us)")                

Scs= getScs(fMemBenchmark)
data= getData(Scs, fMemBenchmark, "Throughput")
names=getScsNames(Scs)
ploter(data, names, "Memcached Benchmark: Throughput (operations per second)", "Throughput(ops/s)")
'''

'''
############################ Plots for the paper ##############################
#----------------- Latency -----------------------------
Scs1= getScs(fAbBenchmark)
Abdata= getData(Scs1, fAbBenchmark, " mean")
Scs2= getScs(fMemBenchmark)
Memdata= getData(Scs2, fMemBenchmark, "The average response time")
ploterMemAb(Abdata, Memdata, "Mean: response time (ms)", "The average response time (ms)", "meanAbMem")

#----------------- Throughput -----------------------------
Scs1= getScs(fAbBenchmark)
Abdata= getData(Scs1, fAbBenchmark, "Requests per second")
Scs2= getScs(fMemBenchmark)
Memdata= getData(Scs2, fMemBenchmark, "Throughput")
ploterMemAb(Abdata, Memdata, "Requests per second", "operations per second", "ThroughputAbMem")
'''