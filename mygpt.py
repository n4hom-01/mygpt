#!/usr/bin/env python3
from llama_cpp import Llama
from os import get_terminal_size,system,path,chdir,listdir,cpu_count
from sty import fg, bg, ef, rs 
from sys import argv
from datetime import datetime
import platform
import argparse
from time import sleep
from ast import literal_eval
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.styles import Style
from prompt_toolkit.history import InMemoryHistory
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

#=============================================================================================
#platform dependent clear screen command
def cls():
	os_name=platform.system().lower()
	if os_name:
		system("cls" if "windows" in os_name else "clear")
	else:
		system("clear")
#clear screen at the start
cls()
#=============================================================================================
class Gpt:
	# some class variables
	Histstr=""
	#
	def __init__(self,model_path,sysprompt,n_ctx=2048,max_tokens=500,temperature=0.8,verbose=False,**kwargs):
		self.maxtoken=max_tokens
		self.llm = Llama(model_path=model_path,n_ctx=n_ctx,max_tokens=max_tokens,temperature=temperature,verbose=verbose,**kwargs)
		self.conv=[{"role": "system", "content": sysprompt }]
				
	def width(self):
		chrcnt = get_terminal_size(0)[0]
		return chrcnt
		
	def ask(self,question,stream=True,**kwargs):
		self.Histstr+=f"\nYou: {question}"
		self.conv.append({"role": "user", "content": question})
		tokens=len(self.llm.tokenize(f"{self.conv}".encode()))
		if tokens>=self.maxtoken/2:
			self.conv.pop(1)
		response = self.llm.create_chat_completion(messages=self.conv,
		stream=stream,**kwargs)
		print(rs.all+"\n"+"‾"*self.width())
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
			print(rs.all+"\n"+"_"*self.width()+"\n")
		else:
			output=response["choices"][0]["message"]["content"]
			print(fg.yellow+f'{output}'+rs.all)
			print("\n"+"="*self.width()+"\n")
	
	def timefmt(self):
		now = datetime.now()
		formatted_time = now.strftime("%B %d, %Y %H:%M:%S")
		tfmt=f"--> Chat on {formatted_time} <---"
		txt=("="*self.width()+"\n"+f"{'-'*int((self.width()-len(tfmt))/2)}{tfmt}{'-'*int((self.width()-len(tfmt))/2)}"+"\n"+"="*self.width())
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

#=============================================================================================	
#commandline argument parsing and model search logic
def auto_type(value):
    try:
        return literal_eval(value)
    except (ValueError, SyntaxError):
        return value

def findmodels(modelpath):
    if path.isfile(modelpath) and modelpath.endswith(".gguf"):  
        return modelpath  
    elif path.isdir(modelpath):  
        mdlist = [x for x in listdir(modelpath) if x.endswith(".gguf")]  
        if not mdlist:  
            print(f"No models found in {modelpath}"); exit()  
        if len(mdlist) == 1:  
            return path.join(modelpath, mdlist[0])  
        while True:  
            try:  
                cls()  
                a = int(input(f'Found models {mdlist} in "{modelpath}"\nEnter [1-{len(mdlist)}]: '))  
                if 1 <= a <= len(mdlist):  
                    return path.join(modelpath, mdlist[a-1])  
                raise ValueError  
            except:  
                cls()  
                input(f"Invalid Input: Enter number [1-{len(mdlist)}]\n\nPress enter to continue... ")  
    else:  
        print(f"Error: Model `{modelpath}` doesn't exist or isn't a model file")  
        exit() 

