import encode
import decode

inscription={}
inscription["taille"]=9
inscription["seq"]=1
inscription["Type"]=1
inscription["user"]="Alice"


film={}
film["taille"]=32
film["seq"]=1
film["Type"]=2
film["taille0"]=13
film["ip0"]="192.168.1.1"
film["port0"]=8888
film["Id0"]=25
film["nom0"]="Taken"
film["taille1"]=15
film["ip1"]="192.168.1.2"
film["port1"]=8889
film["Id1"]=27
film["nom1"]="Taken23"

user={}
user["taille"]=16
user["seq"]=1
user["Type"]=3
user["taille0"]=7
user["Id0"]=25
user["user0"]="Alice"
user["taille1"]=5
user["Id1"]=27
user["user1"]="Bob"

maj_user={}
maj_user["taille"]=10
maj_user["seq"]=1
maj_user["Type"]=4
maj_user["Id"]=25
maj_user["user"]="Alice"


message={}
message["taille"]=36
message["seq"]=1
message["Type"]=5
message["message"]="Test de message envoye par alice"

joindre_salon={}
joindre_salon["taille"]=125
joindre_salon["seq"]=1
joindre_salon["Type"]=6
joindre_salon["Id"]=75

inscription_ok={}
inscription_ok["taille"]=125
inscription_ok["seq"]=1
inscription_ok["Type"]=7

erreur={}
erreur["taille"]=125
erreur["seq"]=1
erreur["Type"]=8
erreur["erreur"]=3

desinscription={}
desinscription["taille"]=125
desinscription["seq"]=1
desinscription["Type"]=9

redir={}
redir["taille"]=55
redir["seq"]=1
redir["Type"]=10
redir["size"]=7
redir["user"]="Patrick"
redir["message"]="Redirection d'un message envoye par Patrick"


joindre_salon_ok={}
joindre_salon_ok["taille"]=125
joindre_salon_ok["seq"]=1
joindre_salon_ok["Type"]=11

joindre_salon_nok={}
joindre_salon_nok["taille"]=125
joindre_salon_nok["seq"]=1
joindre_salon_nok["Type"]=12

ack={}
ack["taille"]=125
ack["seq"]=1
ack["Type"]=63

print("---------- TEST TYPE 1 ----------\n")
print(inscription)
test1=encode.encoder(inscription)
print("\n{0}\n".format(test1))
test1bis=decode.decoder(test1)
print(test1bis)
print("\n---------- TEST TYPE 2 ----------\n")
print(film)
test2=encode.encoder(film)
print("\n{0}\n".format(test2))
test2bis=decode.decoder(test2)
print(test2bis)
print("\n---------- TEST TYPE 3 ----------\n")
print(user)
test3=encode.encoder(user)
print("\n{0}\n".format(test3))
test3bis=decode.decoder(test3)
print(test3bis)
print("\n---------- TEST TYPE 4 ----------\n")
print(maj_user)
test4=encode.encoder(maj_user)
print("\n{0}\n".format(test4))
test4bis=decode.decoder(test4)
print(test4bis)
print("\n---------- TEST TYPE 5 ----------\n")
print(message)
test5=encode.encoder(message)
print("\n{0}\n".format(test5))
test5bis=decode.decoder(test5)
print(test5bis)
print("\n---------- TEST TYPE 6 ----------\n")
print(joindre_salon)
test6=encode.encoder(joindre_salon)
print("\n{0}\n".format(test6))
test6bis=decode.decoder(test6)
print(test6bis)
print("\n---------- TEST TYPE 7 ----------\n")
print(inscription_ok)
test7=encode.encoder(inscription_ok)
print("\n{0}\n".format(test7))
test7bis=decode.decoder(test7)
print(test7bis)
print("\n---------- TEST TYPE 8 ----------\n")
print(erreur)
test8=encode.encoder(erreur)
print("\n{0}\n".format(test8))
test8bis=decode.decoder(test8)
print(test8bis)
print("\n---------- TEST TYPE 9 ----------\n")
print(desinscription)
test9=encode.encoder(desinscription)
print("\n{0}\n".format(test9))
test9bis=decode.decoder(test9)
print(test9bis)
print("\n---------- TEST TYPE 10 ----------\n")
print(redir)
test10=encode.encoder(redir)
print("\n{0}\n".format(test10))
test10bis=decode.decoder(test10)
print(test10bis)
print("\n---------- TEST TYPE 11 ----------\n")
print(joindre_salon_ok)
test11=encode.encoder(joindre_salon_ok)
print("\n{0}\n".format(test11))
test11bis=decode.decoder(test11)
print(test11bis)
print("\n---------- TEST TYPE 12 ----------\n")
print(joindre_salon_nok)
test12=encode.encoder(joindre_salon_nok)
print("\n{0}\n".format(test12))
test12bis=decode.decoder(test12)
print(test12bis)
print("\n---------- TEST TYPE 63 ----------\n")
print(ack)
test63=encode.encoder(ack)
print("\n{0}\n".format(test63))
test63bis=decode.decoder(test63)
print(test63bis)
