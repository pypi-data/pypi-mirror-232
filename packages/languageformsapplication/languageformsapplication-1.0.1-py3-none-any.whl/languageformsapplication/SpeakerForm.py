import pyttsx3

import nltk
import pickle

import spacy
import en_core_web_sm

from googletrans import Translator

import customtkinter as ctk
from tkinter import *
from awesometkinter.bidirender import render_text

import requests

import os

# https://stackoverflow.com/questions/2489669/how-do-python-functions-handle-the-types-of-parameters-that-you-pass-in
class Core() :
    # Initialize
    def __init__(self) -> None:
        self.engine = pyttsx3.init()
        self.folder_path = os.path.join(os.path.dirname(__file__))
        self.set_rate(self)
        self.set_voice(self)
        self.tag_loader()
        self.tag_loader_spacy()

        self.translator = Translator()
        self.translator_lang = self.set_translator_lang(self)

    # Methods    
    def speak(self,text):
        self.engine.say(text)
        self.engine.runAndWait()
        
    def record(self,text):
        self.engine.save_to_file(text, self.folder_path+'output.wav')
        self.engine.runAndWait()
    
    def set_rate(self,Rate=120):
        self.engine.setProperty('rate', Rate) #rate: 120 ~ 200

    def set_voice(self,lang="en"):
        self.engine.setProperty('voice', lang) #lang: en
    
    def tag_loader(self):
        nltk.data.path.append(self.folder_path+"nltk_data")
        file_path = self.folder_path+"\\nltk_data\\taggers\\averaged_perceptron_tagger\\averaged_perceptron_tagger.pickle"
        with open(file_path, 'rb') as file:
            self.tagger = pickle.load(file)

    def tag_loader_spacy(self):
        # self.nlp = spacy.load('en_core_web_sm')
        self.nlp = en_core_web_sm.load()
        
    def tag_translator(self,InputTag):
        
        ## Make Better
        tag_descriptions = {
            'CC': 'Coordinating conjunction',
            'CD': 'Cardinal number',
            'DT': 'Determiner',
            'EX': 'Existential there',
            'FW': 'Foreign word',
            'IN': 'Preposition or subordinating conjunction',
            'JJ': 'Adjective',
            'JJR': 'Adjective, comparative',
            'JJS': 'Adjective, superlative',
            'LS': 'List item marker',
            'MD': 'Modal',
            'NN': 'Noun, singular or mass',
            'NNS': 'Noun, plural',
            'NNP': 'Proper noun, singular',
            'NNPS': 'Proper noun, plural',
            'PDT': 'Predeterminer',
            'POS': 'Possessive ending',
            'PRP': 'Personal pronoun',
            'PRP$': 'Possessive pronoun',
            'RB': 'Adverb',
            'RBR': 'Adverb, comparative',
            'RBS': 'Adverb, superlative',
            'RP': 'Particle',
            'SYM': 'Symbol',
            'TO': 'to',
            'UH': 'Interjection',
            'VB': 'Verb, base form',
            'VBD': 'Verb, past tense',
            'VBG': 'Verb, gerund or present participle',
            'VBN': 'Verb, past participle',
            'VBP': 'Verb, non-3rd person singular present',
            'VBZ': 'Verb, 3rd person singular present',
            'WDT': 'Wh-determiner',
            'WP': 'Wh-pronoun',
            'WP$': 'Possessive wh-pronoun',
            'WRB': 'Wh-adverb'
            }
        
        if InputTag in tag_descriptions:
            description = tag_descriptions[InputTag]
            return description
        else:
            return "unknown"

    def tag_translator_spacy(self,InputTag):

        tag_descriptions = {
            "ADJ": "Adjective",
            "ADP": "Adposition",
            "ADV": "Adverb",
            "AUX": "Auxiliary verb",
            "CONJ": "Conjunction",
            "CCONJ": "Coordinating conjunction",
            "DET": "Determiner",
            "INTJ": "Interjection",
            "NOUN": "Noun",
            "NUM": "Numeral",
            "PART": "Particle",
            "PRON": "Pronoun",
            "PROPN": "Proper noun",
            "PUNCT": "Punctuation",
            "SCONJ": "Subordinating conjunction",
            "SYM": "Symbol",
            "VERB": "Verb",
            "X": "Other",
            "SPACE": "Space",
        }
        ValidateIndex = self.match_tag_spacy(InputTag) # Make Batter This
        if InputTag[ValidateIndex] in tag_descriptions:
            description = tag_descriptions[InputTag[ValidateIndex]]
            return description
        else:
            return "unknown"
            
    def find_tag(self,text):
        tags = nltk.pos_tag([text])
        tag = tags[0][1]
        return tag
    
    def find_tag_spacy(self,text):
        tags = self.nlp(text)
        taglist = []
        for token in tags:
            taglist.append(token.pos_)
            
        return taglist

    def match_tag_spacy(self,TagList):
        if len(TagList)==2 and (set(TagList) == set(["ADP" , "VERB"]) or set(TagList) == set(["PART" , "VERB"])):
            return TagList.index("VERB")
        else :
            return 0

    def set_translator_lang(self,lang="fa"):
        self.translator_lang = lang ;

    def translate_action(self,text):
        translated_text = self.translator.translate(text, self.translator_lang)
        return translated_text.text

        
        
