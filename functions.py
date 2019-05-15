# -*- coding: utf-8 -*-
''' Created on Mon May  6 18:41:00 2019 '''

import sqlite3
from os import name, system
from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta
from time import sleep

def clearscreen():
    if name == 'nt': 
        system('cls')
    else:
        system('clear')
    return

# create 10-day schedule
# if incl_reserv then returns list of tuples including reservation indicator
def generate_schedule(incl_reserv):
    day = today = date.today()
    days = []
    while True:
        if day.weekday() == 5:
            day += timedelta(days=2)
        elif day.weekday() == 6:
            day += timedelta(days=1)
        if day >= today + timedelta(days=14):
            break
        hour = 8
        minutes = 0
        while True:
            if incl_reserv:
                days.append( (datetime.combine(day, time(hour,minutes)), 0) )
            else:
                days.append(datetime.combine(day, time(hour,minutes)))
            if minutes == 30:
                minutes = 0
                if hour == 11:
                    hour += 2
                elif hour == 16:
                    break
                else:
                    hour += 1
            else:
                minutes = 30
        day += timedelta(days=1)
    return days

# updates schedule
# deletes old appointments and adds slots for the current two week period
def setup():
    global services, schedule
    conn = sqlite3.connect('scheduler.db')
    curs = conn.cursor()
    # Initialize reservations if necessary
    curs.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="reservations"')
    rows = curs.fetchall()
    if rows != [('reservations',)]:
        curs.execute('CREATE TABLE reservations (reservation_id INTEGER PRIMARY KEY, \
                                                 client_name TEXT, \
                                                 pet_name TEXT, \
                                                 pet_breed TEXT, \
                                                 pet_weight TEXT, \
                                                 ccard_no TEXT, \
                                                 ccard_exp TEXT, \
                                                 ccard_name TEXT, \
                                                 ccard_code TEXT)')
    # Initiatlize schedule
    schedule = {}
    curs.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="schedule"')
    rows = curs.fetchall()
    if rows != [('schedule',)]:
        curs.execute('CREATE TABLE schedule (schedule_id INTEGER PRIMARY KEY, \
                                             groomer TEXT, \
                                             time TEXT, \
                                             reservation_id INTEGER, \
                                             service_id INTEGER)')
        times = generate_schedule(True)
        for groomer in ("Rachel", "Raul", "Renata", "Ringo"):
            schedule[groomer] = times
        sql = 'INSERT INTO schedule (groomer, time, reservation_id, service_id) VALUES (?, ?, 0, 0)'
        for groomer in schedule:
            for schedtime in schedule[groomer]:
                curs.execute(sql, (groomer, schedtime[0].strftime("%Y-%m-%d %H:%M")))
    else:
        sql = 'DELETE FROM schedule WHERE time < ?'
        curs.execute(sql, (date.today().strftime("%Y-%m-%d"),))    
        times = generate_schedule(False)
        sqlinsert = 'INSERT INTO schedule (groomer, time, reservation_id) VALUES (?, ?, 0)'
        sqlselect = 'SELECT COUNT(*) FROM schedule WHERE time=?'
        for tyme in times:
            curs.execute(sqlselect, (tyme.strftime("%Y-%m-%d %H:%M"),))
            c = curs.fetchall()[0][0]
            if c == 0:
                for groomer in ("Rachel", "Raul", "Renata", "Ringo"):
                    curs.execute(sqlinsert, (groomer, tyme.strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        sql = 'SELECT groomer, time, reservation_id FROM schedule ORDER BY groomer, time'
        curs.execute(sql)
        rows = curs.fetchall()
        times = []
        groomer = ''
        for row in rows:
            if groomer != '':
                if groomer != row[0]:
                    schedule[groomer] = times
                    times = []
                    groomer = row[0]
            times.append( (datetime.strptime(row[1], "%Y-%m-%d %H:%M"), row[2]) )
            groomer = row[0]
        schedule[groomer] = times

    # Initialize services
    curs.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="services"')
    rows = curs.fetchall()
    if rows != [('services',)]:
        curs.execute('CREATE TABLE services (service_id INTEGER PRIMARY KEY, \
                                             service_name TEXT, \
                                             service_type TEXT, \
                                             cost INTEGER)')
        sql = 'INSERT INTO services (service_name, service_type, cost) VALUES (?, ?, ?)'
        for values in [('Wash', 'fancy', 45),
                       ('Wash', 'no nonsense', 20),
                       ('Cut', 'teddy', 45),
                       ('Cut', 'lion', 45),
                       ('Cut', 'summer', 35),
                       ('Cut', 'weed whacker', 20)]:
            curs.execute(sql, values)
    conn.commit()
    services = {}
    sql = 'SELECT service_name, service_type, cost FROM services ORDER BY service_name, service_type'
    curs.execute(sql)
    rows = curs.fetchall()
    for row in rows:
        serv = (row[0], row[1])
        services[serv] = row[2]
    curs.close()
    conn.close()
    return services, schedule

def data_entry(msg):
    while True:
        var = input(msg) 
        if len(var.strip()) == 0:
            print('Cannot be blank. Please try again')
        else:
            break
    return var

def make_appointment():
    global services, schedule
    clearscreen()
    print('\nMAKE APPOINTMENT')
    print("Type 'quit' at any time to return to the Main Menu\n")
    owner_name = data_entry("Enter the owner's name: ")
    if owner_name == 'quit':
        return
    dog_name = data_entry("Enter the dog's name: ")
    if dog_name == 'quit':
        return
    dog_breed = data_entry("Enter the dog's breed: ")
    if dog_breed == 'quit':
        return
    dog_weight = data_entry("Enter the dog's weight: ")
    if dog_weight == 'quit':
        return
    cc_no = data_entry("Enter credit card number: ")
    if cc_no == 'quit':
        return
    cc_exp = data_entry("Enter credit card expiry date: ")
    if cc_exp == 'quit':
        return
    cc_name = data_entry("Enter name on the card: ")
    if cc_name == 'quit':
        return
    cc_code = data_entry("Enter security code: ")
    if cc_code == 'quit':
        return
    while True:
        print('\nIs the booking for a wash, a cut, or both?')
        print('1. Wash')
        print('2. Cut')
        print('3. Both')
        response = input("Enter the number for your choice: ")
        if response == '1':
            wash = True
            cut = False
            combo_booking = False
            break
        elif response == '2':
            wash = False
            cut = True
            combo_booking = False
            break
        elif response == '3':
            wash = True
            cut = True
            combo_booking = True
            break
        elif response == 'quit':
            return
        else:
            print("That is not a valid response. Please try again.\n")
    single_time = False
#    while wash and cut:
#        print('\nDo you want to book a single hour session?')
#        print('Enter Y to make a single booking for both the wash and cut.')
#        response = input('Enter N to make two separate bookings.')
#        if response == 'Y' or response == 'y':
#            single_time = True
#            break
#        elif response == 'N' or response == 'n':
#            single_time = False
#            break
#        else:
#            print("That is not a valid response. Please try again.\n")
#    if single_time:
#        print('\nSingle 1-hour booking chosen.')
    single_time = False
    wgroomer, cgroomer = '', ''
    # groomer for wash
    while wash:
        if single_time:
            print('\nChoose a groomer for both wash and cut: ')
        else:
            print('\nChoose a groomer for the wash: ')
        print('1. Rachel')
        print('2. Raul')
        print('3. Renata')
        print('4. Ringo')
        response = input("Enter the number for your choice: ")    
        if response == "1":
            wgroomer = 'Rachel'
            break
        elif response == "2":
            wgroomer = 'Raul'
            break
        elif response == "3":
            wgroomer = 'Renata'
            break
        elif response == "4":
            wgroomer = 'Ringo'
            break
        elif response == 'quit':
            return
        else:
            print("That is not a valid response. Please try again.\n")
    if wash:
        print('\nGroomer chosen:', wgroomer)
    if single_time:
        cgroomer = wgroomer
    else:
        # groomer for cut
        while cut:
            print('\nChoose a groomer for the cut: ')
            print('1. Rachel')
            print('2. Raul')
            print('3. Renata')
            print('4. Ringo')
            response = input("Enter the number for your choice: ")    
            if response == "1":
                cgroomer = 'Rachel'
                break
            elif response == "2":
                cgroomer = 'Raul'
                break
            elif response == "3":
                cgroomer = 'Renata'
                break
            elif response == "4":
                cgroomer = 'Ringo'
                break
            elif response == 'quit':
                return
            else:
                print("That is not a valid response. Please try again.\n")
        if cut:
            print('\nGroomer chosen:', cgroomer)
    serv_wash = None
    serv_cut = None
    # WASH
    while wash:
        choice = choose_service('Wash')
        serv_wash = choice[1]
        if choice[0]:
            break
        else:        
            print("That is not a valid response. Please try again, or quit.\n")
    # CUT
    while cut:
        choice = choose_service('Cut')
        serv_cut = choice[1]
        if choice[0]:
            break
        else:        
            print("That is not a valid response. Please try again, or quit.\n")
    input('\nPress ENTER to continue.')
    print('\nMAKE APPOINTMENT')
    print("Type 'quit' at any time to return to the Main Menu\n")

    msg = '\nBooking for: ' + owner_name + '(' + dog_name + ')'
    if single_time:
        msg += '\nSingle 1-hour session for both a wash and cut.'
        msg += '\nGroomer: ' + wgroomer
        appt_len = 60
    else:
        appt_len = 30
        if wash and cut:
            msg += '\nSeparate wash and cut sessions.'
            msg += '\n'+serv_wash[0]+', '+serv_wash[1]
            msg += '\n'+serv_cut[0]+', '+serv_cut[1]
            msg += '\nGroomers: ' + wgroomer + ' and ' + cgroomer
        elif wash:
            msg += '\nWash only.'
            msg += '\n'+serv_wash[0]+', '+serv_wash[1]
            msg += '\nGroomer: ' + wgroomer
        else:
            msg += '\nCut only.'
            msg += '\n'+serv_cut[0]+', '+serv_cut[1]
            msg += '\nGroomer: ' + cgroomer
    msg += '\n\nChoose from the options below: '
    if wgroomer:
        msg += '\n1. View ' + wgroomer + "'s schedule"
        if single_time:
            msg += '\n2. Select appointment time'
        else:
            msg += '\n2. Select appointment time for wash'
    if cgroomer and not single_time:
        msg += '\n3. View ' + cgroomer + "'s schedule"
        msg += '\n4. Select appointment time for cut\n'
        if combo_booking:
            msg += '\nPLEASE NOTE: WASH should be booked before CUT\n'
    msg += '\n5. Return to main menu'
#    earliest = None
    wtime, ctime = False, False
    while True:
        clearscreen()
        print(msg)
        response = input('\nEnter the number for your choice, or quit: ')
        if wgroomer and response == '1':
            view_groomer_schedule(wgroomer)
            input('Press ENTER to continue.')
        elif cgroomer and not single_time and response == '3':
            view_groomer_schedule(cgroomer)
            input('Press ENTER to continue.')
        elif wgroomer and response == '2' and not wtime:
            appt_time = choose_appointment_time(wgroomer, appt_len) #, earliest)
#            earliest = appt_time
            wtime = True
            w_appt_time = appt_time
            update_res_db(appt_time, wgroomer, owner_name, dog_name, dog_breed, dog_weight, 
                cc_no, cc_exp, cc_name, cc_code, serv_wash)
            print('Appointment made:', appt_time, dog_name, serv_wash)
        elif cgroomer and not single_time and response == '4' and not ctime:
            appt_time = choose_appointment_time(cgroomer, appt_len) #, earliest)
            ctime = True
            c_appt_time = appt_time
            update_res_db(appt_time, cgroomer, owner_name, dog_name, dog_breed, dog_weight, 
                cc_no, cc_exp, cc_name, cc_code, serv_cut)
            print('Appointment made:', appt_time, dog_name, serv_cut)
        elif response == '5' or response == 'quit':
            return
        elif wtime and response == 2:
            input('Press ENTER to continue.')
        elif ctime and response == 4:
            input('Press ENTER to continue.')
        else:
            print("That is not a valid response. Please try again.\n")
            if wtime:
                print("Wash time already selected.")
                print("Time selected:", w_appt_time.strftime("%A, %B %d, %Y, %H:%M"), '\n')
            if ctime:
                print("Cut time already selected.")
                print("Time selected:", c_appt_time.strftime("%A, %B %d, %Y, %H:%M"), '\n')
            input('Press ENTER to continue.')

def choose_service(category): # wash or cut
    print('\nChoose a service from the list below:\n')
    i = 0
    for service in services:
        if service[0] == category:
            i += 1
            print(str(i)+'. '+service[0]+', '+service[1]+': '+'${:,.2f}'.format(services[service]))
    choice = input("Enter the number for your choice: ")
    if choice == 'quit':
        return
    i = 0
    success = False
    for service in services:
        if service[0] == category:
            i += 1
            if str(i) == choice:
                serv = service
                cost = services[service]
                print('\nService chosen: '+serv[0]+', '+serv[1]+': '+'${:,.2f}'.format(cost))
                success = True
                break
    return (success, serv, cost)


def update_res_db(appt_time, groomer, owner_name, dog_name, dog_breed, 
                       dog_weight, cc_no, cc_exp, cc_name, cc_code, service):
    # update reservations db
    conn = sqlite3.connect('scheduler.db')
    curs = conn.cursor()
    sql = 'SELECT service_id FROM services WHERE service_name = ? AND service_type = ?'
    if service:
        curs.execute(sql, (service[0], service[1]))
        serv_id = curs.fetchall()[0][0]
    else:
        serv_id = 0
    sql = 'INSERT INTO reservations (client_name,\
                                     pet_name, \
                                     pet_breed, \
                                     pet_weight, \
                                     ccard_no, \
                                     ccard_exp, \
                                     ccard_name, \
                                     ccard_code) \
                VALUES (?,?,?,?,?,?,?,?)'
    curs.execute(sql, (owner_name,
                       dog_name,
                       dog_breed,
                       dog_weight,
                       cc_no,
                       cc_exp,
                       cc_name,
                       cc_code)
                )
    curs.execute('SELECT reservation_id FROM reservations ORDER BY reservation_id DESC LIMIT 1')
    reserv_id = curs.fetchall()[0][0]
    # update schedule db 
    sql = 'UPDATE schedule SET reservation_id = ?, service_id = ? WHERE groomer = ? AND time = ?'
    curs.execute(sql, (reserv_id, serv_id, groomer, appt_time.strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    curs.close()
    conn.close()
    # update schedule[groomer]
    new_tuple = (appt_time, reserv_id)
    schedule[groomer] = [new_tuple if item[0]==appt_time else item for item in schedule[groomer]]
    return

#def choose_appointment_time(groomer, length, earliest):
def choose_appointment_time(groomer, length):
    global services, schedule
    day = date.today()
#    if earliest == None:
#        earliest = datetime.combine(day, datetime.strptime("08:00", "%H:%M").time())
    choice_d, choice_t = {}, {}
    print('\nMaking grooming appointment with', groomer)
    print('\nChoose an appointment date from the list below')
    d, e = 0, 1
    appt_date, appt_time = None, None
    while True:
        while d < 14:
            if day.weekday() == 5:
                day += timedelta(days=2)
                d += 2
            elif day.weekday() == 6:
                day += timedelta(days=1)
                d += 1
#            if day >= earliest.date():
            print(str(e)+'. ' + day.strftime("%A, %B %d, %Y"))
            choice_d[e] = day
            day += timedelta(days=1)
            d += 1
            e += 1
        response = input("\nEnter the number for your choice: ")
        if response in ['1','2','3','4','5','6','7','8','9','10']:
            appt_date = choice_d[int(response)]
            print('\nDate chosen:', appt_date.strftime("%A, %B %d, %Y")+'\n')
            e = 1
            for times in schedule[groomer]:
                if not times[1] and times[0].date() == appt_date: # and times[0] >= earliest:
                    print(str(e)+'. '+times[0].time().strftime("%H:%M"))
                    choice_t[e] = times[0]
                    e += 1
            response = input('\nEnter the number for your choice: ')
            if response in [str(key) for key in choice_t.keys()]:
                appt_time = choice_t[int(response)]
                break
            elif response == 'quit':
                return
            else:
                print("That is not a valid response. Please try again.\n")
        elif response == 'quit':
            return
        else:
            print("That is not a valid response. Please try again.\n")
    print('\nAppointment time:', datetime.strftime(appt_time, "%A, %B %d, %Y, %H:%M"))
    input('\nPress ENTER to continue.')
    return appt_time     

def view_groomer_schedule(groomer):
    global services, schedule
    clearscreen()
    print('\n'+groomer.upper()+"'S SCHEDULE:                                   'OPEN' = time is available to book; 'XXXX' = time is NOT available"+'\n')
    day = ''
    count = 0
    times = ''
    for reserv in schedule[groomer]:
        if day != reserv[0].date():
            day = reserv[0].date()
            print(day.strftime("%A, %B %d, %Y"))
            print('-------------------------------------------------------------------------------------------------------------------------')
        times += reserv[0].time().strftime("| %H:%M ")+': '
        times += 'OPEN ' if reserv[1]==0 else 'XXXX '
        count += 1
        if count >=8:
            times += '|'
            print(times)
            print('-------------------------------------------------------------------------------------------------------------------------')
            times = ''
            count = 0
    return

def view_schedule():
    for groomer in schedule:
        view_groomer_schedule(groomer)
        input('Press ENTER to continue.')
    return

def view_appointments():
    clearscreen()
    conn = sqlite3.connect('scheduler.db')
    curs = conn.cursor()
    curs.execute('SELECT * FROM schedule')
    rows = curs.fetchall()
    sql = 'SELECT * FROM reservations, schedule, services \
                WHERE reservations.reservation_id = schedule.reservation_id \
                AND services.service_id = schedule.service_id \
                ORDER BY time, groomer'
    curs.execute(sql)
    rows = curs.fetchall()
    clearscreen()
    print('SCHEDULED APPOINTMENTS\n')
    for row in rows:
        print('Reservation ID:', row[0])
        print('Date/Time:', datetime.strftime(datetime.strptime(row[11], "%Y-%m-%d %H:%M"), "%A, %B %d, %Y, %H:%M"))
        print('Groomer:', row[10])
        print('Client name:', row[1])
        print('Dog name:', row[2])
        print('Breed: '+row[3])
        print('Weight: '+row[4])
        print('Service:', row[15]+', '+row[16]+'.', '${:,.2f}'.format(row[17]))
#        print('Total cost:', '${:,.2f}'.format(total_cost))
        print('Credit card:', row[5]+' EXP: '+row[6]+' CODE: '+row[8])
        print('Name on card:', row[7], '\n')
    input('Press ENTER to continue.')
    curs.close()
    conn.close()
    return

def reschedule_appointment():
    clearscreen()
    print('reschedule appointment')
    sleep(2)
    return