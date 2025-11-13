from token_types import TokenType, Token

class Lexer:
    def __init__(self, source_code):
        self.source = source_code
        self.tokens = []
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

            i = 0
            line_length = len(stripped)
            
            while i < line_length:
                if stripped[i].isspace():
                    i += 1
                    column += 1
                    continue
                
                if stripped[i] == '"':
                    j = i + 1
                    while j < line_length and stripped[j] != '"':
                        j += 1
                    
                    if j < line_length:
                        yarn_literal = stripped[i:j+1]
                        self.tokens.append(Token(TokenType.YARN_LITERAL, yarn_literal, self.line_number, column))
                        i = j + 1
                        column += len(yarn_literal)
                        continue
                
                token_found = False
                for keyword in multiword_keywords:
                    keyword_upper = keyword.upper()
                    if (i + len(keyword)) <= line_length and stripped[i:i+len(keyword)].upper() == keyword_upper:
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
                
                j = i
                while j < line_length and not stripped[j].isspace():
                    j += 1
                
                word = stripped[i:j]
                token_type = None
                
                for t in TokenType:
                    if word.upper() == t.value:
                        token_type = t
                        break
                
                if not token_type:
                    if word.lstrip('-').isdigit():
                        token_type = TokenType.NUMBR_LITERAL
                    elif word.lstrip('-').replace('.', '', 1).isdigit() and word.count('.') <= 1:
                        token_type = TokenType.NUMBAR_LITERAL
                    elif word in ["WIN", "FAIL"]:
                        token_type = TokenType.TROOF_LITERAL
                    elif word == "NOOB":
                        token_type = TokenType.NOOB
                    else:
                        token_type = TokenType.IDENTIFIER
                
                self.tokens.append(Token(token_type, word, self.line_number, column))
                
                i = j
                column += len(word)
            
            self.line_number += 1

        return self.tokens