from .loop import Loop

class DrumMachineDAO:

        def __init__(self, loop_params):
                self.loop_params = loop_params
                self.current_tick = 0
                self.loop = Loop(loop_params)
                self.paused = True

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

        def reset(self):
                self.current_tick = 0
                self.loop = Loop(self.loop_params)
