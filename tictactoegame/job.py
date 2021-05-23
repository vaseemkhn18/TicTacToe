import time
import threading
from .models import session, connection, status
from django.utils import timezone
from schedule import Scheduler

def purge():
    sesn = session.objects.filter()
    for i in sesn:
        if i:
            sess = session.objects.filter(sess_id = str(i))
            con = connection.objects.filter(sess_id = sess[0])
            tuple_time = con[0].timestamp
            curr_time = timezone.now()
            time_diff = curr_time - tuple_time
            if str(time_diff) > "5:00:00.00":
                status.objects.filter(sess_id = sess[0]).update(game_state = "tm")
                sess[0].delete()



def back_process(self, interval=20):
    cease_continuous_run = threading.Event()
    
    class scheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                self.run_pending()
                time.sleep(interval)
    
    back_thread = scheduleThread()
    back_thread.setDaemon(True)
    back_thread.start()
    return cease_continuous_run

Scheduler.back_process = back_process

def start_schedule():
    print("Starting background process....")
    scheduler = Scheduler()
    scheduler.every().second.do(purge)
    scheduler.back_process()
