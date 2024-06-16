import os
import threading
import pyautogui
from gtts import gTTS
from tkinter import *
from tkinter.messagebox import showinfo, showerror
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.simpledialog import askstring
from tkinter.scrolledtext import ScrolledText
import tkinter.font as tkFont
from PIL import Image, ImageTk
from pygments import lex, highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.styles import get_style_by_name
from pygments.formatters import HtmlFormatter
import playsound
import keyword

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
        highlight_syntax()

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
    highlight_syntax()

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
        highlight_syntax()

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
    highlight_syntax()

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
    content = TextArea.get("1.0", END)
    TextArea.mark_set("range_start", "1.0")

    for tag in TextArea.tag_names():
        TextArea.tag_delete(tag)

    try:
        lexer = guess_lexer(content)
    except:
        lexer = get_lexer_by_name("text")

    tokens = list(lex(content, lexer))

    for token_type, token_string in tokens:
        start = TextArea.index("range_start")
        end = f"{start}+{len(token_string)}c"
        TextArea.mark_set("range_start", end)
        TextArea.tag_add(str(token_type), start, end)

    style = get_style_by_name("default")
    for token, style_def in style:
        if token:
            try:
                TextArea.tag_config(str(token), foreground=style_def["color"])
            except TclError:
                TextArea.tag_config(str(token), foreground="#000000")

def take_screenshot():
    screenshot = pyautogui.screenshot()
    file = asksaveasfilename(defaultextension=".png",
                             filetypes=[("PNG Files", "*.png")])
    if file:
        screenshot.save(file)
        showinfo("Screenshot", f"Screenshot saved as {file}")

def show_language_dialog():
    language_dialog = Toplevel(root)
    language_dialog.title("Select Language for Text-to-Speech")
    language_dialog.geometry("300x200")

    Label(language_dialog, text="Select Language:").pack(pady=10)

    language_var = StringVar(language_dialog)
    language_var.set("en")  # default value
    full_languages = {
        "Afrikaans": "af", "Albanian": "sq", "Arabic": "ar", "Armenian": "hy", "Bengali": "bn", "Bosnian": "bs",
        "Catalan": "ca", "Croatian": "hr", "Czech": "cs", "Danish": "da", "Dutch": "nl", "English": "en", "Esperanto": "eo",
        "Estonian": "et", "Filipino": "tl", "Finnish": "fi", "French": "fr", "German": "de", "Greek": "el", "Gujarati": "gu",
        "Hindi": "hi", "Hungarian": "hu", "Icelandic": "is", "Indonesian": "id", "Italian": "it", "Japanese": "ja", "Javanese": "jw",
        "Kannada": "kn", "Khmer": "km", "Korean": "ko", "Latin": "la", "Latvian": "lv", "Lithuanian": "lt", "Macedonian": "mk",
        "Malayalam": "ml", "Marathi": "mr", "Myanmar (Burmese)": "my", "Nepali": "ne", "Norwegian": "no", "Polish": "pl",
        "Portuguese": "pt", "Punjabi": "pa", "Romanian": "ro", "Russian": "ru", "Serbian": "sr", "Sinhala": "si", "Slovak": "sk",
        "Spanish": "es", "Sundanese": "su", "Swahili": "sw", "Swedish": "sv", "Tamil": "ta", "Telugu": "te", "Thai": "th",
        "Turkish": "tr", "Ukrainian": "uk", "Urdu": "ur", "Vietnamese": "vi", "Welsh": "cy", "Xhosa": "xh", "Yiddish": "yi", "Zulu": "zu"
    }

    language_list = sorted(full_languages.keys())
    language_menu = OptionMenu(language_dialog, language_var, *language_list)
    language_menu.pack(pady=10)

    def set_language():
        selected_language = language_var.get()
        language_id = full_languages[selected_language]
        language_var.set(language_id)
        tts_thread = threading.Thread(target=lambda: text_to_speech(language_id))
        tts_thread.start()
        language_dialog.destroy()

    Button(language_dialog, text="OK", command=set_language).pack(pady=10)

def text_to_speech(language):
    text = TextArea.get(1.0, END)
    try:
        tts = gTTS(text=text, lang=language)
        output_file = f"{language}_output.mp3"
        tts.save(output_file)
        playsound.playsound(output_file)
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
    ToolsMenu.add_command(label="Text to Speech", command=show_language_dialog)
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
