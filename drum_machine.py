import mido
from time import perf_counter_ns
import tkinter as tk
import threading

class DrumMachineThread(threading.Thread): # this thread runs the drum machine timer loop

        def __init__(self, dao):
                self.dao = dao
                threading.Thread.__init__(self)
                self.start()

        def run(self):
                self.set_default_loop()
                self.run_loop()

        def set_default_loop(self):
                self.dao.set_subdivision_for_row(4, 0)
                self.dao.set_subdivision_for_row(8, 1)
                self.dao.set_subdivision_for_row(8, 2)
                self.dao.set_subdivision_for_row(12, 3)
                self.dao.set_subdivision_for_row(16, 4)
                self.dao.set_subdivision_for_row(20, 5)
                self.dao.set_subdivision_for_row(28, 6)
                self.dao.set_subdivision_for_row(36, 7)
                self.dao.set_subdivision_for_row(28, 8)
                self.dao.set_subdivision_for_row(56, 9)

        def run_loop(self):
                outport = mido.open_output('IAC Driver Bus 1')
                millisecond = 1_000_000 # default tick length is 1 millisecond. timer measures nanoseconds. 
                startTime = perf_counter_ns()
                while(True):
                        if(not self.dao.is_paused() and perf_counter_ns() - startTime >= millisecond):
                                self.play_notes(outport, self.dao.get_all_notes_at_current_tick())
                                self.dao.increment_current_tick()
                                startTime = perf_counter_ns()

        def play_note(self, outport, midi_note):
                if midi_note is None:
                        return
                note_on = mido.Message('note_on', note=midi_note.get_midi_note(), velocity=midi_note.get_velocity())
                note_off = mido.Message('note_off', note=midi_note.get_midi_note(), velocity=midi_note.get_velocity())
                outport.send(note_on)
                outport.send(note_off)

        def play_notes(self, outport, midi_notes):
                for midi_note in midi_notes:
                        self.play_note(outport, midi_note)

class Note:

        def __init__(self, midi_note, velocity=64):
                self.midi_note = midi_note
                self.velocity = velocity;

        def get_midi_note(self):
                return self.midi_note

        def get_velocity(self):
                return self.velocity

        def copy(self):
                return Note(self.midi_note, self.velocity)

class LoopParams:

        def __init__(self, length_in_ticks, number_of_rows):
                self.length_in_ticks = length_in_ticks
                self.number_of_rows = number_of_rows

        def get_length_in_ticks(self):
                return self.length_in_ticks

        def get_number_of_rows(self):
                return self.number_of_rows

        def set_length_in_ticks(self, new_length_in_ticks):
                self.length_in_ticks = new_length_in_ticks

        def set_number_of_rows(self, new_number_of_rows):
                self.number_of_rows = new_number_of_rows

class Row:

        def __init__(self, subdivision, loop_params):
                self.subdivision = subdivision
                self.loop_params = loop_params
                self.initialize_notes_array()

        def initialize_notes_array(self):
                self.notes = [None] * self.loop_params.get_length_in_ticks()

        def get_subdivision(self):
                return self.subdivision

        def get_loop_params(self):
                return self.loop_params

        def set_subdivision(self, new_subdivision): # just resets the notes array. more complex behavior can be implemented within the loop class.
                self.initialize_notes_array()
                self.subdivision = new_subdivision

        def set_length_in_ticks(self, new_length_in_ticks): # just resets the notes array. more complex behavior can be implemented within the loop class.
                self.loop_params.set_length_in_ticks(new_length_in_ticks)
                self.initialize_notes_array()

        def get_copies_of_notes_at_all_beats(self):
                notes_at_all_beats = []
                for beat in range(0, self.subdivision):
                        note_at_current_beat = self.get_note_at_beat(beat)
                        notes_at_all_beats.append(note_at_current_beat.copy() if note_at_current_beat is not None else None)
                return notes_at_all_beats

        def get_note_at_tick(self, tick):
                return self.notes[tick]

        def set_note_at_tick(self, note, tick):
                self.notes[tick] = note

        def set_note_at_beat(self, note, beat):
                tick = self.get_tick_of_beat(beat)
                self.set_note_at_tick(note, tick)

        def get_note_at_beat(self, beat):
                tick = self.get_tick_of_beat(beat)
                return self.get_note_at_tick(tick)

        def get_beat_at_tick(self, tick): # figure out what beat a particular tick is a part of, e.g. "tick 312 falls within beat 3"
                for index in range(0, self.subdivision):
                        if (index + 1 == self.subdivision) or (tick < self.get_tick_of_beat(index + 1)):
                                return index
                return None

        def get_tick_of_beat(self, beat):
                loop_length = self.loop_params.get_length_in_ticks()
                return int((loop_length * beat) / self.subdivision)

