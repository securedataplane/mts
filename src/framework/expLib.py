import paramiko as pk
import time
import sys
import os
import errno
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


RED = "\033[1;31m"
BLEU = "\033[1;34m"
RESET = "\033[0;0m"

ssh_timeout = 600
vmSleepTime = 20
totalCpuCores = 16
l2fwdCpuCores = 8

Int_MAC = dict()
Int_MAC["Spree_ens2f0"] = "00:0f:53:5b:89:f0"

pf_index = 0

#-------- SR-IOV------------------------
# [(pf_name,pf_PCI,[VF LIST])]
pfs = []
# [(pf_name,vf_PCI)]
vfs = []

# [(vf/pf_name, [rule IDs])]
ntuple = []

#---------- Server IPs------------------
Compute = "130.149.230.48"
Dosse = "130.149.230.131"
Spree = "130.149.230.129"
Havel = "130.149.230.130"
Plane = "130.149.230.132"
Elbe = "130.149.230.140"

#-------------VM IPs--------------------
Tenant1 = "192.168.122.2"
Tenant2 = "192.168.122.3"
Tenant3 = "192.168.122.4"
Tenant4 = "192.168.122.5"

OvsVM = "192.168.122.6"
OvsVM2 = "192.168.122.7"
OvsVM3 = "192.168.122.8"
OvsVM4 = "192.168.122.9"

ContainerVM = "192.168.122.10"
ContainerVM2 = "192.168.122.11"
ContainerVM3 = "192.168.122.12"
ContainerVM4 = "192.168.122.13"

'''
nano /etc/network/interfaces

iface ens3 inet static
address 192.168.122.2
netmask 255.255.255.0
network 192.168.122.0
broadcst 192.168.122.255
gateway 192.168.122.1
dns-nameservers 192.168.122.1
'''
#------------Forwording Ports-----------
Fp_Tenant1 = "9867"
Fp_Tenant2 = "9870"
Fp_Tenant3 = "9871"
Fp_Tenant4 = "9872"

Fp_OvsVM = "9868"
Fp_OvsVM2 = "9869"
Fp_OvsVM3 = "9873"
Fp_OvsVM4 = "9874"

Fp_ContVM = "9875"
Fp_ContVM2 = "9876"
Fp_ContVM3 = "9877"
Fp_ContVM4 = "9878"

Default_port = "22"

#------------CONNECTIONS-----------------
#--------[NAME,IP,PORT,USER]------------
#++++++++++++++Servers++++++++++++++++++
cnx_compute = ["COMPUTE", Compute, Default_port, "shermak"]
cnx_dosse = ["DOSSE", Dosse, Default_port, "root"]
cnx_spree = ["SPREE", Spree, Default_port, "root"]
cnx_havel = ["HAVEL", Havel, Default_port, "root"]
cnx_plane = ["PLANE", Plane, Default_port, "root"]
cnx_elbe = ["ELBE", Elbe, Default_port, "root"]

#++++++++++++++VMs++++++++++++++++++
#------ on DOSSE----------------------
cnx_tenant1 = ["tenant-green-1", Dosse, Fp_Tenant1, "root"]
cnx_ovsvm = ["vswitch-vm", Dosse, Fp_OvsVM, "root"]

#------ on PLANE----------------------
cnx_Ptenant1 = ["tenant-green-1", Plane, Fp_Tenant1, "root"]
cnx_Ptenant2 = ["tenant-green-2", Plane, Fp_Tenant2, "root"]
cnx_Ptenant3 = ["tenant-green-3", Plane, Fp_Tenant3, "root"]
cnx_Ptenant4 = ["tenant-green-4", Plane, Fp_Tenant4, "root"]

cnx_Povsvm = ["vswitch-vm", Plane, Fp_OvsVM, "root"]
cnx_Povsvm2 = ["vswitch-vm-2", Plane, Fp_OvsVM2, "root"]
cnx_Povsvm3 = ["vswitch-vm-3", Plane, Fp_OvsVM3, "root"]
cnx_Povsvm4 = ["vswitch-vm-4", Plane, Fp_OvsVM4, "root"]

#------ on HAVEL----------------------
cnx_Htenant1 = ["tenant-green-1", Havel, Fp_Tenant1, "root"]
cnx_Htenant2 = ["tenant-green-2", Havel, Fp_Tenant2, "root"]
cnx_Htenant3 = ["tenant-green-3", Havel, Fp_Tenant3, "root"]
cnx_Htenant4 = ["tenant-green-4", Havel, Fp_Tenant4, "root"]

cnx_Hovsvm = ["vswitch-vm", Havel, Fp_OvsVM, "root"]
cnx_Hovsvm2 = ["vswitch-vm-2", Havel, Fp_OvsVM2, "root"]
cnx_Hovsvm3 = ["vswitch-vm-3", Havel, Fp_OvsVM3, "root"]
cnx_Hovsvm4 = ["vswitch-vm-4", Havel, Fp_OvsVM4, "root"]

cnx_Hcontvm = ["vswitch-vm-container", Havel, Fp_ContVM, "root"]
cnx_Hcontvm2 = ["vswitch-vm-container-2", Havel, Fp_ContVM2, "root"]
cnx_Hcontvm3 = ["vswitch-vm-container-3", Havel, Fp_ContVM3, "root"]
cnx_Hcontvm4 = ["vswitch-vm-container-4", Havel, Fp_ContVM4, "root"]

#++++++++++++++ServerVms++++++++++++++++++
dosse_Vms = [cnx_tenant1, cnx_ovsvm]
plane_Vms = [cnx_Ptenant1, cnx_Ptenant2, cnx_Ptenant3, cnx_Ptenant4, cnx_Povsvm, cnx_Povsvm2, cnx_Povsvm3, cnx_Povsvm4]
havel_Vms = [cnx_Htenant1, cnx_Htenant2, cnx_Htenant3, cnx_Htenant4, cnx_Hovsvm, cnx_Hovsvm2, cnx_Hovsvm3, cnx_Hovsvm4, cnx_Hcontvm, cnx_Hcontvm2, cnx_Hcontvm3, cnx_Hcontvm4]

#-----------OVS Path--------------------
nodpdk_path = "/usr/local/src/openvswitch-2.9.0/"
path_dosse = "/usr/local/src/ovs/openvswitch-2.9.0/"
dpdk_path = "/usr/local/src/ovs-dpdk/openvswitch-2.9.0/"


#####################################################################################################################################
#-------------------------------------------------------------- SSH Connection-------------------------------------------------------
#####################################################################################################################################

def SSHConnect(cnx):
    timeout_start = time.time()
    while(time.time() < timeout_start + ssh_timeout):
        try:
            client = pk.client.SSHClient()
            client.set_missing_host_key_policy(pk.AutoAddPolicy())
            client.connect(cnx[1], int(cnx[2]),username=cnx[3])
            return client
        except pk.ssh_exception.NoValidConnectionsError:
            sys.exc_clear()
            time.sleep(20)
        except pk.ssh_exception.BadAuthenticationType:
            printLog("EXCEPTION: Authentication Problem ... ! ", RED)
            break
    printLog("Timeout: unable to connect to: "+cnx[0]+"  ....", RED)

  
def RunCommand(sshClient, cmd):
    try:
        stdin, stdout, stderr = sshClient.exec_command(cmd)
        output = stdout.readlines()
        error = stderr.readlines()

        printCmdLog("----------------------------- \n")
        printCmdLog("Command: \n")
        printCmdLog(cmd+"\n")
        printCmdLog("Output: \n")
        printCmdLog("\n".join(output))
        printCmdLog("----------------------------- \n")

        if error and "sfboot" != cmd:
            printLog("Info/error from: \n", RED)
            printCmdLog("Info/error from: \n")

            printLog("                  "+cmd+" \n", BLEU)
            printCmdLog("                  "+cmd+" \n")

            printLog("Info/error message: ", RED)
            printCmdLog("Info/error message: ")

            printLog("\n".join(error), BLEU)
            printCmdLog("\n".join(error))

        return output

    except AttributeError:
        printLog("EXCEPTION: The SSH Session might be DEAD!", RED)


def RunIntCommand(sshClient, cmd, cmdIn):
    try:
        stdin, stdout, stderr = sshClient.exec_command(cmd)
        stdin.write(cmdIn + "\n")
        stdin.flush()
        output = stdout.readlines()
        error = stderr.readlines()

        if error and "sfboot" != cmd:
            printLog("failed to execute: \n", RED)
            printLog("                  " + cmd + " \n", BLEU)
            printLog("Error message: ", RED)
            printLog("\n".join(error), BLEU)
        return output

    except AttributeError:
        printLog("EXCEPTION: The SSH Session might be DEAD!", RED)

#####################################################################################################################################
#-------------------------------------------------------------Forwarding Rules-------------------------------------------------------
#####################################################################################################################################


def setPortForward(cnx, DesPort, DesHost):
    print("Setting up Forwarding Rule: Traffic to " + cnx[0] + " on port: " + DesPort + " will be forwarded to: " + DesHost + "\n")
    ssh = SSHConnect(cnx)
    RunCommand(ssh, "iptables -I FORWARD -o virbr0 -d " + DesHost + " -j ACCEPT")
    RunCommand(ssh, "iptables -t nat -I PREROUTING -p tcp --dport " + DesPort + " -j DNAT --to " + DesHost + ":" + Default_port)
    RunCommand(ssh, "iptables -t nat -A POSTROUTING -s " + DesHost[0:11] + ".0/24 -j MASQUERADE")
    RunCommand(ssh, "iptables -A FORWARD -o virbr0 -m state --state RELATED,ESTABLISHED -j ACCEPT")
    RunCommand(ssh, "iptables -A FORWARD -i virbr0 -o eno1 -j ACCEPT")
    RunCommand(ssh, "iptables -A FORWARD -i virbr0 -o lo -j ACCEPT")
    ssh.close()


#####################################################################################################################################
#-------------------------------------------------------------SR-IOV------------------------------------------------------------------
#####################################################################################################################################
def RebootServer(cnx, wait=True):
    print ("Rebooting "+cnx[0]+"........ \n")
    ssh = SSHConnect(cnx)
    RunCommand(ssh, "reboot")
    ssh.close()

    if wait is True:
        time.sleep(30)

        ssh = SSHConnect(cnx)
        RunCommand(ssh, "ls")
        ssh.close()
        print(cnx[0] + " is ready\n")


