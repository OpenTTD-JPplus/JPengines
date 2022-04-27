#Importing required things
from time import sleep, gmtime, strftime
import time
from random import randint
import sys
import os
import argparse

print("\n=======StarRaid's NML compiler!=======\n")

#Starting with argument handling from command-line interface

parser = argparse.ArgumentParser(description="Patch a GRF in NML from pnml files into one NML file. If no arguments provided, the program will loop and prompt an input for the file to compile. WARNING! This does NOT compile into a .grf file, it patches your pnml files into an nml file for you to compile with NMLC!")

parser.add_argument("-o", "--output", type=str, help='The file to output the written file to. Please enclose the file name in quotation marks (e.g. python nml_compiler.py -o "output.nml)"')
parser.add_argument("-f", "--file", type=str, help="The header file to read from. Please enclose the file name in quotation marks.")
parser.add_argument("-b", "--backup", type=int, help="1 or 0, to say if the program will create a backup if overwriting the output file.", choices=[0,1])

args = parser.parse_args()


#Checking if any of the arguments have any value that is not "None"
used_args = False
arguments = vars(args)

for argument in arguments:
	if not used_args and arguments[argument] != None:
		used_args = True


#Defining general purpose functions

def rm_file_extension(file_name):
	found_file_extension = False
	end_point = len(file_name)-1
	
	#Finding the last decimal point in the header name
	for pos in range(len(file_name)-1,-1,-1):
		if file_name[pos]	== "." and not found_file_extension:
			end_point = pos
			found_file_extension = True
	return file_name[:end_point]

#Backup function that backs up the output file first (if it already exists)
def backup(name):
	if name in os.listdir():
		if not ("backups" in os.listdir()):
			os.mkdir("backups")
		os.rename(name, "backups/" + rm_file_extension(name) + "-" + strftime("%H-%M-%S-%Y-%m-%d", gmtime())+".nml")

		
	
#Known error printing
def print_error(cause, place, action):
	print("\nEncountered error!")
	print("Cause      : ", cause)
	print("Found at   : ", place)
	print("How to fix : ", action)

#Unknown error printing
def print_general_error(cause):
	print("\nEncountered error!")
	print("Cause      : ", cause)
	print("This was most likely an internal error.\n")

	



#Defining the class that writes to the output file

class writer:
	"""The interface that writes to the output file"""
	
	output_text = ""
	
	def __init__(self):
		output = arguments["output"]
		self.output = open(output, "w")
	
	def write_line(self, line):
		self.output.write(str(line) + "\n")
	
	def close(self):
		self.output.close()

		
	
#Defining the main reader class

