#!/usr/bin/env python

##########
#
# 
# run test case with: "python TestCase.py <testcase num>""
# e.g.: "python TestCase.py 1" for test case 1  
# 
#
##########


from __future__ import print_function

from mininet.cli import CLI
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.log import setLogLevel

import os
import sys
import time
import tempfile

current_dir = os.getcwd()

class SimpleNetwork(Topo):
    '''
    Shape:
                   h2
                   |
    h1 -- [s1] -- [s2] -- [s3] -- h3
           /        |       \
          h6        h5       h4

    '''
    def __init__(self, s1_s2 = 10, s2_s3 = 10, **opts):
        Topo.__init__(self, **opts)
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')
        
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        
        self.addLink(h1, s1)
        self.addLink(h6, s1)
        self.addLink(h2, s2)
        self.addLink(h5, s2)
        self.addLink(h3, s3)
        self.addLink(h4, s3)

        self.addLink(s1, s2, bw=s1_s2, delay='40ms')
        self.addLink(s2, s3, bw=s2_s3, delay='10ms')

class ServerSideLowBandWidthNetworks(Topo):
    '''
    Network shape:
          
             h1
             |
     h3     [s4]     h5
     |       |       |
    [s1] -- [s2] -- [s3]
     |       |       |
     h4      h2      h6

    '''

    def __init__(self, s1_s2 = 10, s2_s3 = 10, s3_s4 = 10, **opts):
        Topo.__init__(self, **opts)
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')
        
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        self.addLink(h1, s4)

        self.addLink(h2, s2)

        self.addLink(h3, s1)
        self.addLink(h4, s1)

        self.addLink(h5, s3)
        self.addLink(h6, s3)

        self.addLink(s1, s2, bw=s1_s2, delay='5ms')
        self.addLink(s2, s3, bw=s2_s3, delay='10ms')
        self.addLink(s2, s4, bw=s3_s4, delay = '40ms')

class StarfishShapeNetworks(Topo):
    '''
      h1  h2 h3
        \ | /
    h4 -- s1 -- h5
        / | \
      h6  h7 h8
    '''
    def __init__(self, **opts):
        Topo.__init__(self, **opts)
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')
        h7 = self.addHost('h7')
        h8 = self.addHost('h8')
        s1 = self.addSwitch('s1')

        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(h4, s1)
        self.addLink(h5, s1)
        self.addLink(h6, s1)
        self.addLink(h7, s1)
        self.addLink(h8, s1)

class FileHelper:
    def __init__(self, ip_list):
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.txt', dir=os.getcwd())
        for ip in ip_list:
            self.temp_file.write(ip.encode('utf-8'))
        self.temp_file.flush()
        self.file_path = self.temp_file.name

    def getFilePath(self):
        return os.path.abspath(self.file_path)

    def close(self):
        if self.temp_file:
           self.temp_file.close()

def testcase1():
    '''
    test high bandwidth with low alpha value (slow bitrate increasing)
    '''
    setLogLevel( 'info' )
    # clear mn
    os.system("sudo mn -c")

    topo = SimpleNetwork(s1_s2 = 10, s2_s3 = 10)
    net = Mininet(topo=topo, link=TCLink, autoSetMacs=True,
           autoStaticArp=True)

    PORT = 8888
    ALPHA = 0.01
    LOG_FILE = 'log1.log'
    proxy_node = 2
    proxy_timeout = 50

    # helper file
    server_ip_list=[]
    for i in [1]:
        ip = "10.0.0." + str(i)
        server_ip_list.append(ip)
    tmp_file = FileHelper(server_ip_list)
    tmp_file_path = tmp_file.getFilePath()
  
    # Run network
    net.start()
    
    h1 = net.get("h1")
    h3 = net.get("h3")
    h2 = net.get("h2")

    h1.cmd("sudo python start_server.py 1")

    h3.cmd("python firefox_open_url.py 1 10.0.0.{}:{} & "\
        .format(proxy_node, PORT))

    h2.cmdPrint("make clean && make && timeout {} ./miProxy --nodns {} {} {} {}"\
        .format(proxy_timeout, PORT, tmp_file_path, ALPHA, LOG_FILE))
    
    # CLI( net )
    h1.cmd("sudo killall httpd")

    net.stop()

    tmp_file.close()      