class Loop:

        def __init__(self, loop_params):
                self.loop_params = loop_params
                self.initialize_rows_array()
                self.initialize_all_notes_array()

        def get_loop_params(self):
                return self.loop_params

        def set_note_at_tick_for_row(self, note, tick, row_index):
                self.rows[row_index].set_note_at_tick(note, tick)
                self.update_all_notes_array_for_tick_for_row(note, tick, row_index)

        def set_note_at_beat_for_row(self, note, beat, row_index):
                tick = self.get_tick_of_beat_for_row(beat, row_index)
                self.set_note_at_tick_for_row(note, tick, row_index)

        def get_note_at_tick_for_row(self, tick, row_index):
                return self.rows[row_index].get_note_at_tick(tick)

        def get_note_at_beat_for_row(self, beat, row_index):
                return self.rows[row_index].get_note_at_beat(beat)

        def set_subdivision_for_row(self, new_subdivision, row_index):
                row = self.rows[row_index]
                notes_at_all_beats = row.get_copies_of_notes_at_all_beats() # store all notes from each beat of old subdivision
                row.set_subdivision(new_subdivision) # change the subdivision of the row, resetting its notes
                for beat in range(0, new_subdivision): # add all the beats back (to the degree that that is possible with the new subdivision)
                        if beat >= len(notes_at_all_beats):
                                break
                        self.set_note_at_beat_for_row(notes_at_all_beats[beat], beat, row_index)
                self.update_all_notes_array_for_row(row_index)

        def get_subdivision_for_row(self, row_index):
                return self.rows[row_index].get_subdivision()

        def get_tick_of_beat_for_row(self, beat, row_index):
                return self.rows[row_index].get_tick_of_beat(beat)

        def initialize_rows_array(self):
                self.rows = []
                for row in range(0, self.loop_params.get_number_of_rows()):
                        self.rows.append(Row(4, self.loop_params))

        def initialize_all_notes_array(self):
                self.all_notes = [] # format of the all_notes array: [ tick 0: [row 0, row 1, row 2, row 3], tick 1: [row 0, row 1, row 2, row 3], etc.]
                for tick in range(0, self.loop_params.get_length_in_ticks()):
                        self.all_notes.append([None] * self.loop_params.get_number_of_rows())

        def get_all_notes_at_tick(self, tick):
                return self.all_notes[tick] # all_notes: array containing all notes for each tick. gets updated on 'set' operations. cuts down the number of array accesses during time-sensistive playback.

        def update_all_notes_array_for_tick_for_row(self, note, tick, row_index):
            array_for_tick = self.all_notes[tick] # update the all_notes_array one tick at a time, rather than reinitializing the entire array
            array_for_tick[row_index] = note

        def update_all_notes_array_for_beat_for_row(self, note, beat, row_index):
            tick = self.get_tick_of_beat_for_row(beat, row_index) # update the all_notes_array one beat at a time, rather than reinitializing the entire array
            self.update_all_notes_array_for_tick_for_row(note, tick, row_index)

        def update_all_notes_array_for_row(self, index_of_row):
                for tick in range(0, self.loop_params.get_length_in_ticks()):
                        self.all_notes[tick][index_of_row] = self.get_note_at_tick_for_row(tick, index_of_row)

        def update_all_notes_array_length_in_ticks(self):
                ticks_to_add = self.loop_params.get_length_in_ticks() - len(self.all_notes)
                if ticks_to_add > 0: # add ticks
                        for index in range(0, ticks_to_add):
                                self.all_notes.append([None] * self.loop_params.get_number_of_rows())
                if ticks_to_add < 0: # delete ticks
                        for index in range(0, ticks_to_add * -1):
                                del self.all_notes[-1]

        def set_number_of_rows(self, new_number_of_rows):
                rows_to_add = new_number_of_rows - self.loop_params.get_number_of_rows()
                if rows_to_add < 0: # delete rows case
                        for index in range(0, rows_to_add * -1):
                                del self.rows[-1]
                                for tick_array in self.all_notes:
                                        del tick_array[-1]
                elif rows_to_add > 0: # add rows case
                        for index in range(0, rows_to_add):
                                self.rows.append(Row(4, self.loop_params))
                                for tick_array in self.all_notes:
                                        tick_array.append(None)
                self.loop_params.set_number_of_rows(new_number_of_rows)

        def set_length_in_ticks(self, new_length_in_ticks):
                notes_at_all_beats = [] # get copies of all notes for all beats
                for row in self.rows:
                        notes_at_all_beats.append(row.get_copies_of_notes_at_all_beats())
                for row in self.rows: # set the new length in ticks for every row one at a time
                        row.set_length_in_ticks(new_length_in_ticks)
                self.loop_params.set_length_in_ticks(new_length_in_ticks)
                self.update_all_notes_array_length_in_ticks()
                for row_index in range(0, len(self.rows)): # add all the notes back onto each row
                        for beat in range(0, len(notes_at_all_beats[row_index])):
                                self.rows[row_index].set_note_at_beat(notes_at_all_beats[row_index][beat], beat)
                        self.update_all_notes_array_for_row(row_index)