def ResetTestBed(cnx, Is_sr_iov, NicType):
    print("SR-IOV Configuration on " + cnx[0] + "........ \n")  
    ssh = SSHConnect(cnx)

    print("Config array: " + NicConfig[0] + " , " + NicConfig[1])

    if Is_sr_iov:
        print ("Enable SR-IOV Partitioning on: " + cnx[0] + "\n")
        if NicType == "sf":
            RunCommand(ssh, "sfboot switch-mode=" + NicConfig[0] + " pf-count=" + NicConfig[1] + " pf-vlans=" + NicConfig[3] + " vf-count=" + NicConfig[2])
            time.sleep(10)
        elif NicType == "mlx":
            RunIntCommand(ssh, "mlxconfig -d /dev/mst/mt4117_pciconf0 set SRIOV_EN=" + NicConfig[0] + " NUM_OF_VFS=" + NicConfig[1], "y")
            time.sleep(10)
        else:
            print("Unkown NIC ...")

    else:
        print("Disable SR-IOV Partitioning on: " + cnx[0] + "\n")
        if NicType == "sf":
            RunCommand(ssh, "sfboot --clear")
            time.sleep(10)
        elif NicType == "mlx":
            RunIntCommand(ssh, "mlxconfig -d /dev/mst/mt4117_pciconf0 set SRIOV_EN=0", "y")
            time.sleep(10)
        else:
            print("Unkown NIC ...")

    print("Rebooting " + cnx[0] + "........ \n")    
    RunCommand(ssh, "reboot")
    ssh.close()
    time.sleep(30)

    if((Is_sr_iov and checkSrIov(cnx, NicType)) or (not Is_sr_iov and not checkSrIov(cnx, NicType))):
        print ("SR-IOV Configuration has been finished successfully and " + cnx[0] + " is ready to use \n")
    else:
        printLog("SR-IOV Configuration has NOT been finished successfully on " + cnx[0] + "\n", RED)

    # Disable irq balance as soon as the server boots up
    disableIrqBalance(cnx)

    # clean the VM interfaces of type Hostdev and bridge
    CleanVmInt(cnx)

    # set STP Off on virbr0
    setStp(cnx, "off", "virbr0")


def startMlx(cnx):
    print("Starting Mellanox ... \n")
    ssh = SSHConnect(cnx)
    stdout = RunCommand(ssh, "mst start")
    ssh.close()
    if "Success" in stdout[len(stdout)-1]:
        print("Mellanox has been started successfully ... \n")
    else: 
        print("Failed to start Mellanox ... \n")


def checkSrIov(cnx, NicType):
    ssh = SSHConnect(cnx)
    if NicType == "sf":
        stdout = RunCommand(ssh, "sfboot")
        ssh.close()
        for l in stdout:
            if ("Switch mode" in l and "Partitioning with SR-IOV" in l):
                return True
    elif NicType == "mlx":
        startMlx(cnx)
        stdout = RunCommand(ssh, "mlxconfig -d /dev/mst/mt4117_pciconf0 q")
        ssh.close()
        for l in stdout:
            if ("SRIOV_EN" in l and "True(1)" in l):
                return True
    else:
        printLog("Unkown NIC ...", RED)

    return False


def checkIOMMU(cnx):
    print("Checking if IOMMU is enabled on: " + cnx[0] + "\n")
    ssh = SSHConnect(cnx)
    stdout = RunCommand(ssh, "cat /proc/cmdline")
    ssh.close()
    for l in stdout:
        if "iommu=pt" in l and "intel_iommu=on" in l:
            return True
    return False


def ConfVFs(cnx, pf, vf_Numb):
    print("Configuring the Number of VFs for " + pf + " on " + cnx[0] + "\n")
    ssh = SSHConnect(cnx)
    RunCommand(ssh, "echo " + vf_Numb + " > /sys/class/net/" + pf + "/device/sriov_numvfs")
    time.sleep(2)
    stdout = RunCommand(ssh, "cat /sys/class/net/"+pf+"/device/sriov_numvfs")
    ssh.close()
    for l in stdout:
        if vf_Numb in l:
            ssh.close()
            print("VFs configuration for " + pf + " on " + cnx[0] + " has been finished successfully.\n")
            return
    print("Failed to do VFs configuration for " + pf + " on " + cnx[0] + "\n")


def BindVF(cnx, vf, NicType):
    print("bind" + vf + " on " + cnx[0] + "\n")
    ssh = SSHConnect(cnx)

    if NicType == "sf":
        RunCommand(ssh, "echo " + str(GetPciByVf(vf)) + " > /sys/bus/pci/drivers/sfc/bind ")
    elif NicType == "mlx":
        RunCommand(ssh, "echo " + str(GetPciByVf(vf)) + " > /sys/bus/pci/drivers/mlx5_core/bind ")

    ssh.close()


def BindVFs(cnx, pf, NicType):
    print("bind" + pf + " on " + cnx[0] + "\n")
    for vf in GetVFsByPf(pf):
        BindVF(cnx, vf, NicType)


def UnbindVF(cnx, vf, NicType):
    print ("unbind " + vf + " from " + cnx[0] + "\n")
    ssh = SSHConnect(cnx)

    if NicType == "sf":
        RunCommand(ssh, "echo " + str(GetPciByVf(vf)) + " > /sys/bus/pci/devices/" + str(GetPciByVf(vf)).replace(":", "\:") + "/driver/unbind")
    elif NicType == "mlx":
        RunCommand(ssh, "echo " + str(GetPciByVf(vf)) + " > /sys/bus/pci/drivers/mlx5_core/unbind")

    ssh.close()


def UnbindVFs(cnx, pf, NicType):
    print("unbind" + pf + " from " + cnx[0] + "\n")
    for vf in GetVFsByPf(pf):
        UnbindVF(cnx, vf, NicType)


def GetVfPfData(cnx, NicType, PhyPort):
    print("Getting Pf/VF data \n")
    ssh = SSHConnect(cnx)
    vf_index = 0
    global pf_index

    if NicType == "sf":
        stdout = RunCommand(ssh, "lshw -c network -businfo")
        for l in stdout:
            l = l.split()
            if l[0].startswith("pci@") and l[1].startswith("ens"):
                pfs.append((l[1], l[0][4:], []))
            elif l[0].startswith("pci@") and l[1].startswith("enp"):
                vfs.append((l[1], l[0][4:]))
                pfs[pf_index][2].append(l[1])
                vf_index = vf_index + 1
                if vf_index == int(NicConfig[2]):
                    vf_index = 0
                    pf_index = pf_index+1
    elif NicType == "mlx":
        if PhyPort == "enp3s0f0" or PhyPort == "enp3s0f1":
            stdout = RunCommand(ssh, "lshw -c network -businfo | grep pci@0000:03")
        elif PhyPort == "enp2s0f0" or PhyPort == "enp2s0f1":
            stdout = RunCommand(ssh, "lshw -c network -businfo | grep pci@0000:02")
        index = len(pfs) + len(vfs)

        for l in stdout[index:]:
            l = l.split()
            if index == 0 or index == 1:
                pfs.append((l[1], l[0][4:], []))
                index = index + 1
            else:
                vfs.append((l[1], l[0][4:]))
                pfs[pf_index][2].append(l[1])
                vf_index = vf_index+1
                index = index + 1
                if vf_index == int(NicConfig[1]):
                        vf_index = 0
                        pf_index = pf_index + 1
    ssh.close()
    print ("PF/VF Data is ready.\n")


def SetVfMac(cnx, NicType):
    print ("Setting MAC Address for Vfs \n")
    ssh = SSHConnect(cnx)

    if NicType == "sf":
        for vf in vfs:
            RunCommand(ssh, "ip link set " + vf[0] + " address " + PciTOmac(vf[1]))
    elif NicType == "mlx":
        for vf in vfs:
            pfName, Vfindex = getPFbyVF(cnx, vf[0])
            RunCommand(ssh, "ip link set " + pfName + " vf " + Vfindex + " mac " + PciTOmac(vf[1]))

    ssh.close()
    print ("New Mac address for VFs has been set... \n")


def Setspoofchk(cnx, vf, state):
    print("Setting spoofchk in " + vf + " " + state + " \n")
    ssh = SSHConnect(cnx)
    pfName, Vfindex = getPFbyVF(cnx, vf)
    RunCommand(ssh, "ip link set " + pfName + " vf " + Vfindex + " spoofchk " + state)
    ssh.close()


def setVfVlan(cnx, vf, vlan):
    print("Assigning Vlan " + vlan + " to " + vf + "  \n")
    ssh = SSHConnect(cnx)
    pfName, Vfindex = getPFbyVF(cnx, vf)
    RunCommand(ssh, "ip link set " + pfName + " vf " + Vfindex + " vlan " + vlan)
    ssh.close()


def AddnTuple(cnx, vf_pf, flowType, action):
    print("Adding ntuple Rule for " + vf_pf + " \n")
    ssh = SSHConnect(cnx)
    output = RunCommand(ssh, "ethtool --config-ntuple " + vf_pf + " flow-type " + flowType+" action "+action)
    ssh.close()
    if "Added rule with ID" in output[0]:
        nID = output[0].split()[4]
        print("ntuple Rule has been added successfully with ID " + nID)

        # if the vf/pf is already in the list
        for r in ntuple:
            if r[0] == vf_pf:
                r[1].append(nID)
                return

        # if the vf/pf is not in the list
        ntuple.append((vf_pf, [nID]))
        return
    print("Faid to add the ntuple Rule for " + vf_pf)


def DelnTupleByID(cnx, vf_pf, nID):
    print("Delete ntuple with ID " + nID + " in " + vf_pf + " \n")
    ssh = SSHConnect(cnx)
    RunCommand(ssh, "ethtool --config-ntuple " + vf_pf + " delete " + nID)
    ssh.close()


