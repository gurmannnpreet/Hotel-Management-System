#Hotel Management System Version 1.1.0
#IMPORTING REQUIRED MODULES
from tkinter import *
import csv
from tkcalendar import Calendar, DateEntry
import math
from tkinter import messagebox
import mysql.connector

#Creating root window
root = Tk()
root.title("Hotel Management")
root.iconbitmap("review.ico")

#Frame to take Entries
EntryFrame = LabelFrame(root)
EntryFrame.grid(row = 0, column =0)

#Creating entry fields
fields = ['DATE','ROOM TYPE','NAME','ADDRESS','AGE','TOTAL VISITORS',
          'DAYS','PURPOSE','ROOM NO','BASE AMOUNT','GST','TOTAL']
y = 0
for f in fields:
    Label(EntryFrame, text = f+':', anchor = E).grid(row =y, column = 0, sticky = W+E)
    y +=1

eDate = DateEntry(EntryFrame, width= 16)
eDate.grid(row=0, column =1, sticky = W+E)

#RoomType List
rTypes = [
    'STANDARD SINGLE',
    'STANDARD DOUBLE',
    'PREMIUM SINGLE',
    'PREMIUM DOUBLE',
    'BUSINESS SINGLE',
    'BUSINESS SUITE',
    'CITYVIEW SUITE',
    'PRESIDENTIAL SUITE',
    ]

#Room Type DropDown
rtype = StringVar()
rtype.set(rTypes[0])

eRoomtype = OptionMenu(EntryFrame, rtype, *rTypes).grid(row = 1, column =1)

eName = Entry(EntryFrame, width = 50)
eName.grid(row =2, column = 1, sticky = W+E)

eAddress = Entry(EntryFrame, width = 50)
eAddress.grid(row =3, column = 1, sticky = W+E)

eAge = Entry(EntryFrame, width = 50)
eAge.grid(row =4, column = 1, sticky = W+E)

eTotalvisitors = Entry(EntryFrame, width = 50)
eTotalvisitors.grid(row =5, column = 1, sticky = W+E)

eDays = Entry(EntryFrame, width = 50)
eDays.grid(row =6, column = 1, sticky = W+E)

ePurpose = Entry(EntryFrame, width = 50)
ePurpose.grid(row =7, column = 1, sticky = W+E)


#Room Allotment
def allot_room():
    global data
    global rtype
    global allotted 
    global rTypes
    global ind
    global fname
    
    t = rtype.get()
    ind = rTypes.index(t)
    #Opeming correct File
    if ind == 0:
        fname = 'StandardSingle'
        rent = 1000*int(eDays.get())
    elif ind == 1:
        fname = 'StandardDouble'
        rent = 1750*int(eDays.get())
    elif ind == 2:
        fname = 'PremiumSingle'
        rent= 1500*int(eDays.get())
    elif ind == 3:
        fname = 'PremiumDouble'
        rent = 2500*int(eDays.get())
    elif ind == 4:
        fname = 'BusinessSingle'
        rent = 1250*int(eDays.get())
    elif ind == 5:
        fname = 'BusinessSuite'
        rent = 2000*int(eDays.get())
    elif ind == 6:
        fname = 'CityviewSuite'
        rent = 3500*int(eDays.get())
    elif ind == 7:
        fname = 'PresidentialSuite'
        rent = 5000*int(eDays.get())
    
    #Fetching room number from available rooms
    with open(fname+"Available.txt", 'r') as rNo:
        avail = rNo.readlines()
        global allotted
        if avail == []:
            messagebox.showerror("No room Available", "No room of this type is currently available")
            return None
        allotted = avail[0]
    
    #Calculating costs
    base = (rent*100)/112
    bAmount = math.ceil(base)
    gst = rent - bAmount
       
    #Data list to later add to other files
    data = []
    data.append(eDate.get_date())
    data.append(int(allotted))
    data.append(t)
    data.append(eName.get())
    data.append(eAddress.get())
    data.append(int(eAge.get()))
    data.append(int(eTotalvisitors.get()))
    data.append(int(eDays.get()))
    data.append(ePurpose.get())
    data.append(bAmount)
    data.append(gst)
    data.append(rent)
    
    Label(EntryFrame, text = str(int(allotted)), anchor = W).grid(row = 8, column =1, sticky= W+E)
    Label(EntryFrame, text = str(bAmount), anchor = W).grid(row = 9, column =1, sticky= W+E)
    Label(EntryFrame, text = str(gst), anchor = W).grid(row = 10, column =1, sticky= W+E)
    Label(EntryFrame, text = str(rent), anchor = W).grid(row = 11, column =1, sticky= W+E)
    confirmBtn.config(state =  NORMAL)
    
