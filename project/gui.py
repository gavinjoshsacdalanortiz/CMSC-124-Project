import tkinter as tk # import tkinter library
from tkinter import ttk, filedialog, scrolledtext, messagebox, simpledialog # import tkinter components
from lexer import Lexer # import Lexer class
from parser import Parser # import Parser class

# GUI class for LOL CODE interpreter
class LOLCodeInterpreterGUI:
    # Initialize GUI components
    def __init__(self, root):
        self.root = root
        self.root.title("LOL CODE Interpreter") # set window title
        self.root.geometry("1200x700") # set window size
        
        # Create main container
        main_container = tk.Frame(root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Top menu bar
        menu_frame = tk.Frame(main_container, bg='#2c3e50', height=40)
        menu_frame.pack(fill=tk.X)
        
        open_btn = tk.Button(menu_frame, text="Open File", command=self.open_file, 
                            bg='#3498db', fg='white', padx=15, pady=5)
        open_btn.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.file_label = tk.Label(menu_frame, text="No file loaded", 
                                   bg='#2c3e50', fg='white', font=('Arial', 10))
        self.file_label.pack(side=tk.LEFT, padx=10)
        
        # Create three-column layout
        content_frame = tk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Text Editor
        left_frame = tk.Frame(content_frame, width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        editor_label = tk.Label(left_frame, text="Text Editor", bg='#ecf0f1', 
                               font=('Arial', 10, 'bold'), pady=5)
        editor_label.pack(fill=tk.X)
        
        self.text_editor = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, 
                                                     font=('Courier', 10))
        self.text_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Middle column - Tokens and Symbol Table
        middle_frame = tk.Frame(content_frame, width=400)
        middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Tokens table (top half)
        tokens_label = tk.Label(middle_frame, text="Lexemes", bg='#ecf0f1', 
                               font=('Arial', 10, 'bold'), pady=5)
        tokens_label.pack(fill=tk.X)
        
        tokens_frame = tk.Frame(middle_frame)
        tokens_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tokens_tree = ttk.Treeview(tokens_frame, columns=('Lexeme', 'Classification'), 
                                       show='headings', height=10)
        self.tokens_tree.heading('Lexeme', text='Lexeme')
        self.tokens_tree.heading('Classification', text='Classification')
        self.tokens_tree.column('Lexeme', width=150)
        self.tokens_tree.column('Classification', width=150)
        
        tokens_scroll = ttk.Scrollbar(tokens_frame, orient=tk.VERTICAL, 
                                     command=self.tokens_tree.yview)
        self.tokens_tree.configure(yscrollcommand=tokens_scroll.set)
        
        self.tokens_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        tokens_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Symbol table (bottom half)
        symbol_label = tk.Label(middle_frame, text="SYMBOL TABLE", bg='#ecf0f1', 
                               font=('Arial', 10, 'bold'), pady=5)
        symbol_label.pack(fill=tk.X)
        
        symbol_frame = tk.Frame(middle_frame)
        symbol_frame.pack(fill=tk.BOTH, expand=True)
        
        self.symbol_tree = ttk.Treeview(symbol_frame, columns=('Identifier', 'Value'), 
                                       show='headings', height=10)
        self.symbol_tree.heading('Identifier', text='Identifier')
        self.symbol_tree.heading('Value', text='Value')
        self.symbol_tree.column('Identifier', width=150)
        self.symbol_tree.column('Value', width=150)
        
        symbol_scroll = ttk.Scrollbar(symbol_frame, orient=tk.VERTICAL, 
                                     command=self.symbol_tree.yview)
        self.symbol_tree.configure(yscrollcommand=symbol_scroll.set)
        
        self.symbol_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        symbol_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Right column - Execute button and Console
        right_frame = tk.Frame(content_frame, width=400)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        execute_btn = tk.Button(right_frame, text="EXECUTE", command=self.execute_code,
                               bg='#27ae60', fg='white', font=('Arial', 12, 'bold'),
                               pady=10)
        execute_btn.pack(fill=tk.X, padx=5, pady=5)
        
        console_label = tk.Label(right_frame, text="Console", bg='#ecf0f1', 
                                font=('Arial', 10, 'bold'), pady=5)
        console_label.pack(fill=tk.X)
        
        self.console = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, 
                                                bg='black', fg='#00ff00',
                                                font=('Courier', 10))
        self.console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.symbol_table_data = {}
    
    # Open file dialog to load LOLCODE file
    def open_file(self):
        filename = filedialog.askopenfilename(
            title="Select LOLCODE file",
            filetypes=[("LOLCODE files", "*.lol"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as file:
                    code = file.read()
                    self.text_editor.delete(1.0, tk.END)
                    self.text_editor.insert(1.0, code)
                    self.file_label.config(text=filename.split('/')[-1])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
    
    # Update symbol table display
    def update_symbol_table(self, name, value):
        self.symbol_table_data[name] = value
        
        # Update the treeview
        for item in self.symbol_tree.get_children():
            self.symbol_tree.delete(item)
        
        for var_name, var_value in self.symbol_table_data.items():
            display_value = self.format_value(var_value)
            self.symbol_tree.insert('', tk.END, values=(var_name, display_value))
    
    # Format value for display in symbol table
    def format_value(self, value):
        if value is None:
            return 'NOOB'
        elif isinstance(value, bool):
            return 'WIN' if value else 'FAIL'
        else:
            return str(value)
    
    # Write output to console
    def write_to_console(self, text):
        self.console.insert(tk.END, text)
        self.console.see(tk.END)
        self.root.update()
    
    # Read input from user via dialog
    def read_input(self, prompt):
        result = simpledialog.askstring("Input", prompt)
        return result if result else ''
    
    # Execute the code from text editor
    def execute_code(self):
        # Clear previous results
        self.console.delete(1.0, tk.END)
        for item in self.tokens_tree.get_children():
            self.tokens_tree.delete(item)
        for item in self.symbol_tree.get_children():
            self.symbol_tree.delete(item)
        self.symbol_table_data = {}
        
        code = self.text_editor.get(1.0, tk.END)
        
        try:
            # Lexical analysis
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            
            # Display tokens
            for token in tokens:
                self.tokens_tree.insert('', tk.END, 
                                       values=(token.value, token.type.value))
            
            # Syntax analysis and execution
            parser = Parser(tokens, self.update_symbol_table, 
                          self.write_to_console, self.read_input)
            parser.parse()
            
            self.write_to_console("\n--- Execution completed successfully ---\n")
            
        except (SyntaxError, NameError, ValueError, Exception) as e:
            error_msg = f"Error: {str(e)}\n"
            self.write_to_console(error_msg)
            messagebox.showerror("Execution Error", str(e))