def testcase2():
    '''
    test high bandwidth with large alpha value (fast bitrate increasing)
    '''
    setLogLevel( 'info' )
    # clear mn
    os.system("sudo mn -c")

    topo = SimpleNetwork(s1_s2 = 10, s2_s3 = 10)
    net = Mininet(topo=topo, link=TCLink, autoSetMacs=True,
           autoStaticArp=True)

    PORT = 8888
    ALPHA = 0.5
    LOG_FILE = 'log2.log'
    proxy_node = 2
    proxy_timeout = 100

    # helper file, write server ip to file
    server_ip_list=[]
    for i in [1]:
        ip = "10.0.0." + str(i)
        server_ip_list.append(ip)
    tmp_file = FileHelper(server_ip_list)
    tmp_file_path = tmp_file.getFilePath()
  
    # Run network
    net.start()
    
    h1 = net.get("h1")
    h3 = net.get("h3")
    h2 = net.get("h2")

    h1.cmd("sudo python start_server.py 1")

    h3.cmd("python firefox_open_url.py 1 10.0.0.{}:{} & "\
        .format(proxy_node, PORT))

    h2.cmd("make clean && make && timeout {} ./miProxy --nodns {} {} {} {}"\
        .format(proxy_timeout, PORT, tmp_file_path, ALPHA, LOG_FILE))
    
    # CLI( net )
    h1.cmd("sudo killall httpd")

    net.stop()      

    tmp_file.close()      

def testcase3():
    '''
    test 0.5mbps bandwidth
    '''
    setLogLevel( 'info' )
    # clear mn
    os.system("sudo mn -c")

    topo = SimpleNetwork(s1_s2 = 0.5, s2_s3 = 0.5)
    net = Mininet(topo=topo, link=TCLink, autoSetMacs=True,
           autoStaticArp=True)

    PORT = 8888
    ALPHA = 0.5
    LOG_FILE = 'log3.log'
    proxy_node = 2
    proxy_timeout = 100

    # helper file, write server ip to file
    server_ip_list=[]
    for i in [1]:
        ip = "10.0.0." + str(i)
        server_ip_list.append(ip)
    tmp_file = FileHelper(server_ip_list)
    tmp_file_path = tmp_file.getFilePath()
  
  
    # Run network
    net.start()
    
    h1 = net.get("h1")
    h3 = net.get("h3")
    h2 = net.get("h2")

    h1.cmd("sudo python start_server.py 1")

    h3.cmd("python firefox_open_url.py 1 10.0.0.{}:{} & "\
        .format(proxy_node, PORT))

    h2.cmd("make clean && make && timeout {} ./miProxy --nodns {} {} {} {}"\
        .format(proxy_timeout, PORT, tmp_file_path, ALPHA, LOG_FILE))
    
    # CLI( net )
    h1.cmd("sudo killall httpd")

    net.stop()     

    tmp_file.close()      

def testcase4():
    '''
    test bandwidth change from 10mbps to 1mbps 
    '''
    setLogLevel( 'info' )
    # clear mn
    os.system("sudo mn -c")

    topo = SimpleNetwork(s1_s2 = 10, s2_s3 = 10)
    net = Mininet(topo=topo, link=TCLink, autoSetMacs=True,
           autoStaticArp=True)

    PORT = 8888
    ALPHA = 0.5
    LOG_FILE = 'log4.log'
    proxy_node = 2
    proxy_timeout = 100

    # helper file, write server ip to file
    server_ip_list=[]
    for i in [1]:
        ip = "10.0.0." + str(i)
        server_ip_list.append(ip)
    tmp_file = FileHelper(server_ip_list)
    tmp_file_path = tmp_file.getFilePath()
    
    rate_change_delay1 = 40
    mbit1 = 1
    # Run network
    net.start()
    
    h1 = net.get("h1")
    h3 = net.get("h3")
    h2 = net.get("h2")

    h1.cmd("sudo python start_server.py 1")

    h1.cmd("sleep {} && tc qdisc add dev h1-eth0 root tbf rate {}mbit burst 100kbit latency 400ms &"\
        .format(rate_change_delay1, mbit1))

    h3.cmd("python firefox_open_url.py 1 10.0.0.{}:{} & "\
        .format(proxy_node, PORT))

    h2.cmd("make clean && make && timeout {} ./miProxy --nodns {} {} {} {}"\
        .format(proxy_timeout, PORT, tmp_file_path, ALPHA, LOG_FILE))
    
    # CLI( net )
    h1.cmd("sudo killall httpd")

    net.stop()   

    tmp_file.close()      