def DelAllnTuple(cnx, vf_pf):
    print ("Delete All ntuples in " + vf_pf + "...\n")
    for r in ntuple:
            if r[0] == vf_pf:
                for ids in r[1]:
                    DelnTupleByID(cnx, vf_pf, ids)

    print("All ntuples in " + vf_pf + " has been deleted.\n")


def ShownTuple(cnx, vf_pf):
    print ("ntuple rules for " + vf_pf + " : \n")
    ssh = SSHConnect(cnx)
    output = RunCommand(ssh, "ethtool --show-ntuple " + vf_pf)
    print "\n".join(output)
    ssh.close()


#####################################################################################################################################
#-------------------------------------------------------------Open vSwitch-----------------------------------------------------------
#####################################################################################################################################   
def LoadSfc(cnx):
    print(" Load solarflare driver \n")
    ssh = SSHConnect(cnx)
    stdout = RunCommand(ssh, "lsmod | grep sfc")
    for l in stdout:
        if "sfc" in l:
            ssh.close()
            return 
    RunCommand(ssh, "modprobe sfc")
    ssh.close()


def LoadOVSKernelm(cnx):
    print("Load openvswitch kernel module.\n")
    ssh = SSHConnect(cnx)
    stdout = RunCommand(ssh, "lsmod | grep openvswitch")
    for l in stdout:
        if "openvswitch" in l:
            ssh.close()
            return
    RunCommand(ssh, "modprobe openvswitch")
    ssh.close()


def StartOVS(cnx, path, IsDpdk, CpuAffinity=["0", "3"], DpdkMem="2048,0", DpdkCpu=[4, [1, 2]], ContNum=0):
    print("[+] Starting OVS on: " + cnx[0] + "\n")
    ssh = SSHConnect(cnx)

    if isContainer:
        # load kernel module on docker host so containers can use it
        RunCommand(ssh, "sudo modprobe openvswitch")

        RunCommand(ssh, "docker run -d --cpuset-cpus {} --name=ovsdb-server-{} svs/ovs:ovsdb".format(CpuAffinity[0], ContNum))
        RunCommand(ssh, "docker run -d --cpuset-cpus {0} --volumes-from ovsdb-server-{1} --privileged --name=ovs-vswitchd-{1} svs/ovs:vswitchd".format(CpuAffinity[1], ContNum))

        # pass SRIOV PCI interfaces to container
        for vf in MyVfs:
            if "container" in vf[3] and ContNum == vf[4]:
                interface = VfsMatch[vf[0]]
                # direct-phys: attach interface exclusively to a container without using a macvlan bridge; -i: name of the interface inside the container; 0/0: attach without IP addr
                RunCommand(ssh, "sudo pipework --direct-phys {0} -i {0} ovs-vswitchd-{1} 0/0".format(interface, ContNum))

        RunCommand(ssh, "docker exec ovs-vswitchd-{} ovs-vsctl --no-wait init".format(ContNum))
        return
    else:
        if not IsDpdk:
            LoadOVSKernelm(cnx)

        CleanOVSDB(cnx, path, IsDpdk) 

        if IsDpdk:
            cmd = "taskset  --cpu-list " + CpuAffinity[0] + " ./ovsdb/ovsdb-server --remote=punix:/usr/local/var/run/openvswitch/db.sock --remote=db:Open_vSwitch,Open_vSwitch,manager_options --log-file=/usr/local/var/log/openvswitch/ovsdb-server.log --private-key=db:Open_vSwitch,SSL,private_key --certificate=db:Open_vSwitch,SSL,certificate --bootstrap-ca-cert=db:Open_vSwitch,SSL,ca_cert --pidfile --detach"
            RunCommand(ssh, "cd " + path + "; " + cmd)

            RunCommand(ssh, "cd " + path + "utilities/ ; ./ovs-vsctl --no-wait set Open_vSwitch . other_config:dpdk-init=true")

            cmd = "taskset  --cpu-list " + CpuAffinity[1] + " ./vswitchd/ovs-vswitchd unix:/usr/local/var/run/openvswitch/db.sock -vconsole:emer -vsyslog:err -vfile:err --mlockall --no-chdir --log-file=/usr/local/var/log/openvswitch/ovs-vswitchd.log --pidfile=/usr/local/var/run/openvswitch/ovs-vswitchd.pid --detach --monitor"
            RunCommand(ssh, "cd " + path + "; " + cmd)
            RunCommand(ssh, "cd " + path + "utilities/ ; ./ovs-vsctl --no-wait set Open_vSwitch . other_config:dpdk-socket-mem=\""+DpdkMem+"\"")
            RunCommand(ssh, "cd " + path + "utilities/ ; ./ovs-vsctl --no-wait set Open_vSwitch . other_config:pmd-cpu-mask="+getCpuMask(DpdkCpu))

            time.sleep(5)
        else:
            cmd = "taskset  --cpu-list " + CpuAffinity[0] + " ovsdb-server --remote=punix:/var/run/openvswitch/db.sock --remote=db:Open_vSwitch,Open_vSwitch,manager_options --log-file=/var/log/openvswitch/ovsdb-server.log --private-key=db:Open_vSwitch,SSL,private_key --certificate=db:Open_vSwitch,SSL,certificate --bootstrap-ca-cert=db:Open_vSwitch,SSL,ca_cert --pidfile --detach"
            RunCommand(ssh, cmd)
            time.sleep(5)

            RunCommand(ssh, "ovs-vsctl --no-wait init")

            cmd = "taskset  --cpu-list " + CpuAffinity[1] + " ovs-vswitchd unix:/var/run/openvswitch/db.sock -vconsole:emer -vsyslog:err -vfile:err --mlockall --no-chdir --log-file=/var/log/openvswitch/ovs-vswitchd.log --pidfile=/var/run/openvswitch/ovs-vswitchd.pid --detach --monitor"
            RunCommand(ssh, cmd)
            time.sleep(5)

        if CheckOVS(cnx) == 1:
            print("OVS on: " + cnx[0] + " has been started.\n")
            ssh.close()
            return
    print("[!] Failed to start OVS on " + cnx[0])
    ssh.close()


def StopOVS(cnx):
    print ("Stopping OVS on: "+cnx[0]+"\n")
    ssh = SSHConnect(cnx)

    if isContainer:
        RunCommand(ssh, "sudo systemctl restart docker")
        RunCommand(ssh, "docker stop $(docker ps -a -q)")
        RunCommand(ssh, "docker rm $(docker ps -a -q)")
        print ("[-] OVS on: " + cnx[0] + " has been stopped \n")
        ssh.close()
        return
    else:
        for i in range(5):
            RunCommand(ssh, "sudo kill $(ps aux | grep ovsdb | awk '{ print $2 }' | head -n 1)")
            RunCommand(ssh, "sudo kill $(ps aux | grep vswitchd | awk '{ print $2 }' | head -n 1)")

            if CheckOVS(cnx) == 0:
                print("[-] OVS on: " + cnx[0] + " has been stopped\n")
                ssh.close()
                return

    print("[!] Failed to stop OVS on " + cnx[0])
    ssh.close()


def StopDefaultOVS(cnx):
    print("Stopping OVS on: " + cnx[0] + "\n")
    ssh = SSHConnect(cnx)
    RunCommand(ssh, "/etc/init.d/openvswitch-switch stop")
    ssh.close()


def StopNetronomeOVS(cnx):
    print("Stopping OVS on: " + cnx[0] + "\n")
    ssh = SSHConnect(cnx)
    RunCommand(ssh, "/opt/netronome/bin/ovs-ctl stop")
    ssh.close()


def AddBridge(cnx, path, br, IsDpdk, ContNum=0):
    print("[+] Adding a bridge " + br + " to OVS on " + cnx[0] + "\n")
    ssh = SSHConnect(cnx)

    if IsDpdk:
        RunCommand(ssh, path+"utilities/ovs-vsctl add-br " + br + " -- set bridge " + br + " datapath_type=netdev")
        RunCommand(ssh, path+"utilities/ovs-ofctl -O OpenFlow13 del-flows "+br)
    elif isContainer:
        RunCommand(ssh, "docker exec ovs-vswitchd-{} ovs-vsctl add-br {}".format(ContNum, br))
        RunCommand(ssh, "docker exec ovs-vswitchd-{} ovs-ofctl -O OpenFlow13 del-flows {}".format(ContNum, br))
        print("    Added bridge {} on container ovs-vswitchd-{}".format(br, ContNum))
    else: 
        RunCommand(ssh, path+"utilities/ovs-vsctl add-br "+br)
        RunCommand(ssh, path+"utilities/ovs-ofctl -O OpenFlow13 del-flows "+br)

    ssh.close()


def DelBridge(cnx, path, br, ContNum=0):
    print ("Delete the bridge " + br + " from OVS on " + cnx[0] + "\n") 
    ssh = SSHConnect(cnx)
    if isContainer:
        RunCommand(ssh, "docker exec ovs-vswitchd-{} ovs-vsctl del-br {}".format(ContNum, br))
    else:
        RunCommand(ssh, path+"utilities/ovs-vsctl del-br "+br)
    ssh.close()


