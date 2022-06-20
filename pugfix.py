#!/usr/bin/python

# This script wraps all asset references with the asset() call helper that saasbox needs to use.
# This script also iterates over every pug file in a directory and replace : and \ class names with _
# This is to make pug files compatible with tailwind.

import re, sys, os

# Return new string after inserting string at pos.
def replace_charAtPos(orig, insert, index):
	# Remove char at index:
	# string = orig[:index] + orig[index+1:]
    # Insert new char at index:
    return orig[:index] + insert + orig[index+1:]

# Add asset() call to all src="" attributes
# The ? says non-greedy match everything. 
# Ex: instead of matching this: src='atis-assets/logo/atis/atis-mono-white.svg' alt width='auto'
# it matches: src='atis-assets/logo/atis/atis-mono-white.svg'. 
# Greedy .* matches 'and more mid-text, as long as the whole string ends with a "' as the end component asks.
def add_asset_tag(string):
	pattern = '''(src=["']){1}(?!http)(.*?["']){1}'''
	# Find src=""
	# Fidn index of first ", add asset( before it
	# Find index of second ", add ) after it.
	#re.finditer(pattern, string) 
	#[(m.start(0), m.end(0)) 
	for m in re.finditer(pattern, string):
		print '%02d-%02d: %s' % (m.start(), m.end(), m.group(0))
		# All the string + asset( + matched part + ) + rest of the string
	#	string = string[:m.start()] + "asset(" + string[m.start():m.end()] + ")" + string[m.end():]
	# [m.span() for m in re.finditer(pattern, string)]
	#return string

	# No patterns found don't create a new string.
	if re.search(pattern, string) is None:
		return string

	matches = re.finditer(pattern, string)

	newstring = ""
	lastpos = 0
	# Build up new string from scratch processing each match one by one. 
	for m in matches:
		# Add to new string,
		# print '%02d-%02d: %s' % (m.start(), m.end(), m.group(0))
		newstring += string[lastpos:m.start() + len("src=")] # String from last pos until this match, plus, move until after src=
		newstring += "asset("
		newstring += string[m.start() + len("src="):m.end()] # Add from until after src= since we added 'asset(' there.
		newstring += ")"
		lastpos = m.end()
	newstring += string[m.end():]
	return newstring

# Fix all tailwind classes to use _ for special chars : and / to be compatible with pug.
def fix_class_underscore(string):
	# Match: 
	# Convert all / and : convert to _
	# \.{1}[a-zA-Z0-9-_]+[:/]{1}
	pattern = '''\.{1}[a-zA-Z0-9-_]+(:{1}|[0-9]/[0-9])'''
	for m in re.finditer(pattern, string):
		# print '%02d-%02d: %s' % (m.start(), m.end(), m.group(0))
		# If we matched a :, get its position, always at the end.
		if (string[m.end()-1] == ":"):
			#print "Abspos: %d, relpos %d" % (m.end()-1, m.end()-1)
			pos = m.end()-1
		# We didn't match a dot, so get the position of "/" in matched string
		else:
			pos = m.group(0).find("/")
			# Add position of "/" in matched string to position of match in larger string.
			#print "Abspos: %d, relpos %d" % (m.start() + pos, pos)
			pos = m.start() + pos

		# Now we have the position to modify, and we can update the string:
		string = replace_charAtPos(string, "_", pos)
	return string

def process_pugfile(file):
	with open(file, "r+") as f:
		string = f.read()
		string = add_asset_tag(string)
		string = fix_class_underscore(string)
		string = fix_class_underscore(string) # Second one for multiple fixes on same class, e.g. .lg:1/2-
		f.seek(0)
		f.write(string)
		f.truncate()

def main():
	if len(sys.argv) >= 2:
		file = str(sys.argv[1])
	else:
		file = "./index.pug"
	#print "Arg: %s" % file

	# If argument is a file, just process that file:
	if os.path.isfile(file):
		process_pugfile(file)
		return

	# If argument is a path, traverse all dirs in the path.
	for subdir, dirs, files in os.walk(file):
		for filename in files:
			filepath = subdir + os.sep + filename
			if filepath.endswith(".pug"):
				print "Processing " + filepath
				process_pugfile(filepath)
	print "DONE"

if __name__ == "__main__":
	main()
