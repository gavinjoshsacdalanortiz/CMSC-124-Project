from enum import Enum
import sys 
import os

class TokenType(Enum):
    HAI = "HAI"
    KTHXBYE = "KTHXBYE"
    WAZZUP = "WAZZUP"
    BUHBYE = "BUHBYE"
    BTW = "BTW"
    OBTW = "OBTW"
    TLDR = "TLDR"
    I_HAS_A = "I HAS A"
    ITZ = "ITZ"
    R = "R"
    SUM_OF = "SUM OF"
    DIFF_OF = "DIFF OF"
    PRODUKT_OF = "PRODUKT OF"
    QUOSHUNT_OF = "QUOSHUNT OF"
    MOD_OF = "MOD OF"
    BIGGR_OF = "BIGGR OF"
    SMALLR_OF = "SMALLR OF"
    BOTH_OF = "BOTH OF"
    EITHER_OF = "EITHER OF"
    WON_OF = "WON OF"
    NOT = "NOT"
    ANY_OF = "ANY OF"
    ALL_OF = "ALL OF"
    BOTH_SAEM = "BOTH SAEM"
    DIFFRINT = "DIFFRINT"
    SMOOSH = "SMOOSH"
    MAEK = "MAEK"
    A = "A"
    IS_NOW_A = "IS NOW A"
    VISIBLE = "VISIBLE"
    GIMMEH = "GIMMEH"
    O_RLY = "O RLY?"
    YA_RLY = "YA RLY"
    MEBBE = "MEBBE"
    NO_WAI = "NO WAI"
    OIC = "OIC"
    WTF = "WTF?"
    OMG = "OMG"
    OMGWTF = "OMGWTF"
    IM_IN_YR = "IM IN YR"
    UPPIN = "UPPIN"
    NERFIN = "NERFIN"
    YR = "YR"
    TIL = "TIL"
    WILE = "WILE"
    IM_OUTTA_YR = "IM OUTTA YR"
    HOW_IZ_I = "HOW IZ I"
    IF_U_SAY_SO = "IF U SAY SO"
    GTFO = "GTFO"
    FOUND_YR = "FOUND YR"
    I_IZ = "I IZ"
    MKAY = "MKAY"
    AN = "AN"
    NUMBR_LITERAL = "NUMBR"
    NUMBAR_LITERAL = "NUMBAR"
    YARN_LITERAL = "YARN"
    TROOF_LITERAL = "TROOF"
    
class Token:
    def __init__(self, token_type, value, line_number, column):
        self.type = token_type
        self.value = value
        self.line = line_number
        self.column = column
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}', Line: {self.line}, Col: {self.column})"

class Lexeme:
    def __init__(self, source_code):
        self.source = source_code # store LOLCODE source as a string
        self.tokens = []     #List all generated tokens after  def tokenize
        self.line_number = 1 


    def tokenize(self):
        lines = self.source.splitlines() #split the source code into indiv lines for easier checking
        in_multiline_comment = False #implemented to check if we are reading a multi-line comment   

        for line in lines:  #Loop through each line in the source code
            column = 1      #Counter for column restarts to 1 for every new line
            stripped = line.strip()     #aids in removing leading whitespaces per new line

            if stripped.startswith("BTW") or stripped == "": #skip any single line comments met in the process
                self.line_number += 1
                continue
            
            #Multi-Line comment area
            if stripped.startswith("OBTW"):
                in_multiline_comment = True
                self.line_number += 1
                continue
            
            if in_multiline_comment:
                self.line_number += 1
                continue

            #Code for literals and identifiers
            words = stripped.split() #split the line into individual words for easier checking
            
#check if file provided
if len(sys.argv) < 2:
    print("python project.py <filename.lol>") 
    print("provide .lol file to tokenize")
    sys.exit(1)

filename = sys.argv[1]

if not filename.endswith('.lol'): # check file extension
    print("Error: file must have .lol extension")
    sys.exit(1)

if not os.path.exists(filename): # check if file exists
    print(f"Error: File '{filename}' not found")
    sys.exit(1)

# read the file
try:
    with open(filename, 'r') as file:
        code = file.read()
except Exception as e:
    print(f"Error reading file: {e}")
    sys.exit(1)

# tokenize the code
lexer = Lexeme(code)
tokens = lexer.tokenize()

print(f"Tokens from '{filename}':")
print("=" * 60)
for token in tokens:
    print(token)
print("=" * 60)
print(f"Total tokens: {len(tokens)}")