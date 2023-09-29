#!/usr/bin/env python3

import hashlib
import binascii
import bcrypt
import re
import os
import curses
import sqlite3
import itertools
import multiprocessing
import pyopencl as cl
import pyopencl.array as cl_array
import numpy as np
import time
from crdt import show_credits

# Check if a GPU is available
try:
    ctx = cl.create_some_context()
    queue = cl.CommandQueue(ctx)
    GPU_AVAILABLE = True
except:
    GPU_AVAILABLE = False

# Initialize SQLite database for storing cracked passwords
db_conn = sqlite3.connect("hash_cracker.db")
db_cursor = db_conn.cursor()
db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS cracked_passwords (
        hash_type TEXT,
        hash_value TEXT,
        password TEXT
    )
""")
db_conn.commit()


def identify_hash_type(hash_str):
    hash_patterns = {
        r'^[0-9a-fA-F]{32}$': 'MD5',
        r'^[0-9a-fA-F]{40}$': 'SHA-1',
        r'^[0-9a-fA-F]{64}$': 'SHA-256',
        r'^[0-9a-fA-F]{128}$': 'SHA-512',
        r'^[0-9a-fA-F]{8}$': 'CRC32',
        r'^\$2[ayb]\$[0-9]{2}\$[A-Za-z0-9./]{53}$': 'bcrypt',  # bcrypt hashes
    }

    for pattern, hash_type in hash_patterns.items():
        if re.match(pattern, hash_str):
            return hash_type

    return 'Unknown'

def hash_info(hash_type):
    hash_info_dict = {
        'MD5': 'MD5 (Message Digest Algorithm 5) is a widely used cryptographic hash function that produces a 32-character hexadecimal number.',
        'SHA-1': 'SHA-1 (Secure Hash Algorithm 1) is a cryptographic hash function that produces a 40-character hexadecimal number.',
        'SHA-256': 'SHA-256 (Secure Hash Algorithm 256-bit) is a cryptographic hash function that produces a 64-character hexadecimal number.',
        'SHA-512': 'SHA-512 (Secure Hash Algorithm 512-bit) is a cryptographic hash function that produces a 128-character hexadecimal number.',
        'CRC32': 'CRC32 (Cyclic Redundancy Check 32) is a non-cryptographic hash function that produces an 8-character hexadecimal number.',
        'bcrypt': 'bcrypt is a password hashing function used for secure password storage. It produces a complex hash with a salt and cost factor.',
        'Unknown': 'The hash type is unknown or not supported by this script.'
    }

    return hash_info_dict.get(hash_type, 'Unknown hash type.')

def verify_md5(hash_str, password):
    md5_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
    return hash_str == md5_hash

def verify_sha1(hash_str, password):
    sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest()
    return hash_str == sha1_hash

def verify_sha256(hash_str, password):
    sha256_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return hash_str == sha256_hash

def verify_sha512(hash_str, password):
    sha512_hash = hashlib.sha512(password.encode('utf-8')).hexdigest()
    return hash_str == sha512_hash

def verify_crc32(hash_str, password):
    try:
        crc32_hash = '{:08x}'.format(binascii.crc32(password.encode('utf-8')) & 0xFFFFFFFF)
        return hash_str.lower() == crc32_hash
    except Exception as e:
        return False

def verify_bcrypt(hash_str, password):
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hash_str.encode('utf-8'))
    except Exception as e:
        return False

def crack_with_wordlist(hash_str, hash_type, wordlist):
    if hash_type == 'MD5':
        for word in wordlist:
            if verify_md5(hash_str, word):
                return word
    elif hash_type == 'SHA-1':
        for word in wordlist:
            if verify_sha1(hash_str, word):
                return word
    elif hash_type == 'SHA-256':
        for word in wordlist:
            if verify_sha256(hash_str, word):
                return word
    elif hash_type == 'SHA-512':
        for word in wordlist:
            if verify_sha512(hash_str, word):
                return word
    elif hash_type == 'CRC32':
        for word in wordlist:
            if verify_crc32(hash_str, word):
                return word
    elif hash_type == 'bcrypt':
        for word in wordlist:
            if verify_bcrypt(hash_str, word):
                return word
    return None

def crack_with_bruteforce(hash_str, hash_type, charset, max_length, progress_callback=None):
    if hash_type == 'bcrypt':
        return None  # bcrypt hashes can't be cracked with brute force
    from itertools import product
    total_combinations = sum(len(charset) ** i for i in range(1, max_length + 1))
    combinations_checked = 0

    for length in range(1, max_length + 1):
        for candidate in product(charset, repeat=length):
            candidate_str = ''.join(candidate)
            combinations_checked += 1
            if progress_callback:
                progress_callback(combinations_checked, total_combinations)
            
            if hash_type == 'MD5':
                if verify_md5(hash_str, candidate_str):
                    return candidate_str
            elif hash_type == 'SHA-1':
                if verify_sha1(hash_str, candidate_str):
                    return candidate_str
            elif hash_type == 'SHA-256':
                if verify_sha256(hash_str, candidate_str):
                    return candidate_str
            elif hash_type == 'SHA-512':
                if verify_sha512(hash_str, candidate_str):
                    return candidate_str
            elif hash_type == 'CRC32':
                if verify_crc32(hash_str, candidate_str):
                    return candidate_str
    return None

def crack_with_rainbow_table(hash_str, hash_type, rainbow_table):
    if hash_type in rainbow_table:
        return rainbow_table[hash_type]
    return None

def apply_rules_to_wordlist(wordlist, rules):
    modified_wordlist = []
    for word in wordlist:
        for rule in rules:
            modified_word = rule(word)
            modified_wordlist.append(modified_word)
    return modified_wordlist

def estimate_password_strength(password):
    strength = 'Weak'
    if len(password) >= 8:
        strength = 'Moderate'
    if len(password) >= 12:
        strength = 'Strong'
    if any(c.isalpha() for c in password) and any(c.isdigit() for c in password):
        strength = 'Very Strong'
    return strength

def progress_callback(combinations_checked, total_combinations):
    percentage = (combinations_checked / total_combinations) * 100
    print(f"Progress: {percentage:.2f}%")

def save_cracked_password(hash_type, hash_value, password):
    db_cursor.execute("INSERT INTO cracked_passwords VALUES (?, ?, ?)", (hash_type, hash_value, password))
    db_conn.commit()

def crack_with_bruteforce_gpu(hash_str, hash_type, charset, max_length):
    if not GPU_AVAILABLE:
        return None  # No GPU available, return None

    if hash_type == 'bcrypt':
        return None  # bcrypt hashes can't be cracked with brute force

    total_combinations = sum(len(charset) ** i for i in range(1, max_length + 1))
    combinations_checked = 0

    def generate_passwords():
        for length in range(1, max_length + 1):
            for candidate in itertools.product(charset, repeat=length):
                yield ''.join(candidate)

    def hash_passwords(passwords):
        result = np.empty(len(passwords), dtype=np.uint32)
        cl_passwords = np.array(passwords, dtype=np.uint32)
        cl_hash_str = np.array([hash_str] * len(passwords), dtype='S32')
        program = cl.Program(ctx, """
            __kernel void hash_passwords(__global const char *hash_str, __global const unsigned int *passwords,
            __global unsigned int *result) {
                int i = get_global_id(0);
                char password[32];
                for (int j = 0; j < 32; j++) {
                    password[j] = 0;
                }
                for (int j = 0; j < 32; j++) {
                    if (hash_str[j] == '\\0') {
                        break;
                    }
                    password[j] = hash_str[j];
                }
                char hash[33];
                for (int j = 0; j < 33; j++) {
                    hash[j] = 0;
                }
                for (int j = 0; j < 32; j++) {
                    hash[j] = password[j];
                }
                result[i] = 0;
                for (int j = 0; j < 32; j++) {
                    hash[j] = password[j];
                }
                for (int j = 0; j < 32; j++) {
                    hash[j] = password[j];
                }
                result[i] = 0;
                for (int j = 0; j < 32; j++) {
                    hash[j] = password[j];
                }
                for (int j = 0; j < 32; j++) {
                    hash[j] = password[j];
                }
                result[i] = 0;
                for (int j = 0; j < 32; j++) {
                    hash[j] = password[j];
                }
            }
        """).build()
        mf = cl.mem_flags
        cl_passwords_buffer = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=cl_passwords)
        cl_hash_str_buffer = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=cl_hash_str)
        cl_result_buffer = cl.Buffer(ctx, mf.WRITE_ONLY, result.nbytes)

        program.hash_passwords(queue, passwords.shape, None, cl_hash_str_buffer, cl_passwords_buffer, cl_result_buffer)
        cl.enqueue_copy(queue, result, cl_result_buffer).wait()

        return result

    passwords = list(generate_passwords())
    passwords_hashed = hash_passwords(passwords)

    for i in range(len(passwords)):
        combinations_checked += 1
        if progress_callback:
            progress_callback(combinations_checked, total_combinations)

        if passwords_hashed[i] == int(hash_str, 16):
            return passwords[i]

    return None

def crack_with_bruteforce_cpu(hash_str, hash_type, charset, max_length):
    if hash_type == 'bcrypt':
        return None  # bcrypt hashes can't be cracked with brute force

    total_combinations = sum(len(charset) ** i for i in range(1, max_length + 1))
    combinations_checked = 0

    def generate_passwords():
        for length in range(1, max_length + 1):
            for candidate in itertools.product(charset, repeat=length):
                yield ''.join(candidate)

    for password in generate_passwords():
        combinations_checked += 1
        if progress_callback:
            progress_callback(combinations_checked, total_combinations)

        hashed_password = hashlib.md5(password.encode()).hexdigest()  # Use MD5 as an example
        if hashed_password == hash_str:
            return password

    return None

def generate_wordlist():
    wordlist_file = input("Enter the path to save the wordlist file: ").strip()
    charset = input("Enter the character set for wordlist generation (e.g., abc123): ").strip()
    max_length = int(input("Enter the maximum password length to generate: "))

    with open(wordlist_file, 'w') as file:
        for length in range(1, max_length + 1):
            for candidate in itertools.product(charset, repeat=length):
                password = ''.join(candidate)
                file.write(password + '\n')

    print(f"Wordlist generated and saved to {wordlist_file}")

def text_to_hashes(text):
    print("Choose a hash algorithm:")
    print("1. MD5")
    print("2. SHA-1")
    print("3. SHA-256")
    print("4. SHA-512")
    
    choice = input("Enter your choice (1/2/3/4): ").strip()

    if choice == '1':
        algo_name = 'MD5'
        hasher = hashlib.md5
    elif choice == '2':
        algo_name = 'SHA-1'
        hasher = hashlib.sha1
    elif choice == '3':
        algo_name = 'SHA-256'
        hasher = hashlib.sha256
    elif choice == '4':
        algo_name = 'SHA-512'
        hasher = hashlib.sha512
    else:
        print("Invalid choice. Using MD5 by default.")
        algo_name = 'MD5'
        hasher = hashlib.md5

    hashed_text = hasher(text.encode()).hexdigest()
    print(f"{algo_name} Hash: {hashed_text}")
def about():
    disclimer = '''				Disclaimar!

    #crackR is a powerful tool designed for ethical and legal use. It is intended solely for educational and security testing purposes. Unauthorized use for any malicious activities, including unauthorized access to computer systems or networks, is strictly prohibited.

    By using #crackR, you agree to adhere to all applicable local, national, and international laws and regulations. You are solely responsible for ensuring that your use of this tool complies with the laws in your jurisdiction.

    The developers and maintainers of #crackR do not endorse or condone any illegal or unethical activities. Any misuse or unauthorized access to systems or data is a violation of ethical and legal standards.

    Use #crackR responsibly and with the explicit consent of system owners. Always respect the privacy and security of others' data and systems.

    The developers and maintainers of #crackR assume no liability for any misuse or illegal activities performed using this tool. Users are solely responsible for their actions and their consequences.

    Please use #crackR responsibly and for legitimate security and educational purposes only.'''
    print(disclimer)
    curses.wrapper(show_credits)
    
def interactive_mode():
    while True:
        print("\nSelect an option:")
        print("1. Analyze and Crack Hash")
        print("2. View Cracked Passwords")
        print("3. Generate Wordlist")
        print("4. Genarate a Hash")
        print("5. About")
        print("6. Show Credits")
        choice = input(">> ").strip()

        if choice == '1':
            hash_str = input("Enter the hash: ").strip()
            hash_type = identify_hash_type(hash_str)

            if hash_type != 'Unknown':
                print(f"Identified hash type: {hash_type}")
                print(hash_info(hash_type))

                print("\nSelect a cracking method:")
                print("1. Dictionary Attack")
                print("2. Bruteforce Attack (GPU)")
                print("3. Bruteforce Attack (CPU)")
                print("4. Exit")
                attack_choice = input("Enter your choice (1/2/3/4): ").strip()

                if attack_choice == '1':
                    wordlist_file = input("Enter the path to the wordlist file: ").strip()
                    if os.path.isfile(wordlist_file):
                        with open(wordlist_file, 'r') as file:
                            wordlist = [line.strip() for line in file.readlines()]

                        print("\nDo you want to apply custom rules to the wordlist? (yes/no)")
                        apply_rules = input().strip().lower()
                        if apply_rules == 'yes':
                            print("\nEnter rules to apply (e.g., lambda x: x[::-1] for reverse):")
                            rules_input = input().strip().split(',')
                            rules = [eval(rule.strip()) for rule in rules_input]
                            wordlist = apply_rules_to_wordlist(wordlist, rules)

                        cracked_word = crack_with_wordlist(hash_str, hash_type, wordlist)
                        if cracked_word:
                            print(f"Cracked Password (Dictionary Attack): {cracked_word}")
                            print(f"Estimated Password Strength: {estimate_password_strength(cracked_word)}")
                            save_cracked_password(hash_type, hash_str, cracked_word)
                        else:
                            print("Password not found in the wordlist.")
                    else:
                        print("Wordlist file not found.")
                elif attack_choice == '2' and GPU_AVAILABLE:
                    charset = input("Enter character set for brute force (e.g., abc123): ").strip()
                    max_length = int(input("Enter maximum password length for brute force: "))
                    start_time = time.time()
                    brute_force_result = crack_with_bruteforce_gpu(hash_str, hash_type, charset, max_length)
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    if brute_force_result:
                        print(f"Cracked Password (Bruteforce Attack - GPU): {brute_force_result}")
                        print(f"Estimated Password Strength: {estimate_password_strength(brute_force_result)}")
                        save_cracked_password(hash_type, hash_str, brute_force_result)
                    else:
                        print("Password not found using GPU brute force.")
                    print(f"Time elapsed: {elapsed_time:.2f} seconds")
                elif attack_choice == '3':
                    charset = input("Enter character set for brute force (e.g., abc123): ").strip()
                    max_length = int(input("Enter maximum password length for brute force: "))
                    start_time = time.time()
                    brute_force_result = crack_with_bruteforce_cpu(hash_str, hash_type, charset, max_length)
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    if brute_force_result:
                        print(f"Cracked Password (Bruteforce Attack - CPU): {brute_force_result}")
                        print(f"Estimated Password Strength: {estimate_password_strength(brute_force_result)}")
                        save_cracked_password(hash_type, hash_str, brute_force_result)
                    else:
                        print("Password not found using CPU brute force.")
                    print(f"Time elapsed: {elapsed_time:.2f} seconds")
                elif attack_choice == '4':
                    pass
                else:
                    print("Invalid choice.")
            else:
                print("Unknown hash type.")
        elif choice == '2':
            db_cursor.execute("SELECT * FROM cracked_passwords")
            cracked_passwords = db_cursor.fetchall()
            if cracked_passwords:
                print("\nCracked Passwords:")
                for row in cracked_passwords:
                    print(f"Hash Type: {row[0]} | Hash Value: {row[1]} | Password: {row[2]}")
            else:
                print("No cracked passwords found.")
        elif choice == '3':
            generate_wordlist()
        elif choice == '4':
            text = input("Enter the text to hash: ").strip()
            text_to_hashes(text)
        elif choice == "5":
            about()
        elif choice == "6":
            curses.wrapper(show_credits)
        elif choice == '0':
            break
        else:
            print("Invalid choice.")
            
def main():
    print("Hash Analyzer and Cracker")
    print('''
                _  _                       _    _____  
              _| || |_                    | |  |  __ \ 
             |_  __  _| ___ _ __ __ _  ___| | _| |__) |
              _| || |_ / __| '__/ _` |/ __| |/ /  _  / 
             |_  __  _| (__| | | (_| | (__|   <| | \ \ 
               |_||_|  \___|_|  \__,_|\___|_|\_\_|  \_/
                                                       
''')
    print('''Please, don't use it for any illigial or malicious purpose. Use this tools at your own risk. The developers and maintainers of #crackR assume no liability for any misuse or illegal activities. Read our user guidelines carefully before use it.''')
    interactive_mode()
    db_conn.close()

if __name__ == "__main__":
    main()

