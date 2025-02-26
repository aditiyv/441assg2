import socket
import threading
import random
import os
import base64
import re

#configuration for the proxy server
PROXY_HOST = '127.0.0.1' #IP address the proxy server will bind to
PROXY_PORT = 8080 #the port number the proxy server will listen on
MEME_FOLDER = 'memes/' #folder where meme images are stored
BUFFER_SIZE = 8192 #buffer size for socket communication

#load memes into memory
meme_cache = {}
if not os.path.exists(MEME_FOLDER):
    print(f"Meme folder '{MEME_FOLDER}' does not exist.")
else:
    for meme in os.listdir(MEME_FOLDER):
        if meme.lower().endswith(('jpg', 'jpeg', 'png', 'gif', 'webp', 'svg')):  #check for valid image extensions
            try:
                with open(os.path.join(MEME_FOLDER, meme), 'rb') as f:
                    meme_cache[meme] = f.read()  #read and store the meme data in the cache
            except Exception as e:
                print(f"Error loading meme {meme}: {e}")  #print error message if loading fails

if not meme_cache:
    print("No memes loaded! Exiting.")
    exit(1)

def get_random_meme():
    #select a random meme from the cache
    meme_key = random.choice(list(meme_cache.keys()))
    meme_data = meme_cache[meme_key]
    
    #determine the mime type based on the file extension
    ext = os.path.splitext(meme_key)[1].lower()
    if ext in ['.jpg', '.jpeg']:
        mime_type = 'image/jpeg'
    elif ext == '.png':
        mime_type = 'image/png'
    elif ext == '.gif':
        mime_type = 'image/gif'
    elif ext == '.webp':
        mime_type = 'image/webp'
    elif ext == '.svg':  # SVG Support
        mime_type = 'image/svg+xml'
    else:
        mime_type = 'application/octet-stream'
    
    #return the meme data and its mime type
    return meme_data, mime_type

def encode_meme():
    #get a random meme and encode it in base64
    meme_data, _ = get_random_meme()
    return base64.b64encode(meme_data).decode()

def modify_html_response(body_bytes):
    try:
        #decode HTML body
        html = body_bytes.decode('utf-8', errors='ignore')
    except Exception:
        #return original bytes if decoding fails
        return body_bytes  

    def replace_img(match):
        #replace <img> tag with a random meme with 50% prob
        tag = match.group(0)
        if random.random() < 0.5: #50% probability
            meme_data, mime_type = get_random_meme() #get a random meme
            encoded = base64.b64encode(meme_data).decode() #encode meme in base64
            new_src = f"data:{mime_type};base64,{encoded}"  #create data URL
            new_tag = re.sub(r'src=["\'][^"\']+["\']', f'src="{new_src}"', tag) #replace src attribute
            return new_tag #return modified tag
        return tag 

    modified_html = re.sub(r'<img\s+[^>]*src=["\'][^"\']+["\'][^>]*>', replace_img, html, flags=re.IGNORECASE)  #replace <img> tags in the HTML 
    return modified_html.encode('utf-8') #return modified HTML as bytes

def replace_image_response(header, body):
    meme_data, mime_type = get_random_meme() #get a random meme
    header_str = header.decode(errors='ignore') #decode header bytes to string
    header_str = re.sub(r'Content-Length:\s*\d+', f'Content-Length: {len(meme_data)}', header_str, flags=re.IGNORECASE) #update Content-Length
    header_str = re.sub(r'Content-Type:\s*image/[\w]+', f'Content-Type: {mime_type}', header_str, flags=re.IGNORECASE) #update Content-Type
    return header_str.encode() + b'\r\n\r\n' + meme_data #return modified response

