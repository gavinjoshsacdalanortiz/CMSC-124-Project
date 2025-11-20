import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox, simpledialog
from PIL import Image, ImageTk
from lexer import Lexer
from parser import Parser

# logo from: https://lolcode-redesign.webflow.io

class LOLCodeInterpreterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LOL CODE Interpreter sheesh")
        self.root.geometry("1400x800")
        
        # color palette
        self.colors = {
            # bg colors
            'bg_darkest': '#1A0A3B',     # deepest purple
            'bg_dark': '#2D1B4E',        # deep purple 
            'bg_medium': '#3D2963',      # medium purple 
            'bg_light': '#4A3072',       # light purple
            
            # accent colors
            'accent_primary': '#ED455D', # coral red
            'accent_hover': '#56DCE7',   # light cyan
            'border': '#56DCE7',         # light cyan
            
            # text colors
            'text_primary': '#56DCE7',   # light cyan
            'text_secondary': '#ED455D', # coral red
            'text_button': '#56DCE7',    # light cyan
            
            # UI colors
            'selection': '#264F78',      # selection blue
            'scrollbar': '#ED455D',      # coral red
            'scrollbar_hover': '#FF69B4' # hot pink
        } 
        
        self.root.configure(bg=self.colors['bg_darkest'])
        self.setup_styles()
        
        # main container
        main_container = tk.Frame(root, bg=self.colors['bg_darkest'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # header
        self.create_header(main_container)
        
        # content area
        content_frame = tk.Frame(main_container, bg=self.colors['bg_dark'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # top section (Editor, Lexemes, Symbol Table)
        top_section = tk.Frame(content_frame, bg=self.colors['bg_dark'])
        top_section.pack(fill=tk.BOTH, expand=True)
        
        self.create_editor_section(top_section)
        self.create_lexemes_section(top_section)
        self.create_symbol_table_section(top_section)
        
        # bottom section (Execute & Console)
        bottom_section = tk.Frame(content_frame, bg=self.colors['bg_dark'])
        bottom_section.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.create_execute_section(bottom_section)
        self.create_console_section(bottom_section)
        
        self.symbol_table_data = {}
        self.root.iconphoto(False, ImageTk.PhotoImage(Image.open('logo.png')))
    
    # Set up custom styles for ttk widgets
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # scrollbar style
        style.configure('Vertical.TScrollbar',
                       background=self.colors['scrollbar'],
                       troughcolor=self.colors['bg_dark'],
                       borderwidth=0,
                       arrowcolor=self.colors['text_primary'],
                       relief='flat')
        style.map('Vertical.TScrollbar',
                 background=[('active', self.colors['scrollbar_hover']),
                           ('pressed', self.colors['border'])])
        
        # treeview style
        style.configure('Modern.Treeview',
                       background=self.colors['bg_dark'],
                       foreground=self.colors['text_primary'],
                       fieldbackground=self.colors['bg_dark'],
                       borderwidth=0,
                       rowheight=25,
                       font=('Consolas', 10),
                       highlightthickness=0)
        style.configure('Modern.Treeview.Heading',
                       background=self.colors['bg_medium'],
                       foreground=self.colors['text_secondary'],
                       borderwidth=0,
                       relief='flat',
                       font=('Segoe UI', 10, 'bold'))
        style.map('Modern.Treeview',
                 background=[('selected', self.colors['selection'])],
                 foreground=[('selected', self.colors['text_primary'])])
        style.map('Modern.Treeview.Heading',
                 background=[('active', self.colors['border'])])
    
    # Load logo image
    def load_logo(self, logo_path, size=(40, 40)):
        # load and resize logo image
        try:
            image = Image.open(logo_path)
            image = image.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Could not load logo: {e}")
            return None
    
    # create header section
    def create_header(self, parent):
        header = tk.Frame(parent, bg=self.colors['bg_light'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # left side (logo and title)
        left_frame = tk.Frame(header, bg=self.colors['bg_light'])
        left_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        # try to load logo
        try:
            self.logo_image = self.load_logo('logo.png', size=(40, 40))
            if self.logo_image:
                logo_label = tk.Label(left_frame, image=self.logo_image, 
                                     bg=self.colors['bg_light'])
                logo_label.pack(side=tk.LEFT, padx=(0, 12))
        except:
            pass  # continue without logo if fail
        
        title = tk.Label(left_frame, text="LOLCODE", 
                        bg=self.colors['bg_light'], fg=self.colors['accent_primary'],
                        font=('Consolas', 18, 'bold'))
        title.pack(side=tk.LEFT)
        
        subtitle = tk.Label(left_frame, text=" Interpreter", 
                           bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                           font=('Segoe UI', 18))
        subtitle.pack(side=tk.LEFT)
        
        # right side (file controls)
        controls_frame = tk.Frame(header, bg=self.colors['bg_light'])
        controls_frame.pack(side=tk.RIGHT, padx=20, pady=12)
        
        self.file_label = tk.Label(controls_frame, text="No file loaded",
                                   bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                                   font=('Segoe UI', 9))
        self.file_label.pack(side=tk.RIGHT, padx=(15, 0))
        
        open_btn = tk.Button(controls_frame, text="Open File", command=self.open_file,
                           bg=self.colors['accent_primary'], fg=self.colors['text_button'],
                           font=('Segoe UI', 10, 'bold'), bd=0,
                           padx=18, pady=6, cursor='hand2',
                           activebackground=self.colors['text_button'],
                           activeforeground=self.colors['accent_primary'])
        open_btn.pack(side=tk.RIGHT)
    
    # creates panel with title and content area
    def create_panel(self, parent, title):
        panel = tk.Frame(parent, bg=self.colors['border'], bd=0)
        panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # title bar
        title_bar = tk.Frame(panel, bg=self.colors['bg_medium'], height=35)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)
        
        title_label = tk.Label(title_bar, text=title,
                              bg=self.colors['bg_medium'], fg=self.colors['text_primary'],
                              font=('Segoe UI', 10))
        title_label.pack(side=tk.LEFT, padx=12, pady=8)
        
        # content area
        content = tk.Frame(panel, bg=self.colors['bg_darkest'])
        content.pack(fill=tk.BOTH, expand=True)
        
        return content
    
    # creates custom styled scrollbar
    def create_custom_scrollbar(self, parent, orient=tk.VERTICAL):
        scrollbar = ttk.Scrollbar(parent, orient=orient, style='Vertical.TScrollbar')
        return scrollbar
    
    # creates editor section
    def create_editor_section(self, parent):
        content = self.create_panel(parent, "Editor")
        
        # create frame for text widget + scrollbar
        text_frame = tk.Frame(content, bg=self.colors['bg_darkest'])
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # custom scrollbar
        scrollbar = self.create_custom_scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_editor = tk.Text(text_frame, wrap=tk.WORD,
                                   font=('Consolas', 11),
                                   bg=self.colors['bg_darkest'],
                                   fg=self.colors['text_primary'],
                                   insertbackground=self.colors['text_secondary'],
                                   selectbackground=self.colors['selection'],
                                   selectforeground=self.colors['text_primary'],
                                   highlightthickness=0,
                                   bd=0, padx=12, pady=12,
                                   yscrollcommand=scrollbar.set)
        self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_editor.yview)
    
    # creates lexemes section
    def create_lexemes_section(self, parent):
        content = self.create_panel(parent, "Lexemes")
        
        tree_frame = tk.Frame(content, bg=self.colors['bg_darkest'])
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = self.create_custom_scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tokens_tree = ttk.Treeview(tree_frame, columns=('Lexeme', 'Classification'),
                                       show='headings', style='Modern.Treeview',
                                       yscrollcommand=scrollbar.set)
        self.tokens_tree.heading('Lexeme', text='Lexeme')
        self.tokens_tree.heading('Classification', text='Classification')
        self.tokens_tree.column('Lexeme', width=120, anchor='w')
        self.tokens_tree.column('Classification', width=120, anchor='w')
        
        scrollbar.config(command=self.tokens_tree.yview)
        
        self.tokens_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # creates symbol table section
    def create_symbol_table_section(self, parent):
        content = self.create_panel(parent, "Symbol Table")
        
        tree_frame = tk.Frame(content, bg=self.colors['bg_darkest'])
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = self.create_custom_scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.symbol_tree = ttk.Treeview(tree_frame, columns=('Identifier', 'Value'),
                                       show='headings', style='Modern.Treeview',
                                       yscrollcommand=scrollbar.set)
        self.symbol_tree.heading('Identifier', text='Identifier')
        self.symbol_tree.heading('Value', text='Value')
        self.symbol_tree.column('Identifier', width=120, anchor='w')
        self.symbol_tree.column('Value', width=120, anchor='w')
        
        scrollbar.config(command=self.symbol_tree.yview)
        
        self.symbol_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # creates execute button section
    def create_execute_section(self, parent):
        execute_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        execute_frame.pack(fill=tk.X, pady=(0, 10))
        
        execute_btn = tk.Button(execute_frame, text="▶ Execute",
                               command=self.execute_code,
                               bg=self.colors['accent_primary'], fg=self.colors['text_button'],
                               font=('Segoe UI', 11, 'bold'), bd=0,
                               padx=25, pady=10, cursor='hand2',
                               activebackground=self.colors['text_button'],
                               activeforeground=self.colors['accent_primary'])
        execute_btn.pack(fill=tk.X, padx=5)
    
    # creates console section
    def create_console_section(self, parent):
        console_panel = tk.Frame(parent, bg=self.colors['border'], bd=0)
        console_panel.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # console header
        console_header = tk.Frame(console_panel, bg=self.colors['bg_medium'], height=35)
        console_header.pack(fill=tk.X)
        console_header.pack_propagate(False)
        
        console_label = tk.Label(console_header, text="Console",
                                bg=self.colors['bg_medium'], fg=self.colors['text_primary'],
                                font=('Segoe UI', 10))
        console_label.pack(side=tk.LEFT, padx=12, pady=8)
        
        # console content
        console_content = tk.Frame(console_panel, bg=self.colors['bg_darkest'])
        console_content.pack(fill=tk.BOTH, expand=True)
        
        # create frame for console + scrollbar
        text_frame = tk.Frame(console_content, bg=self.colors['bg_darkest'])
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = self.create_custom_scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.console = tk.Text(text_frame, wrap=tk.WORD,
                              bg=self.colors['bg_darkest'],
                              fg=self.colors['text_primary'],
                              font=('Consolas', 10),
                              insertbackground=self.colors['text_secondary'],
                              selectbackground=self.colors['selection'],
                              bd=0, padx=12, pady=12,
                              highlightthickness=0,
                              yscrollcommand=scrollbar.set)
        self.console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.console.yview)
    
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
    
    # executes the code from the text editor
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
                        
        except (SyntaxError, NameError, ValueError, Exception) as e:
            error_msg = f"✗ Error: {str(e)}\n"
            self.write_to_console(error_msg)
            messagebox.showerror("Execution Error", str(e))