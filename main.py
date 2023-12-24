import os
import time
from tkinter import *
from tkinter import ttk, messagebox
from tkinter.filedialog import askopenfilename

import whisper

file_to_transcribe: str | None = None


class View:
    def __init__(self, controller: "Controller"):
        self.controller = controller

        # init UI elements
        self.root = Tk()
        self.root_frame = ttk.Frame(self.root, padding=16)
        self.control_frame = ttk.Frame(self.root_frame, padding=16)
        self.selected_file_label = ttk.Label(self.control_frame, text="")
        self.start_button = ttk.Button(
            self.control_frame, text="Start", command=self.controller.init_transcription
        )

        ttk.Label(
            self.control_frame,
            text="Pick a file to transcribe!\n"
            "Program will freeze while transcription is in progress!",
            font="bold",
        ).grid(column=0, row=0)
        ttk.Button(
            self.control_frame, text="Pick file", command=self.controller.select_file
        ).grid(column=0, row=2)

        # set some UI params
        self.root.minsize(500, 200)
        self.root.title(string="Helga's tool")
        self.root_frame.grid()
        self.control_frame.grid(column=0, row=0)
        self.selected_file_label.grid(column=0, row=1)

        self.start_button.grid(column=1, row=2)
        self.start_button.config(state="disabled")

    def update(self, state: "State"):
        if state.file_to_transcribe is not None:
            self.start_button.config(state="normal", text="Start")
            self.selected_file_label.config(
                text=f"File picked: {state.file_to_transcribe}"
            )
        else:
            self.start_button.config(state="disabled", text="Start")
            self.selected_file_label.config(text="")

    def show_transcription_start(self):
        self.start_button.config(state="disabled", text="Transcribing...")


class State:
    def __init__(self):
        self.__file_to_transcribe: str | None = None

        self.__views: list[View] = []

    def update_views(self):
        for view in self.__views:
            view.update(self)

    def add_view(self, new_view: View):
        if new_view not in self.__views:
            self.__views.append(new_view)

    def rm_view(self, view_to_rm: View):
        if view_to_rm in self.__views:
            self.__views.remove(view_to_rm)

    def update_file(self, new_file_to_transcribe):
        self.__file_to_transcribe = new_file_to_transcribe
        self.update_views()

    def signal_transcription_start(self):
        for view in self.__views:
            view.show_transcription_start()

    @property
    def file_to_transcribe(self):
        return self.__file_to_transcribe


class Controller:
    def __init__(self, state: State):
        self.__state = state

    def select_file(self):
        picked_file = askopenfilename(filetypes=[("MPEG file", ("*.mp3", "*.mp4"))])
        if picked_file is not None and os.path.exists(picked_file):
            self.__state.update_file(picked_file)

    @staticmethod
    def __transcribe(file):
        if not os.path.exists(file):
            raise ValueError(f"File does not exist ({file}).")

        model = whisper.load_model("small")
        result = model.transcribe(file, language="de")

        # gotta pull out the segments one at a time.
        segments = list(map(lambda s: s["text"], result["segments"]))
        return os.linesep.join(segments)

    @staticmethod
    def __write_transcription_to_disk(result, transcribed_file):
        if transcribed_file is None:
            raise ValueError("Transcribed file cannot be None.")

        # clip off file extension
        filename_no_extension = ".".join(transcribed_file.split(".")[:-1])

        result_filename = ".".join((filename_no_extension, "txt"))

        with open(result_filename, "w") as file:
            file.write(result)

    def init_transcription(self):
        self.__state.signal_transcription_start()
        print(f"Transcribing {self.__state.file_to_transcribe}.")
        time.sleep(1.5)

        try:
            result_text = self.__transcribe(self.__state.file_to_transcribe)
            self.__write_transcription_to_disk(
                result_text, self.__state.file_to_transcribe
            )
            messagebox.showinfo("Success", "File successfully transcribed!")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))
        finally:
            self.__state.update_file(None)


if __name__ == "__main__":
    # root.mainloop()

    # init MVC pattern
    state = State()
    controller = Controller(state)
    view = View(controller)
    state.add_view(view)

    # and run program
    view.root.mainloop()
