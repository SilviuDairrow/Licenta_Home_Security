#https://docs.python.org/3/library/http.cookies.html
#https://www.tutorialspoint.com/how-to-setup-cookies-in-python-cgi-
#https://websockets.readthedocs.io/en/stable/
#https://pypi.org/project/websockets/

import socket
import os 
import json
from http import cookies

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('', 5678))
serversocket.listen(5)


#D:\\VS RANDOM SHIT\\SD_test\\Server Licenta\\users.json
def IncarcareJson():
	with open('F:\\SD_test\\Server Licenta\\users.json', 'r') as file:
		return json.load(file)

users_info = IncarcareJson()


def login(data):
    try:
        date = json.loads(data)
        
        id_user = date.get('username')
        password = date.get('password')

        #print(f"{id_user} : {password}")

        for user in users_info['users']:
            if user['id'] == id_user:
                if user['password'] == password:
                    token = f"{id_user}_ses"
                    return {'status': 'success', 'role': user['role'], 'token': token}

        return {'status': 'failed'}


    finally:
        print("Login prelucrat bruh")


def verif_login(headers):

	cookies = headers.get('Cookie', '')
	cookie_actual = None

	if 'ses=' in cookies:
		cookie_actual = cookies.split('ses=')[1].split(';')[0]

	if cookie_actual != None:
		for user in users_info['users']:
			if cookie_actual == f"{user['id']}_ses":
				return True

	return False

while True:
	print('Server on!')

	(clientsocket, address) = serversocket.accept()

	print('S a conectat un client.')

	request = ''
	linie = ''
	headers = {}

	
	while True:
		buf = clientsocket.recv(1024)
		
		if len(buf) < 1:
			break
		
		request += buf.decode()
		pozitie = request.find('\r\n')
		
		if (pozitie > -1 and linie == ''):
			linie = request[0:pozitie]
			print('Cerere: ' + linie)
			break

	if linie == '':	
		clientsocket.close()
		print('client conectat, 0 mesaje')
		continue
	
	elementeLinie = linie.split()
	metoda = elementeLinie[0]
	numeResursa = elementeLinie[1]

	headerLines = request.split('\r\n')[1:]

	for header in headerLines:
		if ': ' in header:
			k, v = header.split(': ', 1)
			headers[k] = v

	
	if numeResursa == '/':
		numeResursa = '/login.html'
	
	elif numeResursa == '/login':
		if metoda == 'POST':

			body = request.split('\r\n\r\n')[1]
			rasp = login(body)

			if rasp['status'] == 'success':

				clientsocket.sendall(b'HTTP/1.1 200 OK\r\n')
				clientsocket.sendall(f'Set-Cookie: ses={rasp["token"]}; Path=/\r\n'.encode())
				clientsocket.sendall(b'Content-Type: application/json\r\n')
				clientsocket.sendall(b'\r\n')
				clientsocket.sendall(json.dumps(rasp).encode())

			elif rasp['status'] == 'failed':
				clientsocket.sendall(b'HTTP/1.1 401 NOT OK\r\n')
				clientsocket.sendall(b'Content-Type: application/json\r\n')
				clientsocket.sendall(b'\r\n')
				clientsocket.sendall(json.dumps(rasp).encode())				

			clientsocket.close()
			continue
	
	elif numeResursa == '/dashboard':
		if verif_login(headers) == False:
			clientsocket.sendall(b'HTTP/1.1 302 Nu esti logat man\r\n')
			clientsocket.sendall(b'Location: /login.html\r\n')
			clientsocket.sendall(b'\r\n')
			clientsocket.close()
			continue

		numeResursa = '/dashboard.html'

	#D:\\VS RANDOM SHIT\\SD_test\\Server Licenta\\continut
	numeFisier = 'F:\\Proiecte - Visual Studio+Code\\SD_test\\Server Licenta\\continut' + numeResursa
	
	file = None
	
	try:
		
		file = open(numeFisier,'rb')
		numeExtensie = numeFisier[numeFisier.rfind('.')+1:]
		
		tipuriMedia = {
			'html': 'text/html; charset=utf-8',
			'css': 'text/css; charset=utf-',
			'js': 'text/javascript; charset=utf-8',
			'png': 'image/png',
			'jpg': 'image/jpeg',
			'jpeg': 'image/jpeg',
			'gif': 'image/gif', 
			'ico': 'image/x-icon',
			'xml': 'application/xml; charset=utf-8',
			'json': 'application/json; charset=utf-8'
		}
		tipMedia = tipuriMedia.get(numeExtensie,'text/plain; charset=utf-8')
		
		
		clientsocket.sendall(b'HTTP/1.1 200 OK\r\n')
		clientsocket.sendall(('Content-Length: ' + str(os.stat(numeFisier).st_size) + '\r\n').encode())
		clientsocket.sendall(('Content-Type: ' + tipMedia +'\r\n').encode())
		clientsocket.sendall(b'Server: Server Licenta\r\n')
		clientsocket.sendall(b'\r\n')
		
		buf = file.read(1024)
		
		while (buf):
			clientsocket.send(buf)
			buf = file.read(1024)
			
	except IOError:
		
		msg = 'Eroare! Resursa: ' + numeResursa + ' nu exista bruh'
		print(msg)
		clientsocket.sendall(b'HTTP/1.1 404 Not Found\r\n')
		clientsocket.sendall(('Content-Length: ' + str(len(msg.encode('utf-8'))) + '\r\n').encode())
		clientsocket.sendall(b'Content-Type: text/plain; charset=utf-8\r\n')
		clientsocket.sendall(b'Server: Server Licenta\r\n')
		clientsocket.sendall(b'\r\n')
		clientsocket.sendall(msg.encode())

	finally:
		if file is not None:
			file.close()
			
	clientsocket.close()

