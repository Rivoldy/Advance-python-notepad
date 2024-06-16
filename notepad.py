import os
import pyautogui
from gtts import gTTS
from tkinter import *
from tkinter.messagebox import showinfo, showerror
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.simpledialog import askstring
from tkinter.scrolledtext import ScrolledText
import tkinter.font as tkFont
from PIL import Image, ImageTk
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.styles import get_style_by_name
from pygments.token import Token
import playsound

def newFile():
    global file
    root.title("Untitled - Notepad")
    file = None
    TextArea.delete(1.0, END)

def openFile():
    global file
    file = askopenfilename(defaultextension=".txt",
                           filetypes=[("All Files", "*.*"),
                                      ("Text Documents", "*.txt"),
                                      ("Images", "*.png;*.jpg;*.jpeg")])
    if file == "":
        file = None
    else:
        root.title(os.path.basename(file) + " - Notepad")
        TextArea.delete(1.0, END)
        if file.endswith(('.png', '.jpg', '.jpeg')):
            img = Image.open(file)
            img = img.resize((TextArea.winfo_width(), TextArea.winfo_height()), Image.ANTIALIAS)
            img = ImageTk.PhotoImage(img)
            TextArea.image_create(END, image=img)
            TextArea.image = img
        else:
            with open(file, "r") as f:
                TextArea.insert(1.0, f.read())

def saveFile():
    global file
    if file is None:
        file = asksaveasfilename(initialfile='Untitled.txt', defaultextension=".txt",
                                 filetypes=[("All Files", "*.*"),
                                            ("Text Documents", "*.txt"),
                                            ("Images", "*.png;*.jpg;*.jpeg")])
        if file == "":
            file = None
        else:
            if file.endswith(('.png', '.jpg', '.jpeg')):
                img = Image.open(file)
                img.save(file)
            else:
                with open(file, "w") as f:
                    f.write(TextArea.get(1.0, END))
            root.title(os.path.basename(file) + " - Notepad")
    else:
        if file.endswith(('.png', '.jpg', '.jpeg')):
            img = Image.open(file)
            img.save(file)
        else:
            with open(file, "w") as f:
                f.write(TextArea.get(1.0, END))

def quitApp():
    root.destroy()

def cut():
    TextArea.event_generate("<<Cut>>")

def copy():
    TextArea.event_generate("<<Copy>>")

def paste():
    TextArea.event_generate("<<Paste>>")

def undo():
    TextArea.event_generate("<<Undo>>")

def redo():
    TextArea.event_generate("<<Redo>>")

def about():
    showinfo("Notepad", "Notepad by Rivoldy")

def find_replace():
    def find():
        TextArea.tag_remove('found', '1.0', END)
        start_pos = '1.0'
        while True:
            start_pos = TextArea.search(find_entry.get(), start_pos, stopindex=END)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(find_entry.get())}c"
            TextArea.tag_add('found', start_pos, end_pos)
            start_pos = end_pos
        TextArea.tag_config('found', foreground='white', background='blue')

    def replace():
        find()
        TextArea.tag_remove('found', '1.0', END)
        content = TextArea.get('1.0', END)
        new_content = content.replace(find_entry.get(), replace_entry.get())
        TextArea.delete('1.0', END)
        TextArea.insert('1.0', new_content)

    fr_window = Toplevel(root)
    fr_window.title("Find & Replace")
    fr_window.geometry("300x100")

    Label(fr_window, text="Find:").grid(row=0, column=0, padx=4, pady=4)
    find_entry = Entry(fr_window)
    find_entry.grid(row=0, column=1, padx=4, pady=4)

    Label(fr_window, text="Replace:").grid(row=1, column=0, padx=4, pady=4)
    replace_entry = Entry(fr_window)
    replace_entry.grid(row=1, column=1, padx=4, pady=4)

    Button(fr_window, text="Find", command=find).grid(row=2, column=0, padx=4, pady=4)
    Button(fr_window, text="Replace", command=replace).grid(row=2, column=1, padx=4, pady=4)

def change_font():
    def update_font():
        selected_font = font_family.get()
        selected_size = font_size.get()
        TextArea.config(font=(selected_font, selected_size))

    font_window = Toplevel(root)
    font_window.title("Font")
    font_window.geometry("300x150")

    Label(font_window, text="Font Family:").grid(row=0, column=0, padx=4, pady=4)
    font_family = StringVar()
    font_family.set("lucida")
    font_family_dropdown = OptionMenu(font_window, font_family, *tkFont.families())
    font_family_dropdown.grid(row=0, column=1, padx=4, pady=4)

    Label(font_window, text="Font Size:").grid(row=1, column=0, padx=4, pady=4)
    font_size = StringVar()
    font_size.set("13")
    font_size_dropdown = OptionMenu(font_window, font_size, *[str(i) for i in range(8, 73)])
    font_size_dropdown.grid(row=1, column=1, padx=4, pady=4)

    Button(font_window, text="Apply", command=update_font).grid(row=2, columnspan=2, pady=4)

def toggle_theme():
    current_bg = TextArea.cget("background")
    new_bg = "black" if current_bg == "white" else "white"
    new_fg = "white" if new_bg == "black" else "black"
    TextArea.config(bg=new_bg, fg=new_fg, insertbackground=new_fg)

