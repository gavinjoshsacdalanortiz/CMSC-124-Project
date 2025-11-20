from token_types import TokenType  # Import TokenType Enum 
from LOL_exceptions import BreakException, ReturnException  # Import custom exceptions for control flow

# Parser class for parsing LOLCODE tokens + executing program
class Parser:
    # Initialize parser with tokens and callbacks for symbol table updates and console I/O
    def __init__(self, tokens, update_symbol_callback, write_console_callback, read_input_callback):
        self.tokens = tokens
        self.position = 0
        self.variables = {"IT": None}
        self.IT = None
        self.update_symbol_callback = update_symbol_callback
        self.write_console_callback = write_console_callback
        self.read_input_callback = read_input_callback
        self.functions = {}

    # get current token from token list
    def current_token(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    # peek ahead in token list without advancing position
    def peek(self, offset=1):
        if self.position + offset < len(self.tokens):
            return self.tokens[self.position + offset]
        return None

    # advance to next token
    def advance(self):
        self.position += 1

    # expect a specific token type, raise error if not found
    def expect(self, token_type):
        token = self.current_token()
        if not token or token.type != token_type:
            raise SyntaxError(f"Syntax Error at line {token.line if token else 'EOF'}: Expected {token_type.value}, got {token.type.value if token else 'EOF'}")
        self.advance()
        return token

    # main parse function to process tokens
    def parse(self):
        self.expect(TokenType.HAI)  # start of program

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

    # parse variable declaration statement
    def parse_variable_declaration(self):
        self.expect(TokenType.I_HAS_A)
        var_name = self.expect(TokenType.IDENTIFIER).value

        value = None  # NOOB by default

        if self.current_token() and self.current_token().type == TokenType.ITZ:
            self.advance()
            value = self.parse_expression()

        self.variables[var_name] = value
        self.update_symbol_callback(var_name, value)

    # parse a general statement
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
            if getattr(self, "_in_loop", False):
                raise BreakException()
            else:
                raise ReturnException(None)
        elif token.type == TokenType.FOUND_YR:
            self.advance()
            value = self.parse_expression()
            raise ReturnException(value)
        elif token.type == TokenType.I_IZ:
            result = self.parse_function_call()
            self.IT = result
            self.update_symbol_callback('IT', self.IT)
        elif token.type == TokenType.IDENTIFIER:
            if self.peek() and self.peek().type == TokenType.R:
                self.parse_assignment()
            elif self.peek() and self.peek().type == TokenType.IS_NOW_A:
                self.parse_type_cast()
            else:
                self.IT = self.parse_expression()
                self.update_symbol_callback('IT', self.IT)
        else:
            self.IT = self.parse_expression()
            self.update_symbol_callback('IT', self.IT)

    # parse assignment statement
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

    # parse VISIBLE statement
    def parse_visible(self):
        self.advance()
        output_parts = []
        
        while self.current_token():
            token = self.current_token()
            
            # Break on statement-ending tokens - CHECK THIS FIRST
            if token.type in [TokenType.GIMMEH, TokenType.KTHXBYE,
                            TokenType.YA_RLY, TokenType.NO_WAI,
                            TokenType.OIC, TokenType.O_RLY,
                            TokenType.IM_OUTTA_YR, TokenType.OMG,
                            TokenType.OMGWTF, TokenType.GTFO,
                            TokenType.VISIBLE, TokenType.BTW,
                            TokenType.IM_IN_YR]:
                break
                
            # Break on assignment statement
            if token.type == TokenType.IDENTIFIER and self.peek() and self.peek().type == TokenType.R:
                break
            
            # Skip AN separator (explicit concatenation)
            if token.type == TokenType.AN:
                self.advance()
                continue
                
            # Skip PLUS if used as separator
            if token.type == TokenType.PLUS:
                self.advance()
                continue
            
            # Parse and add the expression value
            value = self.parse_expression()
            output_parts.append(self.stringify(value))
        
        # Join all parts and write to console
        output = ''.join(output_parts)
        self.write_console_callback(output + '\n')

    # parse GIMMEH statement
    def parse_gimmeh(self):
        self.advance()
        var_name = self.expect(TokenType.IDENTIFIER).value
        if var_name not in self.variables:
            raise NameError(f"Semantic Error: Variable '{var_name}' not declared")
        input_value = self.read_input_callback(f"Enter value for {var_name}:")
        self.variables[var_name] = input_value
        self.update_symbol_callback(var_name, input_value)

    # parse IF-THEN-ELSE statement
    def parse_if_then_else(self):
        self.advance()  # consume O RLY?
        
        condition = self.IT # use IT as condition
        
        # expect YA RLY
        self.expect(TokenType.YA_RLY)
        
        # evaluate condition and execute appropriate block
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
    
    # parse SWITCH statement
    def parse_switch(self):
        self.advance()  # consume WTF?
        
        switch_value = self.IT
        found_match = False # flag for found matching case
        in_omgwtf = False # flag for default case
        
        # process cases until OIC
        while self.current_token() and self.current_token().type != TokenType.OIC:
            # handle OMG case
            if self.current_token().type == TokenType.OMG:
                self.advance()
                case_value = self.parse_expression()
                
                # check for match if not already matched or in default
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
            
            # handle OMGWTF default case
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
        
        # expect OIC to end switch
        if self.current_token() and self.current_token().type == TokenType.OIC:
            self.expect(TokenType.OIC)
    
    # parse loop statement
    def parse_loop(self):
        self._in_loop = True
        try:
            self.advance()  # consume IM IN YR
            loop_name = self.expect(TokenType.IDENTIFIER).value
        finally:
            self._in_loop = False
        
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
            # Skip the condition for now, evaluate it in the loop
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
    
    # parse function definition
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
    
    # parse function call
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
            args.append(self.parse_expression())
            if self.current_token() and self.current_token().type == TokenType.AN:
                self.advance()

        if self.current_token() and self.current_token().type == TokenType.MKAY:
            self.advance()

        if len(args) != len(func_info['params']):
            raise ValueError(f"Function '{func_name}' expects {len(func_info['params'])} arguments, got {len(args)}")

    # Save global state
        saved_position = self.position
        saved_variables = self.variables.copy()
        saved_IT = self.IT

    # Prepare local function scope - ONLY parameters, no globals
        local_scope = {param: arg for param, arg in zip(func_info['params'], args)}
        local_scope['IT'] = None 

        # Execute function with isolated scope
        self.position = func_info['body_start']
        return_value = None

        try:
            while self.position < func_info['body_end']:
                token = self.current_token()
                if not token:
                    break
                
                # Use ONLY local scope during function execution
                self.variables = local_scope.copy() 
                self.parse_statement()
                
                # Update local_scope with any changes from the statement
                local_scope = self.variables.copy()
                
        except ReturnException as e:
            return_value = e.value

        # Restore original state
        self.position = saved_position
        self.variables = saved_variables
        self.IT = return_value
        self.update_symbol_callback('IT', self.IT)

        return return_value

    
    # skip expression for constructs like loop conditions
    def skip_expression(self):
        token = self.current_token()
        if not token:
            return
        
        # skip literals and identifiers
        if token.type in [TokenType.NUMBR_LITERAL, TokenType.NUMBAR_LITERAL, 
                         TokenType.YARN_LITERAL, TokenType.TROOF_LITERAL,
                         TokenType.NOOB, TokenType.IDENTIFIER]:
            self.advance()
        elif token.type in [TokenType.SUM_OF, TokenType.DIFF_OF, TokenType.PRODUKT_OF,
                           TokenType.QUOSHUNT_OF, TokenType.MOD_OF, TokenType.BIGGR_OF,
                           TokenType.SMALLR_OF, TokenType.BOTH_OF, TokenType.EITHER_OF,
                           TokenType.WON_OF, TokenType.BOTH_SAEM, TokenType.DIFFRINT, TokenType.ALL_OF]:
            self.advance()
            self.skip_expression()
            # consume chained AN expressions
            while self.current_token() and self.current_token().type == TokenType.AN:
                self.advance()
                self.skip_expression()
            # optional MKAY
            if self.current_token() and self.current_token().type == TokenType.MKAY:
                self.advance()
        elif token.type == TokenType.NOT:
            self.advance()
            self.skip_expression()
        else:
            self.advance()
    
    # parse type cast statement
    def parse_type_cast(self):
        # expect identifier
        var_name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.IS_NOW_A)
        type_name = self.current_token().value # get target type
        self.advance()
        
        # check if variable is declared
        value = self.variables[var_name]
        casted_value = self.cast_value(value, type_name)
        
        # assign casted value and update symbol table
        self.variables[var_name] = casted_value
        self.update_symbol_callback(var_name, casted_value)
    
    # parse expression and return its value
    def parse_expression(self):
        token = self.current_token()
        
        # check for end of tokens
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
        
        # Boolean literals
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
        
        # Arithmetic and comparison operations (variadic where applicable)
        if token.type in [TokenType.SUM_OF, TokenType.DIFF_OF, TokenType.PRODUKT_OF,
                          TokenType.QUOSHUNT_OF, TokenType.MOD_OF, TokenType.BIGGR_OF,
                          TokenType.SMALLR_OF]:
            return self.parse_variadic_numeric_op(token.type)
        
        # Boolean operations
        if token.type == TokenType.ALL_OF:
            return self.parse_all_of()
        
        if token.type == TokenType.ANY_OF:
            return self.parse_variadic_boolean_op(token.type)

        if token.type == TokenType.BOTH_OF:
            return self.parse_variadic_boolean_op(token.type)
        
        if token.type == TokenType.EITHER_OF:
            return self.parse_variadic_boolean_op(token.type)
        
        if token.type == TokenType.WON_OF:
            return self.parse_variadic_boolean_op(token.type)
        
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
    
    # parse binary operation (two-arg)
    def parse_binary_op(self, operation):
        self.advance()
        left = self.parse_expression()
        # accept AN separator
        self.expect(TokenType.AN)
        right = self.parse_expression()
        # optional MKAY
        if self.current_token() and self.current_token().type == TokenType.MKAY:
            self.advance()
        return operation(left, right)
    
    # parse variadic numeric operations like SUM OF, PRODUKT OF, etc.
    def parse_variadic_numeric_op(self, op_type):
        # consume operator token
        self.advance()
        # first operand
        first = self.parse_expression()
        args = [first]
        # collect additional operands separated by AN
        while self.current_token() and self.current_token().type == TokenType.AN:
            self.advance()
            args.append(self.parse_expression())
        # optional MKAY (consume if present)
        if self.current_token() and self.current_token().type == TokenType.MKAY:
            self.advance()
        # reduce based on op_type
        if op_type == TokenType.SUM_OF:
            result = 0
            for a in args:
                result = self.to_number(result) + self.to_number(a)
            return result
        if op_type == TokenType.DIFF_OF:
            # left-associative: (((a - b) - c) - ...)
            result = self.to_number(args[0])
            for a in args[1:]:
                result = result - self.to_number(a)
            return result
        if op_type == TokenType.PRODUKT_OF:
            result = 1
            for a in args:
                result = self.to_number(result) * self.to_number(a)
            return result
        if op_type == TokenType.QUOSHUNT_OF:
            result = self.to_number(args[0])
            for a in args[1:]:
                denom = self.to_number(a)
                if denom == 0:
                    result = 0
                else:
                    # integer division
                    result = int(result / denom)
            return result
        if op_type == TokenType.MOD_OF:
            result = self.to_number(args[0])
            for a in args[1:]:
                denom = self.to_number(a)
                if denom == 0:
                    result = 0
                else:
                    result = result % denom
            return result
        if op_type == TokenType.BIGGR_OF:
            result = self.to_number(args[0])
            for a in args[1:]:
                result = max(result, self.to_number(a))
            return result
        if op_type == TokenType.SMALLR_OF:
            result = self.to_number(args[0])
            for a in args[1:]:
                result = min(result, self.to_number(a))
            return result
        return None
    
    # parse variadic boolean ops (ANY_OF, BOTH_OF, EITHER_OF, WON_OF)
    def parse_variadic_boolean_op(self, op_type):
        self.advance()
        first = self.parse_expression()
        args = [first]
        while self.current_token() and self.current_token().type == TokenType.AN:
            self.advance()
            args.append(self.parse_expression())
        # optional MKAY
        if self.current_token() and self.current_token().type == TokenType.MKAY:
            self.advance()
        # evaluate
        if op_type == TokenType.BOTH_OF:
            # logical AND across all
            for a in args:
                if not self.is_truthy(a):
                    return False
            return True
        if op_type == TokenType.ANY_OF or op_type == TokenType.EITHER_OF:
            for a in args:
                if self.is_truthy(a):
                    return True
            return False
        if op_type == TokenType.WON_OF:
            # XOR across arguments: True if an odd number of truthy args
            count = 0
            for a in args:
                if self.is_truthy(a):
                    count += 1
            return (count % 2) == 1
        return False
    
    # parse ALL OF (special variadic that defaults to True and short-circuits)
    def parse_all_of(self):
        self.advance()
        result = True
        while True:
            value = self.parse_expression()
            if not self.is_truthy(value):
                result = False
            # Continue if AN separator is detected
            if self.current_token() and self.current_token().type == TokenType.AN:
                self.advance()
                continue
            break
        # optional MKAY
        if self.current_token() and self.current_token().type == TokenType.MKAY:
            self.advance()
        return result
    
    # utility function to convert value to number
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
    
    # utility function to determine truthiness of a value
    def is_truthy(self, value):
        if value is None: # NOOB is false
            return False
        # if value is boolean, number, or string
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return value != ''
        return True 
    
    # utility function to convert value to string
    def stringify(self, value):
        if value is None: # NOOB
            return ''
        # check for boolean, if so convert to WIN/FAIL
        if isinstance(value, bool):
            return 'WIN' if value else 'FAIL'
        return str(value) # convert other types to string
    
    # utility function to cast value to specified type
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
