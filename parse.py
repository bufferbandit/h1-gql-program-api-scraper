from pprint import pprint
import json

with open("programs.json", "r") as f:
	programs = json.loads(f.read())

	handles = [program["handle"] for program in programs]
	print(len(handles))


	handles = set(handles)
	print(len(handles))

	# pprint(handles)
