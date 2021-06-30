from datetime import date
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
sys.path.append('./A3_data')

import hospital
# import matplotlib
# import sys

# Global Variables
data_donor = []   #donors information
data_stock = []   #stocks information

default_donor_fname = "donors.txt"
default_stock_fname = "bags.txt"
test_stock_fname = "new_bags.txt"
test_donor_fname = "new_donors.txt"

last_bag_ID = 0
# Blood tranfusion table
bloodDictionary = {"O-":"O-,O+,B-,B+,A-,A+,AB-,AB+",
                   "O+":"O+,B+,A+,AB+",
                   "B-":"B-,B+,AB-,AB+",
                   "B+":"B+,AB+",
                   "A-":"A-,A+,AB-,AB+",
                   "A+":"A+,AB+",
                   "AB-":"AB-,AB+",
                   "AB+":"AB+"
                   }

#check inventory-search for any bags  older than 30 days and if ID number, display the ID number
def check_inventory():
    print("Following bags are out of their use-by date")
    deleted_count = 0
    tmp = []
    today = date.today()
    for i in range(len(data_stock)):
        if (today - date.fromisoformat(data_stock[i][2])).days>30:
            deleted_count+=1
            print(data_stock[i][0])
        else:
            tmp.append(data_stock[i])   #save the useful inventory
    data_stock.clear()
    for i  in range(len(tmp)):
        data_stock.append(tmp[i])
    tmp.clear()       
    if deleted_count>0:
        print("Please dispose them of. Press [d] when done...")
        function_key = input()
        while 1:
            if function_key=="d":
                #delete code here
                save_db(test_donor_fname,test_stock_fname,1)            
                print("Updated database files saved to disk.")
                break        
    
def attend_blood_demand():
    type_blood = hospital.check_demand()
    if type_blood == "X":
        print("Could not connect to hospital web server.\nPlease try again after some time.")
        return
    else:
        print("Currently "+type_blood+" blood is required.\nChecking the stock inventory...\n")
        useful_stock = []
        for i in range(len(data_stock)):
            if data_stock[i][1] in bloodDictionary[type_blood]:
                useful_stock.append(data_stock[i])
        if len(useful_stock)!=0:
            print("Following bags should be  supplid\n")
            #for i in range(len(useful_stock)):
            #    print("ID:" + useful_stock[i][0] +"("+useful_stock[i][1]+")")
            print("ID:" + useful_stock[0][0] +"("+useful_stock[0][1]+")")  
            fun_key = input("Press [p] once  it is  packed  for dispatch...")
            while 1:
                if fun_key == "p":
                    data_stock.remove(useful_stock[0])
                    save_db(test_donor_fname,test_stock_fname,1)
                    print("Inventory  records  updated.\n Updated database  files  saved to disk") 
                    break
            return
        else:
            print("We can not meet  the requirement. Checking the  donor  database ...\n")
            print("Following donors  match  the requirements . please  contact  them  for new donation.\n")
            for i in range(len(data_donor)):
                 if data_donor[i][4] in bloodDictionary[type_blood]:
                     print("-"+","+data_donor[i][0]+",12"+data_donor[i][1]+","+data_donor[i][2]+","+data_donor[i][3])         
            return
def attend_new_donation():
    unique = input("Enter the  donor's  unique  ID:")
    if len(data_stock)==0:
        last_bag_ID = 0
    else:
        last_bag_ID = int(data_stock[len(data_stock)-1][0])  
    for i in range(len(data_donor)):
        if unique == data_donor[i][0]:
            if (date.today() - date.fromisoformat(data_donor[i][5])).days<30:
                print("Sorry, this donor  is not  eligible  for donation")
                return
            else:
                print("Recording a new donation with following details:")
                fun_key = input("From:"+data_donor[i][1]+"\n"+"Group:"+data_donor[i][4]+"\n"+"Date:"+str(date.today())+" (today) "+"\n"+"BagID:"+str(last_bag_ID+1)+"\n"+"Please confirm(y/n):")
                while 1:
                    if fun_key=="n":
                        print("Cancelled")
                        return
                    elif fun_key == "y":
                        print("Done. Donor's last  donation  date also  updated to 2021-02-03\nUpdated database  files  saved to disk.")
                        data_donor[i][5] = str(date.today())
                        tmp_stock = [str(last_bag_ID+1),data_donor[i][4], str(date.today())]
                        data_stock.append(tmp_stock)
                        save_db(test_donor_fname,test_stock_fname,2)
                        return
                    else:
                        return
    print("That ID  does not  exist  in the database.\nTo register  a new donor ,please contact  the system  administrator.")
    return        
