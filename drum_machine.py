import mido
from time import perf_counter_ns

def get_tick_of_beat(subdivision, beat, loop_length_in_ticks):
        return int((loop_length_in_ticks * beat) / subdivision)

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

        def get_subdivision(self):
                return subdivision

        def get_loop_params(self):
                return loop_params

        def set_subdivision(self, new_subdivision):
                self.subdivision = new_subdivision

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

class DrumMachineDAO:

        def __init__(self, loop_params):
                self.loop_params = loop_params
                self.current_tick = 0
                self.loop = Loop(loop_params)
                self.all_notes = []

        def get_loop_params(self):
                return self.get_loop_params

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

        def get_current_tick(self):
                return self.current_tick

        def set_subdivision_for_row(self, subdivision, index_of_row):
                self.loop.get_rows()[index_of_row].set_subdivision(subdivision)

        def update_all_notes_array(self):
                self.all_notes = []
                for tick in range(0, self.loop_params.get_length_in_ticks()):
                        all_notes_for_tick = []
                        for row in self.loop.get_rows():
                                all_notes_for_tick.append(row.get_note_at_tick(tick))
                        self.all_notes.append(all_notes_for_tick)
                        all_notes_for_tick = []

        def get_all_notes_at_current_tick(self):
                return self.all_notes[self.current_tick]

def run_loop(dao):
        outport = mido.open_output('IAC Driver Bus 1')
        millisecond = 1_000_000
        play_notes(outport, dao.get_all_notes_at_current_tick())
        startTime = perf_counter_ns()
        while(True):
                if(perf_counter_ns() - startTime >= millisecond):
                        dao.increment_current_tick()
                        play_notes(outport, dao.get_all_notes_at_current_tick())
                        startTime = perf_counter_ns()

def set_loop(dao):
        bass_drum = Note(36)
        snare = Note(37)
        clave = Note(43)

        # row 0: subdivision of 8
        dao.set_subdivision_for_row(8, 0)
        dao.set_note_at_beat_for_row(bass_drum, 0, 0) #
        dao.set_note_at_beat_for_row(snare, 2, 0)
        dao.set_note_at_beat_for_row(bass_drum, 3, 0)
        dao.set_note_at_beat_for_row(bass_drum, 4, 0)
        dao.set_note_at_beat_for_row(snare, 6, 0)
        dao.set_note_at_beat_for_row(snare, 7, 0)
        # row 1: subdivision of 20 (four groups of 5)
        dao.set_subdivision_for_row(20, 1)
        dao.set_note_at_beat_for_row(bass_drum, 4, 1)
        dao.set_note_at_beat_for_row(bass_drum, 9, 1) #
        dao.set_note_at_beat_for_row(snare, 19, 1)
        # row 2: subdivision of 20
        dao.set_subdivision_for_row(20, 2)
        dao.set_note_at_beat_for_row(clave, 0, 2)
        dao.set_note_at_beat_for_row(clave, 4, 2)
        dao.set_note_at_beat_for_row(clave, 5, 2)
        dao.set_note_at_beat_for_row(clave, 9, 2)
        dao.set_note_at_beat_for_row(clave, 10, 2)
        dao.set_note_at_beat_for_row(clave, 14, 2)
        dao.set_note_at_beat_for_row(clave, 15, 2)
        dao.set_note_at_beat_for_row(clave, 19, 2)
        # row 3: subdivision of 16
        dao.set_subdivision_for_row(16, 4)
        dao.set_note_at_beat_for_row(bass_drum, 9, 4)
        dao.set_note_at_beat_for_row(clave, 14, 4)

        dao.update_all_notes_array()

def main():
        loop_params = LoopParams(2_500, 5)
        dao = DrumMachineDAO(loop_params)
        set_loop(dao)
        run_loop(dao)

main()