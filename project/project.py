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
    IDENTIFIER = "IDENTIFIER"
    
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
        lines = self.source.splitlines()
        in_multiline_comment = False
        multiword_keywords = [
            "I HAS A", "SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", 
            "MOD OF", "BIGGR OF", "SMALLR OF", "BOTH OF", "EITHER OF", 
            "WON OF", "ANY OF", "ALL OF", "BOTH SAEM", "IS NOW A", 
            "O RLY?", "YA RLY", "NO WAI", "WTF?", "IM IN YR", "IM OUTTA YR", 
            "HOW IZ I", "IF U SAY SO", "FOUND YR", "I IZ"
        ]

        for line in lines:
            column = 1
            stripped = line.strip()

            if stripped.startswith("BTW") or stripped == "":
                self.line_number += 1
                continue
            
            #Multi-line comment area
            if stripped.startswith("OBTW"):
                in_multiline_comment = True
                self.line_number += 1
                continue
            
            if stripped.startswith("TLDR"):
                in_multiline_comment = False
                self.line_number += 1
                continue
            
            if in_multiline_comment:
                self.line_number += 1
                continue

            #process line character by character
            i = 0
            line_length = len(stripped)
            
            while i < line_length:
                #skip whitespace
                if stripped[i].isspace():
                    i += 1
                    column += 1
                    continue
                
                #handle string literals
                if stripped[i] == '"':
                    #find closing quote
                    j = i + 1
                    while j < line_length and stripped[j] != '"':
                        j += 1
                    
                    if j < line_length:  #found closing quote
                        yarn_literal = stripped[i:j+1]
                        self.tokens.append(Token(TokenType.YARN_LITERAL, yarn_literal, self.line_number, column))
                        i = j + 1
                        column += len(yarn_literal)
                        continue
                    else:
                        # unclosed string --> handle error
                        pass
                
                #check for multi-word keywords
                token_found = False
                for keyword in multiword_keywords:
                    keyword_upper = keyword.upper()
                    if (i + len(keyword)) <= line_length and stripped[i:i+len(keyword)].upper() == keyword_upper:
                        #check if complete word (followed by space or EoL)
                        next_char_index = i + len(keyword)
                        if (next_char_index >= line_length or 
                            stripped[next_char_index].isspace() or
                            stripped[next_char_index] in [',', ';', ')', '(', '.']):
                            
                            token_type = None
                            for t in TokenType:
                                if t.value == keyword_upper:
                                    token_type = t
                                    break
                            
                            if token_type:
                                self.tokens.append(Token(token_type, keyword, self.line_number, column))
                            
                            i += len(keyword)
                            column += len(keyword)
                            token_found = True
                            break
                
                if token_found:
                    continue
                
                #single-word tokens
                j = i
                while j < line_length and not stripped[j].isspace():
                    j += 1
                
                word = stripped[i:j]
                
                #determine token type
                token_type = None
                
                # check if keyword
                for t in TokenType:
                    if word.upper() == t.value:
                        token_type = t
                        break
                
                if not token_type:
                    if word.isdigit():
                        token_type = TokenType.NUMBR_LITERAL
                    elif word.replace('.', '', 1).isdigit() and word.count('.') == 1:
                        token_type = TokenType.NUMBAR_LITERAL
                    elif word in ["WIN", "FAIL"]:
                        token_type = TokenType.TROOF_LITERAL
                    else:
                        token_type = TokenType.IDENTIFIER
                
                self.tokens.append(Token(token_type, word, self.line_number, column))
                
                # move to next word
                i = j
                column += len(word)
            
            self.line_number += 1

        return self.tokens
    
#Section for File Handling
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
for token in tokens:
    print(token)
print(f"Total tokens: {len(tokens)}")

