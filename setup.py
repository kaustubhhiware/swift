#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

class SingleSwitchTopo( Topo ):
	"Single switch connected to n hosts and one server."
	def build( self, n=4 ):
		switch = self.addSwitch( 's1' )
		hs = self.addHost('hs', cpu=.5/(n+1))
		self.addLink(hs, switch)
		for h in range(n):
			# Each host gets 50%/n of system CPU
			host = self.addHost( 'h%s' % (h + 1),
							cpu=.5/(n+1) )
			self.addLink( host, switch)

topos = {'topo' : (lambda: SingleSwitchTopo())}
# def perfTest():
# 	"Create network and run simple performance test"
# 	topo = SingleSwitchTopo( n=4 )
# 	net = Mininet( topo=topo,host=CPULimitedHost, link=TCLink )
# 	net.start()
# 	# print "Dumping host connections"
# 	dumpNodeConnections( net.hosts )
# 	print("Testing network connectivity")
# 	net.pingAll()
# 	print("Testing bandwidth between h1 and h4")
# 	h1, h4, hs = net.get( 'h1', 'h4' , 'hs')
# 	net.iperf( (h1, h4) )
# 	net.iperf( (h1, hs) )



# 	# net.stop()

# if __name__ == '__main__':
# 	setLogLevel( 'info' )
# 	topo = SingleSwitchTopo( n=4 )
# 	net = Mininet( topo=topo,
# 			   host=CPULimitedHost, link=TCLink )
# 	net.start()
# 	h1, h4, hs = net.get( 'h1', 'h4' , 'hs')

# 	# perfTest()
