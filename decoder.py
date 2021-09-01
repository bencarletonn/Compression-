import sys 

def bitsToBytes(bit_array): # Assume len(bit_array) % 8 == 0 
	byte_array = bytearray() 
	for i in range(0, len(bit_array), 8):
		byte = bit_array[i:i+8]  
		byte_array.append(int(byte, 2)) 
	return byte_array

class Node():

	    def __init__(self, left=None, right=None):
	        self.left = left
	        self.right = right

	    def __str__(self):
	        return f"{self.left}_{self.right}"

	    def children(self):
	        return (self.left, self.right)


class CanonicalHuffmanDecoder():
	def __init__(self, string): 
		self.mapping = None 
		self.string = string 


	def decompress(self):

		compressed = self.string 
		encoded = self.fromBytes(compressed) 
		mapping, encoded = self.constructMapping(encoded)
		string = self.decode(mapping, encoded)  

		return string 


	def fromBytes(self, byte_arr):
		# Convert from bytes to binary string 
		encoded = (bin(int.from_bytes(byte_arr, byteorder="big")))[2:] # remove 0b 

		# Check that int.from_bytes hasn't removing any leading 0's 
		leading_zeros =  8 - (len(encoded) % 8)
		if (leading_zeros) != 8: # then the process has removed zeros at the front of the sequence 
			encoded = (leading_zeros * "0") + encoded 
 
 
		padding_info = int(encoded[-8:], 2) # See how many padding bits we have added
		encoded = encoded[:-8] # Remove padding info byte 
		encoded = encoded[:-padding_info] # Remove padding bits   

		return encoded 


	def constructMapping(self, encoded):
		# Read the header information of the bit-stream 
		first_byte = encoded[:8]
		num_chars = int(first_byte, 2) # tells us we have 4 bytes  

		encoded = encoded[8:] # Remove first byte
		x = [] 
		y = []  
		for i in range(num_chars):
			byte = encoded[:8]
			letter = chr(int(byte, 2)) 
			x.append(letter) 
			encoded = encoded[8:] 

		for i in range(num_chars):
			byte = encoded[:8] 
			number = int(byte, 2) 
			y.append(number) 
			encoded = encoded[8:]


		# Construct the map using x and y  
		# We need to make sure each code is at least as long as its y, i.e. if not append zeros to the start 
		mapping = []

		for i in range(len(x)):
			if i == 0:
				mapping.append((x[i], "0" * y[i])) 
			else:
				last_code = mapping[i-1][1] 
				last_code = int(last_code, 2) + 1 
				last_code = bin(last_code)[2:]
				last_code += ("0" * (y[i] - y[i-1])) 
				if len(last_code) < y[i]:
					diff = y[i] - len(last_code) 
					last_code = ("0" * diff) + last_code 
				mapping.append((x[i], last_code)) 

		# Convert mapping to dictionary for ease 
		mapping_dict = dict(mapping)   
		#print(mapping_dict, "canonical mapping constructed") 
 

		return mapping_dict, encoded


	def decode(self, mapping, encoded):

		mapping = {v: k for k, v in mapping.items()} # invert dictionary for simplicity 
 
		decoded = "" 
		encoding = "" 
		for i in encoded:
			encoding += i
			if encoding in mapping:
				decoded += mapping[encoding] 
				encoding = "" 
			else:
				continue 
 
		return decoded 



def LZ77Decoder(mapping):
	decoded = "" 
	for i in mapping:
		(offset, length, char) = i 
		if offset == 0:
			decoded += char 
		else:
			x = len(decoded)-offset
			y = x + length 
			decoded += decoded[x:y] 
			if char == '': # signifies end of string
				continue
			decoded += char 

	return decoded





inputFile = sys.argv[1]
# Read file and turn into string 
with open(inputFile, 'rb') as file:
    data = file.read()


# break bit stream down to consituent parts
encoded = (bin(int.from_bytes(data, byteorder="big")))[2:] # remove 0b 
 
garbage = encoded[:8] 
if garbage == "10000000": # just use canonical to decode 
	encoded = encoded[8:] # Remove garbage byte 
	canonical_bits = bitsToBytes(encoded) 
	huffman_decompress = CanonicalHuffmanDecoder(string=canonical_bits)
	decompressed = huffman_decompress.decompress()

else:
	encoded = encoded[8:]  

	# Seperate offset_byte_arr 
	length1 = int(encoded[:24],2)
	encoded = encoded[24:] 
	offset_byte_arr = encoded[:length1*8]
	encoded = encoded[length1*8:]  

	# Seperate length_byte_arr 
	length2 = int(encoded[:24],2)
	encoded = encoded[24:] 
	length_byte_arr = encoded[:length2*8] 
	encoded = encoded[length2*8:] 

	# Seperate compressed 
	compressed = encoded 

	# Decompress chars using CanonicalHuffmanDecoder
	compressed = bitsToBytes(compressed) 
	huffman_decompress = CanonicalHuffmanDecoder(string=compressed) 
	chars = huffman_decompress.decompress() 
	chars_list = [] 
	for i in chars:
		chars_list.append(i) 

	offsets = [] 
	lengths = [] 
	for i in range(0, len(offset_byte_arr), 16):
		byte_pair = offset_byte_arr[i:i+16] 
		offsets.append(int(byte_pair, 2)) 

	for i in range(0, len(length_byte_arr), 8):
		byte = length_byte_arr[i:i+8] 
		lengths.append(int(byte, 2))   


	# Construct dictionary from 3 lists 
	LZ77Dictionary = list(zip(offsets, lengths, chars_list))   
	# Decode LZ77Dictionary 
	decompressed = LZ77Decoder(LZ77Dictionary)


	# Marks end-of-file if at the end
	if decompressed[-1] == '-': # In latex file doesn't finish with a '-' 
		decompressed = decompressed[:-1]

# Write compressed version to new file 
#outputFile = inputFile + ".tex"  
outputFile = inputFile[:-3] + "-decoded.tex"
with open(outputFile, "w", newline='\n') as output_file: #newline='\n' removes carriage return 
	output_file.write(decompressed) 