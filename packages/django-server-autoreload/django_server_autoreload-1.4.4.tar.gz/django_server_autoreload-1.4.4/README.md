

<!-- # At the  top of your setting.py file in django add : -->

from django_server_autoreload.Django_AutoReloader import Autoreload_Django    


<!-- # At the End of settings.py file add the bellow code.
# Avoid using keybordshort shortcuts Ctrl +s  or Ctrl + c  when using this package ,this will make the server stop responding to requests because this module kills #and creates anew dajngo  main thread for you.  -->


re_run=Autoreload_Django(reload_time="03:00",app_url="127.0.0.1:8080")   
re_run.refresh.start() 




