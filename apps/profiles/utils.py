def convert_rfid_to_binary(number):
    # Convert from integer to binary padded to 32 bits
    binary = bin(number)[2:].zfill(32)
    # Split binary into bytes
    byte_list = [binary[i:i + 8] for i in range(0, len(binary), 8)]
    # Reverse byte groups
    bin_reversed = ""
    for byte in byte_list:
        bin_reversed += byte[::-1]
    return bin_reversed


def convert_to_rfid_integer(bin_reversed):
    # Convert back to integer
    rfid_binary = int(bin_reversed, 2)
    # Pad to length 10
    rfid = str(rfid_binary).zfill(10)
    return rfid
