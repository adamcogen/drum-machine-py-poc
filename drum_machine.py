import mido
from time import perf_counter_ns
import tkinter as tk
import threading

# this thread runs the drum machine timer loop
class DrumMachineThread(threading.Thread):

    def __init__(self, dao):
        self.dao = dao
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        set_loop(self.dao)
        run_loop(self.dao)

def get_tick_of_beat(subdivision, beat, loop_length_in_ticks):
        return int((loop_length_in_ticks * beat) / subdivision)

# def get_beat_of_tick(subdivision, tick, loop_length_in_ticks):
#         return int((subdivision * tick) / loop_length_in_ticks)

def play_note(outport, midi_note):
        if midi_note is None:
                return
        note_on = mido.Message('note_on', note=midi_note.get_midi_note(), velocity=midi_note.get_velocity())
        note_off = mido.Message('note_off', note=midi_note.get_midi_note(), velocity=midi_note.get_velocity())
        outport.send(note_on)
        outport.send(note_off)

def play_notes(outport, midi_notes):
        for midi_note in midi_notes:
                play_note(outport, midi_note)

class Note:

        def __init__(self, midi_note, velocity=64):
                self.midi_note = midi_note
                self.velocity = velocity;

        def get_midi_note(self):
                return self.midi_note

        def set_midi_note(self, midi_note):
                self.midi_note = midi_note

        def get_velocity(self):
                return self.velocity

        def set_velocity(self, velocity):
                self.velocity = velocity

class LoopParams:

        def __init__(self, length_in_ticks, number_of_rows):
                self.length_in_ticks = length_in_ticks
                self.number_of_rows = number_of_rows

        def get_length_in_ticks(self):
                return self.length_in_ticks

        def set_length_in_ticks(self, new_length_in_ticks):
                self.length_in_ticks = new_length_in_ticks

        def get_number_of_rows(self):
                return self.number_of_rows

        def set_number_of_rows(self, new_number_of_rows):
                self.number_of_rows = new_number_of_rows

class Row:

        def __init__(self, subdivision, loop_params):
                self.subdivision = subdivision
                self.loop_params = loop_params
                self.notes = [None] * loop_params.get_length_in_ticks()
                self.tick_for_beat = []
                self.initialize_beats_for_ticks()

        def initialize_beats_for_ticks(self):
                self.tick_for_beat = []
                for beat in range(0, self.subdivision):
                        tick_of_beat = get_tick_of_beat(self.subdivision, beat, self.loop_params.get_length_in_ticks())
                        self.tick_for_beat.append(tick_of_beat)

        def get_subdivision(self):
                return self.subdivision

        def get_loop_params(self):
                return self.loop_params

        def set_subdivision(self, new_subdivision):
                self.subdivision = new_subdivision
                self.initialize_beats_for_ticks()

        def set_loop_params(self, new_loop_params):
                self.loop_params = new_loop_params

        def get_note_at_tick(self, tick):
                return self.notes[tick]

        def set_note_at_tick(self, note, tick):
                if (tick <= self.loop_params.get_length_in_ticks()):
                        self.notes[tick] = note
                else:
                        print("can't add note to row, tick is greater than or equal to length_in_ticks")

        def set_note_at_beat(self, note, beat):
                tick_of_beat = get_tick_of_beat(self.subdivision, beat, self.loop_params.get_length_in_ticks())
                self.set_note_at_tick(note, tick_of_beat)

        def get_note_at_beat(self, beat):
                tick_of_beat = get_tick_of_beat(self.subdivision, beat, self.loop_params.get_length_in_ticks())
                return self.get_note_at_tick(tick_of_beat)

        def get_beat_at_tick(self, tick):
                for index in range(0, self.subdivision):
                        if (index + 1 == self.subdivision) or (tick < self.tick_for_beat[index + 1]):
                                return index
                return None

