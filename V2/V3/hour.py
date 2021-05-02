import time
import datetime
print(time.strftime('el día %Y-%m-%d a la hora %h,%m', time.localtime()))
print(datetime.datetime.now().hour,"hrs",datetime.datetime.now().minute,"min",datetime.datetime.now().second,"s")