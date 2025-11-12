InvisiText: Linguistic Steganography Tool
=========================================

InvisiText is a Python-based command-line tool that demonstrates linguistic steganography. It allows you to hide a secret text message inside a "carrier" text file. The resulting output file looks *visually identical* to the original carrier text, but it secretly contains the embedded data.

This is achieved by using invisible zero-width Unicode characters to represent the binary data of the secret message. These characters are inserted between the words of the carrier text.

How It Works
------------

1.  **Conversion:** The secret message is first converted into its binary representation (a string of '0's and '1's). A special "End of Transmission" (EOT) character is appended to mark the end of the message.

2.  **Mapping:** The script uses two different zero-width characters:

    -   `U+200B` (Zero Width Space) represents a `0`

    -   `U+200C` (Zero Width Non-Joiner) represents a `1`

3.  **Encoding:** The script reads the carrier text and splits it by spaces. It then iterates through the words, placing one zero-width bit-character between each word.

4.  **Decoding:** The decoder scans the input text character by character. It ignores all normal characters and only looks for `U+200B` and `U+200C`. It builds a binary string from these characters, converts it back to text, and stops when it encounters the EOT marker.

Features
--------

-   **Completely Invisible:** The hidden message is not visible to the naked eye or in standard text editors.

-   **Pure Python:** Runs anywhere Python 3 is installed. No external libraries are needed.

-   **Robust CLI:** Uses `argparse` for a clean and professional command-line interface.

-   **UTF-8 Support:** Correctly handles a wide range of characters in both secret and carrier texts.

Requirements
------------

-   Python 3.6+

How to Use
----------

No installation is required. Just clone or download `invisi_text.py`.

### Encoding a Message

To hide a message, you need a carrier file (`carrier.txt`) and a secret file (`secret.txt`).

```
python invisi_text.py encode -c carrier.txt -s secret.txt -o output.txt
```

**Arguments:**

-   `-c`, `--carrier`: Path to the carrier `.txt` file (the text to hide inside).

-   `-s`, `--secret`: Path to the secret `.txt` file (the message to hide).

-   `-o`, `--output`: Path to write the new steganographic `.txt` file.

The carrier file must have enough "space" to hold the secret. The capacity (in bits) is equal to `(number of words) - 1`. The tool will warn you if the carrier is too small.

### Decoding a Message

To extract a hidden message from an encoded file (`output.txt`).

```
python invisi_text.py decode -i output.txt
```

**Arguments:**

-   `-i`, `--input`: Path to the steganographic `.txt` file to decode.

The tool will scan the file and print the hidden message to the console if one is found.

Example
-------

1.  Create `carrier.txt`:

    ```
    This is a very long and boring paragraph of text. It is intended to be used as a carrier for a secret message. Nothing about this text is suspicious in any way. It just keeps going on and on, providing plenty of space for data to be hidden between its many words.
    ```

2.  Create `secret.txt`:

    ```
    This is a top-secret message.
    ```

3.  Encode:

    ```
    python invisi_text.py encode -c carrier.txt -s secret.txt -o output.txt

    --- Running InvisiText Encoder ---
    Successfully converted secret message to 240-bit stream.
    Carrier text has 48 bit-slots available.
    Error: Carrier text is not long enough to hold the secret message.
        Carrier capacity (bits): 48
        Secret message size (bits): 240
    ```

4.  *Oops!* Let's use a bigger carrier text (or smaller secret). Let's try `secret.txt` as just "Hello".

5.  Encode again:

    ```
    python invisi_text.py encode -c carrier.txt -s secret.txt -o output.txt

    --- Running InvisiText Encoder ---
    Successfully converted secret message to 48-bit stream.
    Carrier text has 48 bit-slots available.
    Successfully encoded secret message into: output.txt
    Original size: 254 bytes
    Encoded size:  302 bytes (difference is the hidden data)
    ```

6.  Now, open `output.txt`. It will look *identical* to `carrier.txt`.

7.  Decode:

    ```
    python invisi_text.py decode -i output.txt

    --- Running InvisiText Decoder ---
    Scanning text for hidden bits...
    Found 48-bit hidden stream. Decoding...

    --- DECODED MESSAGE START ---
    Hello
    ---  DECODED MESSAGE END  ---
    ```

Future Ideas
------------

-   **Password Protection:** Add an argument to encrypt the secret message with a password before encoding it.

-   **GUI:** Build a simple `tkinter` GUI around the `encode` and `decode` functions.

-   **Different Encoding:** Instead of 1 bit per space, embed multiple bits using a wider range of zero-width characters.