class Loop:

        def __init__(self, loop_params):
                self.loop_params = loop_params
                self.rows = []
                for row in range(0, loop_params.get_number_of_rows()):
                        self.rows.append(Row(4, self.loop_params))

        def get_loop_params(self):
                return self.loop_params

        def get_rows(self):
                return self.rows

        def set_note_at_tick_for_row(self, note, tick, row):
                self.rows[row].set_note_at_tick(note, tick)

        def set_note_at_beat_for_row(self, note, beat, row):
                self.rows[row].set_note_at_beat(note, beat)

        def set_subdivision_for_row(self, subdivision, row):
                self.rows[row].set_subdivision(subdivision)

        def get_subdivision_for_row(self, row):
                return self.rows[row].get_subdivision()

class DrumMachineDAO:

        def __init__(self, loop_params):
                self.loop_params = loop_params
                self.current_tick = 0
                self.loop = Loop(loop_params)
                self.all_notes = []
                self.paused = False;

        def is_paused(self):
                return self.paused

        def toggle_paused(self):
                # print("pause style")
                self.paused = not self.paused

        def get_loop_params(self):
                return self.loop_params

        def set_current_tick(self, tick):
                self.current_tick = tick

        def increment_current_tick(self):
                updated_tick = self.current_tick + 1
                self.current_tick = updated_tick if updated_tick < self.loop_params.get_length_in_ticks() else 0

        def get_all_notes_at_current_tick(self):
                return get_all_notes_at_tick(self.current_tick)

        def set_note_at_tick_for_row(self, note, tick, index_of_row):
                self.loop.get_rows()[index_of_row].set_note_at_tick(note, tick)

        def set_note_at_beat_for_row(self, note, beat, index_of_row):
                self.loop.get_rows()[index_of_row].set_note_at_beat(note, beat)

        def get_note_at_beat_for_row(self, beat, index_of_row):
                return self.loop.get_rows()[index_of_row].get_note_at_beat(beat)

        def get_current_tick(self):
                return self.current_tick

        def set_subdivision_for_row(self, subdivision, index_of_row):
                self.loop.get_rows()[index_of_row].set_subdivision(subdivision)

        def get_subdivision_for_row(self, index_of_row):
            return self.loop.get_subdivision_for_row(index_of_row)

        def update_all_notes_array(self):
                self.all_notes = []
                # format of the all_notes array:
                # [ tick 0: [row 0, row 1, row 2, row 3], tick 1: [row 0, row 1, row 2, row 3], etc.]
                for tick in range(0, self.loop_params.get_length_in_ticks()):
                        all_notes_for_tick = []
                        for row in self.loop.get_rows():
                                all_notes_for_tick.append(row.get_note_at_tick(tick))
                        self.all_notes.append(all_notes_for_tick)
                        all_notes_for_tick = []

        def update_all_notes_array_for_tick_for_row(self, note, tick, row_index):
            # update the all_notes_array one tick at a time, rather than reinitializing the entire array
            array_for_tick = self.all_notes[tick]
            array_for_tick[row_index] = note

        def update_all_notes_array_for_beat_for_row(self, note, beat, row_index):
            # update the all_notes_array one tick at a time, rather than reinitializing the entire array
            tick_of_beat = get_tick_of_beat(self.loop.get_rows()[row_index].get_subdivision(), beat, self.loop_params.get_length_in_ticks())
            array_for_tick = self.all_notes[tick_of_beat]
            array_for_tick[row_index] = note

        def get_all_notes_at_current_tick(self):
                return self.all_notes[self.current_tick]

        def get_loop(self):
                return self.loop

def run_loop(dao):
        # print("run loop style")
        outport = mido.open_output('IAC Driver Bus 1')
        millisecond = 1_000_000
        startTime = perf_counter_ns()
        while(True):
                if(not dao.is_paused() and perf_counter_ns() - startTime >= millisecond):
                        play_notes(outport, dao.get_all_notes_at_current_tick())
                        dao.increment_current_tick()
                        startTime = perf_counter_ns()