def handle_client(client_socket):
    try:
        request = client_socket.recv(BUFFER_SIZE)  #receive the request from the client
        if not request:  #if no data is received, close the connection
            client_socket.close()
            return

        try:
            request_lines = request.decode(errors='ignore').split('\r\n')  #decode the request and split into lines
        except Exception:  #if decoding fails, close the connection
            client_socket.close()
            return

        if len(request_lines) == 0:  #if no lines are present, close the connection
            client_socket.close()
            return

        first_line = request_lines[0].split()  #split the first line of the request
        if len(first_line) < 2:  #if the first line is invalid, close the connection
            client_socket.close()
            return

        method, url = first_line[0], first_line[1]  #extract the method and URL from the first line

        # if the method is CONNECT, return an error response indicating HTTPS tunnel failure
        if method.upper() == "CONNECT":
            response = ("HTTP/1.1 502 Bad Gateway\r\n"
                        "Content-Type: text/plain\r\n\r\n"
                        "CONNECT tunnel failed")
            client_socket.send(response.encode())
            client_socket.close()
            return

        host = None
        for line in request_lines:  #extract the host header from the request
            if line.lower().startswith('host:'):  #search for host header
                parts = line.split()  #split line
                if len(parts) > 1:
                    host = parts[1].strip()  #extract host value
                break

        if "google.ca" in url.lower() or (host and "google.ca" in host.lower()):  #if request is for google.ca
            # Choose a random meme header line
            meme_headers = [
                "You typed 'Google' but your heart said 'Meme'",
                "Stop trying to access Google - You Belong Here Now",
                "Google was a lie, memes are the only truth",
                "Think of this as a CAPTCHA, but for your soul",
                "This server is optimized for high-speed meme delivery, Google could never",
                "You don\'t need search results, you need serotonin",
                "Google is overrated, memes are forever",
                "You were looking for Google, but you found yourself",
                "You came for Google, but you stayed for the memes"
            ]
            header_line = random.choice(meme_headers)  #choose a random meme header line
            meme_data, mime_type = get_random_meme()
            encoded = base64.b64encode(meme_data).decode()  #encode meme in base64
            #create a surprise page with the meme
            #basic html code for easter egg page
            surprise_page = f"""  
HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n
<html>
<head>
  <title>Google, whooo?</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    html, body {{
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      background-color: #000;
      color: #fff;
      font-family: Arial, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }}
    h1 {{
      margin: 10px 0;
      font-size: 2em;
    }}
    img {{
      max-width: 100%;
      max-height: calc(100vh - 80px); /* Adjust based on header size */
      object-fit: contain;
    }}
  </style>
</head>
<body>
  <h1>{header_line}</h1>
  <img src="data:{mime_type};base64,{encoded}" alt="Meme" />
</body>
</html>
"""
            client_socket.send(surprise_page.encode())  #send the surprise page to the client
            client_socket.close()  #close the connection
            return

        if url.startswith("https://"):  #if the request is for HTTPS, send error response
            response = ("HTTP/1.1 501 Not Implemented\r\n"
                        "Content-Type: text/plain\r\n\r\n"
                        "HTTPS is not supported by this proxy.")
            client_socket.send(response.encode())  #send error response
            client_socket.close()
            return

        if not host:  #if host header is missing, send error response
            response = ("HTTP/1.1 400 Bad Request\r\n"
                        "Content-Type: text/plain\r\n\r\n"
                        "Host header missing.")
            client_socket.send(response.encode())  #send error response
            client_socket.close()
            return

        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #create a socket to connect to the remote server
        remote_socket.settimeout(10)  #set timeout for the connection
        try:
            remote_socket.connect((host, 80))  #connect to the remote server
        except Exception:  #if connection fails, send error response
            error_response = ("HTTP/1.1 502 Bad Gateway\r\n"
                              "Content-Type: text/plain\r\n\r\n"
                              "Error connecting to target server.")
            client_socket.send(error_response.encode())
            client_socket.close()
            return

        remote_socket.sendall(request)  #send the request to remote server

        response_data = b""  #initialize response data
        while True:  #receive response data from the remote server
            try:
                chunk = remote_socket.recv(BUFFER_SIZE)  #receive data in chunks
                if not chunk:  #if no data is received, break loop
                    break
                response_data += chunk
            except socket.timeout:  #if timeout occurs, break loop
                break
            except Exception:  #if an error occurs, break loop
                break
        remote_socket.close()  #close the connection to the remote server

        header_end = response_data.find(b'\r\n\r\n')  #find the end of the header
        if header_end == -1:  #if header end isn't found, close connection
            client_socket.send(response_data)  #send the response data to the client
            client_socket.close()
            return

        header = response_data[:header_end]  #extract header
        body = response_data[header_end+4:]  #extract body

        header_str = header.decode(errors='ignore')  #decode header bytes to string
        content_type_match = re.search(r'Content-Type:\s*([^\r\n]+)', header_str, re.IGNORECASE)  #search for content type header
        content_type = content_type_match.group(1).strip() if content_type_match else ""  #extract content type

        modified_response = response_data  #initialize modified response

        if 'text/html' in content_type:  #if the response is HTML, modify the response
            new_body = modify_html_response(body)  #modify the HTML body
            new_length = len(new_body)  #calculate new content length
            header_str = re.sub(r'Content-Length:\s*\d+', f'Content-Length: {new_length}', header_str, flags=re.IGNORECASE)  #update content length
            modified_response = header_str.encode() + b'\r\n\r\n' + new_body  #create modified response

        #for image responses, with 50% probability replace image entirely
        elif content_type.startswith("image/"):
            if random.random() < 0.5:
                modified_response = replace_image_response(header, body)

        client_socket.sendall(modified_response)  #send the modified response to the client
    except Exception as e:  #handle exceptions
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()

def accept_clients(server_socket):
    while True: #accept incoming client connections
        try:
            client_socket, addr = server_socket.accept() #accept client connection
            client_thread = threading.Thread(target=handle_client, args=(client_socket,)) #create a thread to handle the client
            client_thread.daemon = True 
            client_thread.start() #start the thread
        except Exception as e:
            print(f"Error accepting client: {e}") #print error message if accepting client fails

def start_proxy():
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create a socket for the proxy server
        server_socket.bind((PROXY_HOST, PROXY_PORT)) #bind the socket to the host and port
        server_socket.listen(5) #listen for incoming connections
        print(f"Proxy Server running on {PROXY_HOST}:{PROXY_PORT}") #print message indicating server is running
        accept_clients(server_socket) #accept incoming clients
    except Exception as e: #handle exceptions
        print(f"Error starting proxy: {e}")

if __name__ == '__main__':
    start_proxy() #start the proxy server
