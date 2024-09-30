#!/usr/bin/python3

import queue
import threading
import datetime
import methods_v2 as m
import os
import scp

MAX_THREADS = 32
COUNTER = 0
start_time = datetime.datetime.now()
print(f'Start at {start_time}')
nameList = []


file_to_write_success = 'success.log'
file_to_write_fail = 'failure.log'

m.set_the_gateway_for_device_pool(m.file_with_sh_script_Template)
nameList = m.configuration_parser(m.file_to_use)

queueLock = threading.Lock()
workQueue = queue.Queue()

# Fill the queue
for word in nameList:
    workQueue.put(word)


class ThrError(Exception):
    """my base class for self generated exceptions"""
    pass

class myThread(threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.daemon = True
        self.q = q

    def run(self):
        while not self.q.empty():
            try:
                process_data(self.name, self.q)
            except ValueError as error:
#                print(f'{error}')
                pass
            except ThrError as error:
                print(f'{error}')
                break

def process_data(threadName, q):
    global COUNTER
    if not q.empty():
        queueLock.acquire()
        data = q.get()
        q.task_done()
        queueLock.release()
        try:
            print(f'{threadName} started processing {data}')
            m.device_migration(data, m.NEW_GATEWAY, m.OLD_GATEWAY)
            COUNTER += 1
            with open(file_to_write_success, 'a') as success_file:
                success_file.write(str(data[1]) + '\n') 
            print(f'{threadName} finished processing {data}')
        except Exception as err:
            with open(file_to_write_fail, 'a') as fail_file:
                fail_file.write(str(data[1]) + ' because of ' + str(err) + '\n')
            raise ValueError(str(err))
#        except TimeoutError as err:
#            with open(file_to_write_fail, 'a') as fail_file:
#                fail_file.write(str(data[1]) + ' because of ' + str(err) + '\n')
#            raise ValueError(str(err))
#        except OSError as err:
#            with open(file_to_write_fail, 'a') as fail_file:
#                fail_file.write(str(data[1]) + ' because of ' + str(err) + '\n')
#            raise ValueError(str(err))
#        except scp.SCPException as err:
#            with open(file_to_write_fail, 'a') as fail_file:
#                fail_file.write(str(data[1]) + ' because of ' + str(err) + '\n')
#            raise ValueError(str(err))
#        except:
#            with open(file_to_write_fail, 'a') as fail_file:
#                fail_file.write(str(data[1]) + ' because of ' + 'Unknown error' + '\n')
#            raise ValueError(str('Unknown error'))  
    else:
        print(f'{threadName} has no elements to take from queue')
        raise ThrError(f'why my thread {threadName} is breaking bad?')


threadList = []
for i in range(MAX_THREADS):
    threadList.append(str("Thread-") + str(i))
threads = []
threadID = 1

# Create new threads
for tName in threadList:
    thread = myThread(threadID, tName, workQueue)
    print(f'{thread.name} starting')
    thread.start()
    threads.append(thread)
    threadID += 1

# Wait for queue to be empty and to check threads
workQueue.join()
print(f'Queue size is {workQueue.qsize()}')
print(f'currently alive {threading.active_count()}')
for t in threads:
    t.join(timeout=10000)
    print(f'{t.name} finished')
end_time = datetime.datetime.now()
print(f'End time {end_time}')
length = end_time - start_time
print(f'process took {length}')
print(f'COUNTED {COUNTER} items')
print(f'Exiting Main Thread with {threading.active_count()} alive like jesus threads')
