#!/usr/bin/env python3

import argparse

from src.ucyph.ciphers import *

FUNCTION_MAP = {'3': caesar,
                '47': rot47,
                '13': rot13,
                '5': vigenere,
                '11': playfair, }


def func_names(a):
    FUNCTION_NAMES = {'3': 'Caesar',
                      '13': 'Rot-13',
                      '47': 'Rot-47',
                      '5': 'Vigenere',
                      '11': 'Playfair'}
    return FUNCTION_NAMES[a]


def parse_args():
    parser = argparse.ArgumentParser(description='Encrypt a string.')
    parser.add_argument('-c', '--code', required=True, choices=FUNCTION_MAP.keys(), metavar='',
                        help='Encrypt message using the given cipher')
    parser.add_argument('-s', '--string', required=True, metavar='', help='String to be Encrypted/Decrypted')
    parser.add_argument('-k', '--key', metavar='', help='Key/Password for the cipher')
    en_de = parser.add_mutually_exclusive_group()
    en_de.add_argument('-D', '--decode', action='store_true', help='decode the string using current cipher')
    en_de.add_argument('-E', '--encode', action='store_true', help='encode the string using current cipher')
    volume = parser.add_mutually_exclusive_group()
    volume.add_argument('-q', '--quiet', action='store_true', help='print quiet')
    volume.add_argument('-v', '--verbose', action='store_true', help='print verbose')
    return parser.parse_args()


def main():
    args = parse_args()
    func = FUNCTION_MAP[args.code]
    encode = args.encode if args.encode or args.decode else True
    final = func(args.string, args.key, encode) if args.key else func(args.string, encode)

    if args.quiet:
        print(final)
    elif args.verbose:
        print(f'Using the {func_names(args.code)} Cipher to encrypt \"{args.string}\" results in:\n\n\"{final}\"')
    else:
        print(f'The encrypted text is: \"{final}\"')


if __name__ == '__main__':
    main()