#Confirming a room booking
def confirm_room():
    global data
    global allotted 
    global ind
    global fname
    
    response = messagebox.askokcancel("Confirm","Confirm this Booking?")
    if response == 0:
        return None
    else:
        #Adding data to current visitors table
        with open("VisitorData.csv", 'a', newline = '') as f:
            csvWrite = csv.writer(f, delimiter = ',')
            csvWrite.writerow(data)
        
        #Removing room from Lists
        with open(fname+"Available.txt", 'r') as rNo:
            avail = rNo.readlines()
            for r in avail:
               if r == allotted:
                   avail.remove(r)
        with open(fname+"Available.txt", 'w') as rNo:
            rNo.writelines(avail)
            rCount = len(avail)
        with open(fname+"Booked.txt", 'r') as rNo:
            avail = rNo.readlines()
            avail.append(allotted)
        with open(fname+"Booked.txt", 'w') as rNo:
           rNo.writelines(avail)   
           
        with open("AvailableRoomList.csv", 'r', newline = '') as roomData:
            csvRead = csv.reader(roomData)
            rd = list(csvRead)
            rd[(2*ind)+2][1] = rCount
        with open("AvailableRoomList.csv", 'w', newline = '') as roomData:
            csvWrite = csv.writer(roomData, delimiter = ',')
            for i in rd:
                csvWrite.writerow(i)
                
        #Adding permament data to mySQL database
        mydb = mysql.connector.connect(host = 'localhost', user = 'root',
                                      password = 'Gurmanpreet@22', database = 'hotel')   
        mycursor = mydb.cursor()
        dataTpl = tuple(data)
        query = "INSERT INTO VISITORDB VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" 
        mycursor.execute(query, dataTpl)
        mydb.commit()
        mydb.close()
        
        confirmBtn.config(state =  DISABLED)
        
        messagebox.showinfo("Room Booked", "Room Number "+ str(int(allotted)) +" has been booked for "+ eName.get())
    
# Buttons in a different frame inside EntryFrame
ButtonFrame= LabelFrame(EntryFrame)
ButtonFrame.grid(row = 12, column =0, columnspan=2)
allotBtn = Button(ButtonFrame, text = "Allot Room", command = allot_room).grid(row = 0, column =0)
confirmBtn = Button(ButtonFrame, text = "Confirm Booking", command = confirm_room, state = DISABLED)
confirmBtn.grid(row = 0, column =1)
    
#Another frame for other buttons
addFrame = LabelFrame(root)
addFrame.grid(row = 1, column =0)


