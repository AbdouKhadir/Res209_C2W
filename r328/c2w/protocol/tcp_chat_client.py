# -*- coding: utf-8 -*-
from twisted.internet.protocol import Protocol
import logging
from c2w.protocol.utils.encode import encoder
from c2w.protocol.utils.decode import decoder
from c2w.protocol.utils.framing import framing
from c2w.main.constants import ROOM_IDS
from twisted.internet import reactor

logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.tcp_chat_client_protocol')


class c2wTcpChatClientProtocol(Protocol):

    def __init__(self, clientProxy, serverAddress, serverPort):
        """
        :param clientProxy: The clientProxy, which the protocol must use
            to interact with the Graphical User Interface.
        :param serverAddress: The IP address (or the name) of the c2w server,
            given by the user.
        :param serverPort: The port number used by the c2w server,
            given by the user.

        Class implementing the UDP version of the client protocol.

        .. note::
            You must write the implementation of this class.

        Each instance must have at least the following attribute:

        .. attribute:: clientProxy

            The clientProxy, which the protocol must use
            to interact with the Graphical User Interface.

        .. attribute:: serverAddress

            The IP address of the c2w server.

        .. attribute:: serverPort

            The port number used by the c2w server.

        .. note::
            You must add attributes and methods to this class in order
            to have a working and complete implementation of the c2w
            protocol.
        """

        #: The IP address of the c2w server.
        self.serverAddress = serverAddress
        #: The port number used by the c2w server.
        self.serverPort = serverPort
        #: The clientProxy, which the protocol must use
        #: to interact with the Graphical User Interface.
        self.clientProxy = clientProxy
        self.seq = 1
        self.tailleHeader = 4
        self.dicoFilm={}  # dictionnaire {Id:titreFilm,.....} ex:{"5":"Big Bunny",....}
        self.compteurSAW = 0 #Useful for the programming of the send & wait policy
        self.user="" # le nom d utilisateur que le client va utiliser: ca ne changera pas 
        self.deco=-1 #pour savoir si le dernier message envoyé est une déconnexion totale du système
        self.fram = b''
        self.initComplete=0
        
    def incrementeSeq(self):
        if (self.seq<1023):
            self.seq+=1
        else:
            self.seq = 1
            
    def sendAndWait(self, message):
        """
        Takes in parameter :
            - the name of the concerned user
            
        Sets the SendAndWait functionality : it sends the message every second
        
        """
        if(self.compteurSAW<10):
            
            #send=encoder(user.message[0])
            print("compteur = {0}".format(self.compteurSAW))
            print("{0} envoie: {1}".format(self.user,decoder(message)))
            self.transport.write(message)
            self.compteurSAW+=1
            self.RerunFunction = reactor.callLater(1,self.sendAndWait,message)
            #reactor.run()
        else:
            print("la valeur max du compteur est atteinte, message non transmis")
            #self.RerunFunction.cancel()
            self.compteurSAW=0
            
    def sendLoginRequestOIE(self, userName):
        """
        :param string userName: The user name that the user has typed.

        The client proxy calls this function when the user clicks on
        the login button.
        """
        moduleLogger.debug('loginRequest called with username=%s', userName)
        dico={}
        dico["taille"]=self.tailleHeader+len(userName.encode('utf-8'))
        dico["Type"]=1
        dico["seq"]=self.seq
        dico["user"]=userName
        self.user=userName
        connexionRq=encoder(dico)
        self.sendAndWait(connexionRq)
        
    def sendChatMessageOIE(self, message):
        """
        :param message: The text of the chat message.
        :type message: string

        Called by the client proxy when the user has decided to send
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
        dicoMessage["taille"] = self.tailleHeader+len(message.encode('utf-8'))
        dicoMessage["Type"] = 5
        dicoMessage["seq"] = self.seq
        dicoMessage["message"] = message
        msgchat = encoder(dicoMessage)
        self.sendAndWait(msgchat)
        
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
        
        dicoRequete = {}
        dicoRequete["taille"] = self.tailleHeader+1
        dicoRequete["Type"] = 6
        dicoRequete["seq"] = self.seq
        if roomName == ROOM_IDS.MAIN_ROOM:#if the user wants to go to the main room, the room ID is set to 0
            dicoRequete["Id"] = 0
        else:#we have to find the room ID which corresponds to the given roomName.
            for Id,nom in self.dicoFilm.items():# in order to do this, we can use the attibute "dicoFilm", a dictionnary with (str(roomID), roomName) as items
                if nom==roomName:
                    dicoRequete["Id"] = int(Id)
        joindreRq = encoder(dicoRequete)
        self.sendAndWait(joindreRq)

        pass

    def sendLeaveSystemRequestOIE(self):
        """
        Called by the client proxy  when the user
        has clicked on the leave button in the main room.
        """
        #on prépare le message pour l'envoie au serveur
        
        logoutDico={}
        logoutDico["taille"]=self.tailleHeader
        logoutDico["Type"]=9
        logoutDico["seq"]=self.seq
        paquet=encoder(logoutDico)
        self.deco=self.seq
        self.sendAndWait(paquet)

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
        print("{0} envoie un ack de sequence: {1}".format(self.user, ackSeq))
        self.transport.write(ackDatagram)

    def dataReceived(self, data):
        """
        :param data: The data received from the client (not necessarily
                     an entire message!)

        Twisted calls this method whenever new data is received on this
        connection.
        """
        self.fram+=data #un buffer ou on stocke tous les paquets arrivant
        
        datagram=framing(self.fram) #datagram est un tuple à 2 elements: (données incompletes ou en excès à traiter plus tard, message complet à traiter immédiatement)
        
        while (datagram[1]!=b''): #tant qu'il y a un message complet, le décoder et le traiter
     
            
            messageDico = decoder(datagram[1])#The complete message's fields are decoded in a dictionnary (messageDico)
            print("{0} recoit : {1}".format(self.user,messageDico))
            Type = messageDico.get("Type")
 
            if Type==2: #le datagram contient la liste des films

                self.movieList=[]#list of 3-elements-Tuples [(filmName,filmIpAdresse,filmPort)...]. used by the client Proxy (initCompleteONE()) to display the available movies
                i=0
                while "taille{0}".format(i) in messageDico:#to fill in the movieList and the dicoFilm dictionnary
                    #print(messageDico)
                    tupleTemporaire=(str(messageDico["nom{}".format(i)]),str(messageDico["ip{}".format(i)]),str(messageDico["port{}".format(i)]))
                    self.movieList.append(tupleTemporaire)
                    self.dicoFilm["{0}".format(messageDico["Id{}".format(i)])]=messageDico["nom{0}".format(i)] #ex: dicoFilm={"5":'Big Buck Bunny',..... }
                    #print(self.dicoFilm)
                    i+=1
                ackSeq=messageDico["seq"]#pour l'acquittement du datagram
                self.sendAcknowledgeOIE(ackSeq)

            if Type==3: #Le datagram contient la liste des utilisateurs
                self.userList=[] #list of 2-elements-Tuples [(userName,movieTitle)...]. used by the client Proxy (initCompleteONE()) to display the online users
                i=0
                while "taille{0}".format(i) in messageDico:#to fill in the userList
                    if messageDico["Id{0}".format(i)]==0:
                        roomName=ROOM_IDS.MAIN_ROOM
                    else:#find the movieTitle which matches the room ID of each client
                        roomId=messageDico["Id{0}".format(i)]  #roomId est un str contenant un decimal: ex  "5"
                        roomName=self.dicoFilm["{0}".format(roomId)]
                    tupleTemporaire=(str(messageDico["user{0}".format(i)]),roomName)
                    #print("tupletemporaire={0}".format(tupleTemporaire))
                    self.userList.append(tupleTemporaire)
                    i+=1
                #print(self.userList)
                #print(self.movieList)
                ackSeq=messageDico["seq"]  #pour l'acquittement du datagram
                self.sendAcknowledgeOIE(ackSeq)
                if self.initComplete==0:
                    print("j appelle initCompleteONE()")
                    self.initComplete=1
                    self.clientProxy.initCompleteONE(self.userList, self.movieList) #affiche les listes des films disponibles et des utilisateurs connectes
                    

            if Type==4: # le datagram est une MAJ utilisateur
            
                roomId=messageDico["Id"]
                userName=messageDico["user"]

                if roomId==0:#l'utilisateur veualler dans la salle principale
                    roomName=ROOM_IDS.MAIN_ROOM
                elif roomId==255:#deconnexion totale du systeme
                    roomName=ROOM_IDS.OUT_OF_THE_SYSTEM_ROOM
                else: # l' utilisateur veut aller dans une movieRoom spécifique   
                    for Id,nom in self.dicoFilm.items():#chercher le titre du Film associé à cet Id (et pas le nom générique ROOM_IDS.MOVIE_ROOM)
                        if int(Id)==roomId:
                            roomName= nom
                self.clientProxy.userUpdateReceivedONE(userName, roomName)#MAJ la list des utilisateurs dans le systeme et la modifier sur l'interface graphique

                ackSeq=messageDico["seq"]  #pour l'acquittement du datagram
                self.sendAcknowledgeOIE(ackSeq)

            if Type==7: #  inscription acceptee
                ackSeq=messageDico["seq"]  #pour l'acquittement du datagram
                self.sendAcknowledgeOIE(ackSeq)
            

            if Type==8: # error: inscription refusee
                errorCode=messageDico["erreur"]# recuperer le code erreur contenu dans le message et informer le client selon la valeur du code
                if errorCode==1:
                    self.clientProxy.connectionRejectedONE("nom d'utilisateur déjà utilisé")
                elif errorCode==2:
                    self.clientProxy.connectionRejectedONE("nom d'utilisateur dépassant 254 octets")
                elif errorCode==3:
                    self.clientProxy.connectionRejectedONE("nom d'utilisateur contenant un ou plusieurs espaces")

                ackSeq=messageDico["seq"]  #pour l'acquittement du datagram
                self.sendAcknowledgeOIE(ackSeq)

            if Type==10: #recevoir un message de chat des autres utilisateurs
                if not messageDico["user"]==self.user:#Pour ne pas afficher un message dont le client est l'auteur
                    rUserName=messageDico["user"]
                    message=messageDico["message"]
                    self.clientProxy.chatMessageReceivedONE(rUserName, message)#afficher le message sur l'interface graphique avec son auteur

                ackSeq=messageDico["seq"]  #pour l'acquittement du datagram
                self.sendAcknowledgeOIE(ackSeq)

           

            if Type==11: #demande de connexion a une salle acceptee par le serveur
                self.clientProxy.joinRoomOKONE()#commander la connection de l'interface graphique à la salle de film que j'ai demandée

                ackSeq=messageDico["seq"]  #pour l'acquittement du datagram
                self.sendAcknowledgeOIE(ackSeq)

            if Type==12: #demande de connexion a une salle rejetee par le serveur
                ackSeq=messageDico["seq"]  #pour l'acquittement du datagram
                self.sendAcknowledgeOIE(ackSeq)

                self.clientProxy.connectionRejectedONE("Echec: veuillez vous reconnecter") #message erreur + reouverture de l interface pour une nouvelle tentative
        
            if Type==63:
                if messageDico["seq"]==self.seq: #le message recu est bien un ack à mon dernier message
                    self.RerunFunction.cancel() # arreter le renvoi programmé dans la methode sendAndWait
                    if self.deco==self.seq: # si mon dernier message était une deconnexion totale
                        self.clientProxy.leaveSystemOKONE() #fermer l interface graphique
                    
                    self.incrementeSeq()# N incrementer la sequence que si j'ai recu le bon acquittement
                    self.compteurSAW=0 #Reinitialise le compteur du sensAndWait
            self.fram=datagram[0]
            datagram=framing(self.fram)
            
