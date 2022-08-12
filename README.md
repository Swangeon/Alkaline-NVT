# Alkaline Network Shell
A Client/Server Networking Shell!
Made in Python3 and tested in Linux

# NOTICE/CAUTION/ATTENTION
- I AM NOT RESPONSIBLE FOR ANY USER MISUSE OF THE CODE IN THIS REPOSITORY!
- If you're using it, only use it on your own system/systems you have legal authority to use/pentest

# How to Use
1. Setup the server first using `python3 alkaline-server.py -a 'ip-address-to-bind-to' -p 'port-number'`without the quotes
2. Next, connect to the server by using `python3 alkaline-client.py -a 'ip-address-of-server' -p 'port-number-of-server'`without the quotes

## Features
- Can output nice messages to the terminal or can be ran in the background using the `-o` or `--output` optional flags
  - 1 is the default and will show output to the terminal while 0 will hide output
- The connection is encrypted via [libsodium's](https://doc.libsodium.org/) implementation of the XSalsa20 Encryption scheme
- Can upload files from the clients machine to wherever the server's cwd is using `upload path-to-file-on-clients-machine` 
- Can download files from the server to the client's directory where the shell is running using `download path-to-file`
- Can support up to 5 simultaneous users per server

