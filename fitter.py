import csv
import pandas as pd
import collections as col
import os
import smtplib


class Person:
    def __init__(self, info, keys, iloc):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        self.avail = col.OrderedDict.fromkeys(days, [])
        #print(self.avail)
        #get the info with the column of the person
        indiv_info = info.iloc[[iloc]]
        
        #first get name
        temp = indiv_info['Name']
        #dataframe of name in temp
        self.name = temp.iloc[0]
        
		#getting phone number
        temp = indiv_info['Number']
        self.number = temp.iloc[0]	

		#getting email
        temp = indiv_info['Email']
        self.email = temp.iloc[0]	
		

        #then get times available
        self.avail['Monday'] = self.get_times(indiv_info, "Monday", keys)
        self.avail['Tuesday'] = self.get_times(indiv_info, "Tuesday", keys)
        self.avail['Wednesday'] = self.get_times(indiv_info, "Wednesday", keys)
        self.avail['Thursday'] = self.get_times(indiv_info, "Thursday", keys)
        self.avail['Friday'] = self.get_times(indiv_info, "Friday", keys)
        self.avail['Saturday'] = self.get_times(indiv_info, "Saturday", keys)
        self.avail['Sunday'] = self.get_times(indiv_info, "Sunday", keys)
        
        #print(self.avail)
        #then get type of workout
        self.workout = self.get_types(indiv_info)
        
        #and finally the intensity
        self.intensity = int(indiv_info['Intensity'])
        
        #add a dictionary of buddies that a person can workout with
        self.buddies = col.OrderedDict.fromkeys(days)
        for k in self.buddies:
            self.buddies[k] = col.OrderedDict.fromkeys(keys)
            for key in self.buddies[k]:
                self.buddies[k][key] = set();

    #function for getting the times that a person is available
    def get_times(self, info, column, keys):
        #create a dictionary with all the times in it
        time_keys = col.OrderedDict.fromkeys(keys, 0)
        #get the times that they are available
        temp = info[column]
        times = temp.iloc[0].split(';')
        #make the time values 1 that are for the
        for time in times:
            if(time != ''):
                time_keys[time] = 1
        return time_keys

    #function for getting the types of workout someone likes in a list
    def get_types(self, info):
        #first put get just workout types
        temp = info['Type']
        #divide by semicolon
        types = temp.iloc[0].split(';')
        
        return types
    
    def add_buddy(self, otherperson, day, time):
        #self.buddies[day][time].add(othername)
        #print(type(self.buddies[day][time]))
        #print(type(self.buddies[day]))
        self.buddies[day][time].add(otherperson)

def compare(people, person):
    for other in people:
        if person.name != other.name:
            #compare availablilities
            #intensity has a tolerance of 1
            if person.intensity <= 1 + other.intensity and person.intensity >= other.intensity-1:
                #then match by type of workout
                if(compare_types(person, other)):
                    compare_times(person, other)

def compare_types(person, other):
    for types in person.workout:
        for othertypes in other.workout:
            if othertypes == types:
                return True

def compare_times(person, other):
    #this is the most complex method
    #first check the day
    for day in person.avail:
        #second go through time
        for time in person.avail[day]:
            if person.avail[day][time] == 1:
                if other.avail[day][time] == 1:
                    person.add_buddy(other, day, time)

def write_file(person, email):	

    #so we have a person object
	with open('people/%s.txt' % person.name, 'w') as file:
		#first write the header of the email
		file.write('From:%s\n' % email)
		file.write('Subject: Your workout buddies result!\n')
		file.write('\n')


		for day in person.buddies:
			buddies = False
			file.write('%s:\n' %(day))
			for time in person.buddies[day]:
				if(len(person.buddies[day][time]) != 0):
					buddies = True
					file.write('	%s:\n' % time)
					file.write('\n')
					for buddy in person.buddies[day][time]:
						file.write('		%s		Contact them at %s\n' %(buddy.name, buddy.number))
						file.write('\n')
			if not buddies:
				file.write('no workout buddies found for this day :( \n')
				file.write('\n')
		file.close()



def send_email(person, sender, password):
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(sender, password)

	#assign message
	text = open('people/%s.txt' % person.name, 'r')
	msg = text.read()
	text.close()
	
	server.sendmail(sender, person.email, msg)
	server.quit()

