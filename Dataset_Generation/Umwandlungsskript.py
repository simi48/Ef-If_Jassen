for i in range(10000):
    f = open("C:\\Users\\ramon\\DeepJass\\Textfiles\\"+str(i)+ "_scene.txt", "r")
    first= f.readline()
    second = f.readline()
    third = f.readline()
#NUMMER1
    if first[2] == " ":
        XCenter = 100 * float(first[3]) + 10 * float(first[4]) + float(first[5])
        XCenter_new = XCenter/1000
        #print(XCenter_new)

        YCenter = 100 * float(first[7]) + 10 * float(first[8]) + float(first[9])
        YCenter_new = YCenter/1000
        #print(YCenter_new)
    
        width = 100 * float(first[11]) + 10 * float(first[12]) + float(first[13])
        width_new = width/1000
        #print(width_new)
    
        height = 100 * float(first[15]) + 10 * float(first[16]) + float(first[17])
        height_new = height/1000
        #print(height_new)
    

    else:
        XCenter = 100 * float(first[2]) + 10 * float(first[3]) + float(first[4])
        XCenter_new = XCenter/1000
        #print(XCenter_new)
    
        YCenter = 100 * float(first[6]) + 10 * float(first[7]) + float(first[8])
        YCenter_new = YCenter/1000
        #print(YCenter_new)
    
        width = 100 * float(first[10]) + 10 * float(first[11]) + float(first[12])
        width_new = width/1000
        #print(width_new)
    
        height = 100 * float(first[14]) + 10 * float(first[15]) + float(first[16])
        height_new = height/1000
        #print(height_new)

    #NUMMER2
    if second[2] == " ":
        XCenter_2 = 100 * float(second[3]) + 10 * float(second[4]) + float(second[5])
        XCenter_new_2 = XCenter_2/1000
        #print(XCenter_new)

        YCenter_2 = 100 * float(second[7]) + 10 * float(second[8]) + float(second[9])
        YCenter_new_2 = YCenter_2/1000
        #print(YCenter_new)
    
        width_2 = 100 * float(second[11]) + 10 * float(second[12]) + float(second[13])
        width_new_2 = width_2/1000
        #print(width_new)
    
        height_2 = 100 * float(second[15]) + 10 * float(second[16]) + float(second[17])
        height_new_2 = height_2/1000
        #print(height_new)


    else:
        XCenter_2 = 100 * float(second[2]) + 10 * float(second[3]) + float(second[4])
        XCenter_new_2 = XCenter_2/1000
        #print(XCenter_new)
    
        YCenter_2 = 100 * float(second[6]) + 10 * float(second[7]) + float(second[8])
        YCenter_new_2 = YCenter_2/1000
        #print(YCenter_new)
    
        width_2 = 100 * float(second[10]) + 10 * float(second[11]) + float(second[12])
        width_new_2 = width_2/1000
        #print(width_new)
    
        height_2 = 100 * float(second[14]) + 10 * float(second[15]) + float(second[16])
        height_new_2 = height_2/1000
        #print(height_new)      

    #NUMMER3
    if third[2] == " ":
        XCenter_3 = 100 * float(third[3]) + 10 * float(third[4]) + float(third[5])
        XCenter_new_3 = XCenter_3/1000
        #print(XCenter_new)

        YCenter_3 = 100 * float(third[7]) + 10 * float(third[8]) + float(third[9])
        YCenter_new_3 = YCenter_3/1000
        #print(YCenter_new)
    
        width_3 = 100 * float(third[11]) + 10 * float(third[12]) + float(third[13])
        width_new_3 = width_3/1000
        #print(width_new)
    
        height_3 = 100 * float(third[15]) + 10 * float(third[16]) + float(third[17])
        height_new_3 = height_3/1000
        #print(height_new)
    

    else:
        XCenter_3 = 100 * float(third[2]) + 10 * float(third[3]) + float(third[4])
        XCenter_new_3 = XCenter_3/1000
        #print(XCenter_new)
    
        YCenter_3 = 100 * float(third[6]) + 10 * float(third[7]) + float(third[8])
        YCenter_new_3 = YCenter_3/1000
        #print(YCenter_new)
    
        width_3 = 100 * float(third[10]) + 10 * float(third[11]) + float(third[12])
        width_new_3 = width_3/1000
        #print(width_new)
    
        height_3 = 100 * float(third[14]) + 10 * float(third[15]) + float(third[16])
        height_new_3 = height_3/1000
        #print(height_new)


    File = open("C:\\Users\\ramon\\DeepJass\\Textfiles_umgewandelt\\"+str(i)+ "_scene.txt","w")
    if first[2] == " ":
        File.write(""+str(first[0])+str(first[1])+" "+str(XCenter_new)+" "+str(YCenter_new)+" "+str(width_new)+" "+str(height_new)+"\n")
    else:   
        File.write(""+str(first[0])+" "+str(XCenter_new)+" "+str(YCenter_new)+" "+str(width_new)+" "+str(height_new)+"\n")

    if second[2] == " ":
        File.write(""+str(second[0])+str(second[1])+" "+str(XCenter_new_2)+" "+str(YCenter_new_2)+" "+str(width_new_2)+" "+str(height_new_2)+"\n")    
    else:
        File.write(""+str(second[0])+" "+str(XCenter_new_2)+" "+str(YCenter_new_2)+" "+str(width_new_2)+" "+str(height_new_2)+"\n")    

    if third[2] == " ":
        File.write(""+str(third[0])+str(third[1])+" "+str(XCenter_new_3)+" "+str(YCenter_new_3)+" "+str(width_new_3)+" "+str(height_new_3)+"\n")
    else:
        File.write(""+str(third[0])+" "+str(XCenter_new_3)+" "+str(YCenter_new_3)+" "+str(width_new_3)+" "+str(height_new_3)+"\n")    
    
    File.close
    

    