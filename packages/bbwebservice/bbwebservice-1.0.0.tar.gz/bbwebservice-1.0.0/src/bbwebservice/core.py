import socket
from threading import Thread, Event, current_thread
import ssl
import sys as system
from urllib.response import addinfourl
from .config_loader import *
from .http_parser import HTTP_Message_Factory, LOGGING_OPTIONS, log

SESSIONS:dict = {}
PAGES:dict = {}
POST_HANDLER:dict = {}

ERROR_HANDLER:dict = {}

SERVER_THREADS:list = []
CONFIG = Config()
SERVER_LOGGING:dict = LOGGING_OPTIONS


def servlet(conn, addr, worker_state) -> None:

    '''The servlet function is invoked on every new client accepted by the server
    each servlet runs in its own thread and represents a session.'''

    while worker_state.is_set():
        try:

            log(f'[THREADING] thread {current_thread().ident} listens now.', log_lvl='debug')

            message_factory = HTTP_Message_Factory(conn,addr,PAGES,POST_HANDLER,ERROR_HANDLER)
            resp = message_factory.get_message()
            conn.sendall(resp)
            
            header,_,content = resp.partition(b'\r\n\r\n')
            log('\n\nRESPONSE:',str(header,'utf-8'),content,'\n\n', log_lvl='response',sep='\n')
            
            if message_factory.stay_alive:
                continue

        except Exception as err:
            log(f'[THREADING] thread {current_thread().ident} closes due to an error that occured "{err}"', log_lvl='debug')
            conn.close()
            break
        
        log(f'[THREADING] thread {current_thread().ident} closes because stay_alive is set to False', log_lvl='debug')
        conn.close()
        break

def main(server:socket.socket,state:Event) ->None:

    '''The main function acts as a dispatcher on accepting new clients approaching the server.
       Each client is handet to the servlet function which is started in its own thread and appended
       to the SERVER_THRADS list'''
    
    print('[SERVER] '+ CONFIG.SERVER_IP + ' running on port '+str(CONFIG.SERVER_PORT)+'...')
    while state.is_set():
        global SERVER_THREADS
        SERVER_THREADS = [t for t in SERVER_THREADS if t[0].is_alive()]
        try:
            conn,addr = server.accept()
            worker_state = Event()
            worker_state.set()
            worker_thread = Thread(target=servlet , args = [conn, addr, worker_state])
            SERVER_THREADS.append([worker_thread,worker_state,conn])
            worker_thread.start()
        except:
            if state.is_set():
                print('[CONNECTION_ERROR] a connection failed.')

def start():

    '''The start function starts the server. First it tries to initiate a socket Object and 
       then proceeds to call the server main function.'''
       
    if CONFIG.SERVER_IP == 'default':
        CONFIG.SERVER_IP = socket.gethostbyname(socket.gethostname())
    try:
        server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server.bind((CONFIG.SERVER_IP,CONFIG.SERVER_PORT))
        server.listen(CONFIG.QUE_SIZE)
        if CONFIG.SSL:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(CONFIG.CERT_PATH,CONFIG.KEY_PATH)
            server = context.wrap_socket(server, server_side=True)

    except:
        print('[SERVER] error while attempting to start the server\n')
        system.exit(0)
        
    server_state = Event()
    server_state.set()
    server_thread = Thread(target=main , args = [server,server_state])
    server_thread.start()
    while True:
        state = input()
        if state in ['quit','q','exit','e','stop']:
            server_state.clear()
            for obj in SERVER_THREADS:
                obj[1].clear()
                try:
                    obj[2].shutdown(socket.SHUT_RDWR)
                except:
                    pass
                obj[2].close()
            try:
                server.shutdown(socket.SHUT_RDWR)
            except:
                pass
            server.close()
            for obj in SERVER_THREADS:
                obj[0].join()
            server_thread.join()
            print('[SERVER] closed...')
            system.exit(0)





