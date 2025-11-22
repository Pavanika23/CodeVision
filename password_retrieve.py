def caesar_cipher_decrypt(ciphertext, shift):
    plaintext = ""
    for char in ciphertext:
        if char.isalpha():
            shifted = ord(char) - shift
            if char.islower():
                if shifted < ord('a'):
                    shifted += 26
            elif char.isupper():
                if shifted < ord('A'):
                    shifted += 26
            plaintext += chr(shifted)
        else:
            plaintext += char
    return plaintext
#Enter your encrypted password from csv file
ciphertext = "YOUR PASSWORD HERE"

shift = 15

plaintext = caesar_cipher_decrypt(ciphertext, shift)
print(f"Decrypted passowrd is : {plaintext}")
