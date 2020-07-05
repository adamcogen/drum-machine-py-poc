from dao import Note
from .gui_params import GUIParams
import sys
import tkinter as tk
from tkinter import filedialog

class DrumMachineGUI:
        def __init__(self, dao, gui_status):
                self.dao = dao
                self.gui_status = gui_status
                self.set_subdivisions_button = None
                self.start_gui()

        def initialize_rectangles(self):
                box_top_left_x = self.gui_params.get_box_top_left_x()
                box_top_left_y = self.gui_params.get_box_top_left_y()
                row_height = self.gui_params.get_row_height()
                row_width = self.gui_params.get_row_width()
                self.rectangles = [[] for i in range(0, self.dao.get_loop_params().get_number_of_rows())]
                for row_index in range(0, self.dao.get_loop_params().get_number_of_rows()):
                        subdivision_of_row = self.dao.get_subdivision_for_row(row_index)
                        note_width = (row_width / subdivision_of_row)
                        for note_index in range(0, subdivision_of_row):
                                note_top_left_x = box_top_left_x + (note_width * note_index)
                                note_top_left_y = box_top_left_y + (row_height * row_index)
                                note_bottom_left_x = note_top_left_x + note_width
                                note_bottom_left_y = note_top_left_y + row_height
                                color = self.note_off_color
                                if self.dao.get_note_at_beat_for_row(note_index, row_index) is not None:
                                        color = self.note_on_color
                                self.rectangles[row_index].append(self.canvas.create_rectangle(note_top_left_x, note_top_left_y, note_bottom_left_x, note_bottom_left_y, fill=color))

        def draw_pause_button(self, top_left_x, top_left_y):
                self.pause_button_rectangles = {}
                self.pause_button_rectangles["outer"] = self.canvas.create_rectangle(top_left_x, top_left_y, top_left_x + 20, top_left_y + 20, fill="gray94")
                self.pause_button_rectangles["inner"] = self.canvas.create_rectangle(top_left_x + 3, top_left_y + 3, top_left_x + 17, top_left_y + 17, fill="gray94")
                self.pause_button_rectangles["left"] = self.canvas.create_rectangle(top_left_x + 7, top_left_y + 7, top_left_x + 9, top_left_y + 13, fill="indian red")
                self.pause_button_rectangles["right"] = self.canvas.create_rectangle(top_left_x + 11, top_left_y + 7, top_left_x + 13, top_left_y + 13, fill="indian red")
                self.pause_button_rectangles["triangle"] = self.canvas.create_polygon([top_left_x + 7, top_left_y + 7, top_left_x + 13, top_left_y + 10, top_left_x + 7, top_left_y + 13], fill="indian red", outline="black")

        def adjust_pause_button(self):
                color = "gray94"
                if self.dao.is_paused():
                        self.canvas.itemconfig(self.pause_button_rectangles["left"], state="hidden")
                        self.canvas.itemconfig(self.pause_button_rectangles["right"], state="hidden")
                        self.canvas.itemconfig(self.pause_button_rectangles["triangle"], state="normal")
                else:
                        color = "gray64"
                        self.canvas.itemconfig(self.pause_button_rectangles["left"], state="normal")
                        self.canvas.itemconfig(self.pause_button_rectangles["right"], state="normal")
                        self.canvas.itemconfig(self.pause_button_rectangles["triangle"], state="hidden")
                self.canvas.itemconfig(self.pause_button_rectangles["inner"], fill=color)

        def draw_add_button(self, top_left_x, top_left_y):
                icon_color = self.note_selected_color
                self.add_button_rectangles = {}
                self.add_button_rectangles["outer"] = self.canvas.create_rectangle(top_left_x, top_left_y, top_left_x + 20, top_left_y + 20, fill="gray94")
                self.add_button_rectangles["inner"] = self.canvas.create_rectangle(top_left_x + 3, top_left_y + 3, top_left_x + 17, top_left_y + 17, fill="gray94")
                self.add_button_rectangles["square"] = self.canvas.create_rectangle(top_left_x + 6, top_left_y + 6, top_left_x + 14, top_left_y + 14, fill=icon_color)
                self.add_button_rectangles["horizontal stripe 1"] = self.canvas.create_rectangle(top_left_x + 6, top_left_y + 8, top_left_x + 15, top_left_y + 9, fill=icon_color, outline="")
                self.add_button_rectangles["horizontal stripe 2"] = self.canvas.create_rectangle(top_left_x + 6, top_left_y + 12, top_left_x + 15, top_left_y + 13, fill=icon_color, outline="")
                self.add_button_rectangles["vertical stripe 1"] = self.canvas.create_rectangle(top_left_x + 8, top_left_y + 6, top_left_x + 9, top_left_y + 15, fill=icon_color, outline="")
                self.add_button_rectangles["vertical stripe 2"] = self.canvas.create_rectangle(top_left_x + 12, top_left_y + 6, top_left_x + 13, top_left_y + 15, fill=icon_color, outline="")

        def adjust_add_button(self):
                rectangle_color = self.note_selected_color
                rectangle_state = "normal"
                if self.gui.is_adding:
                        self.set_note_and_velocity_entries(self.new_note_before_selection)
                        if self.selections["current selected row index"] is not None and self.selections["current selected beat"] is not None:
                                self.canvas.itemconfig(self.rectangles[self.selections["current selected row index"]][self.selections["current selected beat"]], fill=self.note_on_color)
                        self.selections["current selected row index"] = None
                        self.selections["current selected beat"] = None
                        self.selections["previous selected row index"] = None
                        self.selections["previous selected beat"] = None
                        rectangle_state = "hidden"
                        rectangle_color = self.note_on_color
                else: # we are going into 'selection' mode
                        self.new_note_before_selection = Note(self.new_midi_note, self.new_midi_velocity)
                self.canvas.itemconfig(self.add_button_rectangles["horizontal stripe 1"], state=rectangle_state)
                self.canvas.itemconfig(self.add_button_rectangles["horizontal stripe 2"], state=rectangle_state)
                self.canvas.itemconfig(self.add_button_rectangles["vertical stripe 1"], state=rectangle_state)
                self.canvas.itemconfig(self.add_button_rectangles["vertical stripe 2"], state=rectangle_state)
                self.canvas.itemconfig(self.add_button_rectangles["square"], fill=rectangle_color)

        def set_note_and_velocity_entries(self, note):
                self.note_entry.delete(0, tk.END)
                self.note_entry.insert(0, str(note.get_midi_note()))
                self.velocity_entry.delete(0, tk.END)
                self.velocity_entry.insert(0, str(note.get_velocity()))

        def handle_click(self, event):
                click_x = event.x
                click_y = event.y
                top_left_x = self.gui_params.get_box_top_left_x()
                row_width = self.gui_params.get_row_width()
                top_left_y = self.gui_params.get_box_top_left_y()
                row_height = self.gui_params.get_row_height()
                number_of_rows = self.dao.get_loop_params().get_number_of_rows()
                if (top_left_x <= click_x) and (click_x <= top_left_x + row_width) and (top_left_y <= click_y) and (click_y <= top_left_y + (row_height * number_of_rows)):
                        self.figure_out_clicked_rectangle(click_x, click_y)
                if self.pause_top_left_x <= click_x and click_x <= self.pause_top_left_x + 20 and self.pause_top_left_y <= click_y and click_y <= self.pause_top_left_y + 20:
                        self.dao.toggle_paused()
                        self.adjust_pause_button()
                if self.add_top_left_x <= click_x and click_x <= self.add_top_left_x + 20 and self.add_top_left_y <= click_y and click_y <= self.add_top_left_y + 20:
                        self.gui.is_adding = not self.gui.is_adding
                        self.adjust_add_button()
                if self.load_top_left_x <= click_x and click_x <= self.load_top_left_x + 20 and self.load_top_left_y <= click_y and click_y <= self.load_top_left_y + 20:
                        self.load_button_callback()
                if self.save_top_left_x <= click_x and click_x <= self.save_top_left_x + 20 and self.save_top_left_y <= click_y and click_y <= self.save_top_left_y + 20:
                        self.save_button_callback()

        def figure_out_clicked_rectangle(self, click_x, click_y):
                top_left_x = self.gui_params.get_box_top_left_x()
                row_width = self.gui_params.get_row_width()
                top_left_y = self.gui_params.get_box_top_left_y()
                row_height = self.gui_params.get_row_height()
                number_of_rows = self.dao.get_loop_params().get_number_of_rows()
                row_index = int((click_y - top_left_y) / (row_height))
                beat = int((click_x - top_left_x) / (row_width / self.dao.get_subdivision_for_row(row_index)))
                if self.gui.is_adding:
                        self.toggle_rectangle(row_index, beat)
                else: # selection logic goes here
                        self.select_rectangle(row_index, beat)

        def toggle_rectangle(self, row_index, beat):
                current_note = self.dao.get_note_at_beat_for_row(beat, row_index)
                new_color = self.note_off_color
                note = None
                if current_note is None:
                        new_color = self.note_on_color
                        note = Note(self.new_midi_note, self.new_midi_velocity)
                self.dao.set_note_at_beat_for_row(note, beat, row_index)
                self.canvas.itemconfig(self.rectangles[row_index][beat], fill=new_color)

        def select_rectangle(self, row_index, beat):
                current_note = self.dao.get_note_at_beat_for_row(beat, row_index)
                if current_note is None:
                        return
                else: 
                        self.selections["previous selected row index"] = self.selections["current selected row index"]
                        self.selections["previous selected beat"] = self.selections["current selected beat"]
                        self.selections["current selected row index"] = row_index
                        self.selections["current selected beat"] = beat
                        if self.selections["previous selected row index"] is not None and self.selections["previous selected beat"] is not None:
                                self.canvas.itemconfig(self.rectangles[self.selections["previous selected row index"]][self.selections["previous selected beat"]], fill=self.note_on_color)
                        self.canvas.itemconfig(self.rectangles[self.selections["current selected row index"]][self.selections["current selected beat"]], fill=self.note_selected_color)
                        self.set_note_and_velocity_entries(self.dao.get_note_at_beat_for_row(self.selections["current selected beat"], self.selections["current selected row index"]))

        def draw_note_entry(self, top_left_x, top_left_y):
                self.new_midi_note = 36
                self.note_entry = tk.Entry(self.gui, highlightthickness=0, font="Calibri 10", width=3)
                self.note_entry.insert('end', '36')
                self.note_entry.place(x=top_left_x, y=top_left_y + 6)
                button = tk.Button(self.gui, text="set midi note",  width=8, command=lambda: self.note_entry_callback(self.note_entry.get()), highlightbackground=self.background_color)
                button.place(x=top_left_x + 30, y=top_left_y)

        def note_entry_callback(self, param):
                if self.gui.is_adding: # we're in 'adding' mode
                        self.new_midi_note = int(param)
                else: # we're in 'selection' mode
                        self.dao.get_note_at_beat_for_row(self.selections["current selected beat"], self.selections["current selected row index"]).set_midi_note(int(param))


        def draw_velocity_entry(self, top_left_x, top_left_y):
                self.new_midi_velocity = 64
                self.velocity_entry = tk.Entry(self.gui, highlightthickness=0, font="Calibri 10", width=3)
                self.velocity_entry.insert('end', '64')
                self.velocity_entry.place(x=top_left_x, y=top_left_y + 6)
                button = tk.Button(self.gui, text="set midi velocity", width=11, command=lambda: self.velocity_entry_callback(self.velocity_entry.get()), highlightbackground=self.background_color)
                button.place(x=top_left_x + 30, y=top_left_y)

        def subdivision_entry_callback(self):
                for row_index in range(0, len(self.subdivision_entries)):
                        old_subdivision = self.dao.get_subdivision_for_row(row_index)
                        new_subdivision = int(self.subdivision_entries[row_index].get())
                        if old_subdivision != new_subdivision:
                                self.dao.set_subdivision_for_row(new_subdivision, row_index)
                                self.redraw_rectangle_row(row_index)

        def velocity_entry_callback(self, param):
                if self.gui.is_adding: # we're in 'adding' mode
                        self.new_midi_velocity = int(param)
                else: # we're in 'selection' mode
                        self.dao.get_note_at_beat_for_row(self.selections["current selected beat"], self.selections["current selected row index"]).set_velocity(int(param))

        def draw_subdivision_entries(self):
                self.subdivision_entries = []
                for index in range(0, self.dao.get_loop_params().get_number_of_rows()):
                        self.subdivision_entries.append(tk.Entry(self.gui, highlightthickness=0, font="Calibri 10", width=3))
                        self.subdivision_entries[index].insert('end', self.dao.get_subdivision_for_row(index))
                        self.subdivision_entries[index].place(x=self.gui_params.get_box_top_left_x() - 30, y=self.gui_params.get_box_top_left_y() + (index * self.gui_params.get_row_height()))
                if self.set_subdivisions_button is None:
                        self.set_subdivisions_button = tk.Button(self.gui, text="set subdivisions", width=11, command=self.subdivision_entry_callback, highlightbackground=self.background_color)
                self.set_subdivisions_button.place(x=self.gui_params.get_box_top_left_x() - 30, 
                        y=self.gui_params.get_box_top_left_y() + (self.dao.get_loop_params().get_number_of_rows() * self.gui_params.get_row_height() + 5))

        def redraw_rectangle_row(self, row_index):
                for old_rectangle in self.rectangles[row_index]:
                        self.canvas.delete(old_rectangle)
                self.rectangles[row_index].clear()
                box_top_left_x = self.gui_params.get_box_top_left_x()
                box_top_left_y = self.gui_params.get_box_top_left_y()
                row_height = self.gui_params.get_row_height()
                row_width = self.gui_params.get_row_width()
                subdivision_of_row = self.dao.get_subdivision_for_row(row_index)
                note_width = (row_width / subdivision_of_row)
                for note_index in range(0, subdivision_of_row):
                        note_top_left_x = box_top_left_x + (note_width * note_index)
                        note_top_left_y = box_top_left_y + (row_height * row_index)
                        note_bottom_left_x = note_top_left_x + note_width
                        note_bottom_left_y = note_top_left_y + row_height
                        color = self.note_off_color
                        if self.dao.get_note_at_beat_for_row(note_index, row_index) is not None:
                                color = self.note_on_color
                        self.rectangles[row_index].append(self.canvas.create_rectangle(note_top_left_x, note_top_left_y, note_bottom_left_x, note_bottom_left_y, fill=color))

        def draw_number_of_rows_entry(self, top_left_x, top_left_y):
                self.number_of_rows_entry = tk.Entry(self.gui, highlightthickness=0, font="Calibri 10", width=3)
                self.number_of_rows_entry.insert('end', str(self.dao.loop_params.get_number_of_rows()))
                self.number_of_rows_entry.place(x=top_left_x, y=top_left_y + 6)
                button = tk.Button(self.gui, text="set number of rows", width=13, command=lambda: self.set_number_of_rows_callback(self.number_of_rows_entry.get()), highlightbackground=self.background_color)
                button.place(x=top_left_x + 30, y=top_left_y)

        def set_number_of_rows_callback(self, param):
                rows_to_add = int(param) - self.dao.get_loop_params().get_number_of_rows()
                self.dao.set_number_of_rows(int(param))
                if rows_to_add > 0: # add rows case
                        for index in range(0, rows_to_add):
                                self.rectangles.append([])
                                self.redraw_rectangle_row(len(self.rectangles) - 1)
                elif rows_to_add < 0: # delete rows case 
                        for index in range(0, rows_to_add * -1):
                                for old_rectangle in self.rectangles[len(self.rectangles) - 1]:
                                        self.canvas.delete(old_rectangle)
                                del self.rectangles[len(self.rectangles) - 1]
                for entry in self.subdivision_entries: # delete then redraw the 'set subdivision' text entries and button
                        entry.destroy()
                self.subdivision_entries.clear()
                self.draw_subdivision_entries()
                self.refresh_canvas_size()

        def draw_length_in_ticks_entry(self, top_left_x, top_left_y):
                self.length_entry = tk.Entry(self.gui, highlightthickness=0, font="Calibri 10", width=5)
                self.length_entry.insert('end', str(self.dao.loop_params.get_length_in_ticks()))
                self.length_entry.place(x=top_left_x, y=top_left_y + 6)
                button = tk.Button(self.gui, text="set millisecond length", highlightthickness=0, width=14, command=lambda: self.set_length_in_ticks_callback(self.length_entry.get()), highlightbackground=self.background_color)
                button.place(x=top_left_x + 40, y=top_left_y)

        def redraw_all_rectangles(self):
                for row_index in range(0, self.dao.get_loop_params().get_number_of_rows()):
                        self.redraw_rectangle_row(row_index)

        def set_length_in_ticks_callback(self, param):
                self.dao.set_length_in_ticks(int(param))

        def load_length_in_ticks(self, new_length_in_ticks):
                self.set_length_in_ticks_callback(new_length_in_ticks)
                self.length_entry.delete(0, tk.END)
                self.length_entry.insert(0, str(new_length_in_ticks))

        def load_number_of_rows(self, new_number_of_rows):
                self.set_number_of_rows_callback(new_number_of_rows)
                self.redraw_all_rectangles()
                self.number_of_rows_entry.delete(0, tk.END)
                self.number_of_rows_entry.insert(0, str(new_number_of_rows))

        def load_file(self, file_path):
                file_contents = None
                with open(file_path, 'r') as file:
                        file_contents = file.read().split('\n')
                self.dao.reset()
                length_in_ticks = int(file_contents.pop(0).split()[1])
                number_of_rows = int(file_contents.pop(0).split()[1])
                self.load_length_in_ticks(length_in_ticks)
                self.load_number_of_rows(number_of_rows)
                for row_index in range(0, len(file_contents)):
                        row_specification = file_contents[row_index].split()
                        if len(row_specification) > 0:
                                subdivision = int(row_specification.pop(0)) # removes the first item from the list, which specifies subdivision for this row
                                self.dao.set_subdivision_for_row(subdivision, row_index)
                                for note in range(0, len(row_specification)): # the rest of the items in the row_specification list specify notes at certain beats
                                        note_specification = row_specification[note].split(',')
                                        beat = int(note_specification[0])
                                        midi_note = int(note_specification[1])
                                        midi_velocity = int(note_specification[2])
                                        self.dao.set_note_at_beat_for_row(Note(midi_note, midi_velocity), beat, row_index)
                self.set_number_of_rows_callback(number_of_rows)
                self.reset_selections()
                self.redraw_all_rectangles()
                self.refresh_canvas_size()

        def reset_selections(self):
                self.selections["previous selected row index"] = None
                self.selections["previous selected beat"] = None
                self.selections["current selected row index"] = None
                self.selections["current selected beat"] = None

        def load_button_callback(self):
                self.canvas.itemconfig(self.load_button_rectangles["inner"], fill="gray64")
                self.gui.update()
                file_path = filedialog.askopenfilename(initialdir = "/",title = "Load file", filetypes = (("txt files","*.txt"), ("all files","*.*")))
                if file_path != "":
                        self.load_file(file_path)
                self.canvas.itemconfig(self.load_button_rectangles["inner"], fill="gray94")

        def draw_load_button(self, top_left_x, top_left_y):
                icon_color_dark = "black"
                icon_color_light = "khaki1"
                self.load_button_rectangles = {}
                self.load_button_rectangles["outer"] = self.canvas.create_rectangle(top_left_x, top_left_y, top_left_x + 20, top_left_y + 20, fill="gray94")
                self.load_button_rectangles["inner"] = self.canvas.create_rectangle(top_left_x + 3, top_left_y + 3, top_left_x + 17, top_left_y + 17, fill="gray94")
                self.load_button_rectangles["back"] = self.canvas.create_rectangle(top_left_x + 6, top_left_y + 7, top_left_x + 9, top_left_y + 14, fill=icon_color_dark)
                self.load_button_rectangles["front"] = self.canvas.create_rectangle(top_left_x + 7, top_left_y + 8, top_left_x + 14, top_left_y + 14, fill=icon_color_light)
                self.load_button_rectangles["middle"] = self.canvas.create_rectangle(top_left_x + 7, top_left_y + 9, top_left_x + 7, top_left_y + 13, fill=icon_color_light, outline=icon_color_light)

        def save_button_callback(self):
                self.canvas.itemconfig(self.save_button_rectangles["inner"], fill="gray64")
                self.gui.update()
                file_path =  filedialog.asksaveasfilename(initialdir = "/", initialfile = "Untitled", defaultextension="*.txt", title = "Save file", filetypes = (("txt files","*.txt"), ("all files","*.*")))
                if file_path != "":
                        self.save_file(file_path)
                self.canvas.itemconfig(self.save_button_rectangles["inner"], fill="gray94")

        def save_file(self, file_path):
                with open(file_path, 'w') as file:
                        loop_params = self.dao.get_loop_params()
                        length_in_ticks = loop_params.get_length_in_ticks()
                        number_of_rows = loop_params.get_number_of_rows()
                        file.write("length_in_milliseconds: " + str(length_in_ticks) + "\n")
                        file.write("number_of_rows: " + str(number_of_rows) + "\n")
                        for row_index in range(0, number_of_rows):
                                subdivision = self.dao.get_subdivision_for_row(row_index)
                                row_specification_list = []
                                row_specification_list.append(str(subdivision))
                                for beat in range(0, subdivision):
                                        note = self.dao.get_note_at_beat_for_row(beat, row_index) 
                                        if note is not None:
                                                midi_note = note.get_midi_note()
                                                midi_velocity = note.get_velocity()
                                                note_specification = ",".join([str(beat), str(midi_note), str(midi_velocity)])
                                                row_specification_list.append(note_specification)
                                row_specification_list.append("\n")
                                row_specification = " ".join(row_specification_list)
                                file.write(row_specification)

        def draw_save_button(self, top_left_x, top_left_y):
                self.save_button_rectangles = {}
                self.save_button_rectangles["outer"] = self.canvas.create_rectangle(top_left_x, top_left_y, top_left_x + 20, top_left_y + 20, fill="gray94")
                self.save_button_rectangles["inner"] = self.canvas.create_rectangle(top_left_x + 3, top_left_y + 3, top_left_x + 17, top_left_y + 17, fill="gray94")
                self.save_button_rectangles["back"] = self.canvas.create_rectangle(top_left_x + 6, top_left_y + 6, top_left_x + 14, top_left_y + 14, fill="blue")
                self.save_button_rectangles["slider"] = self.canvas.create_rectangle(top_left_x + 10, top_left_y + 7, top_left_x + 13, top_left_y + 9, fill="gray84", outline="")
                self.save_button_rectangles["paper"] = self.canvas.create_rectangle(top_left_x + 8, top_left_y + 11, top_left_x + 13, top_left_y + 14, fill="white", outline="")

        def on_close(self):
            self.gui.destroy()
            self.gui_status.exit()
            sys.exit()

        def refresh_canvas_size(self):
            self.canvas.config(width=self.gui_params.get_row_width() + 125, height=self.dao.get_loop_params().get_number_of_rows() * self.gui_params.get_row_height() + 115)
            self.canvas.pack()

        def start_gui(self):
                self.gui = tk.Tk()
                self.gui.resizable(False, False)
                self.background_color = "white"
                self.note_on_color = "pale green"
                self.note_off_color = "SlateGray1"
                self.note_selected_color = "#c9ffc9"
                self.gui_params = GUIParams(box_top_left_x = 80, box_top_left_y = 70, row_height = 20, row_width = 450)
                self.canvas = tk.Canvas(self.gui, width=1, height=1, background=self.background_color, highlightbackground=self.background_color)
                self.refresh_canvas_size()
                self.initialize_rectangles()
                self.canvas.bind("<Button-1>", self.handle_click)
                self.draw_note_entry(50, 3)
                self.draw_velocity_entry(50, 30)
                self.draw_subdivision_entries()
                self.draw_number_of_rows_entry(240, 3)
                self.draw_length_in_ticks_entry(240, 30)
                self.pause_top_left_x = 14
                self.pause_top_left_y = 13
                self.draw_pause_button(self.pause_top_left_x, self.pause_top_left_y)
                self.adjust_pause_button()
                self.new_note_before_selection = Note(self.new_midi_note, self.new_midi_velocity)
                self.selections = {}
                self.reset_selections()
                self.add_top_left_x = 14
                self.add_top_left_y = 38
                self.gui.is_adding = True
                self.draw_add_button(self.add_top_left_x, self.add_top_left_y)
                self.adjust_add_button()
                self.load_top_left_x = 14
                self.load_top_left_y = 88
                self.draw_load_button(self.load_top_left_x, self.load_top_left_y)
                self.save_top_left_x = 14
                self.save_top_left_y = 63
                self.draw_save_button(self.save_top_left_x, self.save_top_left_y)
                self.canvas.pack()
                self.gui.title("Polyrhythmic Drum Machine")
                self.gui.protocol("WM_DELETE_WINDOW", self.on_close)
                self.gui.mainloop()
