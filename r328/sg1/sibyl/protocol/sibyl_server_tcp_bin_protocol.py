# -*- coding: utf-8 -*-
from twisted.internet.protocol import Protocol
from utils.sibyl_building import *
import time

class SibylServerTcpBinProtocol(Protocol):
    """The class implementing the Sibyl TCP binary server protocol.

        .. note::
            You must not instantiate this class.  This is done by the code
            called by the main function.

        .. note::

            You have to implement this class.  You may add any attribute and
            method that you see fit to this class.  You must implement the
            following method (called by Twisted whenever it receives data):
            :py:meth:`~sibyl.main.protocol.sibyl_server_tcp_bin_protocol.dataReceived`
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
        self.buf=b''

    def dataReceived(self, line):
        """Called by Twisted whenever a data is received

        Twisted calls this method whenever it has received at least one byte
        from the corresponding TCP connection.

        Args:
            line (bytes): the data received (can be of any length greater than
            one);

        .. warning::
            You must implement this method.  You must not change the parameters,
            as Twisted calls it.

        """
        
        
        self.buf=self.buf+line #concatener self.buf et line
        #print(self.buf)
        #print (line)
        #print (len(self.buf))
        while(len(self.buf)>=6): #si self.buf contient au moins une en-tete
            #print ("enter while")
            #print(self.buf)
            #print (len(self.buf))
            taille=header(self.buf)[1]
            #print ("header ok")
            #print (taille)
            if(taille==len(self.buf)): #si la taille presente dans l'en-tete est la meme que la taille de self.buf
                self.transport.write(building(decoding(self.buf)[0],self.sibylServerProxy.generateResponse(decoding(self.buf)[2].decode('utf-8')))) #renvoyer le message sans aucune autre action
                self.buf=b''
                #print("OK1")
            elif(taille>len(self.buf)): #si la taille presente dans l'en-tete est plus grande que la taille de self.buf...
                self.buf=self.buf+line #concatener self.buf et self.buf
                #print("OK2")
                break
            elif(taille<len(self.buf)): #si la taille presente dans l'en-tete est plus petite que la taille de self.buf ...
                self.transport.write(building(decoding(self.buf)[0],self.sibylServerProxy.generateResponse(decoding(self.buf)[2].decode('utf-8')))) #... décoder un message complet de la taille de "taille"
                self.buf=self.buf[taille:] #placer le reste dans le buffer
                #print("OK3")
        pass
