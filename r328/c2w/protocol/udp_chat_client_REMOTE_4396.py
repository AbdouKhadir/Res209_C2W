# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from c2w.main.lossy_transport import LossyTransport
import logging
from c2w.main.constants import ROOM_IDS
from c2w.protocol.utils.encode import encoder
from c2w.protocol.utils.decode import decoder
import time


logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.udp_chat_client_protocol')


class c2wUdpChatClientProtocol(DatagramProtocol):

    def __init__(self, serverAddress, serverPort, clientProxy, lossPr):
        """
        :param serverAddress: The IP address (or the name) of the c2w server,
            given by the user.
        :param serverPort: The port number used by the c2w server,
            given by the user.
        :param clientProxy: The clientProxy, which the protocol must use
            to interact with the Graphical User Interface.

        Class implementing the UDP version of the client protocol.

        .. note::
            You must write the implementation of this class.

        Each instance must have at least the following attributes:

        .. attribute:: serverAddress

            The IP address of the c2w server.

        .. attribute:: serverPort

            The port number of the c2w server.

        .. attribute:: clientProxy

            The clientProxy, which the protocol must use
            to interact with the Graphical User Interface.

        .. attribute:: lossPr

            The packet loss probability for outgoing packets.  Do
            not modify this value!  (It is used by startProtocol.)

        .. note::
            You must add attributes and methods to this class in order
            to have a working and complete implementation of the c2w
            protocol.
        """

        #: The IP address of the c2w server.
        self.serverAddress = serverAddress
        #: The port number of the c2w server.
        self.serverPort = serverPort
        #: The clientProxy, which the protocol must use
        #: to interact with the Graphical User Interface.
        self.clientProxy = clientProxy
        self.lossPr = lossPr
        self.seq = 1
        self.tailleHeader = 4
        self.dicoFilm={}  # dictionnaire {Id:titreFilm,.....} ex:{"5":"Big Bunny",....}
        #Useful for the programming of the send & wait policy
        self.compteurSAW = 0
        self.Ackrecieved = False 
        self.user="" # le nom d utilisateur que le client va utiliser: ca ne changera pas 
        self.deco=-1
        
    def incrementeSeq(self):
        if (self.seq<1023):
            self.seq+=1
        else:
            self.seq = 1

        
    def writingMessage(self,Liste):
            """
            Will be used for the function in the reactors. The reactor function callLater() has 3 arguments. Delay, the function to call and its argument
            It is thus easier to use function with only one argument for callLater
            """
            [message,(adresse,port)]=Liste
            self.transport.write(message, (adresse,port))


    def sendAndWait(self, message):
    
        #on initialise la variable qui va être appelée par la fonction callLater
        ListeArg =[message,(self.serverAddress, self.serverPort)]
        
        #on initialise les deux callLater qui vont être utilisées au cas où
        callServer = reactor.callLater(1,self.writingMessage,ListeArg)
        message = ListeArg[0]
        RerunFunction = reactor.callLater(1,self.sendAndWait,message)
                    
        if self.compteurSAW == 10:
            #notifier le serveur avec un message d'erreur
            print("warning, didn't recieved any message of the following type:",str(63))
        
        else:
            if self.AckRecieved == False:
                #si aucun message de type 63 n'est reçu, on en renvoie un 
                self.compteurSAW+=1
                print("compteurSAW =",self.compteurSAW,"at time:",time.time()) 
                reactor.run()
            else:
                print("compteurSAW =",self.compteurSAW,"at time:",time.time())
                #une fois que cela s'est fait, on arrete les envois en boucles.
                callServer.cancel()
                RerunFunction.cancel()
                #on réinitialise l'attribut AckRecieved
                self.AckRecieved = False
                pass



    def startProtocol(self):
        """
        DO NOT MODIFY THE FIRST TWO LINES OF THIS METHOD!!

        If in doubt, do not add anything to this method.  Just ignore it.
        It is used to randomly drop outgoing packets if the -l
        command line option is used.
        """
        self.transport = LossyTransport(self.transport, self.lossPr)
        DatagramProtocol.transport = self.transport

    def sendLoginRequestOIE(self, userName):
		#"""
		#:param string userName: The user name that the user has typed.
		#The client proxy calls this function when the user clicks on
		#the login button.
		#"""
        moduleLogger.debug('loginRequest called with username=%s', userName)
        dico={}
        dico["taille"]=self.tailleHeader+len(userName)
        dico["Type"]=1
        dico["seq"]=self.seq
        dico["user"]=userName
        self.user=userName
        connexionRq=encoder(dico)
        self.transport.write(connexionRq,(self.serverAddress, self.serverPort))

        #sendAndWait(connexionRq)





    def sendChatMessageOIE(self, message):
        """
        :param message: The text of the chat message.
        :type message: string

        Called by the client proxy  when the user has decided to send
        a chat message

        .. note::
           This is the only function handling chat messages, irrespective
           of the room where the user is.  Therefore it is up to the
           c2wChatClientProctocol or to the server to make sure that this
           message is handled properly, i.e., it is shown only by the
           client(s) who are in the same room.
        """
        #on prépare le message pour l'envoie au serveur
        dicoMessage = {}
        dicoMessage["taille"] = self.tailleHeader+len(message)
        dicoMessage["Type"] = 5
        dicoMessage["seq"] = self.seq
        dicoMessage["message"] = message
        msgchat = encoder(dicoMessage)
        self.transport.write(msgchat,(self.serverAddress, self.serverPort))
        #on applique la politique de send-and-wait
        self.sendAndWait(msgchat)
        #une fois que le serveur a acquitté, on attends la liste de film

        pass

    def sendJoinRoomRequestOIE(self, roomName):
        """
        :param roomName: The room name (or movie title.)

        Called by the client proxy  when the user
        has clicked on the watch button or the leave button,
        indicating that she/he wants to change room.

        .. warning:
            The controller sets roomName to
            c2w.main.constants.ROOM_IDS.MAIN_ROOM when the user
            wants to go back to the main room.
        """
        #on prépare le message pour l'envoie au serveur
        #print("roomname={0}".format(roomName))
        dicoRequete = {}
        dicoRequete["taille"] = self.tailleHeader+1
        dicoRequete["Type"] = 6
        dicoRequete["seq"] = self.seq
        if roomName == ROOM_IDS.MAIN_ROOM:
            dicoRequete["Id"] = 0
        else:
            for Id,nom in self.dicoFilm.items():
                if nom==roomName:
                    dicoRequete["Id"] = int(Id)
        joindreRq = encoder(dicoRequete)
        #sendAndWait(joindreRq)
        self.transport.write(joindreRq,(self.serverAddress, self.serverPort))


        pass

    def sendLeaveSystemRequestOIE(self):
        """
        Called by the client proxy  when the user
        has clicked on the leave button in the main room.
        """
        logoutDico={}
        logoutDico["taille"]=self.tailleHeader
        logoutDico["Type"]=9
        logoutDico["seq"]=self.seq
        paquet=encoder(logoutDico)
        self.deco=self.seq
        self.transport.write(paquet,(self.serverAddress, self.serverPort))

        pass


    def sendAcknowledgeOIE(self, ackSeq): #ackSeq est la sequence contenue dans le message à acquitter
        """
        Send an aknowledgment message
        """
        ackDico={}
        ackDico["taille"]=self.tailleHeader
        ackDico["Type"]=63
        ackDico["seq"]=ackSeq
        ackDatagram=encoder(ackDico)
        self.transport.write(ackDatagram,(self.serverAddress, self.serverPort))

    def datagramReceived(self, datagram, host_port): # a finir
        """
        :param string datagram: the payload of the UDP packet.
        :param host_port: a touple containing the source IP address and port.

        Called **by Twisted** when the client has received a UDP
        packet.
        """
        messageDico = decoder(datagram)
        Type = messageDico.get("Type")
        ##if Type!=63: #il faut acquitter tous les paquets sauf un acquittement


        if Type==2: #le datagram contient la liste des films

            self.movieList=[]
            i=0
            while "taille{0}".format(i) in messageDico:
                #print(messageDico)
                tupleTemporaire=(str(messageDico["nom{}".format(i)]),str(messageDico["ip{}".format(i)]),str(messageDico["port{}".format(i)]))
                self.movieList.append(tupleTemporaire)
                self.dicoFilm["{0}".format(messageDico["Id{}".format(i)])]=messageDico["nom{0}".format(i)]
                print(self.dicoFilm)
                i+=1
            ackSeq=messageDico["seq"]
            self.sendAcknowledgeOIE(ackSeq)

        if Type==3: #Le datagram contient la liste des utilisateurs
            self.userList=[(self.user,ROOM_IDS.MAIN_ROOM)]
            i=0
            while "taille{0}".format(i) in messageDico:
                if messageDico["Id{0}".format(i)]==0:
                    roomName=ROOM_IDS.MAIN_ROOM
                else:
                    roomId=messageDico["Id{0}".format(i)]  #roomId est un str contenant un decimal: ex  "5"
                    roomName=self.dicoFilm["{0}".format(roomId)]
                tupleTemporaire=(str(messageDico["user{0}".format(i)]),roomName)
                print("tupletemporaire={0}".format(tupleTemporaire))
                self.userList.append(tupleTemporaire)
                i+=1
            #print(self.userList)
            #print(self.movieList)
            ackSeq=messageDico["seq"]  #pour l'acquittement du datagram
            self.sendAcknowledgeOIE(ackSeq)

            self.clientProxy.initCompleteONE(self.userList, self.movieList)

        if Type==4: # le datagram est une MAJ utilisateur
            #print("entree type 4")
            roomId=messageDico["Id"]
            userName=messageDico["user"]

            if roomId==0:
                roomName=ROOM_IDS.MAIN_ROOM
            else:                          #chercher le titre du Film associé à cet Id (et pas le nom générique ROOM_IDS.MOVIE_ROOM)
                for Id,nom in self.dicoFilm.items():
                    if int(Id)==roomId:
                        roomName= nom
                #roomName=ROOM_IDS.MOVIE_ROOM
            for Tuple in self.userList:
                if Tuple[0]==userName:
                    self.userList[self.userList.index(Tuple)][1]=roomName
            #self.setUserListONE(self.userList)
            self.clientProxy.userUpdateReceivedONE(userName, roomName)

            ackSeq=messageDico["seq"]  #pour l'acquittement du datagram
            self.sendAcknowledgeOIE(ackSeq)

        if Type==7: #  inscription acceptee
            #self.clientProxy.joinRoomOKONE() #charger l interface graphique
            #ackSeq=messageDico["seq"]  #pour l'acquittement du datagram
            #self.sendAcknowledgeOIE(ackSeq)
            pass

        if Type==8: # error: inscription refusee
            errorCode=messageDico["erreur"]
            if errorCode==1:
                self.clientProxy.connectionRejectedONE("nom d'utilisateur déjà utilisé")
            elif errorCode==2:
                self.clientProxy.connectionRejectedONE("nom d'utilisateur dépassant 254 octets")
            elif errorCode==3:
                self.clientProxy.connectionRejectedONE("nom d'utilisateur contenant un ou plusieurs espaces")

            ackSeq=messageDico["seq"]  #pour l'acquittement du datagram
            self.sendAcknowledgeOIE(ackSeq)

        if Type==10: #recevoir un message de chat des autres utilisateurs
            if not messageDico["user"]==self.user:
                rUserName=messageDico["user"]
                message=messageDico["message"]
                self.clientProxy.chatMessageReceivedONE(rUserName, message)

            ackSeq=messageDico["seq"]  #pour l'acquittement du datagram
            self.sendAcknowledgeOIE(ackSeq)

            ackSeq=messageDico["seq"]  #pour l'acquittement du datagram
            self.sendAcknowledgeOIE(ackSeq)

        if Type==11: # ack: connexion a une salle réussie
            self.clientProxy.joinRoomOKONE()

            ackSeq=messageDico["seq"]  #pour l'acquittement du datagram
            self.sendAcknowledgeOIE(ackSeq)

        if Type==12: # ack: connexion a une salle echouee ou rejetee
            ackSeq=messageDico["seq"]  #pour l'acquittement du datagram
            self.sendAcknowledgeOIE(ackSeq)

            self.clientProxy.connectionRejectedONE("Echec: veuillez vous reconnecter") #message erreur + reouverture de l interface pour une nouvelle tentative
        
        if Type==63:
            if self.deco==-1:
                self.AckRecieved = True
                #on incrémente le numéro de séquence
                self.incrementeSeq()
            else:
                self.clientProxy.leaveSystemOKONE()


        return messageDico