def set_loop(dao):
        bass_drum = Note(36)
        snare = Note(37)
        clave = Note(43)

        dao.set_subdivision_for_row(4, 0)
        dao.set_subdivision_for_row(8, 1)
        dao.set_subdivision_for_row(8, 2)
        dao.set_subdivision_for_row(12, 3)
        dao.set_subdivision_for_row(16, 4)
        dao.set_subdivision_for_row(20, 5)
        dao.set_subdivision_for_row(28, 6)
        dao.set_subdivision_for_row(36, 7)
        dao.set_subdivision_for_row(28, 8)

        dao.update_all_notes_array()

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
        self.start_gui()

    def initialize_rectangles(self):
        box_top_left_x = self.gui_params.get_box_top_left_x()
        box_top_left_y = self.gui_params.get_box_top_left_y()
        row_height = self.gui_params.get_row_height()
        row_width = self.gui_params.get_row_width()
        self.rectangles = [[] for i in range(0, self.dao.get_loop_params().get_number_of_rows())]
        for row_index in range(0, self.dao.get_loop_params().get_number_of_rows()):
                subdivision_of_row = self.dao.get_loop().get_rows()[row_index].get_subdivision()
                note_width = (row_width / subdivision_of_row)
                for note_index in range(0, subdivision_of_row):
                        note_top_left_x = box_top_left_x + (note_width * note_index)
                        note_top_left_y = box_top_left_y + (row_height * row_index)
                        note_bottom_left_x = note_top_left_x + note_width
                        note_bottom_left_y = note_top_left_y + row_height
                        color = "SlateGray1"
                        if self.dao.get_note_at_beat_for_row(note_index, row_index) is not None:
                                color = "pale green"
                        self.rectangles[row_index].append(self.canvas.create_rectangle(note_top_left_x, note_top_left_y, note_bottom_left_x, note_bottom_left_y, fill=color))

    def draw_pause_button(self, top_left_x, top_left_y):
        self.pause_button_rectangles = {}
        self.pause_button_rectangles["outer"] = self.canvas.create_rectangle(10, 10, 30, 30, fill="gray94")
        self.pause_button_rectangles["inner"] = self.canvas.create_rectangle(13, 13, 27, 27, fill="gray94")
        self.pause_button_rectangles["left"] = self.canvas.create_rectangle(17, 17, 19, 23, fill="indian red")
        self.pause_button_rectangles["right"] = self.canvas.create_rectangle(21, 17, 23, 23, fill="indian red")

    def adjust_pause_button(self):
        color = "gray94"
        if self.dao.is_paused():
            color = "gray64"
        self.canvas.itemconfig(self.pause_button_rectangles["inner"], fill=color)

    def toggle_rectangle(self, row_index, beat):
        # we know a rectangle was clicked, and we know which one.
        # now we need to handle clicking it. that means updating the dao,
        # and updating the GUI. we can save time by not redrawing all
        # rectangles, just changing the color of the one that was clicked. 
        # figure out: is there a note on the beat we clicked? 
        current_note = self.dao.get_note_at_beat_for_row(beat, row_index)
        # if yes, set rectangle to no-note color, and get rid of the note in the dao.
        new_color = "SlateGray1"
        note = None
        if current_note is None:
            new_color = "pale green"
            note = Note(self.new_midi_note)
        # if no, set the rectangle to yes-note color, and add a note to the dao 
        # (any random note will do for now)
        self.dao.set_note_at_beat_for_row(note, beat, row_index)
        self.canvas.itemconfig(self.rectangles[row_index][beat], fill=new_color)
        self.dao.update_all_notes_array_for_beat_for_row(note, beat, row_index)

    def click_rectangle(self, event):
        # print("rectangle clicked at", event.x, event.y)
        # figure out exactly which rectangle was clicked based on x and y cordinates of click
        x = event.x
        y = event.y
        top_left_x = self.gui_params.get_box_top_left_x()
        row_width = self.gui_params.get_row_width()
        top_left_y = self.gui_params.get_box_top_left_y()
        row_height = self.gui_params.get_row_height()
        number_of_rows = self.dao.get_loop_params().get_number_of_rows()
        row_index = int((y - top_left_y) / (row_height))
        beat = int((x - top_left_x) / (row_width / self.dao.get_subdivision_for_row(row_index)))
        # print("row: " + str(row_index) + ". beat: " + str(beat) + ".")
        self.toggle_rectangle(row_index, beat)

    def handle_click(self, event):
        # print("window clicked at", event.x, event.y)
        x = event.x
        y = event.y
        # to do:
        # figure out if a rectangle was clicked
        top_left_x = self.gui_params.get_box_top_left_x()
        row_width = self.gui_params.get_row_width()
        top_left_y = self.gui_params.get_box_top_left_y()
        row_height = self.gui_params.get_row_height()
        number_of_rows = self.dao.get_loop_params().get_number_of_rows()
        if (top_left_x <= x) and (x <= top_left_x + row_width) and (top_left_y <= y) and (y <= top_left_y + (row_height * number_of_rows)):
            self.click_rectangle(event)
        # if a rectangle was clicked, call "click_rectangle" and pass in the click event info 
        # (we specifically want x and y coordinates of the click event)
        if 10 <= x and x <= 30 and 10 <= y and y <= 30:
            # print("toggling pause")
            self.dao.toggle_paused()
            self.adjust_pause_button()

    def note_entry_callback(self, param):
        self.new_midi_note = int(param)

    def draw_note_entry(self):
        self.new_midi_note = 36
        e = tk.Entry(self.gui, font="Calibri 10", width=3)
        e.insert('end', '36')
        e.place(x=80, y=5)
        e.focus_set()
        b = tk.Button(self.gui, text="set midi note", width=10, command=lambda: self.note_entry_callback(e.get()))
        b.place(x=110, y=3)

    def subdivision_entry_callback(self):
        for index in range(0, len(self.subdivision_entries)):
            self.dao.set_subdivision_for_row(int(self.subdivision_entries[index].get()), index)
        # what should happen if a row's subdivision has changed? beats shouldn't change from note-on to note-off.
        # instead, beats should just be added or subtracted from the end of the bar without changing whether any are active.
        # that's a little tricky with the current setup so i'm gonna have to take some time to think about how best to do that.

    def draw_subdivision_entries(self):
        self.subdivision_entries = []
        for index in range(0, self.dao.get_loop_params().get_number_of_rows()):
            self.subdivision_entries.append(tk.Entry(self.gui, font="Calibri 10", width=3))
            self.subdivision_entries[index].insert('end', self.dao.get_subdivision_for_row(index))
            self.subdivision_entries[index].place(x=self.gui_params.get_box_top_left_x() - 30, y=self.gui_params.get_box_top_left_y() + (index * self.gui_params.get_row_height()))
        b = tk.Button(self.gui, text="set subdivisions", width=11, command=self.subdivision_entry_callback)
        b.place(x=self.gui_params.get_box_top_left_x() - 30, y=self.gui_params.get_box_top_left_y() + (self.dao.get_loop_params().get_number_of_rows() * self.gui_params.get_row_height() + 5))

    def start_gui(self):
        self.gui = tk.Tk()
        self.gui.resizable(False, False)
        self.canvas = tk.Canvas(self.gui, width=600, height=500, background="white")
        self.gui_params = GUIParams(box_top_left_x = 80, box_top_left_y = 50, row_height = 20, row_width = 450)
        self.initialize_rectangles()
        self.canvas.bind("<Button-1>", self.handle_click)
        self.draw_note_entry()
        self.draw_pause_button(10, 10)
        self.adjust_pause_button()
        self.draw_subdivision_entries()

        self.canvas.pack()
        self.gui.mainloop()

# this main method runs on "the main thread".
# all this thread does is initialize objects (the dao, the gui)
# then pass them to the other threads, then this thread
# starts the gui's main loop, which is blocking
def main():
        loop_params = LoopParams(2_500, 9)
        dao = DrumMachineDAO(loop_params)
        drum_thread = DrumMachineThread(dao)
        gui = GUI(dao)

main()