def testcase5():
    '''
    test sudden bandwidth drop to less than 100kbps (50kbs)
    '''
    setLogLevel( 'info' )
    # clear mn
    os.system("sudo mn -c")

    topo = SimpleNetwork(s1_s2 = 2, s2_s3 = 2)
    net = Mininet(topo=topo, link=TCLink, autoSetMacs=True,
           autoStaticArp=True)

    PORT = 8888
    ALPHA = 0.9
    LOG_FILE = 'log5.log'
    proxy_node = 2
    proxy_timeout = 100

    # helper file, write server ip to file
    server_ip_list=[]
    for i in [1]:
        ip = "10.0.0." + str(i)
        server_ip_list.append(ip)
    tmp_file = FileHelper(server_ip_list)
    tmp_file_path = tmp_file.getFilePath()
    
    rate_change_delay1 = 20
    kbit1 = 50
    # Run network
    net.start()
    
    h1 = net.get("h1")
    h3 = net.get("h3")
    h2 = net.get("h2")

    h1.cmd("sudo python start_server.py 1")

    h1.cmdPrint("sleep {} && tc qdisc add dev h1-eth0 root tbf rate {}kbit burst 100kbit latency 400ms &"\
        .format(rate_change_delay1, kbit1))

    h3.cmd("python firefox_open_url.py 1 10.0.0.{}:{} & "\
        .format(proxy_node, PORT))

    h2.cmd("make clean && make && timeout {} ./miProxy --nodns {} {} {} {}"\
        .format(proxy_timeout, PORT, tmp_file_path, ALPHA, LOG_FILE))
    
    # CLI( net )
    h1.cmd("sudo killall httpd")

    net.stop()   

    tmp_file.close()      

def testcase6():
    '''
    test two browser case
    '''
    setLogLevel( 'info' )
    # clear mn
    os.system("sudo mn -c")

    topo = ServerSideLowBandWidthNetworks(s1_s2 = 10, s2_s3 = 10, s2_s4 = 10)
    net = Mininet(topo=topo, link=TCLink, autoSetMacs=True,
           autoStaticArp=True)

    PORT = 8888
    ALPHA = 0.5 
    LOG_FILE = 'log6.log'
    proxy_node = 2
    proxy_timeout = 100
  
    # helper file, write server ip to file
    server_ip_list=[]
    for i in [1]:
        ip = "10.0.0." + str(i)
        server_ip_list.append(ip)
    tmp_file = FileHelper(server_ip_list)
    tmp_file_path = tmp_file.getFilePath()

    # Run network
    net.start()
    
    h1 = net.get("h1")
    h3 = net.get("h3")
    h5 = net.get("h5")
    h2 = net.get("h2")

    h1.cmd("sudo python start_server.py 1")

    h3.cmd("python firefox_open_url.py 1 10.0.0.{}:{} & "\
        .format(proxy_node, PORT))
    h5.cmd("python firefox_open_url.py 2 10.0.0.{}:{} & "\
        .format(proxy_node, PORT))
    h2.cmd("make clean && make && timeout {} ./miProxy --nodns {} {} {} {}"\
        .format(proxy_timeout, PORT, tmp_file_path, ALPHA, LOG_FILE))
    
    # CLI( net )
    h1.cmd("sudo killall httpd")

    net.stop()  

    tmp_file.close()      


