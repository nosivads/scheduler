# -*- coding: utf-8 -*-
''' Created on Mon May  6 18:35:27 2019 '''

from functions import setup, clearscreen
from functions import make_appointment, view_appointments
from functions import view_schedule #, reschedule_appointment
from time import sleep

services = {}
schedule = {}
setup()

while True:
    clearscreen()
    print('------------------------------------------')
    print('| Welcome to Madra Dog Grooming Services |')
    print('------------------------------------------')
    print('\nFor best results please maximize the size of your window\n')
    print('Choose from the menu below:\n')
    print('1. View schedule of appointments (by groomer)')
    print('2. View appointment details (by client)')
    print('3. Make new appointment')
#    print('4. Reschedule appointment')
    print('5. Quit the system\n')
    response = input("\nEnter the number for your choice: ")    
    if response == "1":
        view_schedule()
    elif response == "2":
        view_appointments()
    elif response == "3":
        make_appointment()
#    elif response == "4":
#        reschedule_appointment()
    elif response == "5":
        break
    else:
        print("That is not a valid response. Please try again.\n")

print("\nGoodbye.")
sleep(1)
clearscreen()