def SetPort(cnx, path, br, port, IsDpdk, Cpu=0, ContNum=0):
    print("Assign " + port + " to " + br + " on " + cnx[0] + "\n")
    ssh = SSHConnect(cnx)
    if IsDpdk and isSRIOV is True:
        RunCommand(ssh, "cd "+path+"utilities/; ./ovs-vsctl add-port " + br + " " + port + " -- set Interface " + port + " type=dpdk options:dpdk-devargs=" + str(getIntPCIbyName(cnx, port)) + ",n_rxq_desc=1024,n_txq_desc=1024,n_rxq=1,pmd-rxq-affinity=" + str(Cpu) + " -- set Interface " + port + " mtu_request=2048")
    elif isContainer:
        # simple, no-DPDK mode
        RunCommand(ssh, "docker exec ovs-vswitchd-{} ovs-vsctl add-port {} {}".format(ContNum, br, port))
    elif IsDpdk and isSRIOV is False:
        # Need to subtract 1 as one core is for the host os.
        queueNumber = str(len(Cpu.split(',')) - 1)
        queuesWithHost = Cpu.split(',')
        queues = queuesWithHost[:-1]
        cpus = queuesWithHost[1:]
        rxqAffinity = ""
        RunCommand(ssh, "cd " + path + "utilities/; ./ovs-vsctl add-port " + br + " " + port + " -- set Interface "+port+" type=dpdk options:dpdk-devargs=" + str(getIntPCIbyName(cnx, port)))
        RunCommand(ssh, "cd " + path + "utilities/; ./ovs-vsctl set Interface " + port + " mtu_request=2048")
        RunCommand(ssh, "cd " + path + "utilities/; ./ovs-vsctl set Interface " + port + " options:n_rxq_desc=1024 -- set Interface " + port + " options:n_txq_desc=1024")
        RunCommand(ssh, "cd " + path + "utilities/; ./ovs-vsctl set Interface " + port + " options:n_rxq=" + queueNumber)
        RunCommand(ssh, "cd " + path + "utilities/; ./ovs-vsctl set Interface " + port + " options:n_txq=" + queueNumber)
        for q, c in zip(queues, cpus):
            rxqAffinity += q + ":" + c + ","
        RunCommand(ssh, "cd "+path+"utilities/; ./ovs-vsctl set Interface " + port + " other_config:pmd-rxq-affinity=" + rxqAffinity[:-1])
    else:
        RunCommand(ssh, path + "utilities/ovs-vsctl add-port " + br + " " + port)

    ssh.close()


# return OpenFlow internal interface representation/mapping (unnecessary in OvS >2.9.0)
def getOFport(cnx, interface, ContNum=0):
    ssh = SSHConnect(cnx)
    if isContainer:
        port = RunCommand(ssh, "docker exec ovs-vswitchd-{} ovs-vsctl get Interface {} ofport".format(ContNum, interface))
    else:
        port = RunCommand(ssh, "ovs-vsctl get Interface {} ofport".format(interface))
    ssh.close()
    return str(port[0].strip('\n'))


# adjust MAC addresses in compiled l2fwd aplications to match VFs in dynamic container scenarios
def patchMAC(cnx, file_name, mac):
    if type(cnx) == str:
        cnx = getVmCnx(cnx)
    ssh = SSHConnect(cnx)

    mac_byte_0, mac_byte_1 = mac.split(':')[-2:]

    # try replacing both MACs (00:00:00:00:30:XX and [...]:20:XX, should be dependent on interface name but you never know)
    RunCommand(ssh,
                'cd /usr/local/src/dpdk/dpdk-stable-17.11.1/examples/l2fwd/build/;'+\
                'bbe -b "/\\x48\\xbf\\x00\\x00\\x00\\x00\\x20/:8" -e "r 6 \\x{0}\\x{1}" {2} > {2}.mod;'.format(mac_byte_0, mac_byte_1, file_name)+\
                'mv {0} {0}.old; mv {0}.mod {0}; chmod +x {0}'.format(file_name))
    RunCommand(ssh,
                'cd /usr/local/src/dpdk/dpdk-stable-17.11.1/examples/l2fwd/build/;'+\
                'bbe -b "/\\x48\\xbf\\x00\\x00\\x00\\x00\\x30/:8" -e "r 6 \\x{0}\\x{1}" {2} > {2}.mod;'.format(mac_byte_0, mac_byte_1, file_name)+\
                'mv {0} {0}.old; mv {0}.mod {0}; chmod +x {0}'.format(file_name))


def addFlowRule(cnx, path, br, match, action, ContNum=0):
    if type(cnx) == str:
        cnx = getVmCnx(cnx)
        
    print ("[+] Adding a new Flow Rule \n")
    ssh = SSHConnect(cnx)
    if isContainer:
        RunCommand(ssh, "docker exec ovs-vswitchd-{} ovs-ofctl -O OpenFlow13 add-flow {} {},actions={}".format(ContNum, br, match, action))
    else:
        RunCommand(ssh, path + "utilities/ovs-ofctl -O OpenFlow13 add-flow " + br + " " + match + ",actions=" + action)
    ssh.close()
    

def ShowBridges(cnx, path):
    print("Bridge Info: \n")  
    ssh = SSHConnect(cnx)
    stdout = RunCommand(ssh, path+"utilities/ovs-vsctl show")
    print("\n".join(stdout))
    ssh.close()
   

def showFlowRules(cnx, path, br, ContNum=0):
    if type(cnx) == str:
        cnx = getVmCnx(cnx)

    print("Flow Rules Info: \n")  
    ssh = SSHConnect(cnx)
    if isContainer:
        stdout = RunCommand(ssh, "docker exec ovs-vswitchd-{} ovs-ofctl -O OpenFlow13 dump-flows {}".format(ContNum, br))
    else:    
        stdout = RunCommand(ssh, path+"utilities/ovs-ofctl -O OpenFlow13 dump-flows " + br)
    print("\n".join(stdout))
    ssh.close()


def CheckOVS(cnx):
    ovsdb_active = False
    ovs_deamon_active = False  
    ssh = SSHConnect(cnx)
    output = RunCommand(ssh, "ps aux| grep ovs")
    ssh.close()
    
    for l in output:
        if "ovs-vswitchd" in l:
            ovs_deamon_active = True
        if "ovsdb-server" in l: 
            ovsdb_active = True
   
    if ovsdb_active and ovs_deamon_active:
        return 1
    elif (not ovsdb_active and ovs_deamon_active) or (ovsdb_active and not ovs_deamon_active):
        return 2
    else:
        return 0 # inactive
        

def CleanOVSDB(cnx, path, IsDPDK):
    ssh =  SSHConnect(cnx)
    if IsDPDK:
        RunCommand(ssh, "rm -rf /usr/local/var/run/openvswitch/")
        RunCommand(ssh, "rm -rf /usr/local/etc/openvswitch/")
        RunCommand(ssh, "rm -f /usr/local/etc/openvswitch/conf.db")
        RunCommand(ssh, "mkdir -p /usr/local/var/run/openvswitch/")
        RunCommand(ssh, "mkdir -p /usr/local/etc/openvswitch/")
        RunCommand(ssh, "mkdir -p /usr/local/var/log/openvswitch/")
        RunCommand(ssh, "rm -f /tmp/conf.db")
        RunCommand(ssh, "cd " + path + " ; ./ovsdb/ovsdb-tool create /usr/local/etc/openvswitch/conf.db vswitchd/vswitch.ovsschema")
    else:
        RunCommand(ssh, "rm -rf /var/run/openvswitch/")
        RunCommand(ssh, "rm -f /etc/openvswitch/conf.db")
        RunCommand(ssh, "rm -rf /etc/openvswitch/")
        RunCommand(ssh, "mkdir -p /var/run/openvswitch/")
        RunCommand(ssh, "mkdir -p /etc/openvswitch/")
        RunCommand(ssh, "mkdir -p /var/log/openvswitch/")
        RunCommand(ssh, "rm -f /tmp/conf.db")
        RunCommand(ssh, "cd " + path + "; ovsdb-tool create /etc/openvswitch/conf.db vswitchd/vswitch.ovsschema")
    ssh.close()
    time.sleep(5)

#####################################################################################################################################
#-----------------------------------------------------ARP / IPs / MAC  Configuration-------------------------------------------------
#####################################################################################################################################   

def SetInt(cnx, intr, state):
    print("Setting " + intr + " " + state + "\n")
    ssh = SSHConnect(cnx)
    RunCommand(ssh, "ip link set " + intr + " " + state)
    ssh.close()


# ip_form: 10.0.0.10/24  
def SetIpInt(cnx, intr, ip):
    print("set Ip address " + ip + " for " + intr + "\n")
    ssh = SSHConnect(cnx)
    RunCommand(ssh, "ip addr add " + ip + " dev " + intr)
    ssh.close()    


def ResetInt(cnx, intr):
    print("Reset Interface:" + intr + "\n")
    ssh = SSHConnect(cnx)
    RunCommand(ssh, "ifconfig " + intr + " 0")
    ssh.close()    


# ip_form: 10.0.0.10
def DelArpEntry(cnx, ip):
    print("Delete ARP entry for :" + ip + "\n")
    ssh = SSHConnect(cnx)
    RunCommand(ssh, "arp -d "+ip)
    ssh.close()   


def SetArpEntry(cnx, ip, mac, intrName):
    print("Set static ARP entry for :" + ip + ". MAC=" + mac + " \n")
    ssh = SSHConnect(cnx)
    RunCommand(ssh, "arp -s " + ip + " " + mac + " -i " + intrName)
    ssh.close()     


def SetMTU(cnx, intr, mtuVal):
    print("Set MTU for " + intr + ": " + mtuVal + " \n")
    ssh = SSHConnect(cnx)
    RunCommand(ssh, "ip link set "+intr+" mtu "+mtuVal)
    ssh.close()   
    
#####################################################################################################################################
#----------------------------------------------------------------VMs // Servers -----------------------------------------------------------------
##################################################################################################################################### 
#cores [1,2,3]
def StartVM(cnx_host, cnx_vm, cores, memory="4G"):
    print("Starting " + cnx_vm[0] + " ...........  \n")
    ssh = SSHConnect(cnx_host)
    
    # Setting Memory 
    RunCommand(ssh, "virsh setmaxmem " + cnx_vm[0] + "  " + memory + " --config")
    RunCommand(ssh, "virsh setmem " + cnx_vm[0] + "  " + memory + " --config")
    
    # Setting CPU Affinity
    RunCommand(ssh, "virsh setvcpus --count " + str(len(cores)) + "  " + cnx_vm[0] + " --config --maximum")
    RunCommand(ssh, "virsh setvcpus " + cnx_vm[0] + " --current " + str(len(cores)))
    for i in range(len(cores)):
        RunCommand(ssh, "virsh vcpupin --domain " + cnx_vm[0] + " --vcpu " + str(i) + " --cpulist " + str(cores[i]) + " --config")
     
    output = RunCommand(ssh, "virsh start "+cnx_vm[0])    
    time.sleep(vmSleepTime)
    ssh.close()

    if "started" in output[0]:
        print(cnx_vm[0] + " has been started succesfully \n")
        time.sleep(vmSleepTime)
    else:
        print("[!] Failed to start " + cnx_vm[0] + "\n")
  
    
