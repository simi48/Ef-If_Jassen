Anfangswert = 57200
Endwert = 87000
f = open("C:\\Users\\ramon\\darknet\\build\\darknet\\x64\\data\\train.txt","w")
for i in range(Anfangswert, Endwert):
    f.write("data/obj/"+str(i)+"_scene.jpg"+"\n")