def cmdargs():
	parser = argparse.ArgumentParser(
	    description="Simple local LLM Terminal Chat interface in python",
	    usage="%(prog)s --model MODEL [--kwargs VALUE]...",
	    epilog=" kwargs example: --n_ctx 2040 --max_tokens 500",
		formatter_class=argparse.RawDescriptionHelpFormatter
	)
	# Model configuration
	parser.add_argument('-m', '--model', 
                       default=path.dirname(path.abspath(__file__)),
                       dest="model_path",
                       type=findmodels,
                       help="GGUF model file or directory containing models")
    
    # Standard parameters
	parser.add_argument('--n_ctx','-ctx',dest="n_ctx",type=auto_type,default=500,
                       help="Context window size in tokens")
	parser.add_argument('--temperature','-t',dest="temperature",type=auto_type,default=0.8,
                       help="Sampling temperature (0.0-2.0)")
	parser.add_argument('--max_tokens','-mt',dest="max_tokens",type=auto_type,default=200,
                       help="Max tokens to generate")
	parser.add_argument('--n_thread','-nt',dest="n_thread",type=auto_type, default=cpu_count(),
                       help="CPU threads for inference")
	parser.add_argument('--system-prompt','-sp',dest="sysprompt",type=auto_type,default="You are a helpful assistant",
                       help="System message for model behavior")
	parser.add_argument('-v', '--verbose',dest="verbose", action='store_true',
                       help="Enable verbose output")
    
	fixed_args, remaining = parser.parse_known_args()
	keyargs= {}
	it = iter(remaining)
	for arg in it:
	    if arg.startswith('--'):
	        keyargs[arg[2:]] = auto_type(next(it, None))
	return vars(fixed_args)|keyargs

#============================================================================================
#Experimental special keywords autocompletion
COMMANDS = ['save', 'clear', 'sysprompt', 'exit', 'help', 'info']
PROMPT_STYLE = Style.from_dict({'prompt': 'noinherit bold','': 'fg:#ff5555 bold'})
HISTORY = InMemoryHistory()

class CommandCompleter(Completer):
    def __init__(self):
        self.commands = COMMANDS
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.lower()
        if not text.startswith('/') or ' ' in text:
            return
        current_word = text[1:]
        for cmd in self.commands:
            if cmd.startswith(current_word):
                yield Completion(
                    cmd,
                    start_position=-len(current_word),
                    style='bg:#008888 #ffffff')
                    
def get_user_input(prompt_text='>>>: '):
    user_input = prompt(
        prompt_text,
        style=PROMPT_STYLE,
        completer=CommandCompleter(),
        complete_while_typing=True,
        history=HISTORY)
    HISTORY.store_string(user_input)
    return user_input
    
#=============================================================================================
#Model loading & chat logic
keyword_args=cmdargs()
cls()
print(f'[ --> Loading model "{path.basename(keyword_args["model_path"])}" <-- ]\n')
chat=Gpt(**keyword_args)
input("\n"+ef.bold+"Press enter to continue..."+ef.rs)
cls()
print(chat.timefmt()+"\n")
# Main chat Loop
while True:
	message = get_user_input("[You]: ")
	#special keywords that different functionality and cannot be passed to the model	
	#-----------------------------------------------------------------------------------------
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
	elif message.strip().startswith("/save"):
		print(rs.all+"\n"+"_"*chat.width()+"\n")
		svpath=message.replace("/save","").strip()
		svpath=svpath if svpath else f'{path.dirname(path.abspath(__file__))}/ChatHistory.txt'
		if svpath and not svpath.isspace():
			savefile=chat.save(svpath)
			print(f"{ef.bold}[Sys:] Saved to '{savefile[1]}' ")
			if savefile[0]=="Error" :
				print(f"{ef.bold}[Sys:] Error: {savefile[1]}")
		else:
			print(fg.rs+f'{ef.bold}[Sys:] Saved to "{savefile[1]}"')
		print(rs.all+"\n"+"‾"*chat.width())	
	elif message=="/help":
		print(rs.all+"\n"+"_"*chat.width()+"\n")
		print(f"{ef.bold}[Sys:]{help}")
		print(rs.all+"\n"+"_"*chat.width()+"\n")
	elif message.strip().startswith("/sysprompt"):
		prom=message.replace("/sysprompt","").strip()
		print(rs.all+"\n"+"_"*chat.width()+"\n")
		if prom:
			chat.conv[0]["content"]=keyword_args["sysprompt"]=prom
			print(f"{ef.bold}[Sys]: Changed system prompt to '{prom}'")
		else:
			print(f"{ef.bold}[Sys]: System prompt: '{chat.conv[0]['content']}'")
		print(rs.all+"\n"+"_"*chat.width()+"\n")
	elif message=="/info":
	    print(rs.all+"\n"+"_"*chat.width()+"\n")
	    print(f"{ef.bold}[Sys]: info: {keyword_args}")
	    print(rs.all+"\n"+"_"*chat.width()+"\n")
	#-----------------------------------------------------------------------------------------
	else:
		chat.ask(question=message,stream=True)

#=============================================================================================		