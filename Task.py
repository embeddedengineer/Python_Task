"""
Created on Sun Jun 23 10:21:22 2019

@author: abdelrhman
"""
# Import necessary libraries

import smtplib
import os	
import logging
import threading
from time import sleep as Sleep
from random import randrange as RandomNumber , getrandbits as RandomBits

# Global variables to pass the number of appends and removes between different threads.
NumberofAppends = 0
NumberofRemoves = 0

# Create a new binary file if it`s not already exists with a given size and randomize it`s data .
def CreateFileWithRandomData(Filename : str, Filesize : int) :
    if os.path.isfile(Filename)  == False :      # If the file doesn`t exist .
        BinaryFile = open(Filename , 'wb')       # Create and open the file in write mode .
        BinaryFile.write(os.urandom(Filesize))   # Fill the file with random data .
        BinaryFile.close()                       # Close the file .


# Append random number of bits to the binary file .
def AppendRandomNumberOfBits(Filename : str, Interval : int) :
    global NumberofAppends
    while(True) :
        BinaryFile = open(Filename , 'ab')                      # Open the file in append mode .
        RandomNumberOfBits = RandomNumber(0,100)                # Get a random number between 0 and 100 .
        GeneratedRandomNumber = RandomBits(RandomNumberOfBits)  # Get a random number consists of 0-100 number of bits .
        BinaryFile.write(GeneratedRandomNumber.to_bytes((GeneratedRandomNumber.bit_length() // 8) + 1, byteorder='big')) # Append the generated number to the binary file .
        BinaryFile.close() # Close the file .
        NumberofAppends = NumberofAppends + 1 # Increment the number of appends.
        Sleep(Interval) # Sleep for number of seconds = 10 .

def RemoveRandomNumberOfBits(Filename : str, Interval : int) :
    global NumberofRemoves
    while(True) :
        BinaryFile = open(Filename , 'rb')              # Open the file in read mode .
        RandomNumberOfBits = RandomNumber(0,50)         # Get a random number between 0 and 50 .
        BinaryFile.seek((RandomNumberOfBits // 8) + 1)  # Skip the first 0-50 bits .
        TheRestOfData = BinaryFile.read()               # Read the rest of the file .
        BinaryFile.close()  
        BinaryFile = open(Filename , 'wb')              
        BinaryFile.write(TheRestOfData)                 # Write the new data without the first 0-50 bits .
        BinaryFile.close()  
        NumberofRemoves = NumberofRemoves + 1           # Increment the number of removes .
        Sleep(Interval)                                 # Sleep for number of seconds = 20 .

def FileMaxSize(Filename : str, MaxSize : int , SMTPHost : str , SMTPPort : int , FromEmail : str , FromEmailPass : str , ToEmail : str) :
    global NumberofAppends , NumberofRemoves 
    server = smtplib.SMTP(SMTPHost, SMTPPort)  # Setup a smtp server .        
    server.ehlo()                              # Identify yourself to an ESMTP server .
    server.starttls()                          # Put the SMTP connection in TLS (Transport Layer Security) mode .
    server.login(FromEmail, FromEmailPass)     # login using your email and password .
    while(True) : 
        FileSize = os.path.getsize(Filename)   # Get the size of the file .
        if FileSize >= MaxSize :               # If it exceeds or equals the max size of the file .
            # Create a logging file .
            logging.basicConfig(filename='logFile.log', filemode='w', format='At %(asctime)s - %(message)s' , datefmt='%d-%b-%y %H:%M:%S')
            loggingData = "The binary file reached it`s max size = " + str(MaxSize) + "\nWith "+str(NumberofAppends) + " times bits appended .\n" + "And with " + str(NumberofRemoves) +" times bits removed .\n"
            logging.warning(loggingData)
            BinaryFile = open(Filename , 'rb')     # Open the file in read mode .
            TheRestOfData = BinaryFile.read(10000) # Read the first 10kb only , ignore the rest .
            BinaryFile.close()
            BinaryFile = open(Filename , 'wb') 
            BinaryFile.write(TheRestOfData)       
            BinaryFile.close()
            msg = "\n" + loggingData
            server.sendmail(FromEmail, ToEmail, msg) # Send an email to the target address with the logging info .
             # Reset the number of appends and removes to repeat the process .
            NumberofAppends = 0                     
            NumberofRemoves = 0
            

           
Filename = 'Binaryfile' # File Name .
Filesize = 10000        # File size (10kb) .
CreateFileWithRandomData(Filename, Filesize) # Create the file .

# Create a thread to append data with 10 seconds interval .
AppendingThread = threading.Thread(target=AppendRandomNumberOfBits , args=(Filename, 10, )) 
AppendingThread.start()

# Create a thread to remove data with 20 seconds interval .
RemovingThread = threading.Thread(target=RemoveRandomNumberOfBits , args=(Filename, 20, )) 
RemovingThread.start()

# Create mointoring thread to track the size of the file and take multiple actions .
MonitoringThread = threading.Thread(target=FileMaxSize , args=(Filename, 10050, 'smtp.gmail.com', 587, "pythontestingtask@gmail.com", "abc123___", "abdelrhmanabdo@hotmail.com", )) 
MonitoringThread.start()