### Use:
# List = ["look at"]
# _text = List[0]
# _core = Core()

## Config
# _core.set_rate(120)
# _core.set_voice('en')


# Speak
# _core.speak(_text)

# Record
# _core.record(_text)

# Tag
# _tag = _core.find_tag(_text)
# _expo = _core.tag_translator(_tag)
# print(_text+" is "+_expo)

# Tag_spacy
# _tag = _core.find_tag_spacy(_text)
# _expo = _core.tag_translator_spacy(_tag)
# print(_text+" is "+_expo)

# Translate - Online
# _core.set_translator_lang()
# _trans = _core.translate_action(_text)
# print(_trans)




class App(ctk.CTk):

    def __init__(self, *args, **kwargs):
        ctk.set_appearance_mode("Dark") 
        ctk.set_default_color_theme("blue")
        super().__init__(*args, **kwargs)
        self.folder_path = os.path.join(os.path.dirname(__file__))

        # Initialze
        self.title("Speaker Application")   
        self.geometry("389x689+0+0")
        self.iconbitmap(self.get_software_icon())
        
        # DataBase
        self.Words = self.read_file_in_list()

        # Rows and Columns
        self.NOC = 6 ; # Number of Column
        self.NOR = 6 ; # Number of Row

        for i in range(self.NOR):
            self.grid_rowconfigure(i, weight=1)

        for i in range(self.NOC):
            self.grid_columnconfigure(i, weight=1)

        # Row 0
        self.button1 = ctk.CTkButton(master=self,command=self.backward,text="⏪",font=('Consolas bold',35))
        self.button1.grid(row=0, column=0,columnspan=1,padx=(20,20), pady=(20, 20), sticky="nsew")
        self.button2 = ctk.CTkButton(master=self,command=self.implementation,text="▶️",font=('Consolas bold',35))
        self.button2.grid(row=0, column=1,columnspan=4,padx=(10,10), pady=(20, 20), sticky="nsew")
        self.button3 = ctk.CTkButton(master=self,command=self.forward,text="⏩",font=('Consolas bold',35))
        self.button3.grid(row=0, column=5,columnspan=1,padx=(20,20), pady=(20, 20), sticky="nsew")

        # Row 1,2,3
        self.label1 = ctk.CTkLabel(master=self, text="",font=('Times New Roman bold',40))
        self.label1.grid(row=1, column=0,columnspan=6, padx=(20,20), pady=(20, 20), sticky="w")
        self.label2 = ctk.CTkLabel(master=self, text="",font=('Consolas bold',20))
        self.label2.grid(row=2, column=0,columnspan=6, padx=(20,20), pady=(20, 20), sticky="w")
        self.label3 = ctk.CTkLabel(master=self, text=render_text(""),font=('Homa bold',20),justify=ctk.RIGHT)
        self.label3.grid(row=3, column=0,columnspan=6, padx=(20,20), pady=(20, 20), sticky="e")
        
        # Row 4
        self.combo1 = ctk.CTkOptionMenu(master=self,command=self.combobox_callback,font=('Times New Roman bold',20),width=20,height=60,dropdown_font=('Times New Roman',12),dynamic_resizing=True)
        self.combo1.grid(row=4, column=0,columnspan=6,padx=(20,20), pady=(30, 30), sticky="nsew")
        
        self.combo_bind_var = self.Binding(self.combo1,self.Words,self.update_values)
        

        # Row 5
        self.button4 = ctk.CTkButton(master=self,command=self.add_word_to_list,text="+",font=('Consolas bold',40))
        self.button4.grid(row=5, column=0,columnspan=1,padx=(20,20),pady=(20, 20), sticky="nsew")
        self.button5 = ctk.CTkButton(master=self,command=self.remove_word_from_list,text="-",font=('Consolas bold',40))
        self.button5.grid(row=5, column=1,columnspan=1,padx=(20,20), pady=(20, 20), sticky="nsew")

        # Row 6
        self.text1 = ctk.CTkTextbox(master=self,font=('Consolas bold',35),width=350,height=120)
        self.text1.grid(row=6, column=0,columnspan=6, padx=(20,20), pady=(20, 20), sticky="w")
        self.text1.insert("0.0", "")

    ## Constructors
    def get_software_icon(self):
        file_name = 'icon.ico'
        return os.path.join(self.folder_path, file_name)

    ## Methods
    def read_file_in_list(self):
        file_name = 'Data.db'
        full_name = os.path.join(self.folder_path, file_name)
        lines = []
        with open(full_name, 'r') as file:
            for line in file:
                line = line.strip()  
                lines.append(line)
        return lines
    
    def write_list_in_file(self):
        file_name = 'Data.db'
        full_name = os.path.join(self.folder_path, file_name)
        with open(full_name, "w") as file:
            file.writelines(line + "\n" for line in self.Words)
    
    def internet_connection(self):
        try:
            response = requests.get("https://www.google.com", timeout=1000)
            return True
        except requests.ConnectionError:
            return False   
    
    ## Events
    def add_word_to_list(self):
        new_word = self.text1.get("1.0","end-1c")
        is_unique = not [word for word in self.Words if new_word == word]
        if new_word.replace(" ", "").isalpha() and is_unique: # and not repeated
            self.Words.append(new_word)
            self.combo1.configure(values=self.Words)
            if len(self.Words) > 0 : self.combo1.set(self.Words[-1])
            self.write_list_in_file()
        self.text1.delete("1.0", "end")

    def remove_word_from_list(self):
        if len(self.Words) != 0 :
            index_word = self.combo1.get()

            list_words = self.Words
            index_dict = {word: idx for idx, word in enumerate(list_words)}

            removed_index = index_dict[index_word] ## Will removed
            list_words.remove(index_word)

            self.Words = list_words
            self.combo1.configure(values=self.Words)

            self.combo1.set("None") if len(self.Words) == 0 else self.combo1.set(self.Words[removed_index-1])
            self.write_list_in_file()

    def update_values(self,*args):
        self.label1.configure(text = self.combo_bind_var.get())
        
        _core = Core()
        _tag = _core.find_tag_spacy(self.combo_bind_var.get())
        _expo = _core.tag_translator_spacy(_tag)
        self.label2.configure(text = _expo)

        if self.internet_connection():
            _core.set_translator_lang()
            _trans = _core.translate_action(self.combo_bind_var.get())
            self.label3.configure(text = _trans)
        else :
            self.label3.configure(text = "")

    def implementation(self):
        _core = Core()
        _core.speak(self.combo_bind_var.get())
    
    def backward(self):
        if len(self.Words) != 0 :
            index_word = self.combo1.get()

            list_words = self.Words
            index_dict = {word: idx for idx, word in enumerate(list_words)}

            selected_index = index_dict[index_word]

            value = len(self.Words)-1 if selected_index-1 == -1 else selected_index-1

            self.combo1.set(self.Words[value])

    def forward(self):
        if len(self.Words) != 0 :
            index_word = self.combo1.get()

            list_words = self.Words
            index_dict = {word: idx for idx, word in enumerate(list_words)}

            selected_index = index_dict[index_word]

            value = 0 if selected_index+1 == len(self.Words) else selected_index+1

            self.combo1.set(self.Words[value])

    def combobox_callback(self,choice):
        # print("combobox dropdown clicked:", choice)
        pass
    
    def Binding(self,Obj,List,Method): # Very Important Event
        BindVar = StringVar()
            
        if len(List) == 0:
            BindVar.set("None")
            Obj.configure(values = [],variable = BindVar)
        else :
            BindVar.set(List[-1])
            Obj.configure(values = List,variable = BindVar)

        BindVar.trace('w', Method)
        
        return BindVar
 
 
# if __name__ == "__main__":
#     app = App()
#     app.mainloop() 
