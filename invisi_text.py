#!/usr/bin/env python3

"""
InvisiText: Linguistic Steganography Tool

This script embeds a secret message within a "carrier" text file using
zero-width Unicode characters (U+200B and U+200C) to represent binary.
The resulting text is visually identical to the original carrier text
but contains the hidden secret message.

This tool can be run from the command line.

Encoding Example:
    python invisi_text.py encode -c carrier.txt -s secret.txt -o output.txt

Decoding Example:
    python invisi_text.py decode -i output.txt
"""

import argparse
import sys
import os

# --- Configuration ---

# We use two different zero-width characters to represent 0 and 1.
# U+200B: Zero Width Space (ZWS)
ZERO_BIT = u'\u200B'
# U+200C: Zero Width Non-Joiner (ZWNJ)
ONE_BIT = u'\u200C'

# We use a non-printable character as an End-of-Transmission (EOT) marker.
# This tells the decoder when the secret message is complete.
EOT_CHAR = u'\u0004'

# --- Core Functions ---

def _message_to_binary(message: str) -> str:
    """
    Converts a UTF-8 string into its binary representation (a string of '0's and '1's).
    
    Args:
        message: The string to convert.
    
    Returns:
        A string representing the binary data.
    """
    try:
        # Encode the message to bytes using UTF-8
        message_bytes = message.encode('utf-8')
        
        # Convert each byte into its 8-bit binary representation
        # zfill(8) ensures each byte is represented by 8 bits
        return ''.join(format(byte, '08b') for byte in message_bytes)
    except Exception as e:
        print(f"Error converting message to binary: {e}", file=sys.stderr)
        return ""

def _binary_to_message(binary_stream: str) -> str:
    """
    Converts a binary string ('0's and '1's) back into a UTF-8 string.
    
    Args:
        binary_stream: The binary string to convert.
    
    Returns:
        The decoded UTF-8 string.
    """
    try:
        byte_list = []
        # Process the stream in 8-bit (1-byte) chunks
        for i in range(0, len(binary_stream), 8):
            byte_str = binary_stream[i:i+8]
            
            # Stop if we have an incomplete byte at the end
            if len(byte_str) < 8:
                break
                
            # Convert the binary byte string to an integer
            byte_int = int(byte_str, 2)
            
            # Check for the EOT marker
            if byte_int == ord(EOT_CHAR):
                break
                
            byte_list.append(byte_int)
        
        # Convert the list of byte integers into a bytes object
        # and then decode it back to a string
        return bytes(byte_list).decode('utf-8', 'ignore')
    except Exception as e:
        print(f"Error converting binary to message: {e}", file=sys.stderr)
        return ""

# --- Main API ---

def encode(carrier_text: str, secret_message: str) -> str:
    """
    Embeds a secret message into a carrier text.
    
    Args:
        carrier_text: The public text to hide the message in.
        secret_message: The secret message to hide.
        
    Returns:
        A string of the carrier text with the secret message embedded,
        or an empty string if encoding failed.
    """
    if not carrier_text:
        print("Error: Carrier text cannot be empty.", file=sys.stderr)
        return ""
        
    if not secret_message:
        print("Error: Secret message cannot be empty.", file=sys.stderr)
        return ""

    # Append the EOT marker so the decoder knows when to stop
    secret_with_eot = secret_message + EOT_CHAR
    secret_binary = _message_to_binary(secret_with_eot)
    
    if not secret_binary:
        print("Error: Could not convert secret message to binary.", file=sys.stderr)
        return ""

    # We embed one bit of the secret message *between* each word
    # of the carrier text.
    carrier_words = carrier_text.split(' ')
    
    # Check if the carrier text is long enough to hold the message
    # We need len(words) - 1 spaces to hide the bits.
    if len(secret_binary) > len(carrier_words) - 1:
        print("Error: Carrier text is not long enough to hold the secret message.", file=sys.stderr)
        print(f"    Carrier capacity (bits): {len(carrier_words) - 1}", file=sys.stderr)
        print(f"    Secret message size (bits): {len(secret_binary)}", file=sys.stderr)
        return ""

    print(f"Successfully converted secret message to {len(secret_binary)}-bit stream.")
    print(f"Carrier text has {len(carrier_words) - 1} bit-slots available.")

    # Build the output word by word
    output_words = []
    
    for i, word in enumerate(carrier_words):
        output_words.append(word)
        
        # If we still have bits to hide, add one
        if i < len(secret_binary):
            bit = secret_binary[i]
            bit_char = ONE_BIT if bit == '1' else ZERO_BIT
            output_words.append(bit_char)

    # Re-join the text with spaces. The zero-width characters
    # will be placed right after the space, before the next word.
    stego_text = ' '.join(output_words)
    
    return stego_text

