import os
from tkinter import *
from tkinter import ttk, messagebox
from tkinter.filedialog import askopenfilename

import whisper

file_to_transcribe: str | None = None


def get_file_pick():
    ALLOWED_FILE_TYPES = [
        ("MPEG file", ("*.mp3","*.mp4")),
        # ("MP4 file", "*.mp4"),
    ]

    picked_file = askopenfilename(filetypes=ALLOWED_FILE_TYPES)
    print(picked_file)

    return picked_file if picked_file != () else None


def select_file():
    global selected_file_label, file_to_transcribe
    picked_file = get_file_pick()

    if picked_file is not None and os.path.exists(picked_file):
        file_to_transcribe = picked_file
        selected_file_label.configure(text=f"File selected: {picked_file}")
        start_button.config(state="normal", text="Start")


def init_transcription():
    global file_to_transcribe
    start_button.config(state="disabled", text="Transcribing...")
    print(f"Transcribing {file_to_transcribe}.")

    try:
        result_text = transcribe(file_to_transcribe)
        write_transcription_to_disk(result_text, file_to_transcribe)
    except Exception as ex:
        messagebox.showerror("Error", str(ex))
    finally:
        start_button.config(state="disabled", text="Start")
        file_to_transcribe = None
        selected_file_label.config(text="")
        messagebox.showinfo("Success", "File successfully transcribed!")


def transcribe(file):
    if not os.path.exists(file):
        raise ValueError(f"File does not exist ({file}).")

    model = whisper.load_model("small")
    result = model.transcribe(file, language="de")

    # gotta pull out the segments one at a time.
    segments = list(map(lambda s: s["text"], result["segments"]))
    return os.linesep.join(segments)


def write_transcription_to_disk(result, transcribed_file: str | None):
    if transcribed_file is None:
        raise ValueError("Transcribed file cannot be None.")

    # clip off file extension
    filename_no_extension = ".".join(transcribed_file.split(".")[:-1])

    result_filename = ".".join((filename_no_extension, "txt"))

    with open(result_filename, "w") as file:
        file.write(result)


root = Tk()
root.minsize(500, 200)
root.title(string="Helga's tool")

# frame hierarchy
root_frame = ttk.Frame(root, padding=16)
root_frame.grid()

control_frame = ttk.Frame(root_frame, padding=16)
control_frame.grid(column=0, row=0)

# control frame: buttons and list which file is selected
ttk.Label(
    control_frame,
    text="Pick a file to transcribe!\n"
    "Program will freeze while transcription is in progress!",
    font="bold",
).grid(column=0, row=0)
selected_file_label = ttk.Label(control_frame, text="")
selected_file_label.grid(column=0, row=1)

ttk.Button(control_frame, text="Pick file", command=select_file).grid(column=0, row=2)

start_button = ttk.Button(control_frame, text="Start", command=init_transcription)
start_button.grid(column=1, row=2)
start_button.config(state="disabled")


if __name__ == "__main__":
    root.mainloop()