def testcase7():
    '''
    test two browser case, bandwidths sum up to 1000kbit
    '''
    setLogLevel( 'info' )
    # clear mn
    os.system("sudo mn -c")

    topo = ServerSideLowBandWidthNetworks(s1_s2 = 10, s2_s3 = 10, s2_s4 = 10)
    net = Mininet(topo=topo, link=TCLink, autoSetMacs=True,
           autoStaticArp=True)

    PORT = 8888
    ALPHA = 0.5 
    LOG_FILE = 'log7.log'
    proxy_node = 2
    proxy_timeout = 100

    # helper file, write server ip to file
    server_ip_list=[]
    for i in [1]:
        ip = "10.0.0." + str(i)
        server_ip_list.append(ip)
    tmp_file = FileHelper(server_ip_list)
    tmp_file_path = tmp_file.getFilePath()
    

    rate_change_delay1 = 0
    kbit1 = 1000
  
    # Run network
    net.start()
    
    h1 = net.get("h1")
    h3 = net.get("h3")
    h5 = net.get("h5")
    h2 = net.get("h2")

    h1.cmd("sudo python start_server.py 1")

    h1.cmd("sleep {} && tc qdisc add dev h1-eth0 root tbf rate {}kbit burst 100kbit latency 400ms &"\
        .format(rate_change_delay1, kbit1))

    h3.cmd("python firefox_open_url.py 1 10.0.0.{}:{} & "\
        .format(proxy_node, PORT))
    h5.cmd("python firefox_open_url.py 2 10.0.0.{}:{} & "\
        .format(proxy_node, PORT))
    h2.cmd("make clean && make && timeout {} ./miProxy --nodns {} {} {} {}"\
        .format(proxy_timeout, PORT, tmp_file_path, ALPHA, LOG_FILE))
    
    # CLI( net )
    h1.cmd("sudo killall httpd")

    net.stop()  

    tmp_file.close()      

 

def testcase8():
    '''
    test two browser case, bandwidth change to 1 mbps in 25 sec, then change back to 10 mbps in 60 sec 
    '''
    setLogLevel( 'info' )
    # clear mn
    os.system("sudo mn -c")

    topo = ServerSideLowBandWidthNetworks(s1_s2 = 10, s2_s3 = 10, s2_s4 = 10)
    net = Mininet(topo=topo, link=TCLink, autoSetMacs=True,
           autoStaticArp=True)

    PORT = 8888
    ALPHA = 0.5 
    LOG_FILE = 'log8.log'
    # server_node = 1
    proxy_node = 2
    proxy_timeout = 100
  
    rate_change_delay1 = 25
    rate_change_delay2 = 60

    mbit1 = 1
    mbit2 = 10

    # helper file, write server ip to file
    server_ip_list=[]
    for i in [1]:
        ip = "10.0.0." + str(i)
        server_ip_list.append(ip)
    tmp_file = FileHelper(server_ip_list)
    tmp_file_path = tmp_file.getFilePath()

    # Run network
    net.start()
    
    h1 = net.get("h1")
    h3 = net.get("h3")
    h5 = net.get("h5")
    h2 = net.get("h2")

    h1.cmd("sudo python start_server.py 1")
    h1.cmd("sleep {} && tc qdisc add dev h1-eth0 root tbf rate {}mbit burst 100kbit latency 400ms &"\
        .format(rate_change_delay1, mbit1))
    h1.cmd("sleep {} && tc qdisc change dev h1-eth0 root tbf rate {}mbit burst 100kbit latency 400ms &"\
        .format(rate_change_delay2, mbit2))

    h3.cmd("python firefox_open_url.py 1 10.0.0.{}:{} & "\
        .format(proxy_node, PORT))
    h5.cmd("python firefox_open_url.py 2 10.0.0.{}:{} & "\
        .format(proxy_node, PORT))
    h2.cmd("make clean && make && timeout {} ./miProxy --nodns {} {} {} {}"\
        .format(proxy_timeout, PORT, tmp_file_path, ALPHA, LOG_FILE))
    
    # CLI( net )
    h1.cmd("sudo killall httpd")

    net.stop()  

    tmp_file.close()      


