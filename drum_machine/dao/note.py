class Note:

        def __init__(self, midi_note, velocity=64):
                self.midi_note = midi_note
                self.velocity = velocity;

        def get_midi_note(self):
                return self.midi_note

        def get_velocity(self):
                return self.velocity

        def set_midi_note(self, new_midi_note):
                self.midi_note = new_midi_note

        def set_velocity(self, new_velocity):
                self.velocity = new_velocity

        def copy(self):
                return Note(self.midi_note, self.velocity)
