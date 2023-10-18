# Alkaline NVT
Encrypted Client/Server Network Virtual Terminal (NVT) made in Python3.

# NOTICE/CAUTION/ATTENTION
- I AM NOT RESPONSIBLE FOR ANY USER MISUSE OF THE CODE IN THIS REPOSITORY!
- If you're using it, only use it on your own system/systems you have legal authority to use/pentest

## Features
- Can output nice messages to the terminal or can be ran in the background using the `-o` or `--output` optional flags
  - 1 is the default and will show output to the terminal while 0 will hide output
- The connection is encrypted via python's module for the [libsodium's/NaCl's](https://pypi.org/project/PyNaCl/) implementation of the XSalsa20 Encryption scheme
- Can upload files from the clients machine to wherever the server's cwd is using `upload path-to-file-on-clients-machine` 
- Can download files from the server to the client's directory where the shell is running using `download path-to-file`
- Can support up to 5 simultaneous users per server

# How to Use
1. Run `pip install -r requirements.txt` to get the required modules to run both the server and client.
2. Setup the server first using `python3 alkaline-server.py -a 'ip-address-to-bind-to' -p 'port-number'`without the quotes.
3. Next, connect to the server by using `python3 alkaline-client.py -a 'ip-address-of-server' -p 'port-number-of-server'`without the quotes.
4. (OPTIONAL) If you want to run either the client or server as an executable on a system, then you can run `pip install pyinstaller` and use `pyinstaller --onefile alkaline-client.py/server.py` and you will get the executable.
