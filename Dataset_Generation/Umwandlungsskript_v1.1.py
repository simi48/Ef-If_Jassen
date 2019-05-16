AnzahlBilder = 49430
for i in range(AnzahlBilder):
    f = open("C:\\Users\\ramon\\Downloads\\darknet-master\\darknet-master\\build\\darknet\\x64\\data\\obj\\"+str(i)+ "_scene.txt", "r")
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
            
        if first[13]!=" ":
            width = 100 * float(first[11]) + 10 * float(first[12]) + float(first[13])
            width_new = width/1000
            #print(width_new)
            if first[17] == "0" or first[17] == "1" or first[17] == "2" or first[17] == "3" or first[17] == "4" or first[17] == "5" or first[17] == "6" or first[17] == "7" or first[17] == "8" or first[17] == "9":
                height = 100 * float(first[15]) + 10 * float(first[16]) + float(first[17])
                height_new = height/1000
                #print(height_new)
            else:
                height = 10 * float(first[15]) + float(first[16])
                height_new = height/1000
                #print(height_new)
        else:
            width = 10 * float(first[11]) + float(first[12])
            width_new = width/1000
            
            height = 100 * float(first[14]) + 10 * float(first[15]) + float(first[16])
            height_new = height/1000
            #print(height_new)
            
            

    else:
        XCenter = 100 * float(first[2]) + 10 * float(first[3]) + float(first[4])
        XCenter_new = XCenter/1000
        #print(XCenter_new)
        YCenter = 100 * float(first[6]) + 10 * float(first[7]) + float(first[8])
        YCenter_new = YCenter/1000
        #print(YCenter_new)
        if first[12]!=" ":
            width = 100 * float(first[10]) + 10 * float(first[11]) + float(first[12])
            width_new = width/1000
            #print(width_new)
            if first[16] == "0" or first[16] == "1" or first[16] == "2" or first[16] == "3" or first[16] == "4" or first[16] == "5" or first[16] == "6" or first[16] == "7" or first[16] == "8" or first[16] == "9":
                height = 100 * float(first[14]) + 10 * float(first[15]) + float(first[16])
                height_new = height/1000
                #print(height_new)
            else:
                height = 10 * float(first[14]) + float(first[15])
                height_new = height/1000
                #print(height_new)
        else:
            width = 10 * float(first[10]) + float(first[11])
            width_new = width/1000
            
            height = 100 * float(first[13]) + 10 * float(first[14]) + float(first[15])
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
        if second[13]!=" ":
            width_2 = 100 * float(second[11]) + 10 * float(second[12]) + float(second[13])
            width_new_2 = width_2/1000
            #print(width_new)
            if second[17] == "0" or second[17] == "1" or second[17] == "2" or second[17] == "3" or second[17] == "4" or second[17] == "5" or second[17] == "6" or second[17] == "7" or second[17] == "8" or second[17] == "9":
                height_2 = 100 * float(second[15]) + 10 * float(second[16]) + float(second[17])
                height_new_2 = height_2/1000
                #print(height_new)
            else:
                height_2 = 10 * float(second[15]) + float(second[16])
                height_new_2 = height_2/1000
                #print(height_new)                
        else:
            width_2 = 10 * float(second[11]) + float(second[12])
            width_new_2 = width_2/1000
            #print(width_new) 
            
            height_2 = 100 * float(second[14]) + 10 * float(second[15]) + float(second[16])
            height_new_2 = height_2/1000
            #print(height_new)
    else:
        XCenter_2 = 100 * float(second[2]) + 10 * float(second[3]) + float(second[4])
        XCenter_new_2 = XCenter_2/1000
        #print(XCenter_new)
    
        YCenter_2 = 100 * float(second[6]) + 10 * float(second[7]) + float(second[8])
        YCenter_new_2 = YCenter_2/1000
        #print(YCenter_new)
        if second[12]!=" ":
            width_2 = 100 * float(second[10]) + 10 * float(second[11]) + float(second[12])
            width_new_2 = width_2/1000
            #print(width_new)
            if second[16] == "0" or second[16] == "1" or second[16] == "2" or second[16] == "3" or second[16] == "4" or second[16] == "5" or second[16] == "6" or second[16] == "7" or second[16] == "8" or second[16] == "9":
                height_2 = 100 * float(second[14]) + 10 * float(second[15]) + float(second[16])
                height_new_2 = height_2/1000
                #print(height_new)      
            else:
                height_2 = 10 * float(second[14]) + float(second[15])
                height_new_2 = height_2/1000
                #print(height_new)
        else:
            width_2 = 10 * float(second[10]) + float(second[11])
            width_new_2 = width_2/1000
            #print(width_new) 

            height_2 = 100 * float(second[13]) + 10 * float(second[14]) + float(second[15])
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
        if third[13]!=" ":
            width_3 = 100 * float(third[11]) + 10 * float(third[12]) + float(third[13])
            width_new_3 = width_3/1000
            #print(width_new)
            if third[17] == "0" or third[17] == "1" or third[17] == "2" or third[17] == "3" or third[17] == "4" or third[17] == "5" or third[17] == "6" or third[17] == "7" or third[17] == "8" or third[17] == "9":
                height_3 = 100 * float(third[15]) + 10 * float(third[16]) + float(third[17])
                height_new_3 = height_3/1000
                #print(height_new)
            else:
                height_3 = 10 * float(third[15]) + float(third[16])
                height_new_3 = height_3/1000
                #print(height_new)                
        else:
            width_3 = 10 * float(third[11]) + float(third[12])
            width_new_3 = width_3/1000
            #print(width_new) 
            
            height_3 = 100 * float(third[14]) + 10 * float(third[15]) + float(third[16])
            height_new_3 = height_3/1000
            #print(height_new)            
    else:
        XCenter_3 = 100 * float(third[2]) + 10 * float(third[3]) + float(third[4])
        XCenter_new_3 = XCenter_3/1000
        #print(XCenter_new)
    
        YCenter_3 = 100 * float(third[6]) + 10 * float(third[7]) + float(third[8])
        YCenter_new_3 = YCenter_3/1000
        #print(YCenter_new)
        if third[12]!=" ":
            width_3 = 100 * float(third[10]) + 10 * float(third[11]) + float(third[12])
            width_new_3 = width_3/1000
            #print(width_new)
            if third[16] == "0" or third[16] == "1" or third[16] == "2" or third[16] == "3" or third[16] == "4" or third[16] == "5" or third[16] == "6" or third[16] == "7" or third[16] == "8" or third[16] == "9":
                height_3 = 100 * float(third[14]) + 10 * float(third[15]) + float(third[16])
                height_new_3 = height_3/1000
                #print(height_new)
            else:
                height_3 = 10 * float(third[14]) + float(third[15])
                height_new_3 = height_3/1000
                #print(height_new)                
        else:
            width_3 = 10 * float(third[10]) + float(third[11])
            width_new_3 = width_3/1000
            #print(width_new  
            
            height_3 = 100 * float(third[13]) + 10 * float(third[14]) + float(third[15])
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
    

    