def decode(stego_text: str) -> str:
    """
    Extracts a secret message from steganographic text.
    
    Args:
        stego_text: The text containing the hidden message.
    
    Returns:
        The extracted secret message.
    """
    if not stego_text:
        print("Error: Steganographic text cannot be empty.", file=sys.stderr)
        return ""

    print("Scanning text for hidden bits...")
    bit_stream = ""
    
    # Scan every character in the text
    for char in stego_text:
        if char == ZERO_BIT:
            bit_stream += '0'
        elif char == ONE_BIT:
            bit_stream += '1'
            
    if not bit_stream:
        print("No hidden message found.", file=sys.stderr)
        return ""
        
    print(f"Found {len(bit_stream)}-bit hidden stream. Decoding...")
    
    # Convert the bit stream back to a message
    return _binary_to_message(bit_stream)

# --- Command-Line Interface ---

def main():
    """
    Main function to parse arguments and run the tool.
    """
    # Set up the main parser
    parser = argparse.ArgumentParser(
        description="InvisiText: Hide secret messages in plain text using zero-width steganography.",
        epilog="Example: python invisi_text.py encode -c carrier.txt -s secret.txt -o output.txt"
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True, help="Sub-command to run")
    
    # --- Encoder Sub-parser ---
    parser_encode = subparsers.add_parser("encode", help="Hide a secret message in a carrier text")
    parser_encode.add_argument(
        "-c", "--carrier", 
        metavar="CARRIER_FILE",
        type=str, 
        required=True, 
        help="Path to the carrier .txt file (the text to hide inside)"
    )
    parser_encode.add_argument(
        "-s", "--secret", 
        metavar="SECRET_FILE",
        type=str, 
        required=True, 
        help="Path to the secret .txt file (the message to hide)"
    )
    parser_encode.add_argument(
        "-o", "--output", 
        metavar="OUTPUT_FILE",
        type=str, 
        required=True, 
        help="Path to write the new steganographic .txt file"
    )
    
    # --- Decoder Sub-parser ---
    parser_decode = subparsers.add_parser("decode", help="Extract a secret message from a steganographic text")
    parser_decode.add_argument(
        "-i", "--input", 
        metavar="INPUT_FILE",
        type=str, 
        required=True, 
        help="Path to the steganographic .txt file to decode"
    )
    
    args = parser.parse_args()
    
    # --- Execute Commands ---
    
    if args.command == "encode":
        try:
            print("--- Running InvisiText Encoder ---")
            
            # Read carrier file
            if not os.path.exists(args.carrier):
                raise FileNotFoundError(f"Carrier file not found: {args.carrier}")
            with open(args.carrier, 'r', encoding='utf-8') as f:
                carrier_text = f.read()
            
            # Read secret file
            if not os.path.exists(args.secret):
                raise FileNotFoundError(f"Secret file not found: {args.secret}")
            with open(args.secret, 'r', encoding='utf-8') as f:
                secret_message = f.read()
                
            # Perform encoding
            stego_text = encode(carrier_text, secret_message)
            
            if stego_text:
                # Write the output
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(stego_text)
                print(f"Successfully encoded secret message into: {args.output}")
                
                # Verification
                original_size = os.path.getsize(args.carrier)
                stego_size = os.path.getsize(args.output)
                print(f"Original size: {original_size} bytes")
                print(f"Encoded size:  {stego_size} bytes (difference is the hidden data)")

        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred during encoding: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "decode":
        try:
            print("--- Running InvisiText Decoder ---")
            
            # Read steganographic file
            if not os.path.exists(args.input):
                raise FileNotFoundError(f"Input file not found: {args.input}")
            with open(args.input, 'r', encoding='utf-8') as f:
                stego_text = f.read()
            
            # Perform decoding
            secret_message = decode(stego_text)
            
            if secret_message:
                print("\n--- DECODED MESSAGE START ---")
                print(secret_message)
                print("---  DECODED MESSAGE END  ---")
            else:
                print("Could not decode a message.")
                
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred during decoding: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
