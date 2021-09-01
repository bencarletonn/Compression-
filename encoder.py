import sys

# Canonical Huffman Coding 

class Node():

	    def __init__(self, left=None, right=None):
	        self.left = left
	        self.right = right

	    def __str__(self):
	        return f"{self.left}_{self.right}"

	    def children(self):
	        return (self.left, self.right)


class CanonicalHuffmanEncoder():
	def __init__(self, string):
		self.string = string  
		self.mapping = None 


	# functions for compression 
	def frequencyList(self, string):
		'''
		Takes a string and return a list of tuples
		showing each character and its number of 
		occurences 
		'''
		frequencies = {} 
		for letter in string:
			if letter in frequencies:
				frequencies[letter] += 1 
			else:
				frequencies[letter] = 1 

		frequencies = sorted(frequencies.items(), key=lambda x: x[1]) # Convert dict to list of tuples
		return frequencies



	def priorityQueue(self, frequencies): 
		'''
		Takes a list of tuples and builds huffman
		tree structure, provided us with huffman
		coding scheme
		'''
		nodes = frequencies 
		while len(nodes) > 1:
		    char1, freq1 = nodes[0]
		    char2, freq2 = nodes[1]
		    freq_sum = freq1 + freq2 
		    nodes = nodes[2:]
		    node = Node(char1, char2)
		    nodes.append((node, freq_sum))

		    nodes = sorted(nodes, key=lambda x: x[1]) 
		huffmanCode = nodes[0][0]
		return huffmanCode 


	# Function from https://www.programiz.com/dsa/huffman-coding
	def buildTree(self, node, left=True, binary=''):
	    if type(node) is str:
	    	return {node: binary} 
	    left, right = node.children()
	    d = dict()
	    d.update(self.buildTree(left, True, binary + '0'))
	    d.update(self.buildTree(right, False, binary + '1'))
	    self.mapping = d 
	    return d 

	def canonicalMapping(self, mapping):
		# Convert normal mapping to canonical mapping 
		bit_lengths = {} 
		for i in mapping:
			bit_lengths[i] = len(mapping[i])

		new_order = sorted(bit_lengths, key=lambda key: (bit_lengths[key], key)) #https://stackoverflow.com/questions/25958019/sorting-a-dictionary-in-python-by-two-keys-frequency-and-lexicographically
		canonical = {} 
		for i in new_order:
			canonical[i] = mapping[i] 
		canonical_list = list = [(k, v) for k, v in canonical.items()] # Convert dict to list of tuples for ease

		new_mapping = []
		for i in range(len(canonical_list)):
			if i == 0: # assign the code of the first symbol with the same number of '0's as the bit length
				new_mapping.append((canonical_list[i][0], "0" * len(canonical_list[i][1])))
			else:
			
				last_code = bin(int(new_mapping[i-1][1], 2) + 1)[2:]
				# new code should be atleast as long as the last code 
				if len(last_code) < len(new_mapping[i-1][1]):
					diff = len(new_mapping[i-1][1]) - len(last_code) 
					last_code = (diff * "0") + last_code

				append_zeros = len(canonical_list[i][1]) - len(canonical_list[i-1][1])
				append_zeros = "0" * append_zeros
				new_code = last_code + append_zeros 
				new_mapping.append((canonical_list[i][0], new_code))


		# Convert list of tuples back to dictionary 
		new_mapping_dict = dict(new_mapping) 
		x = [*new_mapping_dict] # list of new_mapping_dict keys 
		y = []  # list of new_mapping_dict value lengths, i.e. 110 -> 3 
		for i in new_mapping_dict:
			y.append(len(new_mapping_dict.get(i)))

		#print(new_mapping_dict, "canonical mapping")  
		return new_mapping_dict, x, y 


	def encode(self, string, mapping, x, y):

		# First, encode the string using the given mapping 
		encoded = "" 
		for character in string:
			encoded += mapping[character] 

		# Now we need to create the header information that allows us to decode 
		# Our first byte denotes how many characters have been turned into codewords 
		header = "" 
		num_chars = len(x) 
		first_byte = format(num_chars, '08b') # format to byte
		header += first_byte 

		# Encode x in bytes 
		for i in range(num_chars): 
			byte = format(ord(x[i]), "08b") 
			header += byte 


		# Encode y in bytes 
		for i in range(num_chars):
			byte = format(y[i], "08b") 
			header += byte 

		encoding = header + encoded  
		#print(len(encoding), "len(encoding)")
		return encoding 





	def toBytes(self, encoded):
		# Add padding so binary string length is divisible by 8 
		# Last byte indicates where padding starts 
		# https://github.com/bhrigu123/huffman-coding/blob/master/huffman.py
		padding = 8 - (len(encoded) % 8) 
		for i in range(padding):
			encoded += '0' 
		padding_info = "{0:08b}".format(padding)   
		encoded += padding_info

		byte_arr = bytearray() 
		for i in range(0, len(encoded), 8):
			byte = encoded[i:i+8] 
			byte_arr.append(int(byte, 2)) 

		return byte_arr 


	def compress(self): 
		'''
		Main function for compressing texts
		'''
		frequencies = self.frequencyList(self.string) 
		Q = self.priorityQueue(frequencies) 
		mapping = self.buildTree(Q)  
		#print(mapping, "original huffman mapping") 
		cannonical_mapping, x, y = self.canonicalMapping(mapping) 
		encoded = self.encode(self.string, cannonical_mapping, x, y)
		encoded_bytes = self.toBytes(encoded) 
		return encoded_bytes







