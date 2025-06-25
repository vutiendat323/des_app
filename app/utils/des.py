import binascii

class DES:
    # Các bảng hoán vị và S-box giữ nguyên
    IP = [
        58, 50, 42, 34, 26, 18, 10, 2,
        60, 52, 44, 36, 28, 20, 12, 4,
        62, 54, 46, 38, 30, 22, 14, 6,
        64, 56, 48, 40, 32, 24, 16, 8,
        57, 49, 41, 33, 25, 17, 9, 1,
        59, 51, 43, 35, 27, 19, 11, 3,
        61, 53, 45, 37, 29, 21, 13, 5,
        63, 55, 47, 39, 31, 23, 15, 7
    ]
    
    IP_INV = [
        40, 8, 48, 16, 56, 24, 64, 32,
        39, 7, 47, 15, 55, 23, 63, 31,
        38, 6, 46, 14, 54, 22, 62, 30,
        37, 5, 45, 13, 53, 21, 61, 29,
        36, 4, 44, 12, 52, 20, 60, 28,
        35, 3, 43, 11, 51, 19, 59, 27,
        34, 2, 42, 10, 50, 18, 58, 26,
        33, 1, 41, 9, 49, 17, 57, 25
    ]
    
    E = [
        32, 1, 2, 3, 4, 5,
        4, 5, 6, 7, 8, 9,
        8, 9, 10, 11, 12, 13,
        12, 13, 14, 15, 16, 17,
        16, 17, 18, 19, 20, 21,
        20, 21, 22, 23, 24, 25,
        24, 25, 26, 27, 28, 29,
        28, 29, 30, 31, 32, 1
    ]
    
    P = [
        16, 7, 20, 21,
        29, 12, 28, 17,
        1, 15, 23, 26,
        5, 18, 31, 10,
        2, 8, 24, 14,
        32, 27, 3, 9,
        19, 13, 30, 6,
        22, 11, 4, 25
    ]
    
    SBOX = [
        # S1
        [
            [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
            [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
            [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
            [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]
        ],
        # S2
        [
            [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
            [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
            [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
            [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]
        ],
        # S3
        [
            [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
            [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
            [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
            [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]
        ],
        # S4
        [
            [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
            [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
            [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
            [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]
        ],
        # S5
        [
            [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
            [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
            [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
            [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]
        ],
        # S6
        [
            [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
            [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
            [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
            [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]
        ],
        # S7
        [
            [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
            [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
            [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
            [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]
        ],
        # S8
        [
            [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
            [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
            [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
            [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]
        ]
    ]
    
    PC1 = [
        57, 49, 41, 33, 25, 17, 9,
        1, 58, 50, 42, 34, 26, 18,
        10, 2, 59, 51, 43, 35, 27,
        19, 11, 3, 60, 52, 44, 36,
        63, 55, 47, 39, 31, 23, 15,
        7, 62, 54, 46, 38, 30, 22,
        14, 6, 61, 53, 45, 37, 29,
        21, 13, 5, 28, 20, 12, 4
    ]
    
    PC2 = [
        14, 17, 11, 24, 1, 5,
        3, 28, 15, 6, 21, 10,
        23, 19, 12, 4, 26, 8,
        16, 7, 27, 20, 13, 2,
        41, 52, 31, 37, 47, 55,
        30, 40, 51, 45, 33, 48,
        44, 49, 39, 56, 34, 53,
        46, 42, 50, 36, 29, 32
    ]
    
    SHIFTS = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
    
    def __init__(self, key, mode='ECB', iv=None):
        if not isinstance(key, bytes) or len(key) != 8:
            raise ValueError("Key must be 8 bytes")
        if mode not in ['ECB', 'CBC', 'OFB', 'CFB']:
            raise ValueError("Mode must be ECB, CBC, OFB, or CFB")
        if mode in ['CBC', 'OFB', 'CFB'] and (not isinstance(iv, bytes) or len(iv) != 8):
            raise ValueError("IV must be 8 bytes for CBC, OFB, CFB modes")
        
        self.key = key
        self.mode = mode
        self.iv = iv
        self.block_size = 8
        self.full_steps = {}
        self.subkeys, self.key_gen_steps = self._generate_subkeys()
        self.full_steps['key_generation'] = self.key_gen_steps
    
    def _bytes_to_bits(self, data):
        """Chuyển bytes thành danh sách bit"""
        bits = []
        for byte in data:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)
        return bits
    
    def _bits_to_bytes(self, bits):
        """Chuyển danh sách bit thành bytes"""
        result = bytearray()
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(8):
                if i + j < len(bits):
                    byte |= bits[i + j] << (7 - j)
            result.append(byte)
        return bytes(result)
    
    def _bits_to_hex(self, bits):
        """Chuyển danh sách bit thành hex"""
        return binascii.hexlify(self._bits_to_bytes(bits)).decode()
    
    def _bits_to_str(self, bits):
        return ''.join(map(str, bits))
    
    def _permute(self, data, table):
        """Hoán vị dữ liệu theo bảng"""
        return [data[i - 1] for i in table]
    
    def _shift_left(self, bits, n):
        """Dịch trái bit"""
        return bits[n:] + bits[:n]
    
    def _generate_subkeys(self):
        """Tạo 16 khóa con từ khóa chính"""
        steps = {
            'initial_key_hex': binascii.hexlify(self.key).decode(),
            'initial_key_bin': self._bits_to_str(self._bytes_to_bits(self.key))
        }
        
        key_bits = self._bytes_to_bits(self.key)
        key_permuted = self._permute(key_bits, self.PC1)
        steps['pc1_output'] = self._bits_to_str(key_permuted)
        
        C, D = key_permuted[:28], key_permuted[28:]
        steps['c0_d0'] = {'c0': self._bits_to_str(C), 'd0': self._bits_to_str(D)}
        
        subkeys = []
        key_rounds = []
        
        c_prev = C
        d_prev = D

        for i, shift in enumerate(self.SHIFTS):
            c_next = self._shift_left(c_prev, shift)
            d_next = self._shift_left(d_prev, shift)
            
            cd_combined = c_next + d_next
            subkey = self._permute(cd_combined, self.PC2)
            subkeys.append(subkey)
            
            key_rounds.append({
                'round': i + 1,
                'shift': shift,
                'c_prev': self._bits_to_str(c_prev),
                'd_prev': self._bits_to_str(d_prev),
                'c_next': self._bits_to_str(c_next),
                'd_next': self._bits_to_str(d_next),
                'cd_combined': self._bits_to_str(cd_combined),
                'subkey': self._bits_to_str(subkey)
            })
            c_prev, d_prev = c_next, d_next

        steps['rounds'] = key_rounds
        return subkeys, steps
    
    def _f_function(self, R, subkey):
        f_steps = {}
        
        expanded = self._permute(R, self.E)
        f_steps['expansion_e'] = self._bits_to_str(expanded)
        
        xor_result = [expanded[i] ^ subkey[i] for i in range(48)]
        f_steps['xor_with_subkey'] = {
            'r_expanded': self._bits_to_str(expanded),
            'subkey': self._bits_to_str(subkey),
            'result': self._bits_to_str(xor_result)
        }
        
        sbox_output_bits = []
        sbox_details = []
        for i in range(8):
            block = xor_result[i*6:(i+1)*6]
            row = (block[0] << 1) + block[5]
            col = (block[1] << 3) + (block[2] << 2) + (block[3] << 1) + block[4]
            val = self.SBOX[i][row][col]
            val_bits = [(val >> j) & 1 for j in range(3, -1, -1)]
            sbox_output_bits.extend(val_bits)
            sbox_details.append({
                "sbox": f"S{i+1}",
                "input": self._bits_to_str(block),
                "row_bits": f"{block[0]}{block[5]}",
                "col_bits": f"{block[1]}{block[2]}{block[3]}{block[4]}",
                "row": row,
                "col": col,
                "output_dec": val,
                "output_bin": self._bits_to_str(val_bits)
            })
        f_steps['sbox_substitution'] = {
            'input': self._bits_to_str(xor_result),
            'details': sbox_details,
            'output': self._bits_to_str(sbox_output_bits)
        }
            
        p_output = self._permute(sbox_output_bits, self.P)
        f_steps['permutation_p'] = self._bits_to_str(p_output)
        
        return p_output, f_steps
    
    def _des_block(self, block, block_num, is_decrypt=False):
        block_steps = {'block_num': block_num, 'initial_block': self._bits_to_str(block)}
        
        permuted_block = self._permute(block, self.IP)
        block_steps['initial_permutation'] = self._bits_to_str(permuted_block)
        
        L, R = permuted_block[:32], permuted_block[32:]
        block_steps['l0_r0'] = {'l0': self._bits_to_str(L), 'r0': self._bits_to_str(R)}
        
        rounds = []
        subkeys_for_op = self.subkeys if not is_decrypt else self.subkeys[::-1]

        for i in range(16):
            L_prev, R_prev = L, R
            
            subkey = subkeys_for_op[i]
            f_output, f_steps = self._f_function(R_prev, subkey)
            
            L = R_prev
            R = [L_prev[j] ^ f_output[j] for j in range(32)]
            
            rounds.append({
                'round': i + 1,
                'l_in': self._bits_to_str(L_prev),
                'r_in': self._bits_to_str(R_prev),
                'f_function': f_steps,
                'l_out': self._bits_to_str(L),
                'r_out': self._bits_to_str(R)
            })

        block_steps['rounds'] = rounds
        
        final_block_swapped = R + L
        block_steps['final_swap'] = self._bits_to_str(final_block_swapped)
        
        final_permuted_block = self._permute(final_block_swapped, self.IP_INV)
        block_steps['final_permutation_inv'] = self._bits_to_str(final_permuted_block)
        
        return final_permuted_block, block_steps
    
    def _pad(self, data):
        """Padding dữ liệu theo PKCS#5/PKCS#7"""
        padding_len = self.block_size - (len(data) % self.block_size)
        padding = bytes([padding_len] * padding_len)
        padded_data = data + padding
        self.full_steps['padding'] = {
            'original_len': len(data),
            'padded_len': len(padded_data),
            'padded_hex': binascii.hexlify(padded_data).decode()
        }
        return padded_data
    
    def _unpad(self, data):
        """Loại bỏ padding"""
        padding_len = data[-1]
        if padding_len > self.block_size or padding_len == 0:
            return data
        return data[:-padding_len]
    
    def _process(self, data, is_decrypt=False):
        process_type = 'Decryption' if is_decrypt else 'Encryption'
        self.full_steps = {'process_type': process_type, 'mode': self.mode}
        
        if is_decrypt:
            self.full_steps['ciphertext_hex'] = binascii.hexlify(data).decode()
        else:
            self.full_steps['plaintext_hex'] = binascii.hexlify(data).decode()
        
        self.full_steps['key_generation'] = self.key_gen_steps

        # Padding / Unpadding
        if is_decrypt:
            blocks = [data[i:i+self.block_size] for i in range(0, len(data), self.block_size)]
        else:
            padded_data = self._pad(data)
            self.full_steps['padding'] = {
                'original_len': len(data),
                'padded_len': len(padded_data),
                'padded_hex': binascii.hexlify(padded_data).decode()
            }
            blocks = [padded_data[i:i+self.block_size] for i in range(0, len(padded_data), self.block_size)]

        processed_blocks_data = []
        block_processing_steps = []

        if self.mode in ['CBC', 'OFB', 'CFB'] and self.iv:
            self.full_steps['iv_hex'] = binascii.hexlify(self.iv).decode()

        # Initialize feedback for modes that need it
        if self.mode in ['CBC', 'OFB', 'CFB']:
            feedback = self.iv
        else:
            feedback = None
        
        for i, block_bytes in enumerate(blocks):
            block_bits = self._bytes_to_bits(block_bytes)
            block_steps = {'block_num': i + 1, 'initial_block': self._bits_to_str(block_bits)}
            
            if self.mode == 'ECB':
                # ECB: Direct encryption/decryption
                input_to_des = block_bits
                processed_bits, des_steps = self._des_block(input_to_des, i + 1, is_decrypt=is_decrypt)
                block_steps['des_operation'] = des_steps
                final_block_bytes = self._bits_to_bytes(processed_bits)
                
            elif self.mode == 'CBC':
                # CBC: Cipher Block Chaining
                if is_decrypt:
                    # Decrypt: DES decrypt then XOR with previous ciphertext (or IV)
                    processed_bits, des_steps = self._des_block(block_bits, i + 1, is_decrypt=True)
                    block_steps['des_decryption'] = des_steps
                    des_output = self._bits_to_bytes(processed_bits)
                    
                    # XOR with previous ciphertext (or IV for first block)
                    xor_input = self._bytes_to_bits(des_output)
                    xor_with = self._bytes_to_bits(feedback)
                    xor_result = [a ^ b for a, b in zip(xor_input, xor_with)]
                    final_block_bytes = self._bits_to_bytes(xor_result)
                    
                    block_steps['xor_operation'] = {
                        'des_output': self._bits_to_str(xor_input),
                        'xor_with': self._bits_to_str(xor_with),
                        'result': self._bits_to_str(xor_result)
                    }
                    
                    # Update feedback for next block
                    feedback = block_bytes
                else:
                    # Encrypt: XOR with previous ciphertext (or IV) then DES encrypt
                    xor_input = block_bits
                    xor_with = self._bytes_to_bits(feedback)
                    xor_result = [a ^ b for a, b in zip(xor_input, xor_with)]
                    
                    block_steps['xor_operation'] = {
                        'plaintext': self._bits_to_str(xor_input),
                        'xor_with': self._bits_to_str(xor_with),
                        'result': self._bits_to_str(xor_result)
                    }
                    
                    processed_bits, des_steps = self._des_block(xor_result, i + 1, is_decrypt=False)
                    block_steps['des_encryption'] = des_steps
                    final_block_bytes = self._bits_to_bytes(processed_bits)
                    
                    # Update feedback for next block
                    feedback = final_block_bytes
                    
            elif self.mode == 'OFB':
                # OFB: Output Feedback
                # Generate keystream by encrypting feedback
                feedback_bits = self._bytes_to_bits(feedback)
                keystream_bits, des_steps = self._des_block(feedback_bits, i + 1, is_decrypt=False)
                block_steps['keystream_generation'] = des_steps
                keystream_bytes = self._bits_to_bytes(keystream_bits)
                
                # XOR plaintext/ciphertext with keystream
                xor_input = block_bits
                xor_with = self._bytes_to_bits(keystream_bytes)
                xor_result = [a ^ b for a, b in zip(xor_input, xor_with)]
                final_block_bytes = self._bits_to_bytes(xor_result)
                
                block_steps['xor_operation'] = {
                    'input': self._bits_to_str(xor_input),
                    'keystream': self._bits_to_str(xor_with),
                    'result': self._bits_to_str(xor_result)
                }
                
                # Update feedback for next block (keystream becomes new feedback)
                feedback = keystream_bytes
                
            elif self.mode == 'CFB':
                # CFB: Cipher Feedback
                if is_decrypt:
                    # Decrypt: Generate keystream, XOR with ciphertext
                    feedback_bits = self._bytes_to_bits(feedback)
                    keystream_bits, des_steps = self._des_block(feedback_bits, i + 1, is_decrypt=False)
                    block_steps['keystream_generation'] = des_steps
                    keystream_bytes = self._bits_to_bytes(keystream_bits)
                    
                    # XOR ciphertext with keystream
                    xor_input = block_bits
                    xor_with = self._bytes_to_bits(keystream_bytes)
                    xor_result = [a ^ b for a, b in zip(xor_input, xor_with)]
                    final_block_bytes = self._bits_to_bytes(xor_result)
                    
                    block_steps['xor_operation'] = {
                        'ciphertext': self._bits_to_str(xor_input),
                        'keystream': self._bits_to_str(xor_with),
                        'result': self._bits_to_str(xor_result)
                    }
                    
                    # Update feedback for next block (current ciphertext becomes new feedback)
                    feedback = block_bytes
                else:
                    # Encrypt: Generate keystream, XOR with plaintext
                    feedback_bits = self._bytes_to_bits(feedback)
                    keystream_bits, des_steps = self._des_block(feedback_bits, i + 1, is_decrypt=False)
                    block_steps['keystream_generation'] = des_steps
                    keystream_bytes = self._bits_to_bytes(keystream_bits)
                    
                    # XOR plaintext with keystream
                    xor_input = block_bits
                    xor_with = self._bytes_to_bits(keystream_bytes)
                    xor_result = [a ^ b for a, b in zip(xor_input, xor_with)]
                    final_block_bytes = self._bits_to_bytes(xor_result)
                    
                    block_steps['xor_operation'] = {
                        'plaintext': self._bits_to_str(xor_input),
                        'keystream': self._bits_to_str(xor_with),
                        'result': self._bits_to_str(xor_result)
                    }
                    
                    # Update feedback for next block (current ciphertext becomes new feedback)
                    feedback = final_block_bytes

            processed_blocks_data.append(final_block_bytes)
            block_processing_steps.append(block_steps)

        self.full_steps['block_processing'] = block_processing_steps
        
        result_data = b''.join(processed_blocks_data)

        if is_decrypt:
            unpadded_data = self._unpad(result_data)
            self.full_steps['unpadding'] = {
                'padded_len': len(result_data),
                'original_len': len(unpadded_data),
                'padded_hex': binascii.hexlify(result_data).decode(),
                'plaintext_hex': binascii.hexlify(unpadded_data).decode()
            }
            self.full_steps['plaintext_utf8'] = unpadded_data.decode('utf-8', errors='ignore')
            return unpadded_data
        else:
            self.full_steps['ciphertext_hex'] = binascii.hexlify(result_data).decode()
            return result_data

    def encrypt(self, plaintext):
        """Mã hóa dữ liệu"""
        if not isinstance(plaintext, bytes):
            raise ValueError("Plaintext must be bytes")
        return self._process(plaintext, is_decrypt=False)
    
    def decrypt(self, ciphertext):
        """Giải mã dữ liệu"""
        if not isinstance(ciphertext, bytes) or len(ciphertext) % self.block_size != 0:
            raise ValueError("Ciphertext must be bytes and multiple of block size")
        return self._process(ciphertext, is_decrypt=True)
    
    def get_steps(self):
        """Trả về các bước trung gian"""
        return self.full_steps

# Ví dụ sử dụng
import binascii

if __name__ == "__main__":
    pass