def ShutVM(cnx_host, cnx_vm):
    print("Stop " + cnx_vm[0] + " \n")
    ssh = SSHConnect(cnx_host)
    output = RunCommand(ssh, "virsh shutdown " + cnx_vm[0])
    ssh.close()
    if "is being shutdown" in output[0]:
        print(cnx_vm[0] + " has been stopped succesfully \n")
        time.sleep(vmSleepTime)
    else:
        print("Failed to shutdown " + cnx_vm[0] + " \n")
     

def RebootVM(cnx_host, cnx_vm): 
    print("Reboot " + cnx_vm[0] + " \n")
    ssh = SSHConnect(cnx_host)
    output = RunCommand(ssh, "virsh reboot " + cnx_vm[0])
    ssh.close()
    
    if "is being rebooted" in output[0]:
        print(cnx_vm[0] + "has been rebooted succesfully \n")
        time.sleep(vmSleepTime)
    else:
        print("[!] Failed to reboot "+cnx_vm[0]+" \n")
    
    
def AttachBrInter(cnx_host, cnx_vm, bridge, macId):
    print("Attaching a bridge interface to "+cnx_vm[0]+" \n")
    ssh = SSHConnect(cnx_host)
    GenerateXmlBr(cnx_host,bridge, macId)
    output=RunCommand(ssh, "virsh attach-device "+cnx_vm[0]+" bridgeInter.xml --config ")
                      
    if "Device attached successfully" in output[0]:
        print("The bridged Interface has been attached succesfully to "+cnx_vm[0]+" \n")
        
    else:
        print("[!] Failed to attach the bridged interface to "+cnx_vm[0]+" \n")

    RunCommand(ssh, "rm bridgeInter.xml")    
    ssh.close()


def AttachNetInter(cnx_host, cnx_vm, macId):
    print("Attaching a network interface (DPDK) to " + cnx_vm[0] + " \n")
    ssh = SSHConnect(cnx_host)
    GenerateXmlnet(cnx_host, macId)
    output = RunCommand(ssh, "virsh attach-device " + cnx_vm[0] + " netInter.xml --config ")

    if "Device attached successfully" in output[0]:
        print("The bridged Interface has been attached succesfully to " + cnx_vm[0] + " \n")
    else:
        print("[!] Failed to attach the bridged interface to "+cnx_vm[0]+" \n")

    RunCommand(ssh, "rm netInter.xml")     
    ssh.close()    
     

def AttachVf(cnx_host, cnx_vm, vf):
    print("Attaching " + vf + " to " + cnx_vm[0] + " \n")
    GenerateXmlVf(cnx_host, vf)
    ssh = SSHConnect(cnx_host)
    output = RunCommand(ssh, "virsh attach-device " + cnx_vm[0] + " HostdevInter.xml --config ")

    if "Device attached successfully" in output[0]:
        print(vf + " has been attached succesfully to " + cnx_vm[0] + " \n")
    else:
        print("Failed to attach "+vf+" interface to " + cnx_vm[0] + " \n")

    RunCommand(ssh, "rm HostdevInter.xml")
    ssh.close()


def DetachVfInt(cnx_host, cnx_vm, IntType, mac):
    print("Detaching an interface of type " + IntType + " with MAC address " + mac + " from " + cnx_vm[0] + " \n")
    ssh = SSHConnect(cnx_host)
    output= RunCommand(ssh, " virsh detach-interface --domain " + cnx_vm[0] + " --type " + IntType + " --mac " + mac + " --persistent")
    ssh.close()
    
    if "Interface detached successfully" in output[0]:
        print("Interface of type "+IntType+" with MAC address "+mac+" has been detached succesfully from "+cnx_vm[0]+" \n")
    
    else:
        print("[!] Failed to detach the interface of type "+IntType+" with MAC address "+mac+" from "+cnx_vm[0]+" \n")


def CleanVmInt(cnx_host): 
    print("Cleaning the VM interfaces on " + cnx_host[0] + " \n")
    ssh = SSHConnect(cnx_host)
    vms = []
    if cnx_host[0] == "DOSSE":
        vms=dosse_Vms
    elif cnx_host[0] == "HAVEL":
        vms=havel_Vms
    elif cnx_host[0] == "PLANE":
        vms=plane_Vms
         
    for vm in vms: 
        intr = GetVmInter(ssh, vm[0])
        for i in intr:
            DetachVfInt(cnx_host, vm, i[0], i[1])

    ssh.close()


def disableIrqBalance(cnx_host):
    print("Disable irqbalance on " + cnx_host[0] + " \n")
    ssh = SSHConnect(cnx_host)
    output = RunCommand(ssh, "/etc/init.d/irqbalance stop")
    ssh.close()
                   
#####################################################################################################################################
#---------------------------------------------------------Helper Functions-----------------------------------------------------------
##################################################################################################################################### 

def GetVmInter(ssh_host, vm_name):
    intr = []
    output = RunCommand(ssh_host, "virsh domiflist " + vm_name)
    for l in output: 
        splited = l.split()
        if len(splited) == 5:
            if "Type" not in splited[1] and "rtl8139" not in splited[3]:
                intr.append([splited[1],splited[4]])
    return intr

# generates XML config files used to attach interfaces via libvirt
def GenerateXmlBr(cnx_host,bridge, macId):
    ssh = SSHConnect(cnx_host)
    RunCommand(ssh, "echo '<interface type=\"bridge\">' >> bridgeInter.xml")
    RunCommand(ssh, "echo '   <mac address=\"" + GenerateMacID(macId) + "\"/>' >> bridgeInter.xml")
    RunCommand(ssh, "echo '   <source bridge=\"" + bridge + "\"/>' >> bridgeInter.xml")
    RunCommand(ssh, "echo '   <virtualport type=\"openvswitch\"/>' >> bridgeInter.xml")
    RunCommand(ssh, "echo '   <model type=\"e1000\"/>' >> bridgeInter.xml")
    RunCommand(ssh, "echo '</interface>' >> bridgeInter.xml")
    ssh.close()


def GenerateXmlnet(cnx_host, macId): 
    ssh =  SSHConnect(cnx_host)
    RunCommand(ssh, "echo '<interface type=\"network\">' >> netInter.xml")
    RunCommand(ssh, "echo '   <mac address=\"" + GenerateMacID(macId) + "\"/>' >> netInter.xml")
    RunCommand(ssh, "echo '   <source network=\"default\"/>' >> netInter.xml")
    RunCommand(ssh, "echo '   <model type=\"virtio\"/>' >> netInter.xml")
    RunCommand(ssh, "echo '</interface>' >> netInter.xml")
    ssh.close()
    

def GenerateXmlVf(cnx_host, vf):
    vfPci = GetPciByVf(vf)
    SplitedPCI = SplitPCI(vfPci)
    ssh = SSHConnect(cnx_host)
    RunCommand(ssh, "echo ' <interface type= \"hostdev\" managed= \"yes\" > ' >> HostdevInter.xml \n")  
    RunCommand(ssh, "echo '   <mac address=\"" + PciTOmac(vfPci) + "\"/>' >> HostdevInter.xml")
    RunCommand(ssh, "echo '   <source>' >> HostdevInter.xml")
    RunCommand(ssh, "echo '       <address type=\"pci\" domain=\"0x" + SplitedPCI[0] + "\" bus=\"0x" + SplitedPCI[1] + "\" slot=\"0x" + SplitedPCI[2] + "\" function=\"0x"+SplitedPCI[3]+"\"/>' >> HostdevInter.xml")
    RunCommand(ssh, "echo '   </source>' >> HostdevInter.xml")
    RunCommand(ssh, "echo ' </interface> '>> HostdevInter.xml ")
    ssh.close()


def PciTOmac(pci):
    pci = str(pci).replace(".","") 
    pci = pci.replace(":","") 
    pci = "000" + pci 
    indx = 2
    while indx < len(pci):
        pci = pci[:indx] + ':' + pci[indx:]
        indx = indx+3
    return pci                          
    

def GetPciByVf(vfn):
    for vf in vfs:
        if vf[0] == vfn:
            return vf[1]


def GetVFsByPf(pfn):
    for pf in pfs:
        if pf[0] == pfn:
            return pf[2]


def GetMacByVf(vfn):
    return PciTOmac(GetPciByVf(vfn))


def printLog(message, color):
    sys.stdout.write(color)
    print(message)
    sys.stdout.write(RESET)


def GenerateMacID(MacId):
    if len(MacId) < 2:
        mac = "98:76:54:32:10:00"
        mac = mac.replace("0", MacId)
    else:
        mac = "98:76:54:00:00:50"
        mac = mac.replace("00", MacId)
        
    return mac


def SplitPCI(pci):
    pci = pci.split(":")
    splitedPci = pci[0:2]
    splitedPci.append(pci[2].split(".")[0])
    splitedPci.append(pci[2].split(".")[1])
    return splitedPci


def getNameByMac(cnx, mac):
    ssh = SSHConnect(cnx)
    output = RunCommand(ssh,"ip a")
    ssh.close()
    i = 0 
    for l in output:
        if mac in l: 
            name = output[i-1].split(":")[1].strip()
            return name
        i = i + 1
    # libvirt/QEMU seems to have problems attaching more than 37 interfaces to a given VM (may be a limitation in container scenarios)
    print("There is no interface with the given Mac")


def getIntPCIbyName(cnx, Intname):
    ssh = SSHConnect(cnx)
    output = RunCommand(ssh,"lshw -c network -businfo | grep " + Intname)
    ssh.close()

    for l in output:
        line = l.split()
        if line[1] == Intname: 
            return line[0][4:]
    print("[!] There is no interface with the given Mac")

        
def getPFbyVF(cnx, vf): 
    for pf in pfs:
        pfn = pf[0]

        VfIndx=0
        for vfn in pf[2]:
            if vfn == vf:            
                return pfn, str(VfIndx)
            VfIndx = VfIndx+1


# cpuList=[Overall #cpus, [1,3 ..]]         
def getCpuMask(cpuList):
    zeros = [0]*cpuList[0]
    temp = range(cpuList[0])
    temp.reverse()

    for i in cpuList[1]:
        indx = 0
        for t in temp:
            if t == i:
                zeros[indx]=1
                break
            indx = indx+1
            
    BinaryStr = ''.join(str(e) for e in zeros)
    return hex(int(BinaryStr, 2))
                
        
