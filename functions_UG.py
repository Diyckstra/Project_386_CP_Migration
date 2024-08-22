from functions import *

def UG_get_token(SERVER, PORT, USER, PASSWORD):
    try:
        server = xmlrpc.client.ServerProxy(f'http://{SERVER}:{PORT}/rpc', verbose=False)
        res = server.v1.core.login(USER, PASSWORD, {})
        auth_token = res['auth_token']
        return server, auth_token
    except BlockingIOError:
        return "Server unavailable or invalid port", 0
    except xmlrpc.client.Fault as error:
        return error.faultString, 0

def UG_UTM_get_token(SERVER, PORT, USER, PASSWORD):
    try:
        server = xmlrpc.client.ServerProxy(f'http://{SERVER}:{PORT}/rpc', verbose=False)
        res = server.v2.core.login(USER, PASSWORD)
        auth_token = res['auth_token']
        return server, auth_token
    except BlockingIOError:
        return "Server unavailable or invalid port", 0
    except xmlrpc.client.Fault as error:
        return error.faultString, 0

















# release token
def UG_release_token(server, auth_token):
    try:
        server.v1.core.logout(auth_token)
        return 0
    except ValueError:
        return 1
    






