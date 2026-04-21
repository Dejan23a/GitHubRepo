# Create a Tkinter app with:
# - text input
# - OK and Cancel buttons
# - word counter on OK
# - exit on Cancel

import tkinter as tk
def count_words():
    text = input_box.get("1.0", tk.END).strip()
    count = len(text.split())
    result_label.config(text=f"Words: {count}")

def close_app():
    root.destroy()

root = tk.Tk()
root.title("Word Counter")
root.geometry("360x240")

input_box = tk.Text(root, wrap="word", width=40, height=8)
input_box.pack(padx=10, pady=(10, 0))

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

ok_button = tk.Button(button_frame, text="OK", width=10, command=count_words)
ok_button.pack(side="left", padx=5)

cancel_button = tk.Button(button_frame, text="Cancel", width=10, command=close_app)
cancel_button.pack(side="left", padx=5)

result_label = tk.Label(root, text="Words: 0")
result_label.pack(pady=(0, 10))

root.mainloop()