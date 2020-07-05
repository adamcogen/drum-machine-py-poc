import mido
import threading
from time import perf_counter_ns

class DrumMachineThread(threading.Thread): # this thread runs the drum machine timer loop

        def __init__(self, dao, gui_status):
                self.dao = dao
                self.gui_status = gui_status
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
                while(self.gui_status.is_not_exited()):
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
