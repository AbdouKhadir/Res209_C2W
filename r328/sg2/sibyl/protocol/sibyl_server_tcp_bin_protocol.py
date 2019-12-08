# -*- coding: utf-8 -*-
from twisted.internet.protocol import Protocol


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
        while len(line)>=6:
            timestamp, length = struct.unpack_from('LH',datagram,0)
            if length= len(line)-6:
                message = struct.unpack_from('{0}s'.format(length-6),datagram,6)
                print('message received', line)
                answer=self.sibylServerProxy.generateResponse(message)
                self.transport.write(answer)
    
            elif length>len(line)-6: 
            
                message = struct.unpack_from('{0}s'.format(len(line)-6),datagram,6)
                return line[6:]
                while len(message)<length:
                    
        

        print('message received', line)
        
        