class DrumMachineDAO:

        def __init__(self, loop_params):
                self.loop_params = loop_params
                self.current_tick = 0
                self.loop = Loop(loop_params)
                self.paused = False

        def is_paused(self):
                return self.paused

        def toggle_paused(self):
                self.paused = not self.paused

        def get_loop_params(self):
                return self.loop_params

        def set_current_tick(self, tick):
                self.current_tick = tick

        def increment_current_tick(self):
                updated_tick = self.current_tick + 1
                self.current_tick = updated_tick if updated_tick < self.loop_params.get_length_in_ticks() else 0

        def get_all_notes_at_current_tick(self):
                return self.all_notes[self.current_tick]

        def set_note_at_beat_for_row(self, note, beat, row_index):
                self.loop.set_note_at_beat_for_row(note, beat, row_index)

        def get_note_at_beat_for_row(self, beat, row_index):
                return self.loop.get_note_at_beat_for_row(beat, row_index)

        def set_subdivision_for_row(self, subdivision, row_index):
                self.loop.set_subdivision_for_row(subdivision, row_index)

        def get_subdivision_for_row(self, row_index):
                return self.loop.get_subdivision_for_row(row_index)

        def get_all_notes_at_current_tick(self):
                return self.loop.get_all_notes_at_tick(self.current_tick)

        def get_tick_of_beat_for_row(self, beat, row_index):
                return self.loop.get_tick_of_beat_for_row(beat, row_index)

        def set_number_of_rows(self, new_number_of_rows):
                self.loop.set_number_of_rows(new_number_of_rows)

        def set_length_in_ticks(self, new_length_in_ticks):
                self.current_tick = 0
                loop_was_paused = self.paused
                if loop_was_paused == False:
                        self.paused = True
                self.loop.set_length_in_ticks(new_length_in_ticks)
                self.loop_params.set_length_in_ticks(new_length_in_ticks)
                if loop_was_paused == False:
                        self.paused = False

class GUIParams:
        def __init__(self, box_top_left_x, box_top_left_y, row_height, row_width):
                self.box_top_left_x = box_top_left_x
                self.box_top_left_y = box_top_left_y
                self.row_height = row_height
                self.row_width = row_width

        def get_box_top_left_x(self):
                return self.box_top_left_x

        def get_box_top_left_y(self):
                return self.box_top_left_y

        def get_row_height(self):
                return self.row_height

        def get_row_width(self):
                return self.row_width

