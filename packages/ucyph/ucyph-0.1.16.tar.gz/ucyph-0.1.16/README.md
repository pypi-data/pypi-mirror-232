# ucyph
Encrypt and Decrypt text from the command line using ciphers that are common and/or historical. 

## Table of Contents

## Installation
```bash
pip install ucyph
```

## Usage

### Examples:

This command calls the ```Vigenere``` cipher with a **key** of 'password', and encrypts the text from **hello.txt** in place as an output file is not specified.
```shell
ucyph 5 hello.txt -k 'password'
```

To decrypt the text, simply add ```-d``` flag to the end of the command:
```shell
ucyph 5 hello.txt -k 'password' -d
```

This command calls the ```Playfair``` cipher with a **key** of 'password', and writes the encrypted text from **hello.txt** into **output.txt**.
```shell

ucyph 11 hello.txt -o output.txt -k password
```
Now, to decrypt the text from **output.txt**, simply add ```-d``` flag to the end of the command(note that an output file is not specified):
```shell
ucyph 11 output.txt -k password -d
```

## Ciphers

#### Cipher list and usage codes:
| Cipher   | Usage Code  | Requires Key |
|----------|-------------|--------------|
| Caesar   | 3           | No           |
| Vigenere | 5           | Yes          |
| Playfair | 11          | Yes          |
| Rot-13   | 13          | No           |
| Rot-47   | 47          | No           |




