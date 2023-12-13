from O365 import Account

CLIENT_ID = "e91b486a-c2d6-41e3-a346-6964af4bfcac"
CLIENT_SECRET = "clF8Q~g4qaBLRNjcmi1QrMrH593BKgNbe6B8HduA"


#Getting credentials and setting up
credentials = (CLIENT_ID, CLIENT_SECRET)
scopes = ['Calendars.Read']
account = Account(credentials)

if not account.is_authenticated:
    account.authenticate(scopes=scopes)
    print('Authenticated!')

schedule = account.schedule()

#Supposedly getting all calendar events
calendar = schedule.get_default_calendar()
events = calendar.get_events(include_recurring=False) 


#Getting all events of one calendar

#deadline_cal = schedule.get_calendar(calender_name='Deadlines')
#main_cal = schedule.get_calendar(calender_name='Calendar')

#deadlines = deadline_cal.get_events(include_recurring=False) 

import datetime


start = datetime.datetime.combine(datetime.date(2023, 11, 28), datetime.time(0, 00))
end = datetime.datetime.combine(datetime.date(2023, 11, 28), datetime.time(23, 59))

query = calendar.new_query('start').greater_equal(start)
query.new('end').less_equal(end)
items = calendar.get_events(query=query, include_recurring=True)

for item in items:
    print(item)

'''

for event in events:
    try:
        print(event)
    except:
        print("oop")

'''