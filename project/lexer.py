from token_types import TokenType, Token # Import TokenType enum and Token class

# Lexer class for lexing LOLCODE code
class Lexer:
    # Initialize lexer with source code
    def __init__(self, source_code):
        self.source = source_code
        self.tokens = []
        self.line_number = 1

    # Tokenize source code into a list of tokens
    def tokenize(self):
        # split source code into lines for processing and tracking line numbers
        # separates handling for single-line and multi-line comments as well as string literals / multi-word keywords / single-word tokens etc.
        lines = self.source.splitlines()
        in_multiline_comment = False
        
        # List of multi-word keywords in LOLCODE
        multiword_keywords = [
            "I HAS A", "SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", 
            "MOD OF", "BIGGR OF", "SMALLR OF", "BOTH OF", "EITHER OF", 
            "WON OF", "ANY OF", "ALL OF", "BOTH SAEM", "IS NOW A", 
            "O RLY?", "YA RLY", "NO WAI", "WTF?", "IM IN YR", "IM OUTTA YR", 
            "HOW IZ I", "IF U SAY SO", "FOUND YR", "I IZ"
        ]

        # Process each line
        for line in lines:
            column = 1 # Track column number for error reporting
            stripped = line.strip() # Remove leading/trailing whitespace

            # Handle comments
            if stripped.startswith("BTW ") or stripped == "":
                self.line_number += 1
                continue
            
            # Handle start/end of multi-line comments
            if stripped.startswith("OBTW "):
                in_multiline_comment = True
                self.line_number += 1
                continue
            
            # Handle end of multi-line comment
            if stripped.startswith("TLDR"):
                in_multiline_comment = False
                self.line_number += 1
                continue
            
            # Skip line inside multi-line comments
            if in_multiline_comment:
                self.line_number += 1
                continue

            # Tokenization logic --
            # track position in line
            i = 0 # 
            line_length = len(stripped) 
            
            # Process characters in the line
            while i < line_length:
                # Skip whitespace
                if stripped[i].isspace():
                    i += 1
                    column += 1
                    continue
                
                # Handle string literals by checking for opening quote and finding closing quote
                if stripped[i] == '"':
                    j = i + 1
                    while j < line_length and stripped[j] != '"':
                        j += 1
                    
                    # If closing quote found, get string literal token
                    if j < line_length:
                        yarn_literal = stripped[i:j+1]
                        self.tokens.append(Token(TokenType.YARN_LITERAL, yarn_literal, self.line_number, column))
                        i = j + 1
                        column += len(yarn_literal)
                        continue
                
                # Check for multi-word keywords first
                token_found = False # boolean flag to indicate if token was found
                
                # Check each multi-word keyword by iterating through list + matching at current position
                for keyword in multiword_keywords:
                    keyword_upper = keyword.upper()
                    if (i + len(keyword)) <= line_length and stripped[i:i+len(keyword)].upper() == keyword_upper:
                        # Ensure keyword is not part of a larger word
                        next_char_index = i + len(keyword)
                        # Check if next character is whitespace or punctuation or end of line
                        if (next_char_index >= line_length or 
                            stripped[next_char_index].isspace() or
                            stripped[next_char_index] in [',', ';', ')', '(', '.']):
                            
                            # Identify token type for the multi-word keyword
                            token_type = None
                            for t in TokenType:
                                if t.value == keyword_upper:
                                    token_type = t
                                    break
                            
                            # Add token if type found
                            if token_type:
                                self.tokens.append(Token(token_type, keyword, self.line_number, column))
                            
                            # Move index and column forward by length of keyword
                            i += len(keyword)
                            column += len(keyword)
                            token_found = True
                            break
                
                # If multi-word keyword found --> skip to next iteration
                if token_found:
                    continue
                
                # Handle single-word tokens (keywords, literals, identifiers)
                j = i
                while j < line_length and not stripped[j].isspace():
                    j += 1
                
                # Extract word and determine type
                word = stripped[i:j]
                token_type = None
                
                # Check if word matches any single-word keyword
                for t in TokenType:
                    if word.upper() == t.value:
                        token_type = t
                        break
                    
                # If not a keyword, check for literals or identifiers
                if not token_type:
                    # Check for numeric literals (NUMBR, NUMBAR), TROOF, NOOB, or IDENTIFIER
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
                
                # add identified token to list
                self.tokens.append(Token(token_type, word, self.line_number, column))
                
                i = j
                column += len(word)
            
            self.line_number += 1

        # return list of tokens
        return self.tokens