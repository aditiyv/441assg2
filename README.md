# 🚀 Meme-Generating Proxy Server

A TCP-based HTTP proxy server that intercepts client requests, modifies HTML responses by replacing images with memes, and serves a special Easter egg page when a request for google.ca is detected. Built with Python socket programming and multithreading, this proxy injects fun into everyday browsing while demonstrating networking and web data manipulation concepts.

The project supports:
- HTTP Proxying: Forwards client HTTP requests and responses.
- Image Interception & Replacement: Modifies HTML pages by replacing 50% of <img> tags with memes from a pre-defined folder.
- Image Format Support: Handles JPEG, PNG, GIF, WebP, and SVG formats.
- Personalized Easter Egg: Displays a custom meme page for google.ca requests.
- Robust Error Handling: Manages missing Host headers, unsupported HTTPS requests, empty meme folders, and more.

## 📌 Table of Contents
- Prerequisites
- Running the Proxy Server
- Configuring the Browser for Testing
- Testing the Proxy
- Assumptions and Limitations

## 🔧 Prerequisites
Before running the project, make sure you have Python 3 installed. You can check by running:

```bash
python --version
```

Ensure you have the Python source file (meme_proxy_server.py) downloaded.
A folder named memes/ must be present in the same directory. This folder should contain at least 15 meme images in supported formats (JPEG, PNG, GIF, WebP, or SVG).

## 🎯 Running the Proxy Server

To run the server, use the command:

```bash
python3 meme_proxy_server.py
```

This proxy server listens on 127.0.0.1 at port 8080.

## 🌐 Configuring the Browser for Testing
- Open Firefox.
- Configure Proxy Settings:
    - Go to your browser’s network or proxy settings.
    - Set the HTTP proxy to 127.0.0.1 and port to 8080.

## 🧪 Testing the Proxy
- Browser Testing:
    - Visit http://httpbin.org/ to see meme replacements on webpages.
    - Visit http://google.ca/ to trigger the special Easter egg page.

- Testing HTTPS Requests with cURL:
    - To verify that the proxy correctly handles unsupported HTTPS requests without crashing, open a terminal and run:

```bash
curl -v -x 127.0.0.1:8080 https://www.google.ca/
```
The command should result in an error message (e.g., "connect failed" or a 501 error response), demonstrating that the proxy gracefully rejects HTTPS requests.

- General Robustness:
    - The proxy is designed to handle missing host headers, malformed requests, and an empty meme folder gracefully, ensuring stable operation under various conditions.

## ✨ Assumptions and Limitationsn 
- The proxy handles only HTTP; HTTPS requests are rejected.
- Image replacement occurs randomly (50% probability).
- The proxy exits if the meme folder is empty, ensuring robustness.
- Proper browser proxy configuration is necessary for testing.