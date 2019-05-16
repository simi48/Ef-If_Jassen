Startwert = 7500
Endwert = 9999
f = open("C:\\Users\\ramon\\darknet\\build\\darknet\\x64\\data\\validate.txt","w")
for i in range(Startwert, Endwert):
    f.write("data/obj/"+str(i)+"_scene.jpg"+"\n")