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
