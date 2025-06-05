#!/usr/bin/env python3
from llama_cpp import Llama
from os import get_terminal_size,system,path,chdir, listdir
from sty import fg, bg, ef, rs 
from sys import argv
from datetime import datetime
import platform

help = """
USAGE:
======

# Runtime arguments (when starting the program):
-----------------------------------------------
# Run with automatic model detection in current directory
python mygpt.py

# Specify a model file directly
python mygpt.py -m /path/to/model.gguf

# Specify a directory containing models
python mygpt.py -m /path/to/models/


Mid-chat commands (available during conversation):
-------------------------------------------------
/save    - Save current session
/exit    - Exit the program
/clear   - Clear the terminal screen
/help    - Show this help message


TIPS:
=====
- The program automatically detects compatible models if no model is specified
- When specifying a directory, the program uses the first compatible model found
- Mid-chat commands must be entered as the only text in your message
"""

def cls():
	os_name=platform.system().lower()
	if os_name:
		system("cls" if "windows" in os_name else "clear")
	else:
		system("clear")
#clear screen at the start
cls()
class Gpt:
	# some class variables
	chrcnt = get_terminal_size(0)[0]
	Histstr=""
	#
	def __init__(self,model_path,sysprompt,n_ctx=2048,max_tokens=500,temperature=0.8,verbose=False,**kwargs):
		self.maxtoken=max_tokens
		self.llm = Llama(model_path=model_path,n_ctx=n_ctx,max_tokens=max_tokens,temperature=temperature,verbose=verbose,**kwargs)
		self.conv=[{"role": "system", "content": sysprompt }]
				
	def ask(self,question,stream=True,**kwargs):
		self.Histstr+=f"\nYou: {question}"
		self.conv.append({"role": "user", "content": question})
		tokens=len(self.llm.tokenize(f"{self.conv}".encode()))
		if tokens>=self.maxtoken/2:
			self.conv.pop(1)
		response = self.llm.create_chat_completion(messages=self.conv,
		stream=stream,**kwargs)
		print(rs.all+"\n"+"‾"*self.chrcnt)
		print(ef.bold+"[AI]: ",end="")
		resp=""
		if stream:
			for chunk in response:
				delta = chunk["choices"][0]["delta"]
				if "content" in delta:
					output=delta["content"]
					resp+=output
					print(ef.bold+fg.yellow+output,end="",flush=True)		
			self.Histstr+=f"\nAI: {resp}"
			print(rs.all+"\n"+"_"*self.chrcnt+"\n")
		else:
			output=response["choices"][0]["message"]["content"]
			print(fg.yellow+f'{output}'+rs.all)
			print("\n"+"="*self.chrcnt+"\n")
	
	def timefmt(self):
		now = datetime.now()
		formatted_time = now.strftime("%B %d, %Y %H:%M:%S")
		tfmt=f"--> Chat on {formatted_time} <--"
		txt=("="*self.chrcnt+"\n"+f"{'-'*int((self.chrcnt-len(tfmt))/2)}{tfmt}{'-'*int((self.chrcnt-len(tfmt))/2)}"+"\n"+"="*self.chrcnt)
		return txt
				
	def save(self,filename=None):
		if filename is None:
			filename = path.join(path.dirname(argv[0]), "ChatHistory.txt")
		name=f"{path.splitext(path.basename(filename))[0]}.txt"	
		sdir=path.dirname(filename) if path.exists(path.dirname(filename)) else path.dirname(argv[0])
		chdir(sdir)
		try:
			with open(name,"a") as file:
				file.write("\n\n"+self.timefmt()+"\n")
				file.write(f"{self.Histstr}")
			return [sdir,name]
		except Exception as e:
			return ["Error",str(e)]
		
def SelectModel():
	model=""
	def findmodels(directory):
		mdlst=listdir(directory)
		my_list = [x for x in mdlst if "gguf" in x]
		dmd=[directory,my_list] if my_list else my_list
		if dmd:
			if len(dmd[1])>1:
				prompt=input(f'Models {dmd[1]} found in "{dmd[0]}"\n\nEnter 1-{len(dmd[1])} to select a model: ')
				try:
					ind=int(prompt)
					return f"{dmd[0]}/{dmd[1][ind-1]}"
				except:
					print(f'Invalid input "{prompt}"')
					exit()
			else:
				return f"{dmd[0]}/{dmd[1][0]}"
		else:
			print(f'No model file found in "{directory}" ')
			exit()
	
	if len(argv)>1:
		for h in ["--help","-h","--h","help","-help"]:
			if h in argv:
				print(help)
				exit()
		
		tmp=argv[2 if argv[1].lower() in ["-m","-model","-models","-l","-llm"] else 1]
		if path.isfile(tmp):
			if ".gguf" in tmp:
				model=tmp
		elif path.isdir(tmp):
			model=findmodels(tmp)
		else:
			print(f'Invalid Path "{tmp}"')
	else:
		model=findmodels(path.dirname(argv[0]))
	cls()
	return model


sysprom="you are advanced Ai assistant called quantum"
aimodel=SelectModel()
print(f'[ Loading model "{path.basename(aimodel)}" ]')
chat=Gpt(model_path=aimodel,sysprompt=sysprom,n_ctx=8192,temperature=0.8,n_threads=8)
cls()
print(chat.timefmt()+"\n")
# Main chat Loop
while True:
	message=input(ef.bold+"[You]: "+fg(187, 148, 239))
	if message=="/clear":
		cls()
	elif message=="/exit":
		saveprom=input("\n\nWould you like to save the conversation to a file?: ")
		if saveprom.strip().lower() in ["y","yes","yeah","yep"]:
		  svfl=chat.save(path.join(path.dirname(argv[0]),"ChatHistory.txt"))
		  if svfl[0]=="Error":
		  	print(f"Error: {svfl[1]}")
		  else:
		  	print(fg.rs+f'\n{ef.bold}[ Saved to "{svfl[1]}" ]')
		print("[ Exiting Chat... ]")
		exit()
	elif message=="/save":
		savefile=chat.save(path.join(path.dirname(argv[0]),"ChatHistory.txt"))
		print(rs.all+"\n"+"_"*chat.chrcnt+"\n")
		if savefile[0]=="Error" :
			print(f"{ef.bold}[Sys:] Error: {savefile[1]}")
		else:
			print(fg.rs+f'{ef.bold}[Sys:] Saved to "{savefile[1]}"')
		print(rs.all+"\n"+"‾"*chat.chrcnt)	
	else:
		chat.ask(question=message,stream=True )