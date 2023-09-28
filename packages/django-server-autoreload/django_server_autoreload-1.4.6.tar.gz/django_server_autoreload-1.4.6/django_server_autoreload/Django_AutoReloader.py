
import psutil 
import signal 
import os
import schedule 
import time
from threading import *   


class Autoreload_Django():
                """
                Enter Reload Time and App url example: reload_time='03:00',app_url='127.0.0.1:8080'
                """
                def __init__(self,reload_time="03:00",app_url="127.0.0.1:8080"):
                      self.reload_time=reload_time
                      self.app_url=app_url  
                      self.refresh=Thread(target=self.reload_server,args=[])
                      self.refresh.setDaemon(True)   
                

                def load(self):
                         try:
                                        print("------------------------------------------------Server changes detected-----------------------------------------------------")      
                                        PROCNAME="python.exe"
                                        PIDS=[]
                                        
                                        for proc in psutil.process_iter():   
                                                if proc.name()==PROCNAME:
                                                        PIDS.append(proc.pid)
                                        main_pid=PIDS[-1]         
                                        os.kill(main_pid,signal.CTRL_C_EVENT) #signal.SIGTERM    
                                        print("############################################{}##{}##########################################".format(PROCNAME,main_pid)) 
                                        os.system("python manage.py runserver 127.0.0.1:8080 ")
                                        print("++++++++++++++++++++++++++++++++++++++++++++++++++++  Reloading Server   +++++++++++++++++++++++++++++++++++++++++++++++++++++++++") 
                                        PIDS.clear() 
                         except:
                                     pass 
                                
                        
                        
                def reload_server(self):
                    schedule.every().day.at(self.reload_time).do(self.load)  

                    while True: 
                        schedule.run_pending()    
                        time.sleep(1) 
                

                    
                


        
                # """
                # Once you have used  reload method avoid using keyboard short cut Ctl + s
                # if you use ctrl + s after using this method your server will stop responding to requests because reload creates anew django main thread killing the 
                # the previous thread that was running when you first started the djnago server.
                # """
                

