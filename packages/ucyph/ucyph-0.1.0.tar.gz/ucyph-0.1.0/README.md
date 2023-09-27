# ucyph
Encrypt and Decrypt text from the command line using ciphers that are common and/or historical. 

## Table of Contents

## Setup
Coming soon.

## Usage

### Examples:
The basic syntax for a command includes the cipher to be used, the text to be used, and whether to encrypt or decrypt the text. Here is an example command:
```shell
ucyph -c 5 -k 'password' -s 'Hello World' -Ev
```

This command calls the ```Vigenere``` cipher via the ```-c``` flag with a **key** of 'password', **encrypts** the text via the ```-E``` flag, and prints a verbose version of the output. 