class reader:
	"""The class that reads from a file and does various things with it"""
	
	list_of_definitions = {}
	total_list_of_errors = []
	faulty_definitions = []
	
	def __init__(self, file_name, *parent_variables):
		try:
			self.current_line = 0
			self.errors_made = 0
			self.file_name = file_name
			self.input = ""
			self.input = open(self.file_name, "r")
		except (OSError, FileNotFoundError) as inst:
			self.errors_made += 1
			if parent_variables:
				self.total_list_of_errors.append([inst, "Line " + str(parent_variables[2]) + " of " + str(parent_variables[0]) + ": " + str(parent_variables[1]), "Check that the line of code is correct"])
			else:
				self.total_list_of_errors.append([inst, "Direct/Argument input", "Make sure you enter a valid file name"])
			
	
	def read_line(self):
		line_read = self.input.readline()
		return line_read.replace("\n","")
		
	def close(self):
		if str(type(self.input)) == "<class '_io.TextIOWrapper'>":
			self.input.close()
		
		if len(self.total_list_of_errors):
			if len(self.total_list_of_errors) == 1:
				print("\nEncountered 1 error in this patch")
			else:
				print("\nEncountered", len(self.total_list_of_errors), "errors in this patch.")
			for error in self.total_list_of_errors:
				if len(error) == 1:
					print_general_error(error[0])
				else:
					print_error(error[0], error[1], error[2])
	
	def main(self):
		#The main function that reads a file and writes it to the output file
		
		#Generating a list of each line of code in the target file, then removing the new line characters
		lines = [line.replace("\n","") for line in self.input]
		
		#The main loop that loops through each line of code
		self.line_counter = 0
		for line in lines:
			self.line_counter += 1
			do_write = True
			
			#If the line starts with the "#include" command, then it create another instance that reads and writes that file first
			if line.lower()[:8] == "#include":
			
				self.subreader = reader(line.replace('"', '')[9:], self.file_name, line, self.line_counter)
				self.subreader.main()
				
				if self.subreader.errors_made == 1:
					print("Patched", line.replace('"', '')[9:], "with 1 error!")
				elif self.subreader.errors_made > 1:
					print("Patched", line.replace('"', '')[9:], "with", self.subreader.errors_made, "errors!")
				else:
					print("Patched", line.replace('"', '')[9:], "with no errors.")
							
				do_write = False
				
			elif line.lower()[:7] == "#define":
				new_line = line[8:]
				
				#Finding the end of the definition name
				def_name = ""
				found_def_name = False
				for letter in new_line:
					if letter == " " and not found_def_name:
						new_line = new_line.replace(def_name + " ", "")
						if len(new_line) > 0:
							print("Made custom definition", def_name, "with a value of", new_line)
							self.list_of_definitions[def_name] = new_line
						elif len(def_name) > 1:
							self.total_list_of_errors.append(["Invalid custom definition!", "Line" + str(self.line_counter) + " of " + self.file_name + ": " + line, "Check the definition's value"])
						
						found_def_name = True
						
					def_name += letter
				
				do_write = False
				
			else:
				#Checking for custom definitions
				for definition in self.list_of_definitions:
					if definition in line:
						line = line.replace(definition, self.list_of_definitions[definition])
						
				#If a definition that is known to be faulty is found then throw an error
				for definition in self.faulty_definitions:
					if definition in line:
						self.errors_made +=1
						self.total_list_of_errors.append(["Invalid custom definition used!", "Line " + str(self.line_counter) + " of " + self.file_name + ": " + line, "Check the definition's value"])
					
			
			if do_write:
				output.write_line(line)
		
				


#Defining other general functions



#If output is not defined but the header file is, then it will be defined as the same as the input
if arguments["file"] != None and arguments["output"] == None:
	arguments["output"] = rm_file_extension(arguments["file"])+".nml"

#Backing up if backup is set to 1
if arguments["backup"] != None and str(arguments["backup"]) != "0" :
	print("Attempting to backup", arguments["output"])
	backup(arguments["output"])


#Displaying the given arguments to the user
for argument in arguments:
	if arguments[argument] != None:
		print(argument.capitalize(), ":", arguments[argument])


#Checking if any arguments are used

if used_args:

	#Check if the 'file' argument was given, as the program cannot continue without it
	if arguments["file"] != None:
		
		try:
			#The main sequence that opens the files and then writes to the output
			output = writer()
			header = reader(arguments["file"])
			header.main()
			output.close()
			header.close()
			
			#Display messages after patching
			if len(header.list_of_definitions) > 0:
				print("\nList of custom definitions used in this file:")
				for definition in header.list_of_definitions:
					print(definition, header.list_of_definitions[definition])
			
		#Catch any other raised errors
		except Exception as inst:
			print_general_error(str(inst) + " from " + str(type(inst))) 
	else:
		print("\nNo input file given!")
	
else:
	print("\nType 'exit' to exit the program\n")
	#Entering a loop that can be broken with either Ctrl + C or a command
	while True:
	
		try:
			print("\n==============================\n")
			#Getting the users input
			arguments["file"] = input("Input file: ")
			
			#If the user types exit the program will exit
			if arguments["file"].lower() == "exit":
				raise KeyboardInterrupt
				
			#Creating the output file from the input file name
			arguments["output"] = rm_file_extension(arguments["file"])+".nml"
				
			#The main sequence that opens the files and then writes to the output
			output = writer()
			header = reader(arguments["file"])
			header.main()
			output.close()
			header.close()
			
			#Display messages after patching
			if len(header.list_of_definitions) > 0:
				print("\nList of custom definitions used in this file:")
				for definition in header.list_of_definitions:
					print(definition, header.list_of_definitions[definition])
		
		#If the command is entered or Ctrl + C is pressed, then the program will terminate
		except KeyboardInterrupt:
			print("\nExiting the program!")
			break
			
		#Catching any other raised errors
		except SyntaxError:#Exception as inst:
			print_general_error(str(inst) + " from " + str(type(inst))) 



#input("\nPress enter to continue\n")