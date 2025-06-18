import json
import os
import tkinter as tk
from tkinter.colorchooser import askcolor
from tkinter import ttk, simpledialog, messagebox, filedialog, PhotoImage
from tkinter import font as tkfont
from tkinter.filedialog import asksaveasfile, askopenfilename

from PIL import ImageTk, Image

# Packages for AI features
from ideageneration import generate_ideas
from textfromimage import extract_text
from cliforshortinfo import fetch_and_summarize
import voiceassistant

#packages for voice assistant
import speech_recognition as sr
import pyttsx3
import datetime
import threading

#document to flowchart code
import tkinter as tk
from tkinter import filedialog
import re
import docx
import PyPDF2
from graphviz import Digraph

def parse_text(text):
    # Split text into sections based on empty lines
    sections = text.strip().split('\n\n')

    # Initialize the classification dictionary
    classification = {}

    # Process each section to extract title and content
    for section in sections:
        lines = section.strip().split('\n')
        if lines:
            title = lines[0].strip()
            content = [line.strip() for line in lines[1:]]
            classification[title] = content

    return classification

def read_text_from_plain_file(file_path):
    with open(file_path, 'r') as file:
        text = file.read()
    return text

def read_text_from_docx(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def read_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

def create_structure(classification):
    structure = {"Start": classification}
    return structure

def sanitize_label(label):
    # Replace special characters with safe characters for Graphviz
    return re.sub(r'[^\w\s]', '_', label)

def add_edges(dot, node, structure):
    for key, value in structure.items():
        sanitized_key = sanitize_label(key)
        dot.node(sanitized_key, label=key, shape='box', style='filled', fillcolor='lightblue', fontname='Arial', fontsize='12')
        dot.edge(node, sanitized_key)

        if isinstance(value, list):
            for item in value:
                subkey, *subcontent = item.split(':', 1)
                subkey = subkey.strip()
                sanitized_subkey = sanitize_label(subkey)
                dot.node(sanitized_subkey, label=subkey, shape='ellipse', style='filled', fillcolor='lightgreen', fontname='Arial', fontsize='10')
                dot.edge(sanitized_key, sanitized_subkey)

                if subcontent:
                    content_node = f"{sanitized_subkey}_content"
                    content_text = subcontent[0].strip()
                    dot.node(content_node, label=content_text, shape='note', style='filled', fillcolor='lightyellow', fontname='Arial', fontsize='10')
                    dot.edge(sanitized_subkey, content_node)
        elif isinstance(value, dict):
            add_edges(dot, sanitized_key, value)
#end of document to flowchart code

class ColorPalette(tk.Frame):
    def __init__(self, parent, whiteboard, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.whiteboard = whiteboard
        self.create_palette()

    def create_palette(self):
        colors = [
            "#000000", "#808080", "#FF0000", "#800000", "#FFA500", "#808000",
            "#FFFF00", "#00FF00", "#008000", "#00FFFF", "#008080", "#0000FF",
            "#000080", "#800080", "#FF00FF", "#FFC0CB", "#FFA07A", "#FFE4E1"
        ]

        for color in colors:
            btn = tk.Button(self, bg=color, width=2, height=1, command=lambda col=color: self.set_color(col))
            btn.pack(side=tk.LEFT, padx=2, pady=2)

            # Add custom color button
        custom_color_btn = tk.Button(self, text='+', width=2, height=1, command=self.choose_custom_color)
        custom_color_btn.pack(side=tk.LEFT, padx=2, pady=2)

    def set_color(self, color):
        self.whiteboard.color_fg = color

    def choose_custom_color(self):
        color_code = askcolor(title="Choose color")[1]
        if color_code:
            self.set_color(color_code)

class Whiteboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Whiteboard")

        self.color_fg = 'black'
        self.color_bg = 'white'
        self.fill_color = 'white'  # Default fill color
        self.penwidth = 5
        self.eraser_on = False
        self.active_button = None
        self.old_x = None
        self.old_y = None
        self.shape = 'line'
        self.shape_id = None
        self.selected_object = None
        self.objects = []  # List to keep track of objects

        self.undo_stack = []
        self.redo_stack = []

        # Image insertion
        self.image = None
        self.image_id = None
        self.dragging = False
        self.resizing = False
        self.offset_x = 0
        self.offset_y = 0

        self.current_font = "Arial"  # Default font
        self.font_size = 24  # Default font size

        # for voice assistant
        self.actions = []
        self.current_filename = None
        self.voice_assistant_on = False
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.engine = pyttsx3.init()
        self.is_listening = False 
        self.current_y = 20  # Starting vertical position for text

        # Load images and resize them
        self.pen_color_img = ImageTk.PhotoImage(Image.open(r"D:\AI Whiteboard\Icons\pen_color.png").resize((30, 30), Image.LANCZOS))
        self.canvas_color_img = ImageTk.PhotoImage(Image.open(r"D:\AI Whiteboard\Icons\canvas_color.png").resize((30, 30), Image.LANCZOS))
        self.color_fill_img = ImageTk.PhotoImage(Image.open(r"D:\AI Whiteboard\Icons\color_fill.png").resize((30, 30), Image.LANCZOS))
        self.Line_img = ImageTk.PhotoImage(Image.open(r"D:\AI Whiteboard\Icons\Line.png").resize((30, 30), Image.LANCZOS))
        self.rectangle_img = ImageTk.PhotoImage(Image.open(r"D:\AI Whiteboard\Icons\rectangle.png").resize((30, 30), Image.LANCZOS))
        self.oval_img = ImageTk.PhotoImage(Image.open(r"D:\AI Whiteboard\Icons\oval.png").resize((30, 30), Image.LANCZOS))
        self.eraser_img = ImageTk.PhotoImage(Image.open(r"D:\AI Whiteboard\Icons\eraser.png").resize((30, 30), Image.LANCZOS))
        self.text_img = ImageTk.PhotoImage(Image.open(r"D:\AI Whiteboard\Icons\A_text.png").resize((30, 30), Image.LANCZOS))
        self.select_img = ImageTk.PhotoImage(Image.open(r"D:\AI Whiteboard\Icons\selection.png").resize((30, 30), Image.LANCZOS))
        self.insert_image_img = ImageTk.PhotoImage(Image.open(r"D:\AI Whiteboard\Icons\insert_image.png").resize((30, 30), Image.LANCZOS))
        self.undo_img = ImageTk.PhotoImage(Image.open(r"D:\AI Whiteboard\Icons\undo.png").resize((30, 30), Image.LANCZOS))
        self.redo_img = ImageTk.PhotoImage(Image.open(r"D:\AI Whiteboard\Icons\redo.png").resize((30, 30), Image.LANCZOS))
        self.voice_img= ImageTk.PhotoImage(Image.open(r"D:\AI Whiteboard\Icons\voice.png").resize((30, 30), Image.LANCZOS))
        self.clear_img = ImageTk.PhotoImage(Image.open(r"D:\AI Whiteboard\Icons\clear.png").resize((30, 30), Image.LANCZOS))

        self.drawWidgets()

    def drawWidgets(self):
        self.controls = tk.Frame(self.root, padx=5, pady=5)
        self.controls.pack(side=tk.TOP, fill=tk.X)

        tk.Label(self.controls, text='Pen Width:', font=('arial', 10)).grid(row=0, column=0)
        self.slider = ttk.Scale(self.controls, from_=1, to=100, command=self.changeW, orient=tk.HORIZONTAL)
        self.slider.set(self.penwidth)
        self.slider.grid(row=0, column=1, ipadx=30)

        self.color_btn = tk.Button(self.controls, image=self.pen_color_img, text="Pen Color", compound="top",
                                   command=self.change_fg)
        self.color_btn.grid(row=0, column=2, padx=5)

        self.bg_btn = tk.Button(self.controls, image=self.canvas_color_img, text="Canvas Color", compound="top",
                                command=self.change_bg)
        self.bg_btn.grid(row=0, column=3, padx=5)

        self.fill_btn = tk.Button(self.controls, image=self.color_fill_img, text="Fill Color", compound="top",
                                  command=self.change_fill_color)
        self.fill_btn.grid(row=0, column=4, padx=5)

        self.clear_btn = tk.Button(self.controls, image=self.clear_img, text="Clear", compound="top", command=self.clear)
        self.clear_btn.grid(row=0, column=5, padx=5)

        # Font selection dropdown
        self.font_var = tk.StringVar(value=self.current_font)
        self.fonts = list(tkfont.families())
        self.font_menu = tk.OptionMenu(self.controls, self.font_var, *self.fonts)
        self.font_menu.grid(row=0, column=6, padx=5, pady=5)
        self.font_var.trace_add("write", self.update_font)

        # Font size dropdown
        self.size_var = tk.StringVar(value=self.font_size)
        self.size_menu = tk.OptionMenu(self.controls, self.size_var, *list(range(8, 73, 2)))
        self.size_menu.grid(row=0, column=7, padx=5, pady=5)
        self.size_var.trace_add("write", self.update_font_size)

        # Tool buttons
        self.line_btn = tk.Button(self.controls, image=self.Line_img, text="Line", compound="top",
                                  command=lambda: self.select_tool('line'))
        self.line_btn.grid(row=0, column=8, padx=5)

        self.rect_btn = tk.Button(self.controls, image=self.rectangle_img, text="Rectangle", compound="top",
                                  command=lambda: self.select_tool('rectangle'))
        self.rect_btn.grid(row=0, column=9, padx=5)

        self.oval_btn = tk.Button(self.controls, image=self.oval_img, text="Oval", compound="top",
                                  command=lambda: self.select_tool('oval'))
        self.oval_btn.grid(row=0, column=10, padx=5)

        self.eraser_btn = tk.Button(self.controls, image=self.eraser_img, text="Eraser", compound="top",
                                    command=self.toggle_eraser)
        self.eraser_btn.grid(row=0, column=11, padx=5)

        self.text_btn = tk.Button(self.controls, image=self.text_img, text="Text", compound="top",
                                  command=self.add_text)
        self.text_btn.grid(row=0, column=12, padx=5)

        self.select_btn = tk.Button(self.controls, image=self.select_img, text="Select", compound="top",
                                    command=lambda: self.select_tool('select'))
        self.select_btn.grid(row=0, column=13, padx=5)

        # Image insertion
        self.add_image_button = tk.Button(self.controls, image=self.insert_image_img, text="Insert Image",
                                          compound="top", command=self.add_image)
        self.add_image_button.grid(row=0, column=14, padx=5)

        self.undo_btn = tk.Button(self.controls, image=self.undo_img, text="Undo", compound="top", command=self.undo)
        self.undo_btn.grid(row=0, column=15, padx=5)

        self.redo_btn = tk.Button(self.controls, image=self.redo_img, text="Redo", compound="top", command=self.redo)
        self.redo_btn.grid(row=0, column=16, padx=5)

        self.voice_btn = tk.Button(self.controls, image=self.voice_img, text="Voice", compound="top",
                                   command=lambda: voiceassistant.toggle_voice_assistant(self))
        self.voice_btn.grid(row=0, column=17, padx=5)

        self.create_menu()

        self.palette = ColorPalette(self.root, self)
        self.palette.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.c = tk.Canvas(self.root, bg=self.color_bg, width=800, height=600)
        self.c.pack(fill=tk.BOTH, expand=True)

        self.c.bind('<B1-Motion>', self.paint)
        self.c.bind('<ButtonPress-1>', self.on_button_press)
        self.c.bind('<ButtonRelease-1>', self.on_button_release)
        self.c.bind('<Double-Button-1>', self.select_or_edit_text)  # Bind double-click for text editing
        self.c.bind('<B1-Motion>', self.on_motion)
        # Unbind drag_text when mouse is released
        self.c.unbind('<B1-Motion>')

        #for inserting image,resizing and dragging it
        self.c.bind("<ButtonPress-3>", self.on_mouse_down)  # Right mouse button press
        self.c.bind("<B3-Motion>", self.on_mouse_drag)  # Right mouse button drag
        self.c.bind("<ButtonRelease-3>", self.on_mouse_up)  # Right mouse button release

        # Create scrollbars
        self.v_scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=self.c.yview)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scrollbar = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=self.c.xview)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Configure the canvas scrollbars
        self.c.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        # Bind the canvas configure event
        self.c.bind("<Configure>", self.on_canvas_configure)

    def on_canvas_configure(self, event):
        self.c.configure(scrollregion=self.c.bbox("all"))

    def create_menu(self):
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save", command=self.save_canvas)
        file_menu.add_command(label="Open", command=self.open_canvas)
        file_menu.add_command(label="Clear", command=self.clear)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo)
        edit_menu.add_command(label="Redo", command=self.redo)
        edit_menu.add_command(label="Voice Notes", command=self.start_listening)

        brush_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Brush", menu=brush_menu)
        brush_menu.add_command(label="Brush Size", command=self.set_brush_size)
        brush_menu.add_command(label="Brush Color", command=self.change_fg)
        brush_menu.add_command(label="Eraser", command=self.activate_eraser)
        brush_menu.add_command(label="Text Size", command=self.set_text_size)

        tool_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Tools", menu=tool_menu)
        tool_menu.add_command(label="Brush", command=self.use_brush)
        tool_menu.add_command(label="Text", command=self.add_text)
        tool_menu.add_command(label="Rectangle", command=lambda: self.select_tool('rectangle'))
        tool_menu.add_command(label="Oval", command=lambda: self.select_tool('oval'))
        tool_menu.add_command(label="Line", command=lambda: self.select_tool('line'))
        tool_menu.add_command(label="Sticky Note",command=self.create_sticky_note)  # Sticky note option

        ai_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="AI features", menu=ai_menu)
        ai_menu.add_command(label="Idea Generation", command=self.execute_idea_generation)
        ai_menu.add_command(label="Extract text from image", command=self.execute_text_extraction)
        ai_menu.add_command(label="Generate information", command=self.execute_short_info)
        ai_menu.add_command(label="Document to Flowchart", command=self.generate_flowchart_from_file)

    # speech-to-text
    def start_listening(self):
        if not self.is_listening:
            self.is_listening = True
            print("Starting speech recognition...")
            threading.Thread(target=self.listen).start()

    def listen(self):
        with sr.Microphone() as source:
            print("Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.recognizer.dynamic_energy_threshold = True

            while self.is_listening:
                try:
                    print("Listening for speech...")
                    audio_data = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                    print("Recognizing speech...")
                    text = self.recognizer.recognize_google(audio_data)
                    text = text.capitalize()

                    if "quit" in text.lower():
                        print("Quit command detected. Stopping...")
                        self.is_listening = False
                        break

                    # Print the recognized text on the canvas
                    self.c.create_text(10, self.current_y, anchor=tk.NW, text=text, fill="black",
                                       font=("Arial", 12))
                    self.current_y += 20  # Move down for next line of text
                    self.root.update()

                    print(f"Recognized text: {text}")

                except sr.WaitTimeoutError:
                    print("Timeout occurred while listening.")
                    continue
                except sr.UnknownValueError:
                    print("Speech was not recognized.")
                    continue
                except sr.RequestError as e:
                    print(f"Request error: {e}")
                    continue
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    continue

        print("Speech recognition stopped.")
        self.is_listening = False

#main code
    def on_button_press(self, event):
        self.old_x = event.x
        self.old_y = event.y

        if self.eraser_on:
            self.erase(event)

        if self.shape == 'rectangle':
            self.shape_id = self.c.create_rectangle(self.old_x, self.old_y, self.old_x, self.old_y,
                                                    outline=self.color_fg, width=self.penwidth,
                                                    fill=self.fill_color)
            self.c.config(cursor='cross')
            self.objects.append(self.shape_id)

        elif self.shape == 'oval':
            self.shape_id = self.c.create_oval(self.old_x, self.old_y, self.old_x, self.old_y,
                                               outline=self.color_fg, width=self.penwidth,
                                               fill=self.fill_color)
            self.c.config(cursor='cross')
            self.objects.append(self.shape_id)

        elif self.shape == 'line':
            self.shape_id = self.c.create_line(self.old_x, self.old_y, self.old_x, self.old_y,
                                               width=self.penwidth, fill=self.color_fg)
            self.c.config(cursor='cross')
            self.objects.append(self.shape_id)

        elif self.shape == 'select':
            self.select_object(event.x, event.y)
            if self.selected_object and self.c.type(self.selected_object) == 'text':
                self.c.bind('<B1-Motion>', self.drag_text)

    def on_button_release(self, event):
        if self.shape == 'rectangle':
            self.c.coords(self.shape_id, self.old_x, self.old_y, event.x, event.y)
            self.undo_stack.append(('create_rectangle', self.shape_id, self.old_x, self.old_y, event.x, event.y,
                                    self.color_fg, self.penwidth))

        elif self.shape == 'oval':
            self.c.coords(self.shape_id, self.old_x, self.old_y, event.x, event.y)
            self.undo_stack.append(
                ('create_oval', self.shape_id, self.old_x, self.old_y, event.x, event.y, self.color_fg, self.penwidth))

        elif self.shape == 'line':
            self.c.coords(self.shape_id, self.old_x, self.old_y, event.x, event.y)
            self.undo_stack.append(
                ('create_line', self.shape_id, self.old_x, self.old_y, event.x, event.y, self.color_fg, self.penwidth))

            # Unbind drag_text when mouse is released
        self.c.unbind('<B1-Motion>')
        self.reset(event)

        # Reset cursor to default after drawing
        self.c.config(cursor='arrow')

    def toggle_eraser(self):
        self.eraser_on = not self.eraser_on
        self.shape = None  # Deactivate shape drawing when eraser is active

    def on_motion(self, event):
        self.move_object(event)
        self.drag_text(event)

    def drag_text(self, event):
        if self.selected_object and self.c.type(self.selected_object) == 'text':
            # Move the text item
            current_x, current_y = event.x, event.y
            self.c.move(self.selected_object, current_x - self.old_x, current_y - self.old_y)
            # Update old_x and old_y to current_x and current_y
            self.old_x, self.old_y = current_x, current_y

    def paint(self, event):
        if self.eraser_on:
            self.erase(event)
        elif self.shape != 'select':
            self.update_shape(event)
        elif self.selected_object:
            self.move_object(event)

    def update_shape(self, event):
        if self.shape_id:
            if self.shape == 'line':
                self.c.coords(self.shape_id, self.old_x, self.old_y, event.x, event.y)
            elif self.shape == 'rectangle':
                self.c.coords(self.shape_id, self.old_x, self.old_y, event.x, event.y)
            elif self.shape == 'oval':
                self.c.coords(self.shape_id, self.old_x, self.old_y, event.x, event.y)

    def move_object(self, event):
        coords = self.c.coords(self.selected_object)
        dx = event.x - self.old_x
        dy = event.y - self.old_y
        new_coords = [coords[0] + dx, coords[1] + dy, coords[2] + dx, coords[3] + dy]
        self.c.coords(self.selected_object, *new_coords)
        self.old_x = event.x
        self.old_y = event.y

    def reset(self, event):
        if self.selected_object:
            item_type = self.c.type(self.selected_object)

            if item_type in ["line", "rectangle", "oval"]:
                self.c.itemconfig(self.selected_object, outline=self.color_fg)
            elif item_type == "text":
                self.c.itemconfig(self.selected_object, fill=self.color_fg)

            # Reset other properties or perform additional logic if needed
            self.selected_object = None
            self.c.config(cursor='arrow')

    def changeW(self, e):
        self.penwidth = int(float(e))

    def clear(self):
        self.c.delete(tk.ALL)
        self.objects.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()

    def change_fg(self):
        self.color_fg = askcolor(color=self.color_fg)[1]

    def change_bg(self):
        self.color_bg = askcolor(color=self.color_bg)[1]
        self.c['bg'] = self.color_bg

    def change_fill_color(self):
        self.fill_color = askcolor(color=self.fill_color)[1]

    def select_tool(self, tool):
        self.shape = tool
        self.eraser_on = False

    def activate_eraser(self):
        # self.brush_color = "white"
        self.tool = 'erase'

    def erase(self, event):
        x, y = event.x, event.y
        self.c.create_rectangle(x - 10, y - 10, x + 10, y + 10, fill="white", outline="white")

        self.old_x = event.x
        self.old_y = event.y

    def undo(self):
        if self.undo_stack:
            item = self.undo_stack.pop()
            action, item_id, *item_data = item
            self.redo_stack.append(item)
            self.c.delete(item_id)

    def redo(self):
        if self.redo_stack:
            item = self.redo_stack.pop()
            action, item_id, *item_data = item

            if action == 'create_line':
                x0, y0, x1, y1, color, width = item_data
                line_id = self.c.create_line(x0, y0, x1, y1, fill=color, width=width)
                self.undo_stack.append(('create_line', line_id, x0, y0, x1, y1, color, width))

            elif action == 'create_rectangle':
                x0, y0, x1, y1, color, width = item_data
                rect_id = self.c.create_rectangle(x0, y0, x1, y1, outline=color, width=width)
                self.undo_stack.append(('create_rectangle', rect_id, x0, y0, x1, y1, color, width))

            elif action == 'create_oval':
                x0, y0, x1, y1, color, width = item_data
                oval_id = self.c.create_oval(x0, y0, x1, y1, outline=color, width=width)
                self.undo_stack.append(('create_oval', oval_id, x0, y0, x1, y1, color, width))

            elif action == 'create_text':
                x, y, text, color, font_size = item_data
                text_id = self.c.create_text(x, y, text=text, fill=color, font=("Arial", font_size))
                self.undo_stack.append(('create_text', text_id, x, y, text, color, font_size))

            elif action == 'add_image':
                file_path, x, y = item_data
                self.image = Image.open(file_path)
                self.image.thumbnail((200, 200))
                self.photo_image = ImageTk.PhotoImage(self.image)
                image_id = self.c.create_image(x, y, anchor=tk.NW, image=self.photo_image)
                self.resize_handle = self.c.create_rectangle(x + self.image.width - 10, y + self.image.height - 10,
                                                             x + self.image.width, y + self.image.height, outline='', fill='',
                                                             tags='resize')
                self.undo_stack.append(('add_image', image_id, file_path, x, y))
                self.image_id = image_id

    def add_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image = Image.open(file_path)
            self.image.thumbnail((200, 200))
            self.photo_image = ImageTk.PhotoImage(self.image)

            if self.image_id:
                self.c.delete(self.image_id)

            self.image_id = self.c.create_image(100, 100, anchor=tk.NW, image=self.photo_image)
            self.resize_handle = self.c.create_rectangle(100 + self.image.width - 10, 100 + self.image.height - 10,
                                                         100 + self.image.width, 100 + self.image.height, outline='',
                                                         fill='red',
                                                         tags='resize')
            # Save the state for undo
            self.undo_stack.append(('add_image', self.image_id, file_path, 100, 100))
            self.redo_stack.clear()  # Clear redo stack when a new action is performed

    def use_brush(self):
        self.current_tool = 'brush'

    def create_sticky_note(self):
        # Create a sticky note with a default size and position
        note = tk.Toplevel(self.root)
        note.title("Sticky Note")
        note.geometry("200x150")
        note_text = tk.Text(note, wrap=tk.WORD, bg="yellow", fg="black", font=("Arial", 12))
        note_text.pack(expand=True, fill=tk.BOTH)

    def update_resize_handle(self):
        if self.image_id:
            x1, y1, x2, y2 = self.c.bbox(self.image_id)
            self.c.coords('resize', x2 - 10, y2 - 10, x2, y2)

    def on_mouse_down(self, event):
        if self.image_id:
            x1, y1, x2, y2 = self.c.bbox(self.image_id)
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                if self.c.find_withtag(tk.CURRENT) == self.c.find_withtag('resize'):
                    self.resizing = True
                    self.start_x = event.x
                    self.start_y = event.y
                else:
                    self.dragging = True
                    self.offset_x = event.x - x1
                    self.offset_y = event.y - y1

    def on_mouse_drag(self, event):
        if self.eraser_on:
            self.erase(event)

        if self.dragging and self.image_id:
            x = event.x - self.offset_x
            y = event.y - self.offset_y
            self.c.coords(self.image_id, x, y)
            self.update_resize_handle()
        elif self.resizing:
            x1, y1, x2, y2 = self.c.bbox(self.image_id)
            new_width = event.x - x1
            new_height = event.y - y1
            if new_width > 0 and new_height > 0:
                self.image = self.image.resize((new_width, new_height), Image.LANCZOS)
                self.photo_image = ImageTk.PhotoImage(self.image)
                self.c.itemconfig(self.image_id, image=self.photo_image)
                self.update_resize_handle()

    def on_mouse_up(self, event):
        self.dragging = False
        self.resizing = False

    def add_text(self):
        text = simpledialog.askstring("Input", "Enter text:")
        if text:
            x, y = self.c.winfo_pointerx() - self.c.winfo_rootx(), self.c.winfo_pointery() - self.c.winfo_rooty()
            text_id = self.c.create_text(x, y, text=text, fill=self.color_fg, font=(self.current_font, self.font_size))
            self.undo_stack.append(('create_text', text_id, x, y, text, self.color_fg, self.font_size))
            self.redo_stack.clear()

    def update_font(self, *args):
        self.current_font = self.font_var.get()
        if self.selected_object:
            self.update_text_properties(self.selected_object)

    def update_font_size(self, *args):
        self.font_size = int(self.size_var.get())
        if self.selected_object:
            self.update_text_properties(self.selected_object)

    def set_text_size(self):
        size = simpledialog.askinteger("Text Size", "Enter text size:", minvalue=1, maxvalue=100)
        if size:
            self.font_size = size
            self.size_var.set(size)  # Update the font size in the dropdown menu if you have it

    def set_brush_size(self):
        # Prompt the user to enter a brush size
        size = simpledialog.askinteger("Brush Size", "Enter brush size:", minvalue=1, maxvalue=100)
        if size is not None:
            self.pen_size = size
            # Update the brush size in the drawing tool if necessary
            self.update_brush_size(size)

    def update_brush_size(self, size):
        # This method should update the brush size in your drawing tool
        print(f"Brush size set to {size}")
        # Implement integration with your drawing tool here

    def select_object(self, x, y):
        self.selected_object = self.c.find_closest(x, y)[0]
        item_type = self.c.type(self.selected_object)

        if item_type in ["line", "rectangle", "oval"]:
            self.c.itemconfig(self.selected_object, outline="blue")
        elif item_type == "text":
            self.show_text_edit_options()

    def show_text_edit_options(self):
        # Ensure text properties are updated for the selected text item
        if self.selected_object and self.c.type(self.selected_object) == "text":
            self.update_text_properties(self.selected_object)

    def update_text_properties(self, text_id):
        self.c.itemconfig(text_id, font=(self.current_font, self.font_size))

    def select_or_edit_text(self, event):
        item = self.c.find_closest(event.x, event.y)[0]
        if self.c.type(item) == "text":
            self.edit_text_dialog(item)

    def edit_text_dialog(self, text_id):
        def apply_changes():
            new_text = text_editor.get("1.0", tk.END).strip()
            self.c.itemconfig(text_id, text=new_text)
            edit_window.destroy()

        current_text = self.c.itemcget(text_id, "text")
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Text")

        text_editor = tk.Text(edit_window, wrap='word', width=40, height=10)
        text_editor.pack(expand=True, fill='both')
        text_editor.insert(tk.END, current_text)

        apply_btn = tk.Button(edit_window, text="Apply", command=apply_changes)
        apply_btn.pack(pady=5)

    def save_canvas(self):
        # Determine filename
        if hasattr(self, 'current_filename') and self.current_filename:
            filename = self.current_filename
        else:
            file = asksaveasfile(defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if file:
                filename = file.name
                self.current_filename = filename
            else:
                return

        # Collect canvas data
        canvas_data = []
        for obj in self.c.find_all():
            obj_type = self.c.type(obj)
            coords = self.c.coords(obj)
            item_data = {
                'type': obj_type,
                'coords': coords
            }
            if obj_type == 'line':
                item_data['width'] = self.c.itemcget(obj, 'width')
                item_data['fill'] = self.c.itemcget(obj, 'fill')
            elif obj_type in ['rectangle', 'oval']:
                item_data['outline'] = self.c.itemcget(obj, 'outline')
                item_data['width'] = self.c.itemcget(obj, 'width')
                item_data['fill'] = self.c.itemcget(obj, 'fill')
            elif obj_type == 'text':
                item_data['text'] = self.c.itemcget(obj, 'text')
                item_data['fill'] = self.c.itemcget(obj, 'fill')
                item_data['font'] = self.c.itemcget(obj, 'font')
            elif obj_type == 'image':
                image_id = self.c.itemcget(obj, 'image')
                if image_id:
                    # Save the image file path or a placeholder name
                    # Ensure that `self.image_files` is properly populated
                    image_file = self.image_files.get(image_id, '')
                    item_data['image'] = image_file

            canvas_data.append(item_data)

        # Save data to file
        with open(filename, 'w') as file:
            json.dump(canvas_data, file)

    def open_canvas(self):
        # Prompt for a file to open
        filename = askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filename:
            try:
                with open(filename, 'r') as file:
                    canvas_data = json.load(file)

                # Clear current canvas
                self.c.delete("all")
                self.image_refs = []  # Reset image references list

                # Load all items to the canvas
                for item in canvas_data:
                    obj_type = item['type']
                    coords = item['coords']
                    if obj_type == 'line':
                        self.c.create_line(*coords, fill=item.get('fill', ''), width=item.get('width', 1))
                    elif obj_type == 'rectangle':
                        self.c.create_rectangle(*coords, outline=item.get('outline', ''), width=item.get('width', 1),
                                                fill=item.get('fill', ''))
                    elif obj_type == 'oval':
                        self.c.create_oval(*coords, outline=item.get('outline', ''), width=item.get('width', 1),
                                           fill=item.get('fill', ''))
                    elif obj_type == 'text':
                        self.c.create_text(*coords, text=item.get('text', ''), fill=item.get('fill', ''),
                                           font=item.get('font', ''))
                    elif obj_type == 'image':
                        image_path = item.get('image', '')
                        if image_path:
                            try:
                                image = Image.open(image_path)
                                photo_image = ImageTk.PhotoImage(image)
                                self.c.create_image(*coords, image=photo_image)
                                # Store reference to avoid garbage collection
                                self.image_refs.append(photo_image)
                            except Exception as e:
                                print(f"Error loading image: {e}")

                # Save the filename for future saves
                self.current_filename = filename
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
            except Exception as e:
                print(f"Error opening file: {e}")

    def on_click(self, event):
        # Detect if the click is on one of the shapes
        shape_id = self.c.find_closest(event.x, event.y)[0]
        if shape_id:
            self.current_shape = shape_id
            self.start_x = event.x
            self.start_y = event.y

    def on_drag(self, event):
        if self.current_shape:
            # Get the current coordinates
            x1, y1, x2, y2 = self.c.coords(self.current_shape)
            dx = event.x - self.start_x
            dy = event.y - self.start_y

            # Resize the shape
            if self.c.type(self.current_shape) == "rectangle":
                self.c.coords(self.current_shape, x1, y1, x2 + dx, y2 + dy)
            elif self.c.type(self.current_shape) == "oval":
                self.c.coords(self.current_shape, x1, y1, x2 + dx, y2 + dy)

            self.start_x = event.x
            self.start_y = event.y

    def add_action_to_canvas(self, item):
        action_type, item_id, *item_data = item

        if action_type == 'create_line':
            x0, y0, x1, y1, color, width = item_data
            line_id = self.c.create_line(x0, y0, x1, y1, fill=color, width=width)
            self.actions[self.actions.index(item)] = (action_type, line_id, x0, y0, x1, y1, color, width)

        elif action_type == 'create_rectangle':
            x0, y0, x1, y1, color, width = item_data
            rect_id = self.c.create_rectangle(x0, y0, x1, y1, outline=color, width=width)
            self.actions[self.actions.index(item)] = (action_type, rect_id, x0, y0, x1, y1, color, width)

        elif action_type == 'create_oval':
            x0, y0, x1, y1, color, width = item_data
            oval_id = self.c.create_oval(x0, y0, x1, y1, outline=color, width=width)
            self.actions[self.actions.index(item)] = (action_type, oval_id, x0, y0, x1, y1, color, width)

        elif action_type == 'create_text':
            x, y, text, color, font_size = item_data
            text_id = self.c.create_text(x, y, text=text, fill=color, font=("Arial", font_size))
            self.actions[self.actions.index(item)] = (action_type, text_id, x, y, text, color, font_size)

        # speech-to-text
    def start_listening(self):
        if not self.is_listening:
            self.is_listening = True
            print("Starting speech recognition...")
            threading.Thread(target=self.listen).start()

    def listen(self):
        with sr.Microphone() as source:
            print("Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.recognizer.dynamic_energy_threshold = True

            while self.is_listening:
                try:
                    print("Listening for speech...")
                    audio_data = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                    print("Recognizing speech...")
                    text = self.recognizer.recognize_google(audio_data)
                    text = text.capitalize()

                    if "quit" in text.lower():
                        print("Quit command detected. Stopping...")
                        self.is_listening = False
                        break

                    # Print the recognized text on the canvas
                    self.c.create_text(10, self.current_y, anchor=tk.NW, text=text, fill="black",
                                       font=("Arial", 12))
                    self.current_y += 20  # Move down for next line of text
                    self.root.update()

                    print(f"Recognized text: {text}")

                except sr.WaitTimeoutError:
                    print("Timeout occurred while listening.")
                    continue
                except sr.UnknownValueError:
                    print("Speech was not recognized.")
                    continue
                except sr.RequestError as e:
                    print(f"Request error: {e}")
                    continue
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    continue

        print("Speech recognition stopped.")
        self.is_listening = False


    #AI FEATURES
    def execute_idea_generation(self):
        topic = simpledialog.askstring("Idea Generation", "Enter a topic:").strip().lower()
        if topic:
            ideas = generate_ideas(topic)
            ideas_text = "\n".join(ideas)
            messagebox.showinfo("Generated Ideas", f"New ideas about {topic}:\n\n{ideas_text}")


    def create_text_entry_display(self, text):
        # Place text on the canvas at a default position (e.g., (10, 10))
        text_id = self.c.create_text(10, 10, anchor='nw', text=text, font=('Arial', 12), tags='editable')
        self.undo_stack.append(('create_text', text_id, 10, 10, text, 'black', 12))

    def execute_text_extraction(self):
        image_path = filedialog.askopenfilename(title="Select an image",
                                                filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")])
        # If a file was selected
        if image_path:
            # Extract and display the text from the selected image
            text = extract_text(image_path)

            if text:
                self.create_text_entry_display(text)
            else:
                messagebox.showinfo("Error", "No text found in image")
        else:
            messagebox.showinfo("Error", "No image selected")

    def execute_short_info(self):
        topic = simpledialog.askstring("Information Generation", "Enter a topic:").strip().lower()
        if topic:
            info = fetch_and_summarize(topic)
            if info:
                # Display the extracted information on the canvas
                self.create_text_entry_display(info)
            else:
                messagebox.showinfo("Error", "No relevant information found")

    def generate_flowchart_from_file(self):
        file_path = filedialog.askopenfilename()

        if file_path:
            try:
                if file_path.lower().endswith('.txt'):
                    text = read_text_from_plain_file(file_path)
                elif file_path.lower().endswith('.docx'):
                    text = read_text_from_docx(file_path)
                elif file_path.lower().endswith('.pdf'):
                    text = read_text_from_pdf(file_path)
                else:
                    messagebox.showerror("Error", "Unsupported file format. Please select a .txt, .docx, or .pdf file.")
                    return

                if not text.strip():
                    messagebox.showerror("Error", "No content in the file.")
                    return

                classification = parse_text(text)
                flowchart_structure = create_structure(classification)

                # Initialize Digraph with adjusted graph attributes
                dot = Digraph(graph_attr={'size': '12,12', 'dpi': '300', 'bgcolor': 'white', 'rankdir': 'LR'})

                # Add nodes and edges for the entire structure
                add_edges(dot, 'Start', flowchart_structure['Start'])

                try:
                    dot.render('flowchart', format='png', view=True)
                except Exception as e:
                    messagebox.showerror("Error", f"Error generating flowchart:")
            except FileNotFoundError:
                messagebox.showerror("Error", f"File '{file_path}' not found.")
            except Exception as e:
                messagebox.showerror("Error", f"Error reading file:")

if __name__ == '__main__':
    root = tk.Tk()
    Whiteboard(root)
    root.mainloop()