def testcase9():
    '''
    test multiple http server case (SimpleNetwork topology)
    '''
    setLogLevel( 'info' )
    # clear mn
    os.system("sudo mn -c")

    topo = SimpleNetwork(s1_s2 = 10, s2_s3 = 10)
    net = Mininet(topo=topo, link=TCLink, autoSetMacs=True,
           autoStaticArp=True)

    PORT = 8888
    ALPHA = 0.01
    LOG_FILE = 'log9.log'
    proxy_node = 2
    proxy_timeout = 150

    # helper file
    server_ip_list=[]
    for i in [1,4]:
        ip = "10.0.0." + str(i) + "\n"
        server_ip_list.append(ip)
    tmp_file = FileHelper(server_ip_list)
    tmp_file_path = tmp_file.getFilePath()
  
    # Run network
    net.start()
    
    h1 = net.get("h1")
    h2 = net.get("h2")
    h3 = net.get("h3")
    h4 = net.get("h4")
    h5 = net.get("h5")
    h6 = net.get("h6")

    h1.cmd("sudo python start_server.py 1")
    h4.cmd("sudo python start_server.py 4")

    h3.cmd("python firefox_open_url.py 1 10.0.0.{}:{} & "\
        .format(proxy_node, PORT))
    h5.cmd("sleep 10 && python firefox_open_url.py 5 10.0.0.{}:{} & "\
        .format(proxy_node, PORT))
    h6.cmd("sleep 20 && python firefox_open_url.py 6 10.0.0.{}:{} & "\
        .format(proxy_node, PORT))
    
    h2.cmdPrint("make clean && make && timeout {} ./miProxy --nodns {} {} {} {}"\
        .format(proxy_timeout, PORT, tmp_file_path, ALPHA, LOG_FILE))
    

    # CLI( net )
    h1.cmd("sudo killall httpd")

    net.stop()

    tmp_file.close()   


def testcase10():
    '''
    test multiple http server case (SimpleNetwork topology)
    '''
    setLogLevel( 'info' )
    # clear mn
    os.system("sudo mn -c")

    topo = StarfishShapeNetworks()
    # topo = ServerSideLowBandWidthNetworks(s1_s2 = 10, s2_s3 = 10, s2_s4 = 10)
    net = Mininet(topo=topo, link=TCLink, autoSetMacs=True,
           autoStaticArp=True)

    PORT = 8888
    ALPHA = 0.5
    LOG_FILE = 'log10.log'
    proxy_node = 2
    proxy_timeout = 150

    # helper file
    server_ip_list=[]
    for i in [1,4]:
        ip = "10.0.0." + str(i) + "\n"
        server_ip_list.append(ip)
    tmp_file = FileHelper(server_ip_list)
    tmp_file_path = tmp_file.getFilePath()
  
    # Run network
    net.start()
    
    h1 = net.get("h1")
    h2 = net.get("h2")
    h3 = net.get("h3")
    h4 = net.get("h4")
    h5 = net.get("h5")
    h6 = net.get("h6")

    h1.cmd("sudo python start_server.py 1")
    h4.cmd("sudo python start_server.py 4")

    h3.cmd("python firefox_open_url.py 1 10.0.0.{}:{} & "\
        .format(proxy_node, PORT))
    h5.cmd("sleep 20 && python firefox_open_url.py 5 10.0.0.{}:{} & "\
        .format(proxy_node, PORT))
    h6.cmd("sleep 40 && python firefox_open_url.py 6 10.0.0.{}:{} & "\
        .format(proxy_node, PORT))
    
    h2.cmdPrint("make clean && make && timeout {} ./miProxy --nodns {} {} {} {}"\
        .format(proxy_timeout, PORT, tmp_file_path, ALPHA, LOG_FILE))
    

    # CLI( net )
    h1.cmd("sudo killall httpd")

    net.stop()

    tmp_file.close()  

########################################################
########################################################

 


if __name__ == "__main__":
    testcase_list = [
            testcase1, 
            testcase2,
            testcase3,
            testcase4,
            testcase5,
            testcase6,
            testcase7,
            testcase8,
            testcase9,
            testcase10,
            ]
    assert len(sys.argv) == 2, "Argument number error"
    case_idx = int(sys.argv[1]) - 1
    assert 0 <= case_idx <= 9, "Test case number not in 1-10"
    testcase_list[case_idx]()

    