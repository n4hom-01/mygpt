#!/usr/bin/env python3
from llama_cpp import Llama
from os import get_terminal_size,system,path,chdir, listdir
from sty import fg, bg, ef, rs 
from sys import argv
from datetime import datetime
import platform

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
	def __init__(self,model_path,sysprompt,n_ctx=2048,max_tokens=500,temprature=0.8,verbose=False,**kwargs):
		self.maxtoken=max_tokens
		self.llm = Llama(model_path=model_path,n_ctx=n_ctx,max_tokens=max_tokens,temprature=temprature,verbose=verbose,**kwargs)
		self.conv=[{"role": "system", "content": sysprompt }]
	
	def ask(self,question,stream=True,**kwargs):
		self.Histstr+=f"\nYou: {question}"
		self.conv.append({"role": "user", "content": question})
		tokens=len(self.llm.tokenize(f"{self.conv}".encode()))
		if tokens>=self.maxtoken/2:
			self.conv.pop(1)
		response = self.llm.create_chat_completion(messages=self.conv,
		stream=stream)
		print(rs.all+"\n"+"‾"*self.chrcnt)
		print(ef.bold+"AI"+": ",end="")
		resp=""
		if stream:
			for chunk in response:
				delta = chunk["choices"][0]["delta"]
				if "content" in delta:
					output=delta["content"]
					resp+=output
					print(fg.yellow+f'{output}',end="", flush=True)
			self.Histstr+=f"\nAI: {resp}"
			print(rs.all+"\n"+"_"*self.chrcnt+"\n")
		else:
			output=response["choices"][0]["message"]["content"]
			print(fg.yellow+f'{output}'+rs.all)
			print("\n"+"="*self.chrcnt+"\n")
	
	def timefmt(self):
		now = datetime.now()
		formatted_time = now.strftime("%B %d, %Y %H:%M:%S")
		tfmt=f"--- Chat on {formatted_time} ---"
		txt=("="*self.chrcnt+"\n"+f"{'-'*int((self.chrcnt-len(tfmt))/2)}{tfmt}{'-'*int((self.chrcnt-len(tfmt))/2)}"+"\n"+"="*self.chrcnt)
		return txt

				
	def save(self,filename):
		sdir=path.dirname(filename)
		name=path.basename(filename)
		chdir(sdir if path.exists(sdir) else path.dirname(argv[0]))
		with open(f"{name[0:name.index(".")]}.txt","a") as file:
			file.write("\n\n"+self.timefmt()+"\n")
			file.write(f"{self.Histstr}")
			file.close()
		print(fg.rs+f'\n>>> Saved sucessfully to "{name[0:name.index(".")]}.txt" <<<')
			

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


sysprom="you are helpful assistant called dan"
model=SelectModel()
print(f'[ Loading model "{model}"...]')
chat=Gpt(model_path=model,sysprompt=sysprom,n_ctx=8192,temprature=0.8,n_threads=8)
cls()
print(chat.timefmt()+"\n")

while True:
	question=input(ef.bold+"You: "+fg(187, 148, 239))
	if question=="/clear":
		cls()
	elif question=="/exit":
		prompt=input("\n\nWould you like to save the conversation to a file?: ")
		if prompt=="y" or prompt=="yes":
		  chat.save("/sdcard/ChatHistory.txt")
		print("[ Exiting Chat... ]")
		exit()
	else:
		chat.ask(question=question,stream=True)