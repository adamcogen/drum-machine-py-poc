from .row import Row

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