def StartDpdkApp(cnx): 
    print ("starting DPDK forwording App on " + cnx[0] + "\n")    
    if type(cnx) == str:
        cnx = getVmCnx(cnx)
        
    ssh = SSHConnect(cnx)
    RunCommand(ssh,"cd /usr/local/src/dpdk/dpdk-stable-17.11.1/examples/l2fwd; ./l2fwd -l 1-2 -n 2 -- -q 1 -p 0x0003")   
    ssh.close()
    
    
def SetBridging(cnx, InPort, OutPort):  
    print("[+] Creating a linux bridge between " + InPort + " and " + OutPort + " on: " + cnx[0] + "\n")   

    if type(cnx) == str:
        cnx = getVmCnx(cnx)
        
    ssh = SSHConnect(cnx)
    RunCommand(ssh, "brctl addbr br0")   
    RunCommand(ssh, "brctl addif br0 " + InPort) 
    RunCommand(ssh, "brctl addif br0 " + OutPort) 
    SetInt(cnx, "br0", "up") 
    ssh.close()
    
  
def setStp(cnx, state, intr):    
    print ("Set " + intr + " Stp " + state + " on " + cnx[0] + "\n")          
    ssh = SSHConnect(cnx)
    RunCommand(ssh, "brctl stp " + intr + " " + state)   
    ssh.close()        


# used to delete vnets from the virbr0
def deleteInrFromBr(cnx, br, intr):    
    print("Delete " + intr + " from " + br + " on " + cnx[0] + "\n")          
    ssh = SSHConnect(cnx)
    RunCommand(ssh, "brctl delif " + br + " " + intr)   
    ssh.close()   
    

def setCnxLimit(cnx, limit):
    print("Set the Limit of concurrent connextions to " + str(limit) + " on " + cnx[0] + "\n")          
    ssh = SSHConnect(cnx)
    RunCommand(ssh, "ulimit -n " + str(limit))   
    ssh.close()


def setInterruptMod(cnx, intr, state):
   print("Set adaptive interrupt moderation on " + intr + " :+" + state + " \n")
   ssh = SSHConnect(cnx)
   RunCommand(ssh, "ethtool -C " + intr + " adaptive-rx " + state)
   RunCommand(ssh, "ethtool -C " + intr + " adaptive-tx " + state)
   ssh.close()


#####################################################################################################################################
#------------------------------------------------Helper Functions for Creating Scenarios-----------------------------------------------------------------
#####################################################################################################################################     
#---------------- **************** General Vars#---------------- ****************#
NicType = ""
isSRIOV = False
IsDPDK = False
isContainer = False
OVS_PATH = ""
HOST_CPU = ""
Server_cnx = []

#----------------------------Nic Configuration----------------------------------- 
#[partitioning-TYPE, #PF, #VF, #PF-VLANS]
#NicConfig=["partitioning-with-sriov","4","4","0,10,20,30"]

# Nic Configuration for Mlx [0 or 1, #VF]
NicConfig = ["1","8"]
#---------------- **************** In Case: SR-IOV #---------------- ****************#
VfsMatch = dict()

#("interface Name", "Number of VFs")
PhyPorts = []

#("Vf name", "Vlan", "spoofchk state", "Vm connextion")
MyVfs = []

# ("Vm connextion", Cpu affinity [1,2,3,4])
usedVms = []

#---------------- **************** In Case: Non_SR-IOV #---------------- ****************#
VirPortsMatch = dict()

# ("interface Name", "Bridge Name")
PhyPorts = []

# ("Mac Id", "Bridge Name", "Vm connextion")
VirtualPorts = []

# ("Vm connextion", Cpu affinity [1,2,3,4])
usedVms = []

#---------------- **************** Logs Vars#---------------- ****************#
scsName = ""
CmdLogPath = ""
DefaultCmdLogPath = "/tmp/ExpLib_logs/temp_log.txt"
SummaryPath = ""
#####################################################################################################################################   


def InitialConfig(custom=False):
    hostCpuAllocation(HOST_CPU)

    # the costum case is added to handle the Baseline_DPDK case
    if custom == False:
        ResetTestBed(Server_cnx, isSRIOV, NicType) 
    else:
        # in case of Baseline_DPDK just reboot and clean the interfaces 
        RebootServer(Server_cnx)
        CleanVmInt(Server_cnx)
        setStp(Server_cnx ,"off", "virbr0")
    
    StopOVS(Server_cnx)
    
    if isSRIOV:        
        for p in PhyPorts:
            SetInt(Server_cnx, p[0], "up")
            SetMTU(Server_cnx, p[0], "2048")
            setInterruptMod(Server_cnx, p[0], "off")
            ConfVFs(Server_cnx, p[0], p[1])
            GetVfPfData(Server_cnx , NicType, p[0])
            UnbindVFs(Server_cnx,  p[0], NicType)    
        SetVfMac(Server_cnx, NicType)
    else: 
        for p in PhyPorts:
            SetInt(Server_cnx, p[0], "up")
            SetMTU(Server_cnx, p[0], "2048")
            setInterruptMod(Server_cnx, p[0], "off")


'''
this function requires:
    ports=[
    ("Vf name", "is a DPDK ports?", "if True add CPU affinity")
    ]
    
    OvsCpu=["OVSDB CPU", "Vswitchd CPU"]
'''
resets = []
def ConfigOVS(cnx, bridge, ports, OvsCpu=["0","3"],  DpdkMem="2048,0", DpdkCpu=[4,[1,2]], ContNum=0, VMNum=1):
    if type(cnx) == str:
        cnx = getVmCnx(cnx)
       
    # make sure to call StopOVS only once per VM in the Dynamic_Container setting [hacky solution for now]
    if (isContainer and VMNum not in resets) or not isContainer:
        StopOVS(cnx)
        resets.append(VMNum)
    if IsDPDK:
        StartOVS(cnx, OVS_PATH, IsDPDK, OvsCpu, DpdkMem, DpdkCpu)
    else:
        StartOVS(cnx, OVS_PATH, IsDPDK, OvsCpu, ContNum=ContNum)
        
    DelBridge(cnx, OVS_PATH, bridge, ContNum=ContNum)
    AddBridge(cnx, OVS_PATH, bridge, IsDPDK, ContNum=ContNum)
    
    if isSRIOV:
        for p in ports: 
            if p[1] == True:
                SetPort(cnx, OVS_PATH, bridge, VfsMatch[p[0]], p[1], p[2])
            else:
                SetPort(cnx, OVS_PATH, bridge, VfsMatch[p[0]], p[1], ContNum=ContNum)
    else:
        for phyp in PhyPorts:
            if len(phyp) > 2:
                if phyp[2] == True:
                    SetPort(cnx, OVS_PATH, phyp[1], phyp[0],  phyp[2],  phyp[3])
            else:
                SetPort(cnx, OVS_PATH, phyp[1], phyp[0], False)


def Vfsconfig(): 
    for vf in MyVfs:
        VM_cnx = getVmCnx(vf[3])
        setVfVlan(Server_cnx, vf[0], vf[1])
        Setspoofchk(Server_cnx, vf[0], vf[2])
        AttachVf(Server_cnx, VM_cnx, vf[0])
    
    for vm in usedVms:
        VM_cnx = getVmCnx(vm[0])
        StartVM(Server_cnx , VM_cnx, vm[1], vm[2])
        AutoSetForword(Server_cnx, VM_cnx)
        getVfsMatch(VM_cnx)
        setVmIntrUp(VM_cnx)
        setVmIntrMtu(VM_cnx)
        disableVmInterruptMod(VM_cnx)


def VirPortConfig():    
    for p in VirtualPorts: 
        VM_cnx = getVmCnx(p[2])
        if not IsDPDK:
            AttachBrInter(Server_cnx, VM_cnx, p[1], p[0])
        else:
            AttachNetInter(Server_cnx, VM_cnx, p[0])
                
    for vm in usedVms:
        VM_cnx = getVmCnx(vm[0])
        StartVM(Server_cnx , VM_cnx, vm[1], vm[2])
        AutoSetForword(Server_cnx, VM_cnx)
        getVirPortMatch(VM_cnx)
        setVmIntrUp(VM_cnx)
        # setting MTU for virtual ports is not possible for now (Under Test)
        setVmIntrMtu(VM_cnx)
    
    if IsDPDK: 
        for p in VirtualPorts:
            SetPort(Server_cnx, OVS_PATH, p[1], "vnet"+p[0], False)
            deleteInrFromBr(Server_cnx ,"virbr0", "vnet"+p[0])
            
                        
def AutoSetForword(cnx, cnx_vm): 
    if cnx_vm[0] == "vswitch-vm":
        setPortForward(cnx, Fp_OvsVM, OvsVM)

    elif cnx_vm[0] == "vswitch-vm-2":
        setPortForward(cnx, Fp_OvsVM2, OvsVM2)

    elif cnx_vm[0] == "vswitch-vm-3":
        setPortForward(cnx, Fp_OvsVM3, OvsVM3)
        
    elif cnx_vm[0] == "vswitch-vm-4":
        setPortForward(cnx, Fp_OvsVM4, OvsVM4)

    elif cnx_vm[0] == "vswitch-vm-container":
        setPortForward(cnx, Fp_ContVM, ContainerVM)

    elif cnx_vm[0] == "vswitch-vm-container-2":
        setPortForward(cnx, Fp_ContVM2, ContainerVM2)
    
    elif cnx_vm[0] == "vswitch-vm-container-3":
        setPortForward(cnx, Fp_ContVM3, ContainerVM3)
    
    elif cnx_vm[0] == "vswitch-vm-container-4":
        setPortForward(cnx, Fp_ContVM4, ContainerVM4)
        
    elif cnx_vm[0] == "tenant-green-1":
        setPortForward(cnx, Fp_Tenant1, Tenant1)
    
    elif cnx_vm[0] == "tenant-green-2":
        setPortForward(cnx, Fp_Tenant2, Tenant2)
        
    elif cnx_vm[0] == "tenant-green-3":
        setPortForward(cnx, Fp_Tenant3, Tenant3)
        
    elif cnx_vm[0] == "tenant-green-4":
        setPortForward(cnx, Fp_Tenant4, Tenant4)


