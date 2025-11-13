from token_types import TokenType
from LOL_exceptions import BreakException, ReturnException

class Parser:
    def __init__(self, tokens, update_symbol_callback, write_console_callback, read_input_callback):
        self.tokens = tokens
        self.position = 0
        self.variables = {}
        self.IT = None
        self.update_symbol_callback = update_symbol_callback
        self.write_console_callback = write_console_callback
        self.read_input_callback = read_input_callback
        self.functions = {}
    
    def current_token(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None
    
    def peek(self, offset=1):
        if self.position + offset < len(self.tokens):
            return self.tokens[self.position + offset]
        return None
    
    def advance(self):
        self.position += 1
    
    def expect(self, token_type):
        token = self.current_token()
        if not token or token.type != token_type:
            raise SyntaxError(f"Syntax Error at line {token.line if token else 'EOF'}: Expected {token_type.value}, got {token.type.value if token else 'EOF'}")
        self.advance()
        return token
    
    def parse(self):
        self.expect(TokenType.HAI)
        
        # Optional version number
        if self.current_token() and self.current_token().type in [TokenType.NUMBR_LITERAL, TokenType.NUMBAR_LITERAL]:
            self.advance()
        
        # Optional variable declaration section
        if self.current_token() and self.current_token().type == TokenType.WAZZUP:
            self.advance()
            while self.current_token() and self.current_token().type != TokenType.BUHBYE:
                self.parse_variable_declaration()
            self.expect(TokenType.BUHBYE)
        
        # Main program body
        while self.current_token() and self.current_token().type != TokenType.KTHXBYE:
            if self.current_token().type == TokenType.HOW_IZ_I:
                self.parse_function_definition()
            else:
                self.parse_statement()
        
        self.expect(TokenType.KTHXBYE)
    
    def parse_variable_declaration(self):
        self.expect(TokenType.I_HAS_A)
        var_name = self.expect(TokenType.IDENTIFIER).value
        
        value = None  # NOOB by default
        
        if self.current_token() and self.current_token().type == TokenType.ITZ:
            self.advance()
            value = self.parse_expression()
        
        self.variables[var_name] = value
        self.update_symbol_callback(var_name, value)
    
    def parse_statement(self):
        token = self.current_token()
        
        if not token:
            return
        
        if token.type == TokenType.I_HAS_A:
            self.parse_variable_declaration()
        elif token.type == TokenType.VISIBLE:
            self.parse_visible()
        elif token.type == TokenType.GIMMEH:
            self.parse_gimmeh()
        elif token.type == TokenType.O_RLY:
            self.parse_if_then_else()
        elif token.type == TokenType.WTF:
            self.parse_switch()
        elif token.type == TokenType.IM_IN_YR:
            self.parse_loop()
        elif token.type == TokenType.GTFO:
            self.advance()
            raise BreakException()
        elif token.type == TokenType.FOUND_YR:
            self.advance()
            value = self.parse_expression()
            raise ReturnException(value)
        elif token.type == TokenType.I_IZ:
            result = self.parse_function_call()
            self.IT = result
            self.update_symbol_callback('IT', self.IT)
        elif token.type == TokenType.IDENTIFIER:
            # Check for assignment or type cast
            if self.peek() and self.peek().type == TokenType.R:
                self.parse_assignment()
            elif self.peek() and self.peek().type == TokenType.IS_NOW_A:
                self.parse_type_cast()
            else:
                # Expression statement (updates IT)
                self.IT = self.parse_expression()
                self.update_symbol_callback('IT', self.IT)
        else:
            # Expression statement
            self.IT = self.parse_expression()
            self.update_symbol_callback('IT', self.IT)
    
    def parse_assignment(self):
        var_name = self.expect(TokenType.IDENTIFIER).value
        
        if var_name not in self.variables:
            raise NameError(f"Semantic Error: Variable '{var_name}' not declared")
        
        self.expect(TokenType.R)
        value = self.parse_expression()
        
        self.variables[var_name] = value
        self.update_symbol_callback(var_name, value)
        self.IT = value
        self.update_symbol_callback('IT', self.IT)
    
    def parse_visible(self):
        self.advance()  # consume VISIBLE
        
        output = ''
        first = True
        suppress_newline = False
        
        while (self.current_token() and 
               self.current_token().type not in [TokenType.I_HAS_A, TokenType.VISIBLE, 
                                                   TokenType.GIMMEH, TokenType.KTHXBYE,
                                                   TokenType.YA_RLY, TokenType.NO_WAI,
                                                   TokenType.OIC, TokenType.O_RLY,
                                                   TokenType.IM_OUTTA_YR, TokenType.OMG,
                                                   TokenType.OMGWTF, TokenType.GTFO]):
            
            # Check for exclamation mark (suppress newline)
            if self.current_token().value == '!':
                suppress_newline = True
                self.advance()
                break
            
            if not first:
                output += ' '
            first = False
            
            value = self.parse_expression()
            output += self.stringify(value)
            
            if self.current_token() and self.current_token().type == TokenType.AN:
                self.advance()
        
        if not suppress_newline:
            output += '\n'
        
        self.write_console_callback(output)
    
    def parse_gimmeh(self):
        self.advance()  # consume GIMMEH
        var_name = self.expect(TokenType.IDENTIFIER).value
        
        if var_name not in self.variables:
            raise NameError(f"Semantic Error: Variable '{var_name}' not declared")
        
        input_value = self.read_input_callback(f"Enter value for {var_name}:")
        self.variables[var_name] = input_value
        self.update_symbol_callback(var_name, input_value)
    
    def parse_if_then_else(self):
        self.advance()  # consume O RLY?
        
        condition = self.IT
        
        self.expect(TokenType.YA_RLY)
        
        if self.is_truthy(condition):
            # Execute YA RLY block
            while (self.current_token() and 
                   self.current_token().type not in [TokenType.NO_WAI, TokenType.MEBBE, TokenType.OIC]):
                self.parse_statement()
            
            # Skip else branches
            while self.current_token() and self.current_token().type != TokenType.OIC:
                self.advance()
        else:
            # Skip YA RLY block
            while (self.current_token() and 
                   self.current_token().type not in [TokenType.NO_WAI, TokenType.MEBBE, TokenType.OIC]):
                self.advance()
            
            # Execute NO WAI if present
            if self.current_token() and self.current_token().type == TokenType.NO_WAI:
                self.advance()
                while self.current_token() and self.current_token().type != TokenType.OIC:
                    self.parse_statement()
        
        self.expect(TokenType.OIC)
    
    def parse_switch(self):
        self.advance()  # consume WTF?
        
        switch_value = self.IT
        found_match = False
        in_omgwtf = False
        
        while self.current_token() and self.current_token().type != TokenType.OIC:
            if self.current_token().type == TokenType.OMG:
                self.advance()
                case_value = self.parse_expression()
                
                if not found_match and not in_omgwtf:
                    if switch_value == case_value:
                        found_match = True
                        # Execute this case
                        while (self.current_token() and 
                               self.current_token().type not in [TokenType.OMG, TokenType.OMGWTF, TokenType.OIC]):
                            try:
                                self.parse_statement()
                            except BreakException:
                                # GTFO encountered, break out of switch
                                while self.current_token() and self.current_token().type != TokenType.OIC:
                                    self.advance()
                                break
                    else:
                        # Skip this case
                        while (self.current_token() and 
                               self.current_token().type not in [TokenType.OMG, TokenType.OMGWTF, TokenType.OIC]):
                            self.advance()
                else:
                    # Already found match or in default, skip
                    while (self.current_token() and 
                           self.current_token().type not in [TokenType.OMG, TokenType.OMGWTF, TokenType.OIC]):
                        self.advance()
            
            elif self.current_token().type == TokenType.OMGWTF:
                self.advance()
                in_omgwtf = True
                if not found_match:
                    # Execute default case
                    while self.current_token() and self.current_token().type != TokenType.OIC:
                        try:
                            self.parse_statement()
                        except BreakException:
                            while self.current_token() and self.current_token().type != TokenType.OIC:
                                self.advance()
                            break
            else:
                self.advance()
        
        if self.current_token() and self.current_token().type == TokenType.OIC:
            self.expect(TokenType.OIC)
    
    def parse_loop(self):
        self.advance()  # consume IM IN YR
        loop_name = self.expect(TokenType.IDENTIFIER).value
        
        # Check for operation (UPPIN or NERFIN)
        operation = None
        loop_var = None
        
        if self.current_token() and self.current_token().type in [TokenType.UPPIN, TokenType.NERFIN]:
            operation = self.current_token().type
            self.advance()
            self.expect(TokenType.YR)
            loop_var = self.expect(TokenType.IDENTIFIER).value
            
            if loop_var not in self.variables:
                raise NameError(f"Semantic Error: Loop variable '{loop_var}' not declared")
        
        # Check for condition (TIL or WILE)
        condition_type = None
        condition_start_pos = None
        
        if self.current_token() and self.current_token().type in [TokenType.TIL, TokenType.WILE]:
            condition_type = self.current_token().type
            self.advance()
            condition_start_pos = self.position
            # Skip the condition for now, we'll evaluate it in the loop
            self.skip_expression()
        
        # Mark the start of loop body
        loop_body_start = self.position
        
        # Find the end of the loop
        depth = 1
        loop_end = self.position
        while loop_end < len(self.tokens):
            if self.tokens[loop_end].type == TokenType.IM_IN_YR:
                depth += 1
            elif self.tokens[loop_end].type == TokenType.IM_OUTTA_YR:
                depth -= 1
                if depth == 0:
                    break
            loop_end += 1
        
        # Execute loop
        while True:
            # Check condition if present
            if condition_type:
                saved_pos = self.position
                self.position = condition_start_pos
                condition_value = self.parse_expression()
                self.position = saved_pos
                
                if condition_type == TokenType.TIL:
                    if self.is_truthy(condition_value):
                        break
                else:  # WILE
                    if not self.is_truthy(condition_value):
                        break
            
            # Execute loop body
            self.position = loop_body_start
            try:
                while self.position < loop_end:
                    if self.current_token().type == TokenType.IM_OUTTA_YR:
                        break
                    self.parse_statement()
            except BreakException:
                break
            
            # Update loop variable
            if operation and loop_var:
                if operation == TokenType.UPPIN:
                    self.variables[loop_var] = self.to_number(self.variables[loop_var]) + 1
                else:  # NERFIN
                    self.variables[loop_var] = self.to_number(self.variables[loop_var]) - 1
                self.update_symbol_callback(loop_var, self.variables[loop_var])
        
        # Move position to after loop
        self.position = loop_end
        if self.current_token() and self.current_token().type == TokenType.IM_OUTTA_YR:
            self.advance()
            expected_name = self.expect(TokenType.IDENTIFIER).value
            if expected_name != loop_name:
                raise SyntaxError(f"Loop name mismatch: expected '{loop_name}', got '{expected_name}'")
    
    def parse_function_definition(self):
        self.advance()  # consume HOW IZ I
        func_name = self.expect(TokenType.IDENTIFIER).value
        
        # Parse parameters
        params = []
        while self.current_token() and self.current_token().type == TokenType.YR:
            self.advance()
            param_name = self.expect(TokenType.IDENTIFIER).value
            params.append(param_name)
            if self.current_token() and self.current_token().type == TokenType.AN:
                self.advance()
        
        # Mark start of function body
        func_body_start = self.position
        
        # Find end of function
        depth = 1
        func_end = self.position
        while func_end < len(self.tokens):
            if self.tokens[func_end].type == TokenType.HOW_IZ_I:
                depth += 1
            elif self.tokens[func_end].type == TokenType.IF_U_SAY_SO:
                depth -= 1
                if depth == 0:
                    break
            func_end += 1
        
        # Store function
        self.functions[func_name] = {
            'params': params,
            'body_start': func_body_start,
            'body_end': func_end
        }
        
        # Skip to end of function
        self.position = func_end
        if self.current_token() and self.current_token().type == TokenType.IF_U_SAY_SO:
            self.advance()
    
    def parse_function_call(self):
        self.advance()  # consume I IZ
        func_name = self.expect(TokenType.IDENTIFIER).value
        
        if func_name not in self.functions:
            raise NameError(f"Semantic Error: Function '{func_name}' not defined")
        
        func_info = self.functions[func_name]
        
        # Parse arguments
        args = []
        while self.current_token() and self.current_token().type == TokenType.YR:
            self.advance()
            arg_value = self.parse_expression()
            args.append(arg_value)
            if self.current_token() and self.current_token().type == TokenType.AN:
                self.advance()
        
        if self.current_token() and self.current_token().type == TokenType.MKAY:
            self.advance()
        
        # Check parameter count
        if len(args) != len(func_info['params']):
            raise ValueError(f"Function '{func_name}' expects {len(func_info['params'])} arguments, got {len(args)}")
        
        # Save current state
        saved_position = self.position
        saved_variables = self.variables.copy()
        
        # Set up parameters
        for param, arg in zip(func_info['params'], args):
            self.variables[param] = arg
        
        # Execute function
        self.position = func_info['body_start']
        return_value = None
        
        try:
            while self.position < func_info['body_end']:
                self.parse_statement()
        except ReturnException as e:
            return_value = e.value
        
        # Restore state
        self.position = saved_position
        self.variables = saved_variables
        
        return return_value if return_value is not None else None
    
    def skip_expression(self):
        """Skip an expression without evaluating it"""
        token = self.current_token()
        if not token:
            return
        
        if token.type in [TokenType.NUMBR_LITERAL, TokenType.NUMBAR_LITERAL, 
                         TokenType.YARN_LITERAL, TokenType.TROOF_LITERAL,
                         TokenType.NOOB, TokenType.IDENTIFIER]:
            self.advance()
        elif token.type in [TokenType.SUM_OF, TokenType.DIFF_OF, TokenType.PRODUKT_OF,
                           TokenType.QUOSHUNT_OF, TokenType.MOD_OF, TokenType.BIGGR_OF,
                           TokenType.SMALLR_OF, TokenType.BOTH_OF, TokenType.EITHER_OF,
                           TokenType.WON_OF, TokenType.BOTH_SAEM, TokenType.DIFFRINT]:
            self.advance()
            self.skip_expression()
            if self.current_token() and self.current_token().type == TokenType.AN:
                self.advance()
            self.skip_expression()
        elif token.type == TokenType.NOT:
            self.advance()
            self.skip_expression()
        else:
            self.advance()
    
    def parse_type_cast(self):
        var_name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.IS_NOW_A)
        type_name = self.current_token().value
        self.advance()
        
        value = self.variables[var_name]
        casted_value = self.cast_value(value, type_name)
        
        self.variables[var_name] = casted_value
        self.update_symbol_callback(var_name, casted_value)
    
    def parse_expression(self):
        token = self.current_token()
        
        if not token:
            raise SyntaxError("Unexpected end of input")
        
        # Literals
        if token.type == TokenType.NUMBR_LITERAL:
            self.advance()
            return int(token.value)
        
        if token.type == TokenType.NUMBAR_LITERAL:
            self.advance()
            return float(token.value)
        
        if token.type == TokenType.YARN_LITERAL:
            self.advance()
            return token.value[1:-1]  # Remove quotes
        
        if token.type == TokenType.TROOF_LITERAL:
            self.advance()
            return token.value == "WIN"
        
        if token.type == TokenType.NOOB:
            self.advance()
            return None
        
        # Variable reference
        if token.type == TokenType.IDENTIFIER:
            var_name = token.value
            if var_name not in self.variables:
                raise NameError(f"Semantic Error: Variable '{var_name}' not declared")
            self.advance()
            return self.variables[var_name]
        
        # Arithmetic operations
        if token.type == TokenType.SUM_OF:
            return self.parse_binary_op(lambda a, b: self.to_number(a) + self.to_number(b))
        
        if token.type == TokenType.DIFF_OF:
            return self.parse_binary_op(lambda a, b: self.to_number(a) - self.to_number(b))
        
        if token.type == TokenType.PRODUKT_OF:
            return self.parse_binary_op(lambda a, b: self.to_number(a) * self.to_number(b))
        
        if token.type == TokenType.QUOSHUNT_OF:
            return self.parse_binary_op(lambda a, b: int(self.to_number(a) / self.to_number(b)) if self.to_number(b) != 0 else 0)
        
        if token.type == TokenType.MOD_OF:
            return self.parse_binary_op(lambda a, b: self.to_number(a) % self.to_number(b) if self.to_number(b) != 0 else 0)
        
        if token.type == TokenType.BIGGR_OF:
            return self.parse_binary_op(lambda a, b: max(self.to_number(a), self.to_number(b)))
        
        if token.type == TokenType.SMALLR_OF:
            return self.parse_binary_op(lambda a, b: min(self.to_number(a), self.to_number(b)))
        
        # Boolean operations
        if token.type == TokenType.BOTH_OF:
            return self.parse_binary_op(lambda a, b: self.is_truthy(a) and self.is_truthy(b))
        
        if token.type == TokenType.EITHER_OF:
            return self.parse_binary_op(lambda a, b: self.is_truthy(a) or self.is_truthy(b))
        
        if token.type == TokenType.WON_OF:
            return self.parse_binary_op(lambda a, b: self.is_truthy(a) != self.is_truthy(b))
        
        if token.type == TokenType.NOT:
            self.advance()
            value = self.parse_expression()
            return not self.is_truthy(value)
        
        # Comparison
        if token.type == TokenType.BOTH_SAEM:
            return self.parse_binary_op(lambda a, b: a == b)
        
        if token.type == TokenType.DIFFRINT:
            return self.parse_binary_op(lambda a, b: a != b)
        
        # String concatenation
        if token.type == TokenType.SMOOSH:
            self.advance()
            result = ''
            
            while self.current_token() and self.current_token().type not in [TokenType.MKAY, 
                                                                             TokenType.I_HAS_A,
                                                                             TokenType.VISIBLE]:
                value = self.parse_expression()
                result += self.stringify(value)
                
                if self.current_token() and self.current_token().type == TokenType.AN:
                    self.advance()
                else:
                    break
            
            if self.current_token() and self.current_token().type == TokenType.MKAY:
                self.advance()
            
            return result
        
        # Function call as expression
        if token.type == TokenType.I_IZ:
            return self.parse_function_call()
        
        raise SyntaxError(f"Syntax Error at line {token.line}: Unexpected token {token.type.value}")
    
    def parse_binary_op(self, operation):
        self.advance()
        left = self.parse_expression()
        self.expect(TokenType.AN)
        right = self.parse_expression()
        return operation(left, right)
    
    def to_number(self, value):
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            try:
                if '.' in value:
                    return float(value)
                return int(value)
            except ValueError:
                return 0
        if isinstance(value, bool):
            return 1 if value else 0
        if value is None:
            return 0
        return 0
    
    def is_truthy(self, value):
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return value != ''
        return True
    
    def stringify(self, value):
        if value is None:
            return ''
        if isinstance(value, bool):
            return 'WIN' if value else 'FAIL'
        return str(value)
    
    def cast_value(self, value, type_name):
        type_upper = type_name.upper()
        if type_upper == 'NUMBR':
            return int(self.to_number(value))
        elif type_upper == 'NUMBAR':
            return self.to_number(value)
        elif type_upper == 'YARN':
            return self.stringify(value)
        elif type_upper == 'TROOF':
            return self.is_truthy(value)
        return value