class GUI:
        def __init__(self, dao):
                self.dao = dao
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

        def adjust_pause_button(self):
                color = "gray94"
                if self.dao.is_paused():
                        color = "gray64"
                self.canvas.itemconfig(self.pause_button_rectangles["inner"], fill=color)

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

        def figure_out_clicked_rectangle(self, click_x, click_y):
                top_left_x = self.gui_params.get_box_top_left_x()
                row_width = self.gui_params.get_row_width()
                top_left_y = self.gui_params.get_box_top_left_y()
                row_height = self.gui_params.get_row_height()
                number_of_rows = self.dao.get_loop_params().get_number_of_rows()
                row_index = int((click_y - top_left_y) / (row_height))
                beat = int((click_x - top_left_x) / (row_width / self.dao.get_subdivision_for_row(row_index)))
                self.toggle_rectangle(row_index, beat)

        def toggle_rectangle(self, row_index, beat):
                current_note = self.dao.get_note_at_beat_for_row(beat, row_index)
                new_color = self.note_off_color
                note = None
                if current_note is None:
                        new_color = self.note_on_color
                        note = Note(self.new_midi_note, self.new_midi_velocity)
                self.dao.set_note_at_beat_for_row(note, beat, row_index)
                self.canvas.itemconfig(self.rectangles[row_index][beat], fill=new_color)

        def draw_note_entry(self, top_left_x, top_left_y):
                self.new_midi_note = 36
                note_entry = tk.Entry(self.gui, highlightthickness=0, font="Calibri 10", width=3)
                note_entry.insert('end', '36')
                note_entry.place(x=top_left_x, y=top_left_y + 6)
                button = tk.Button(self.gui, text="set midi note",  width=8, command=lambda: self.note_entry_callback(note_entry.get()), highlightbackground=self.background_color)
                button.place(x=top_left_x + 30, y=top_left_y)

        def note_entry_callback(self, param):
                self.new_midi_note = int(param)

        def draw_velocity_entry(self, top_left_x, top_left_y):
                self.new_midi_velocity = 64
                velocity_entry = tk.Entry(self.gui, highlightthickness=0, font="Calibri 10", width=3)
                velocity_entry.insert('end', '64')
                velocity_entry.place(x=top_left_x, y=top_left_y + 6)
                button = tk.Button(self.gui, text="set midi velocity", width=11, command=lambda: self.velocity_entry_callback(velocity_entry.get()), highlightbackground=self.background_color)
                button.place(x=top_left_x + 30, y=top_left_y)

        def subdivision_entry_callback(self):
                for row_index in range(0, len(self.subdivision_entries)):
                        old_subdivision = self.dao.get_subdivision_for_row(row_index)
                        new_subdivision = int(self.subdivision_entries[row_index].get())
                        if old_subdivision != new_subdivision:
                                self.dao.set_subdivision_for_row(new_subdivision, row_index)
                                self.redraw_rectangle_row(row_index)

        def velocity_entry_callback(self, param):
                self.new_midi_velocity = int(param)

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
                number_of_rows_entry = tk.Entry(self.gui, highlightthickness=0, font="Calibri 10", width=3)
                number_of_rows_entry.insert('end', str(self.dao.loop_params.get_number_of_rows()))
                number_of_rows_entry.place(x=top_left_x, y=top_left_y + 6)
                button = tk.Button(self.gui, text="set number of rows", width=13, command=lambda: self.set_number_of_rows_callback(number_of_rows_entry.get()), highlightbackground=self.background_color)
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

        def draw_length_in_ticks_entry(self, top_left_x, top_left_y):
                length_entry = tk.Entry(self.gui, highlightthickness=0, font="Calibri 10", width=5)
                length_entry.insert('end', str(self.dao.loop_params.get_length_in_ticks()))
                length_entry.place(x=top_left_x, y=top_left_y + 6)
                button = tk.Button(self.gui, text="set millisecond length", highlightthickness=0, width=14, command=lambda: self.set_length_in_ticks_callback(length_entry.get()), highlightbackground=self.background_color)
                button.place(x=top_left_x + 40, y=top_left_y)

        def set_length_in_ticks_callback(self, param):
                self.dao.set_length_in_ticks(int(param))

        def start_gui(self):
                self.gui = tk.Tk()
                self.gui.resizable(False, False)
                self.background_color = "white"
                self.note_on_color = "pale green"
                self.note_off_color = "SlateGray1"
                self.canvas = tk.Canvas(self.gui, width=600, height=500, background=self.background_color, highlightbackground=self.background_color)
                self.gui_params = GUIParams(box_top_left_x = 80, box_top_left_y = 70, row_height = 20, row_width = 450)
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
                self.canvas.pack()
                self.gui.title("Polyrhythmic Drum Machine")
                self.gui.protocol("WM_DELETE_WINDOW", self.gui.destroy)
                self.gui.mainloop()

def main():
        loop_params = LoopParams(2_500, 19)
        dao = DrumMachineDAO(loop_params)
        drum_thread = DrumMachineThread(dao)
        gui = GUI(dao)

main()