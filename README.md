```
           _ _         _ _            
     /\   | | |       | (_)           
    /  \  | | | ____ _| |_ _ __   ___ 
   / /\ \ | | |/ / _` | | | '_ \ / _ \
  / ____ \| |   < (_| | | | | | |  __/
 /_/    \_\_|_|\_\__,_|_|_|_| |_|\___|
```

# Alkaline NVT
Encrypted Client/Server Network Virtual Terminal (NVT) made in Python3.

# NOTICE
- I AM NOT RESPONSIBLE FOR ANY USER MISUSE OF THE CODE IN THIS REPOSITORY!
- If you're using it, only use it on system(s) you have the legal authority to use this on.

## Features
- The connection is encrypted via Python's module for the [libsodium's/NaCl's](https://pypi.org/project/PyNaCl/) implementation of the XSalsa20 Encryption scheme
- Has server debug messages can be shown by setting the `-d` or `--debug` optional flags to 1.
  - 0 is the default meaning it will not show these debug statements.
- Can upload files from the client's machine to wherever the server's cwd is using `upload path-to-file-on-clients-machine` 
- Can download files from the server to the client's directory where the shell is running using `download path-to-file`

# How to Use
1. Run `pip install -r requirements.txt` to get the required modules to run both the server and client.
2. Setup the server first using `python3 alkaline-server.py -a 'ip-address-to-bind-to' -p 'port-number'`without the quotes.
3. Next, connect to the server by using `python3 alkaline-client.py -a 'ip-address-of-server' -p 'port-number-of-server'`without the quotes.
4. (OPTIONAL) If you want to run either the client or server as an executable on a system, then you can run `pip install pyinstaller` and use `pyinstaller --onefile alkaline-client.py/server.py` and you will get the executable.

# Contributing
If you would like to know how you can contribute to this project then you can checkout ![CONTRIBUTING.md](https://github.com/Swangeon/Alkaline-NVT/blob/master/CONTRIBUTING.md)
