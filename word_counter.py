# read a text file and count how many words it contains
with open("text.txt", "r") as f:
    content = f.read()
    words = content.split()
    print(f"Number of words: {len(words)}")