def visual():
    count_Blood = [0,0,0,0,0,0,0,0]
    type_blood = ["O-","O+","B-","B+","A-","A+","AB-","AB+"]
    for i in range(len(data_stock)):
        if data_stock[i][1] == "O-":
            count_Blood[0]+=1
        elif data_stock[i][1] == "O+":
            count_Blood[1]+=1 
        elif data_stock[i][1] == "B-":
            count_Blood[2]+=1
        elif data_stock[i][1] == "B+":
            count_Blood[3]+=1
        elif data_stock[i][1] == "A-":
            count_Blood[4]+=1
        elif data_stock[i][1] == "A+":
            count_Blood[5]+=1
        elif data_stock[i][1] == "AB-":
            count_Blood[6]+=1
        elif data_stock[i][1] == "AB+":
            count_Blood[7]+=1 
    tmp = []        
    mlabels = []
    for i in range(8):
        if count_Blood[i] !=0:
            tmp.append(count_Blood[i])
            mlabels.append(type_blood[i])
    print(tmp)        
    y = np.array(tmp)   
    plt.pie(y,labels = mlabels)
    plt.show()     
    print("Pie chart  opens  in a new  window...\nClose the chart  window  to continue")                            
    return
#load the database
def load_db(donor_fname, stock_fname):
        #if not os.path.isfile(donor_fname):
        #        print("error: {} does not exist".format(donor_fname))
        #        sys.exit(1)
        #else:
            f_donor = open("A3_data/" + donor_fname)
            tmp = f_donor.read()
            donors = tmp.split("\n")
            if len(donors) != 0:
                for i in range(len(donors)-1):
                    content = donors[i].split(",")
                    data_donor.append(content)
            f_donor.close()        
    
        #if not os.path.isfile(stock_fname):
        #            print("error: {} does not exist".format(stock_fname))
        #            sys.exit(1)
       # else:            
            f_stock = open("A3_data/" + stock_fname)
            tmp = f_stock.read()
            stocks = tmp.split("\n")
            if len(stocks)!=0:
                for i in range(len(stocks)-1):
                    content = stocks[i].split(",")
                    data_stock.append(content)
            f_stock.close()  
            print("Database loaded successfully")    
            return
#save the database 
def save_db(donor_name,stock_name,switch):
    f = open(stock_name, "w")
    if switch in [1,2]:
        for i in range(len(data_stock)):
            info = [data_stock[i][0],data_stock[i][1],data_stock[i][2]]
            for j in range(len(info)):
                f.writelines(info[j])
                if j!=len(info)-1:
                    f.write(",")
            f.write("\n")  
        f.close()
    f = open(donor_name, "w")
    if switch ==2 :
        for i in range(len(data_donor)):
            info = [data_donor[i][0],data_donor[i][1],data_donor[i][2],data_donor[i][3],data_donor[i][4],data_donor[i][5]]
            for j in range(len(info)):
                f.writelines(info[j])
                if j!=len(info)-1:
                    f.write(",")
            f.write("\n")  
        f.close()    
        
    return
#start the main program
def main():
    print("Loading database...\nEnter the database filenames without .txt extension\nor just ENTER to accept defaults")
    #input the donor_fname
    try:
        donor_fname = input("Donors database (donors): ")
        if donor_fname == "":
            donor_fname = default_donor_fname
            print(default_donor_fname)

        else:
            donor_fname += ".txt"
            print(donor_fname)
    except IOError:
        print("File does not exist")

    #input the stock_fname
    try:
        stock_fname = input("Stock inventory database (bags): ")
        if stock_fname == "":
            stock_fname = default_stock_fname
            print(default_stock_fname)

        else:
            stock_fname += ".txt"
            print(stock_fname)
    except IOError:
        print("File does not exist")
        
    #loading the database
    load_db(donor_fname, stock_fname)

    menuLoop = True
    while menuLoop is True:
        print("------------\nMain Menu\n------------")
        print("(1) Check inventory\n(2) Attend to blood demand\n(3) Record new donation\n(4) Stock Visual report\n(5) Exit")
        try:
            choice = int(input("Enter your choice: "))
        except ValueError:
            print("Invalid Input. Enter a number between 1 and 5")
            continue
        if choice not in ('1', '2', '3', '4', '5'):
            if choice == 1:
                check_inventory()
            elif choice == 2:
                attend_blood_demand()
            elif choice == 3:
                attend_new_donation()
            elif choice == 4:
                visual()
            elif choice == 5:
                print("Have a good day.")
                menuLoop = False
            else:
                print("Invalid Input. Enter a number between 1 and 5")

print("<<< LifeServe Blood Institute >>>\n")
main()
