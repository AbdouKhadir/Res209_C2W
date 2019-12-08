# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from utils.sibyl_building import *
import math

class SibylServerTimerUdpBinProtocol(DatagramProtocol):
    """The class implementing the Sibyl UDP binary server protocol.

        .. note::
            You must not instantiate this class.  This is done by the code
            called by the main function.

        .. note::

            You have to implement this class.  You may add any attribute and
            method that you see fit to this class.  You must implement the
            following method (called by Twisted whenever it receives a
            datagram):
            :py:meth:`~sibyl.main.protocol.sibyl_server_udp_bin_protocol.datagramReceived`
            See the corresponding documentation below.

    This class has the following attribute:

    .. attribute:: SibylServerProxy

        The reference to the SibylServerProxy (instance of the
        :py:class:`~sibyl.main.sibyl_server_proxy.SibylServerProxy` class).

            .. warning::

                All interactions between the client protocol and the server
                *must* go through the SibylServerProxy.

    """

    def __init__(self, sibylServerProxy):
        """The implementation of the UDP server text protocol.

        Args:
            sibylServerProxy: the instance of the server proxy.
        """
        self.sibylServerProxy = sibylServerProxy


    def datagramReceived(self, datagram, host_port):
        """Called by Twisted whenever a datagram is received

        Twisted calls this method whenever a datagram is received.

        Args:
            datagram (bytes): the payload of the UPD packet;
            host_port (tuple): the source host and port number.

            .. warning::
                You must implement this method.  You must not change the
                parameters, as Twisted calls it.

        """
        def treatment(buff, host_port):
            
            self.transport.write(building(buff[0],self.sibylServerProxy.generateResponse(buff[2].decode('utf-8'))),(host_port[0], host_port[1]))
            #self.transport.write(buf,(host_port[0], host_port[1])) #envoi de la réponse

        #header=struct.unpack_from('IH',datagram) #récupération de la date et de la taille
        #question=struct.unpack_from('{0}s'.format(header[1]-6),datagram,6) #décodage pour récupérer la question
        #print("question={0}".format(question[0].decode('utf-8')))
        #response="{0}: ".format(header[0]) + self.sibylServerProxy.generateResponse(question[0].decode('utf-8')) +"\r\n"; #génération de la réponse à partir de la question 
        #taille=4+2+len(response.encode('utf-8')) #taille en octet      
        #buf=struct.pack('IH{0}s'.format(len(response.encode('utf-8'))),header[0],taille,response.encode('utf-8')) #codage en binaire de la réponse
        buff=decoding(datagram)
        delay=math.log(len(buff[2].decode('utf-8')))
        reactor.callLater(delay, treatment, buff, host_port)
        
        
        pass
    