def autocomplete(event):
    current_text = TextArea.get("insert linestart", "insert")
    wordlist = ["def", "import", "from", "class", "self", "return", "if", "else", "elif"] + keyword.kwlist
    for word in wordlist:
        if word.startswith(current_text):
            TextArea.insert("insert", word[len(current_text):])
            TextArea.mark_set("insert", f"insert-{len(word[len(current_text):])}c")
            break

def word_count():
    text = TextArea.get(1.0, END)
    words = len(text.split())
    showinfo("Word Count", f"Words: {words}")

def auto_save():
    if file is not None:
        saveFile()
    root.after(300000, auto_save)  # Save every 5 minutes

def highlight_syntax(event=None):
    TextArea.tag_remove("Token.Keyword", "1.0", END)
    TextArea.tag_remove("Token.Name.Builtin", "1.0", END)
    TextArea.tag_remove("Token.String", "1.0", END)
    TextArea.tag_remove("Token.Comment", "1.0", END)

    content = TextArea.get("1.0", END)
    for token, content in lex(content, PythonLexer()):
        start = "1.0"
        while True:
            start = TextArea.search(content, start, stopindex=END)
            if not start:
                break
            end = f"{start}+{len(content)}c"
            try:
                TextArea.tag_add(str(token), start, end)
            except TclError:
                # Use a default color if the specified color is not valid
                TextArea.tag_add(str(token), start, end)
                TextArea.tag_config(str(token), foreground="#000000")
            start = end

    style = get_style_by_name("default")
    for token, style_def in style:
        if token:
            try:
                TextArea.tag_config(str(token), foreground=style_def["color"])
            except TclError:
                # Use a default color if the specified color is not valid
                TextArea.tag_config(str(token), foreground="#000000")

def take_screenshot():
    screenshot = pyautogui.screenshot()
    file = asksaveasfilename(defaultextension=".png",
                             filetypes=[("PNG Files", "*.png")])
    if file:
        screenshot.save(file)
        showinfo("Screenshot", f"Screenshot saved as {file}")

def text_to_speech():
    text = TextArea.get(1.0, END)
    language = askstring("Language", "Enter language (e.g., 'en' for English, 'id' for Indonesian):")
    if not language:
        language = "en"
    try:
        tts = gTTS(text=text, lang=language)
        tts.save("output.mp3")
        playsound.playsound("output.mp3")
    except ValueError as e:
        showerror("Language Error", str(e))

if __name__ == '__main__':
    # Basic tkinter setup
    root = Tk()
    root.title("Untitled - Notepad")
    root.geometry("800x600")

    # Add TextArea
    TextArea = ScrolledText(root, font="lucida 13", undo=True, bg="white", fg="black", insertbackground="black")
    file = None
    TextArea.pack(expand=True, fill=BOTH)

    # Create a menubar
    MenuBar = Menu(root)

    # File Menu
    FileMenu = Menu(MenuBar, tearoff=0)
    FileMenu.add_command(label="New", command=newFile)
    FileMenu.add_command(label="Open", command=openFile)
    FileMenu.add_command(label="Save", command=saveFile)
    FileMenu.add_separator()
    FileMenu.add_command(label="Exit", command=quitApp)
    MenuBar.add_cascade(label="File", menu=FileMenu)

    # Edit Menu
    EditMenu = Menu(MenuBar, tearoff=0)
    EditMenu.add_command(label="Undo", command=undo)
    EditMenu.add_command(label="Redo", command=redo)
    EditMenu.add_separator()
    EditMenu.add_command(label="Cut", command=cut)
    EditMenu.add_command(label="Copy", command=copy)
    EditMenu.add_command(label="Paste", command=paste)
    MenuBar.add_cascade(label="Edit", menu=EditMenu)

    # Find & Replace
    EditMenu.add_separator()
    EditMenu.add_command(label="Find & Replace", command=find_replace)

    # Format Menu
    FormatMenu = Menu(MenuBar, tearoff=0)
    FormatMenu.add_command(label="Font", command=change_font)
    MenuBar.add_cascade(label="Format", menu=FormatMenu)

    # View Menu
    ViewMenu = Menu(MenuBar, tearoff=0)
    ViewMenu.add_command(label="Toggle Theme", command=toggle_theme)
    MenuBar.add_cascade(label="View", menu=ViewMenu)

    # Tools Menu
    ToolsMenu = Menu(MenuBar, tearoff=0)
    ToolsMenu.add_command(label="Word Count", command=word_count)
    ToolsMenu.add_command(label="Take Screenshot", command=take_screenshot)
    ToolsMenu.add_command(label="Text to Speech", command=text_to_speech)
    MenuBar.add_cascade(label="Tools", menu=ToolsMenu)

    # Help Menu
    HelpMenu = Menu(MenuBar, tearoff=0)
    HelpMenu.add_command(label="About Notepad", command=about)
    MenuBar.add_cascade(label="Help", menu=HelpMenu)

    # Configure the menubar
    root.config(menu=MenuBar)

    # Status Bar
    status = StringVar()
    status.set("Untitled - Notepad")
    StatusBar = Label(root, textvariable=status, relief=SUNKEN, anchor='w')
    StatusBar.pack(side=BOTTOM, fill=X)

    def update_status(event=None):
        if file:
            status.set(os.path.basename(file) + " - Notepad")
        else:
            status.set("Untitled - Notepad")

    TextArea.bind("<KeyRelease>", update_status)
    TextArea.bind("<KeyRelease>", highlight_syntax)
    TextArea.bind("<Tab>", autocomplete)

    # Enable Auto-Save
    auto_save()

    root.mainloop()
