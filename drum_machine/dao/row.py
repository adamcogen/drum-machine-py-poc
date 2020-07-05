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
