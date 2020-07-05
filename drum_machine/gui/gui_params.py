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