#Confirming a Check Out
def checkoutConfirm():
    global booked
    global br
    
    slcted = br.get()
    rnumber = slcted[0:3]
    for i in vData:
        if i[1] == rnumber:
            check = i
    msg = "Confirm Checkout of "+ check[3] +" from Room Number" + rnumber + "? \n \
        Total Amount: " + check[11]
    responce = messagebox.askokcancel('Confirm Checkout', msg)
    if responce == 0:
        return None
    else: 
        vData.remove(check)
        with open("VisitorData.csv", 'w', newline = '') as visitorData:
            csvWrite = csv.writer(visitorData, delimiter = ',')
            
            fields = ['DATE','ROOM TYPE','NAME','ADDRESS','AGE','TOTAL VISITORS',
                      'DAYS','PURPOSE','ROOM NO','BASE AMOUNT','GST','TOTAL']
            csvWrite.writerow(fields)
            for i in vData:
                csvWrite.writerow(i)
                
                
        #Opeming correct File
        if check[2] == 'STANDARD SINGLE':
            ind = 0
            fname = 'StandardSingle'
        elif check[2] == 'STANDARD DOUBLE':
            ind = 1
            fname = 'StandardDouble'
        elif check[2] == 'PREMIUM SINGLE':
            ind = 2
            fname = 'PremiumSingle'
        elif check[2] == 'PREMIUM DOUBLE':
            ind = 3
            fname = 'PremiumDouble'
        elif check[2] == 'BUSINESS SINGLE':
            ind = 4
            fname = 'BusinessSingle'
        elif check[2] == 'BUSINESS SUITE':
            ind = 5
            fname = 'BusinessSuite'
        elif check[2] == 'CITYVIEW SUITE':
            ind = 6
            fname = 'CityviewSuite'
        elif check[2] == 'PRESIDENTIAL SUITE':
            ind = 7
            fname = 'PresidentialSuite'
            
        #Managing Lists
        with open(fname+"Booked.txt", 'r') as rNo:
            bk = rNo.readlines()
            for r in bk:
               if r == allotted:
                   bk.remove(r)
        with open(fname+"Booked.txt", 'w') as rNo:
            rNo.writelines(bk)
        with open(fname+"Available.txt", 'r') as rNo:
            avail = rNo.readlines()
            avail.append(check[1]+'\n')
            rCount = len(avail)
        with open(fname+"Available.txt", 'w') as rNo:
           rNo.writelines(avail)   
           
        with open("AvailableRoomList.csv", 'r', newline = '') as roomData:
            csvRead = csv.reader(roomData)
            rd = list(csvRead)
            rd[(2*ind)+2][1] = rCount
        with open("AvailableRoomList.csv", 'w', newline = '') as roomData:
            csvWrite = csv.writer(roomData, delimiter = ',')
            for i in rd:
                csvWrite.writerow(i)
        messagebox.showinfo("Check Out", "Successfully Checked Out")
        
#Checkout Pop up window
def check_out():
    global booked
    global vData
    global br
    
    with open('VisitorData.csv', 'r') as visitorData:
        csvRead = csv.reader(visitorData)
        lst = list(csvRead)
        if len(lst) == 1:
            messagebox.showerror("No room", "No room is Booked")
            return None 
        else:
            vData = lst[1:]
            booked = []
            for i in vData:
                booked.append(i[1]+": "+i[3])
                
    top = Toplevel()
    top.title("Check Out")
    top.iconbitmap("review.ico")
    
    #Adding booked rooms to a drop down
    br = StringVar()     
    br.set(booked[0])
    Label(top, text = "Choose Room:", anchor = E).grid(row = 0, column = 0)
    bookedRooms = OptionMenu(top, br, *booked).grid(row = 0, column = 1)
    #Confirm check out button
    Button(top, text = 'Confirm Checkout', command = checkoutConfirm).grid(row = 1, column = 0, columnspan = 2)
    

#CheckOut Button    
Button(addFrame, text = "Check Out", command = check_out).grid(row = 0, column =0)        

#Showing room data
def open_room_popUp():
    top = Toplevel()
    top.title("Room Data")
    top.iconbitmap("review.ico")
    with open("AvailableRoomList.csv", 'r') as roomData:
        csvRead = csv.reader(roomData)
        #creating room table
        x = 1
        for room in csvRead:
            y = 0
            for c in room:
                Label(top, text = c, borderwidth=1, relief = SOLID, 
                      padx =5, pady=5).grid(row=x,column=y, sticky = W+E)
                y+=1
            x+=1
        
#Room Data Button
Button(addFrame, text = "Room Data", command = open_room_popUp).grid(row = 0, column =1)

#Displaying Current Visitors Information
def open_visitordata_popup():
    top = Toplevel()
    top.title("Visitor Data")
    top.iconbitmap("review.ico")
    with open('VisitorData.csv', 'r') as visitorData:
        csvRead = csv.reader(visitorData)
        x=0
        for visitor in csvRead:
            y = 0
            for c in visitor:
                Label(top, text = c, borderwidth=1, relief = SOLID, padx =5, pady=5).grid(row=x,column=y, sticky = W+E)
                y+=1
            x+=1
#Visitor Data button
Button(addFrame, text = "Visitor Data", command = open_visitordata_popup).grid(row = 0, column =2)

#Creating a loop to run the program
mainloop()