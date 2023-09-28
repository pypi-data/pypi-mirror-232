

# At the  top of your setting.py file in django add :

from django_server_autoreload.Django_AutoReloader import Autoreload_Django    


# At the End of settings.py file add the bellow code.
# Enter Reload Time and App url example: reload_time='03:00',app_url='127.0.0.1:8080'

re_run=Autoreload_Django(reload_time="03:00",app_url="127.0.0.1:8080")   
re_run.refresh.start() 