def getVfsMatch(cnx_vm):
    for vf in MyVfs:
        VM_cnx = getVmCnx(vf[3])
        
        if VM_cnx == cnx_vm:
            VfsMatch[vf[0]] = getNameByMac(cnx_vm, GetMacByVf(vf[0]))


def getVirPortMatch(cnx_vm):
    for p in VirtualPorts: 
        VM_cnx = getVmCnx(p[2])
        
        if VM_cnx == cnx_vm:
            VirPortsMatch[p[0]] = getNameByMac(cnx_vm, GenerateMacID(p[0]))


def setVmIntrUp(cnx_vm):
    if isSRIOV: 
        for vf in MyVfs:
            VM_cnx = getVmCnx(vf[3])
            
            if VM_cnx == cnx_vm:
                SetInt(cnx_vm, VfsMatch[vf[0]], "up") 
    else: 
        for p in VirtualPorts: 
            VM_cnx = getVmCnx(p[2]) 
            if VM_cnx == cnx_vm:
                SetInt(cnx_vm, VirPortsMatch[p[0]], "up") 


def setVmIntrMtu(cnx_vm):
    if isSRIOV: 
        for vf in MyVfs:
            VM_cnx = getVmCnx(vf[3])
            
            if VM_cnx == cnx_vm:
                SetMTU(cnx_vm, VfsMatch[vf[0]], "2048") 
    else: 
        for p in VirtualPorts: 
            VM_cnx = getVmCnx(p[2]) 
            if VM_cnx == cnx_vm:
                SetMTU(cnx_vm, VirPortsMatch[p[0]], "2048")  
                SetMTU(Server_cnx, "vnet" + p[0], "2048")  


def disableVmInterruptMod(cnx_vm):
    if isSRIOV: 
        for vf in MyVfs:
            VM_cnx = getVmCnx(vf[3])
            
            if VM_cnx == cnx_vm:
                setInterruptMod(cnx_vm, VfsMatch[vf[0]], "off")


def getVmCnx(VM_name):  
    if Server_cnx == cnx_havel:
        server_vms = havel_Vms
    elif Server_cnx == cnx_plane:
        server_vms = plane_Vms
    elif Server_cnx == cnx_dosse:
        server_vms = dosse_Vms
        
    for vm in server_vms: 
        if vm[0] == VM_name:
            return vm
    
                         
def printCmdLog(strg):
    if len(CmdLogPath) != 0:
        if not os.path.exists(os.path.dirname(CmdLogPath)):
            try:
                os.makedirs(os.path.dirname(CmdLogPath))
            except OSError as exc: 
                if exc.errno != errno.EEXIST:
                    raise
        with open(CmdLogPath, "a") as f:
            f.write(strg)
            f.close()
    else:
        if not os.path.exists(os.path.dirname(DefaultCmdLogPath)):
            try:
                os.makedirs(os.path.dirname(DefaultCmdLogPath))
            except OSError as exc: 
                if exc.errno != errno.EEXIST:
                    raise
        with open(DefaultCmdLogPath, "a") as f:
            logTimeStamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            f.write("##################  "+logTimeStamp+"  ################## \n")
            f.write(strg)
            f.close()

    
def hostCpuAllocation(cores):
    print("Host CPU Allocation ....\n")
    print("the Host is running on "+cores+" core(s) ....\n")
    ssh = SSHConnect(Server_cnx)
    RunCommand(ssh, "cd /root/grubFiles; cp grub-hostOS-"+cores+"cores /etc/default/grub")   
    RunCommand(ssh, "cd /root/grubFiles;  update-grub") 
    time.sleep(10)
    ssh.close()
    

def startL2fwdDpdk(cnx, vswitchMode="SRIOV_NoDPDK", nicType="mlx", tenantNumber="1"):
    print("startL2fwdDpdk")
    ssh = SSHConnect(cnx)
    if nicType == "e1000":
        # Need to unbind the kernel driver for e1000 and bind the igb_uio for dpdk
        RunCommand(ssh,
                    "modprobe uio; cd /usr/local/src/dpdk/dpdk-stable-17.11.1;"
                    "insmod x86_64-native-linuxapp-gcc/kmod/igb_uio.ko")
        RunCommand(ssh,
                    "cd /usr/local/src/dpdk/dpdk-stable-17.11.1; ./usertools/dpdk-devbind.py --bind=igb_uio 0000:00:08.0;")
        RunCommand(ssh,
                    "cd /usr/local/src/dpdk/dpdk-stable-17.11.1; ./usertools/dpdk-devbind.py --bind=igb_uio 0000:00:09.0;")
    if vswitchMode == "Baseline_NoDPDK" or vswitchMode == "Baseline_DPDK" or vswitchMode == "SRIOV_NoDPDK" or vswitchMode == "SRIOV_DPDK":
        RunCommand(ssh,
                   "cd /usr/local/src/dpdk/dpdk-stable-17.11.1/examples/l2fwd/build/;"
                   "screen -dmSL l2fwdSession ./l2fwd-default -l 0,1 -n 2 -- -q 1 -p 0x0003")
    elif vswitchMode == "Baseline_MultiTenant_NoDPDK" or vswitchMode == "Baseline_MultiTenant_DPDK" or vswitchMode == "SRIOV_MultiTenant_NoDPDK" or \
            vswitchMode == "SRIOV_MultiTenant_DPDK":
        RunCommand(ssh,
                   "cd /usr/local/src/dpdk/dpdk-stable-17.11.1/examples/l2fwd/build/;"
                   "screen -dmSL l2fwdSession ./l2fwd-multitenant -l 0,1 -n 2 -- -q 1 -p 0x0003")
    elif vswitchMode == "SRIOV_MultiOvs_NoDPDK" or vswitchMode == "SRIOV_MultiOvs_DPDK":
        RunCommand(ssh,
                   "cd /usr/local/src/dpdk/dpdk-stable-17.11.1/examples/l2fwd/build/;"
                   "screen -dmSL l2fwdSession ./l2fwd-multiovs -l 0,1 -n 2 -- -q 1 -p 0x0003")
    # For 4 tenant scenarios
    elif vswitchMode == "Baseline_4Tenants":
        RunCommand(ssh,
                   "cd /usr/local/src/dpdk/dpdk-stable-17.11.1/examples/l2fwd/build/;"+\
                   "screen -dmSL l2fwdSession ./l2fwd-default -l 0,1 -n 2 -- -q 1 -p 0x0003")
    elif vswitchMode == "SRIOV_1Ovs_4Tenants":
        RunCommand(ssh,
                   "cd /usr/local/src/dpdk/dpdk-stable-17.11.1/examples/l2fwd/build/4tenants;"+\
                   "screen -dmSL l2fwdSession ./l2fwd-SingleOvsVm-4tenants-tenant-"+tenantNumber+" -l 0,1 -n 2 -- -q 1 -p 0x0003")
    elif vswitchMode == "SRIOV_2Ovs_4Tenants":
        RunCommand(ssh,
                   "cd /usr/local/src/dpdk/dpdk-stable-17.11.1/examples/l2fwd/build/4tenants;"+\
                   "screen -dmSL l2fwdSession ./l2fwd-TwoOvsVm-4tenants-tenant-"+tenantNumber+" -l 0,1 -n 2 -- -q 1 -p 0x0003")
    elif vswitchMode == "SRIOV_4Ovs_4Tenants":
        RunCommand(ssh,
                   "cd /usr/local/src/dpdk/dpdk-stable-17.11.1/examples/l2fwd/build/4tenants;"+\
                   "screen -dmSL l2fwdSession ./l2fwd-FourOvsVm-4tenants-tenant-"+tenantNumber+" -l 0,1 -n 2 -- -q 1 -p 0x0003")
    
    elif vswitchMode == "vm2vm_SRIOV_1Ovs":
        RunCommand(ssh,
                   "cd /usr/local/src/dpdk/dpdk-stable-17.11.1/examples/l2fwd/build/4tenants;"+\
                   "screen -dmSL l2fwdSession ./l2fwd-SingleOvsVm-VM-VM-4tenants-tenant-"+tenantNumber+" -l 0,1 -n 2 -- -q 1 -p 0x0003")
    
    elif vswitchMode == "vm2vm_SRIOV_2Ovs":
        RunCommand(ssh,
                   "cd /usr/local/src/dpdk/dpdk-stable-17.11.1/examples/l2fwd/build/4tenants;"+\
                   "screen -dmSL l2fwdSession ./l2fwd-TwoOvsVm-VM-VM-4tenants-tenant-"+tenantNumber+" -l 0,1 -n 2 -- -q 1 -p 0x0003")
    
    elif vswitchMode == "vm2vm_Bench_Baseline":
        RunCommand(ssh,
                   "cd /usr/local/src/dpdk/dpdk-stable-17.11.1/examples/l2fwd/build/4tenants;"
                   "screen -dmSL l2fwdSession ./l2fwd-Baseline-Bench-VM-VM-4tenants-tenant-"+tenantNumber+" -l 0,1 -n 2 -- -q 1 -p 0x0003")
    
    elif "container" in vswitchMode:
        # DPDK options to get multiple sessions on one machine working: socket-mem=1000: take only one hugepage; file-prefix=x: own memory region for each session, no coooperation; 
        RunCommand(ssh,
                   "cd /usr/local/src/dpdk/dpdk-stable-17.11.1/examples/l2fwd/build/container;"
                   "screen -dmSL l2fwdSession-{0} ./l2fwd-container-{0} -l {1},{2} -n 2 --socket-mem=1000 --file-prefix={0} -- -q 1 -p {3}".format(tenantNumber, ((tenantNumber - 1)*2) % l2fwdCpuCores, ((tenantNumber - 1)*2 + 1) % l2fwdCpuCores, hex(3 << (tenantNumber - 1)*2)))

    ssh.close()