def L7ZZEncoder(data, searchBuffSize, lookaheadBuffSize):

	# (i, j, X) 
	dictionary = [] 
	i = 0
	while i < len(data):

		# Edge cases
		if i == 0: # First character
			dictionary.append((0, 0, data[i]))
			i += 1 

		else:

			searchBuffIndex = i - searchBuffSize
			if searchBuffIndex < 0: # To prevent wrapping in string 
				searchBuffIndex = 0 # Index is at start of string 

			lookaheadBuffIndex = i + lookaheadBuffSize

			search = data[searchBuffIndex: i] 
			lookahead = data[i: lookaheadBuffIndex+1] 


			# for each substring in lookahead 
			# if its contained in search, keep track of (offset, length, next_char)
			substring = "" 
			# Initialise offset, length, next_char 
			offset, length, next_char = (0, 0, data[i]) 
			increment = 1 


			for char in lookahead:
				substring += char

				if substring in search:

					length = len(substring) 

					reverse_index_in_search = search[::-1].index(substring[::-1]) + (length-1)
					index_in_search = (len(search) -1) - reverse_index_in_search
					index_in_data = searchBuffIndex + index_in_search
					offset = i - index_in_data

					x = i + length 
					if x >= len(data):
						next_char = '-'
					else:
						next_char = data[x] 


				else: # if substring not in char 
					break 

			i += length 

			# From here we have correct offset and length 
			i += increment
			dictionary.append((offset, length, next_char))

	return dictionary


inputFile = sys.argv[1]
# Read file and turn into string 
with open(inputFile, 'r') as file:
    data = file.read()


LZ77_dictionary = L7ZZEncoder(data, searchBuffSize=2**16-2, lookaheadBuffSize=2**8-2) 

# Allocate offset 2 bytes 
# Allocate length 1 byte 
# Concatenate all chars into a string and run huffman 

offset_bit_array = ""
length_bit_array = ""
chars = ""

for i in LZ77_dictionary: 
	(offset, length, char) = i 
	offset_bits = format(offset, '016b') # Convert offset to 2 bytes each  
	length_bits = format(length, '08b') # Convert length to 1 byte each

	offset_bit_array += offset_bits
	length_bit_array += length_bits
	chars += char # Concatenate chars for huffman encoding 


# Compress chars array by applying Canonical huffman encoding 
huffman_compress = CanonicalHuffmanEncoder(string=chars) 
compressed = huffman_compress.compress()


# Create byte arrays for both offset_bits and length_bits
def bitsToBytes(bit_array): # Assume len(bit_array) % 8 == 0 
	byte_array = bytearray() 
	for i in range(0, len(bit_array), 8):
		byte = bit_array[i:i+8]  
		byte_array.append(int(byte, 2)) 
	return byte_array

offset_byte_arr = bitsToBytes(offset_bit_array) 
length_byte_arr = bitsToBytes(length_bit_array) 


# Create headers for both offset_byte_arr and length_byte_arr so we know the number of bytes when decoding
header1 = format(len(offset_byte_arr), '024b') # allocate 3 bytes each for the headers
header1 = bitsToBytes(header1)  
offset_byte_arr = header1 + offset_byte_arr

header2 = format(len(length_byte_arr), '024b') # unlikely the lengths will exceed 2**24 
header2 = bitsToBytes(header2) 
length_byte_arr = header2 + length_byte_arr


# Call huffman on all of data 
priority = CanonicalHuffmanEncoder(string=data) 
priority = priority.compress() 

if len(priority) < len(offset_byte_arr + length_byte_arr + compressed): # Just use canonical huffman coding
    garbage_byte = bitsToBytes("10000000")
    final_compression = garbage_byte + priority 

else:

	# Allocate 1 byte (11111111) so leading zeros aren't removed from the headers
	garbage_byte = bitsToBytes('11111111') 
	final_compression = garbage_byte + offset_byte_arr + length_byte_arr + compressed   


# Write compressed version to new file 
#outputFile = inputFile + ".lz"  
outputFile = inputFile[:-4] + ".lz" 
with open(outputFile, "wb") as output_file:
	output_file.write(final_compression) 