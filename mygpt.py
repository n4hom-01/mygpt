#!/usr/bin/env python3
from llama_cpp import Llama
from os import get_terminal_size,system,path,chdir,listdir,cpu_count
from sty import fg, bg, ef, rs 
from sys import argv
from datetime import datetime
import platform
import argparse

help = """

USAGE:
======

Runtime Arguments (when launching the program):
-----------------------------------------------
- Automatic Model Detection:
  Run in the current directory to detect a compatible model automatically:
  python mygpt.py [--kwargs VALUE] (e.g., --n_ctx 500 --n_thread 8 --temperature 0.8)

- Specify a Model File:
  Directly provide the path to a model file:
  python mygpt.py [-m | --model] /path/to/model.gguf [--kwargs VALUE] (e.g., --n_ctx 500 --n_thread 8 --temperature 0.8)

- Specify a Model Directory:
  Provide a directory containing models; the first compatible model will be used:
  python mygpt.py [-m | --model] /path/to/modeldir [--kwargs VALUE] (e.g., --n_ctx 500 --n_thread 8 --temperature 0.8)

Mid-Chat Commands (available during conversation):
-------------------------------------------------
/save        - Saves the current session
/exit        - Terminates the program
/clear       - Clears the terminal display
/help        - Displays this help message
/sysprompt   - Views or sets the system prompt

TIPS:
=====
- If no model is specified, the program will automatically detect compatible models in the current directory.
- When a directory is provided, the first compatible model found will be used.
- Mid-chat commands must be entered alone, without additional text, to function correctly."""

#platform dependent clear screen command
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
			#experimental may cause context overflow
			self.conv.append({"role": "assistant", "content": resp[0:int(len(resp)/2)-1]})
			#experimental may cause context overflow
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
		    filename = path.join(path.dirname(path.abspath(__file__)), "ChatHistory.txt")
		name=f"{path.splitext(path.basename(filename))[0]}.txt" if not filename.endswith(".txt") else filename
		sdir=path.dirname(filename) if path.exists(path.dirname(filename)) else path.dirname(path.abspath(__file__))
		chdir(sdir)
		try:
			with open(name,"a") as file:
				file.write("\n\n"+self.timefmt()+"\n")
				file.write(f"{self.Histstr}")
			return [sdir,name]
		except Exception as e:
			return ["Error",str(e)]
		
def findmodels(modelpath):
	ismdfl=path.isfile(modelpath);ismdir=path.isdir(modelpath)
	if ismdfl and modelpath.endswith(".gguf"):
		return modelpath
	elif ismdir:	
		mdlist= [x for x in listdir(modelpath) if ".gguf" in x]
		if mdlist:
			if len(mdlist)==1:
				return mdlist[0]
			else:
				prom=input(f'Found models {mdlist} in "{modelpath}"\nEnter [1{"-"+str(len(mdlist)) if len(mdlist)>1 else ""}]: ')
				return mdlist[int(prom)-1]
		else:
			print(f"No models found in {modelpath}")
	else:
		print(f"Error: Model `{modelpath}` doesnt exist or isn't a model file")
		exit()


def cmdargs():
	parser = argparse.ArgumentParser(
	    description="Simple local LLM Terminal Chat interface in python",
	    usage="%(prog)s --model MODEL [--kwargs VALUE]...",
	    epilog=" kwargs example: --n_ctx 2040 --max_tokens 500",
		formatter_class=argparse.RawDescriptionHelpFormatter
	)
	parser.add_argument(
		'--model',"-m",
		default=path.dirname(path.abspath(__file__)),
		dest='model_path',
		help='GGUF Model directory (default: current script location)\n'
	)
	parser.add_argument(
		'--n_ctx',"-nctx",
		dest='n_ctx',
		default=500,
		help='Context window size (default: 500)\n'
	)
	parser.add_argument(
		'--temperature',"-temp",
		dest='temperature',
		default=0.8,
		help='Temperature (default: 0.8)\n'
	)
	parser.add_argument(
		'--n_thread',"-nth",
		dest='n_thread',
		default=cpu_count(),
		help='Number of treads for faster computation (default: number of your cpu cores)\n'
	)
	parser.add_argument(
		'--system-prompt',"-sysprom",
		dest='sysprompt',
		default="you are helpful assistant",
		help='System Prompt (default: you are helpful assistant)\n'
	)	
	fixed_args, remaining = parser.parse_known_args()	
	keyargs = {}
	it = iter(remaining)
	for arg in it:
	    if arg.startswith('--'):
	        keyargs[arg[2:]] = next(it, None)
	kwdict=vars(fixed_args)|keyargs
	kwdict["model_path"]=findmodels(kwdict["model_path"])
	return kwdict

cls()
kwargs=cmdargs()
print(f'[ Loading model "{path.basename(kwargs["model_path"])}" ]')
chat=Gpt(**kwargs)
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
		  svfl=chat.save(path.join(path.dirname(path.abspath(__file__)),"ChatHistory.txt"))
		  if svfl[0]=="Error":
		  	print(f"Error: {svfl[1]}")
		  else:
		  	print(fg.rs+f'\n{ef.bold}[ Saved to "{svfl[1]}" ]')
		print("[ Exiting Chat... ]")
		exit()
	elif "/save" in message:
		print(rs.all+"\n"+"_"*chat.chrcnt+"\n")
		svpath=message.replace("/save","").strip()
		svpath=svpath if svpath else f'{path.dirname(path.abspath(__file__))}/ChatHistory.txt'
		if svpath and not svpath.isspace():
			savefile=chat.save(svpath)
			print(f"{ef.bold}[Sys:] Saved to '{savefile[1]}' ")
			if savefile[0]=="Error" :
				print(f"{ef.bold}[Sys:] Error: {savefile[1]}")
		else:
			print(fg.rs+f'{ef.bold}[Sys:] Saved to "{savefile[1]}"')
		print(rs.all+"\n"+"‾"*chat.chrcnt)	
	elif message=="/help":
		print(rs.all+"\n"+"_"*chat.chrcnt+"\n")
		print(f"{ef.bold}[Sys:]{help}")
		print(rs.all+"\n"+"_"*chat.chrcnt+"\n")
	elif "/sysprompt" in message:
		prom=message.replace("/sysprompt","").strip()
		print(rs.all+"\n"+"_"*chat.chrcnt+"\n")
		if prom:
			chat.conv[0]["content"]=prom
			print(f"{ef.bold}[Sys]: Changed system prompt to '{prom}'")
		else:
			print(f"{ef.bold}[Sys]: System prompt: '{chat.conv[0]['content']}'")
		print(rs.all+"\n"+"_"*chat.chrcnt+"\n")
		
	else:
		chat.ask(question=message,stream=True)