'''
start DPDK App for a given range of Tenant VMs  
'''  
def startL2Frwd(nbrOvs, nicType="mlx", tenantCount=4, vswitchMode=""):
    # set nr_hugepages = nr_l2fwd-sessions
    if isContainer:
        RunCommand(SSHConnect(getVmCnx("tenant-green-" + str(1))), "sysctl vm.nr_hugepages={}".format(tenantCount))
        if vswitchMode == "v2v_container":
            RunCommand(SSHConnect(getVmCnx("tenant-green-" + str(2))), "sysctl vm.nr_hugepages={}".format(tenantCount))
    
    for t in range(1,tenantCount+1):
        if isContainer:
            if vswitchMode == "p2v_container":
                startL2fwdDpdk(getVmCnx("tenant-green-" + str(1)), vswitchMode=vswitchMode, nicType=nicType, tenantNumber=t)
            elif vswitchMode == "v2v_container":
                startL2fwdDpdk(getVmCnx("tenant-green-" + str(1)), vswitchMode=vswitchMode, nicType=nicType, tenantNumber=t)
                startL2fwdDpdk(getVmCnx("tenant-green-" + str(2)), vswitchMode=vswitchMode, nicType=nicType, tenantNumber=t)
        elif vswitchMode == "Baseline_4Tenants":
            startL2fwdDpdk(getVmCnx("tenant-green-" + str(t)), vswitchMode=vswitchMode, nicType=nicType, tenantNumber=str(t))
        else:
            startL2fwdDpdk(getVmCnx("tenant-green-" + str(t)), vswitchMode="SRIOV_"+str(nbrOvs)+"Ovs_4Tenants", nicType=nicType, tenantNumber=str(t))


'''
#Parameters:
    nbrOvs: Number of OvS VMs 
    isIsolated: Enable/disable sharing of cpu resources among OvS VMs
    isSRIOV: True/False
    nbrTenants: Total number of Tenant VMs
    TenantVmCores: cpu cores per Tenant VMs
    totalCpuCores: Availble cpu Cores
    nbrCores: 
            + if isIsolated => cup cores per OvsVM
            + if shared     => cpu cores for all OvsVMs
            
#Output: 
    it returns an Array with cpu Infos for:
        + Host cpu Cores +1 
        + OvsVMs cpu Arrays
        + TenantVms cpu Arrays
        + OvS Deamon & OVSDB 
        + OvS DPDK
        + DPDK ports
'''
def cpuAllocation(nbrOvs, nbrCores, isIsolated, isSRIOV, nbrTenants, TenantVmCores, totalCpuCores):
    cpuInfoDic = {}
 
    if nbrTenants % nbrOvs != 0 and not isContainer:
        print(str(nbrTenants) + " Tenant VM(s) can be not devided equally by the "  + str(nbrOvs) + " OvsVMs")
        return None

    ovsd = ','.join(str(c) for c in range(nbrCores))  
    ovsdb = ','.join(str(c) for c in range(nbrCores))
    ovsCpu = [ovsd, ovsdb]
    OvsVMsCpuArray = []
    TenantVMsCpuArray = []

    if not isSRIOV:
        ovsDpdk = [totalCpuCores,range(nbrCores)]
        cpuDpdkPorts = ','.join(str(c) for c in range(nbrCores))
        
        hostCpu = nbrCores
        start = hostCpu
        
    else:
        ovsDpdk = [nbrCores,range(nbrCores)]
        cpuDpdkPorts = ','.join(str(c) for c in range(nbrCores))
        
        hostCpu = 1        
        start = hostCpu
        if isIsolated:
            for ovsVM in range(nbrOvs):
                OvsVMsCpuArray.append(range(start, start+nbrCores))
                start = start + nbrCores
        else:
            for ovsVM in range(nbrOvs):
                OvsVMsCpuArray.append(range(start, start+nbrCores))
            start = start + nbrCores
    
    for tenantVM in range(nbrTenants):
        TenantVMsCpuArray.append(range(start, start+TenantVmCores))
        start = start+TenantVmCores    
    
    
    if start >= totalCpuCores:
        print("[!] The required CPU cores are not availble \n")
        print("For the given Scenario "+str(start+1)+" cpu cores are required and only "+str(totalCpuCores)+" are available!\n")
        return None
    
    cpuInfoDic["hostCpu"] = str(hostCpu)
    cpuInfoDic["OvsVMsCpuArray"] = OvsVMsCpuArray
    cpuInfoDic["TenantVMsCpuArray"] = TenantVMsCpuArray
    cpuInfoDic["ovsCpu"] = ovsCpu
    cpuInfoDic["ovsDpdk"] = ovsDpdk
    cpuInfoDic["cpuDpdkPorts"] = cpuDpdkPorts
    
    return cpuInfoDic


def Logs(Summary, time):    
    global CmdLogPath
    global SummaryPath
    
    CmdLogPath = "./ExpLib_logs/"+time+"/"+scsName+"_"+Server_cnx[0]+"_.txt"
    SummaryPath = "./ExpLib_logs/"+time+"/summary.txt"
    
    if not os.path.exists(os.path.dirname(SummaryPath)):
        try:
            os.makedirs(os.path.dirname(SummaryPath))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(SummaryPath, "w") as f:
        f.write(Summary)
        f.close()


def GetScenarioSummary(OvsVmPorts, OvsCpu, DpdkCpu, DpdkMem, IsCpusIsolated=True):    
    
    SummaryMsg = "Scenario Name: " + scsName + "\n"
    SummaryMsg = SummaryMsg + "Nic : "+ str(NicType) + "\n"
    SummaryMsg = SummaryMsg + "Is OVS running with DPDK : " + str(IsDPDK) + "\n"
    SummaryMsg = SummaryMsg + "Is SR-IOV enabled : " + str(isSRIOV) + "\n"
    
    if isSRIOV and len(OvsVmPorts) > 1:
        SummaryMsg = SummaryMsg + "CPU Isolation : " + str(IsCpusIsolated) + "\n"
        
    SummaryMsg = SummaryMsg + " \n \n"
    
    SummaryMsg = SummaryMsg + "Physical Ports config: \n"
    if isSRIOV:
        for p in PhyPorts: 
            SummaryMsg = SummaryMsg + "     +port " + p[0] + " has " + p[1] + " configured Vfs \n"
    else:
        if IsDPDK:
            for p in PhyPorts:
                SummaryMsg = SummaryMsg + "     +port " + p[0] + "  assigned to:" + p[1] + " as a DPDK port on Cores: " + p[3] + " \n"
        else:
            for p in PhyPorts:
                SummaryMsg = SummaryMsg + "     +port " + p[0] + "  assigned to:" + p[1] + " \n"
     
    SummaryMsg = SummaryMsg + " \n \n"

    if isSRIOV:
        SummaryMsg = SummaryMsg + "Vfs config: \n"
        for vf in MyVfs:
            SummaryMsg = SummaryMsg + "     +" + vf[0] + "   Vlan: " + vf[1] + " Spoofchk: " + vf[2] + "  asssigned to " + vf[3] + "\n"
    
    else:
        if len(VirtualPorts) != 0:
            SummaryMsg = SummaryMsg + "Virtual ports config: \n"
            for vp in VirtualPorts:
                SummaryMsg = SummaryMsg + "     +Mac Id: " + vp[0] + "   assigned to bridge: " + vp[1] + "  assigned to: " + vp[2] + "\n"

    SummaryMsg = SummaryMsg+ " \n \n" 
    
    if len(usedVms) != 0:
        SummaryMsg = SummaryMsg + "VMs config: \n"
        for vm in usedVms:
            SummaryMsg = SummaryMsg + "     +" + vm[0] + "  Running on cores:" + str(vm[1]) + "  RAM: " + vm[2] + "\n"
            
    SummaryMsg = SummaryMsg + " \n \n" 
    
    if isSRIOV:
        SummaryMsg = SummaryMsg + "OVS vCPU Config: \n"
    else:
        SummaryMsg = SummaryMsg + "OVS CPU Config: \n" 
        
    SummaryMsg = SummaryMsg + "     +OVSDb:  " + OvsCpu[0] + " \n"
    SummaryMsg = SummaryMsg + "     +Vswitchd:  " + OvsCpu[1] + " \n"
    
    if IsDPDK:
        cpuDpdkCores = ','.join(str(c) for c in DpdkCpu[1])
        SummaryMsg = SummaryMsg + "     +OVS-DPDK:  " + str(cpuDpdkCores) + " \n"
        SummaryMsg = SummaryMsg + "     +DPDK Memory:  " + DpdkMem + " \n"
            
    SummaryMsg = SummaryMsg + " \n \n" 
        
    if isSRIOV and len(OvsVmPorts) != 0:
        SummaryMsg = SummaryMsg + "OVS VM(s) Config: \n"
        indx = 1
        for pl in OvsVmPorts: 
            SummaryMsg = SummaryMsg + "OVS-VM " + str(indx) + " Config: \n"
            indx = indx + 1
            for vmp in pl:
                if vmp[1] == True:
                    SummaryMsg = SummaryMsg + "     +vf "+vmp[0]+"  is a DPDK port Running on cores:"+vmp[2]+"\n"
                else:
                    SummaryMsg = SummaryMsg + "     +vf "+vmp[0]+"\n"
                    
    return SummaryMsg          


def EmailNotify(body, state, time, attachmentPath=""):
    
    if len(Server_cnx) == 0:
        subject = time + " , " + state
    else:  
        subject = time + ": " + scsName + " " + state + " on " + Server_cnx[0]
    
    gmail_sender = 'XXX'
    gmail_passwd = 'XXX'
    
    receivers = "XXX"
    
    msg = MIMEMultipart()
    msg['From'] = gmail_sender
    msg['To'] = receivers
    msg['Subject'] = subject
    
    
    msg.attach(MIMEText(body))
    
    if attachmentPath != "":    
        attachment = open(attachmentPath,'rb')    
        part = MIMEBase('application','octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',"attachment; filename= "+attachmentPath)
        msg.attach(part)
    
    text = msg.as_string()
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(gmail_sender, gmail_passwd)
    
    try:
        server.sendmail(gmail_sender, receivers.split(","), text)
    except:
        print('error sending mail')
    
    server.quit()           
