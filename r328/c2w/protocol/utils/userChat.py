# -*- coding: utf-8 -*-
class userChat():

    def __init__(self, username, host_port):
       
        self.name=username
        self.host=host_port[0]
        self.port=host_port[1]        
        self.userSeq=1
        self.serverSeq=1
        self.message=[]
        self.numberTransmission=1
        self.idSend=0
        self.error=0
        
        
    def incrementeServerSeq(self):
        if (self.serverSeq<1023):
            self.serverSeq+=1
        else:
            self.serverSeq=1
    
    def incrementeUserSeq(self):
        if (self.userSeq<1023):
            self.userSeq+=1
        else:
            self.serverSeq=1
    
    def addMessage(self, message):
        self.message.append(message)
        
    def delMessage(self):
        del self.message[0]
    
   
