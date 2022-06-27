from imports_nps import *


class CreateForm(tk.Frame):
    """
    Create forms for user input.

    - specify exclusion of files from each series folder;
    - selecting size of rectangular ROI when menu 'fixed' is selected;
    - when menu 'array_rois' is selected, specify ROIs array;

    Attributes
    ----------
    entries : list tkinter's objects Entry
        Used to store user's input. Created in method makeform and used in methods
        readform_... for assign contents of entries to variables for further processing.
    accept_button : tkinter's Button object
        For all modes: button to store input information from entries of dialog window.
    entry_width : int
        Length of entry (in symbols) in created form.
    label_width : int
        Length of label (in symbols) in created form.
    color_rect_not_stored : string
        Color of not stored rectangles (blue).
    color_rect_stored : string
        Color of stored rectangles (green).
    color_rect_slided : string
        Color of slided rectangles (red).
    color_rect_resized : string
        Color of resized rectangles (red).
    background : tkinter's Canvas object
        (See attribute background of class GUI)
    file_exclusion_json : string
        Relative path to JSON (txt-file) containing previous settings for file
        exclusion.
    name_of_json : string
        Relative path to JSON (txt-file) containing previous settings for
        the mode 'Fixed_ROI'
    fixed_roi_width : int
        For mode 'Fixed_ROI': width of ROI in pixels.
    fixed_roi_height : int
        For mode 'Fixed_ROI': height of ROI in pixels.
    array : ndarray (2d)
        Pixel array of a dcm-image. Used to get image's size.
        (See attributes px_width and px_height of class CreateForm)
    px_width : int
        Width of dcm-image in pixels. Used for mode 'Array_ROIs' to draw ROIs on Canvas and
        to connect drawn ROIs with pixel array information from DICOMs.
        It is assumed, that all images have the same size.
    px_height : int
        Height of dcm-image in pixels. Used for mode 'Array_ROIs' to draw ROIs on Canvas and
        to connect drawn ROIs with pixel array information from DICOMs.
        It is assumed, that all images have the same size.
    previewed_rect_list : list of tkinter's objects Rectangle
        For mode 'Array_ROIs': shown previewed rectangles, created by clicking on button
        'Preview' in dialog window.
    preview_button : tkinter's Button object
        For mode 'Array_ROIs': button to preview ROIs. Connected with the method
        'preview_array_rois' of class CreateForm.
        Connected to methods beginning with 'readform...' of class CreateForm.
    position_x : int
        For mode 'Array_ROIs': x coordinate (in pixels) of upper left corner of
        upper left ROI in array of ROIs.
    position_y : int
        For mode 'Array_ROIs': y coordinate (in pixels) of upper left corner of
        upper left ROI in array of ROIs.
    number_x : int
        For mode 'Array_ROIs': number of ROIs in array in x direction.
    number_y : int
        For mode 'Array_ROIs': number of ROIs in array in y direction.
    distance_x : int
        For mode 'Array_ROIs': distance in pixels between ROIs in array
        in x direction.
    distance_y : int
        For mode 'Array_ROIs': distance in pixels between ROIs in array
        in y direction.

    Methods
    -------
    makeform()
        Create necessary widgets for the user input form
    fillform(values)
        Fill the form with default or previously specified values
    readform()
        When specifying the size of rectangular ROI ('fixed' menu),
        read the specified values after clicking button 'accept'
    readform_array_roi()
        When specifying parameters of array ROIs,
        read the specified values after clicking button 'accept'
    readform_exclude_files()
        When specifying number of files to be excluded from the beginning
        and the end of each series folder,
        read the specified values after clicking button 'accept'
    preview_array_rois()
        Draw rectangles on the canvas for previewing after clicking
        button 'Preview'
    """

    def __init__(self, master_main_window, fields, values, object_arrays, object_gui, program_start=False):

        """
        :param master_main_window: tkinter's Tk object
            master window for the form's window
        :param fields: list of strings
            list of fields to appear in form
        :param values: list of different data types
            list of the respective values to be filled into fields
        :param object_arrays: instance of the class StartClass
            used to retrieve auxiliary boolean variables and file list (to get images' size)
            it is assumed that all images have same size
        :param object_gui: instance of class GUI
            used to retrieve tool_index (specified mode of ROI selection) and
            to retrieve attributes of this class: colors of the ROI selection's rectangles
        :param program_start: boolean
            auxiliary boolean:
            if False, attributes from object_arrays and object_gui are retrieved;
            if True, they are not retrieved, because these objects don't exist yet
                (used at program start when file exclusion is to be specified)



            """

        # declare attributes
        self.position_x = 0
        self.position_y = 0
        self.number_x = 0
        self.number_y = 0
        self.distance_x = 0
        self.distance_y = 0
        self.entries = []

        self.object_arrays = object_arrays
        self.object_gui = object_gui
        self.program_start = program_start
        self.master_main_window = master_main_window
        super().__init__(master_main_window)
        self.fields = fields
        self.values = values

        if not self.program_start:
            # get measurements of image (assumed they are equal for all images)
            self.array = self.object_arrays.create_base_array(self.object_arrays.filelist[0])['base_array']
            # image measurements
            self.px_height = self.array.shape[0]
            self.px_width = self.array.shape[1]

        # if accept button has been already used, reuse data in the form
        if not self.program_start:
            if self.object_arrays.acceptButtonIsAlreadyUsed:
                self.fixed_roi_width = fixed_roi_width
                self.fixed_roi_height = fixed_roi_height

        # colors of rectangles
        if not self.program_start:
            self.color_rect_not_stored = self.object_gui.color_rect_not_stored
            self.color_rect_stored = self.object_gui.color_rect_stored
            self.color_rect_slided = self.object_gui.color_rect_slided
            self.color_rect_resized = self.object_gui.color_rect_resized

            # initialize source of image shown on GUI
            self.new_source = self.object_gui.new_source
            # retrieve canvas object from the object of GUI
            self.background = self.object_gui.background

            # insert last used parameters of ROI, if they have been already specified
            if self.object_gui.tool_index == 'fixed' and self.object_arrays.acceptButtonIsAlreadyUsed:
                self.values = [self.fixed_roi_height, self.fixed_roi_width]

        # file names of JSONs with stored settings from previous code run sessions
        # for array_rois selection
        self.name_of_json = 'variables_info.txt'
        # for file exclusion
        self.file_exclusion_json = 'file_exclusion_settings.txt'

        # delete all previously previewed rectangles from canvas
        # if obj_gui.previewButtonIsAlreadyUsed:
        #     for rect in self.previewed_rect_list:
        #         obj_gui.background.delete(rect)
        # list for previewed rectangles
        self.previewed_rect_list = []

        # size of labels and entries
        self.label_width = 12
        self.entry_width = 6

        # make form of dialog window
        self.makeform()
        # fill the form with default values
        self.fillform(self.values)

    def makeform(self):

        """
        Create necessary widgets for the user input form.
        :return: nothing
        """

        # list to store frames
        global row_matr
        # list to store entries
        self.entries = []
        # column number of the grid
        t = 0
        # row number of the grid
        q = 0
        row_counter = 0
        row_matr = []
        # iterate through field names
        for field in self.fields:
            # if there more than 50% of fields in one column
            # if q > int(len(self.fields) / 2):
            #     # next column
            #     # +2 since there is also entry
            #     t += 2
            #     # first row
            #     q = 0
            global row
            row = Frame(self.master_main_window)
            lab = Label(row, width=self.label_width, text=field, anchor='w')
            ent = Entry(row, width=self.entry_width)
            row_matr.append(row)

            row.grid(row=q, column=t, padx=5, pady=5)
            lab.grid(row=q, column=t)
            ent.grid(row=q, column=t + 1)
            q += 1
            row_counter += 1
            # store entries as tuple in a list
            self.entries.append((field, ent))

        if not self.program_start:
            if obj_gui.tool_index == 'fixed':
                self.accept_button = tk.Button(master=self.master_main_window, text='accept', command=self.readform,
                                               anchor='w')
                self.accept_button.grid(row=len(self.fields) + 1, column=0, padx=5, pady=5)
            elif obj_gui.tool_index == 'array_rois':
                self.accept_button = tk.Button(master=self.master_main_window,
                                               text='accept',
                                               command=self.readform_array_roi,
                                               anchor='w')
                self.accept_button.grid(row=len(self.fields) + 1, column=0, padx=5, pady=5)
                # button for preview
                self.preview_button = tk.Button(master=self.master_main_window,
                                                text='preview',
                                                command=self.preview_array_rois,
                                                anchor='w')

                self.preview_button.grid(row=len(self.fields) + 2, column=0, padx=5, pady=5)

        # if program is just launched, create button for dialog window
        # to exclude some files from the begin and the end of folders with DICOMs
        if self.program_start:
            self.accept_button = tk.Button(master=self.master_main_window, text='continue',
                                           command=self.readform_exclude_files, anchor='w')
            self.accept_button.grid(row=len(self.fields) + 1, column=0, padx=5, pady=5)

    def fillform(self, values):

        """
        Fill the form with default or previously specified values

        :param values: list
            Values to fill the form.
        :return: nothing
        """

        counter = 0
        for value in self.values:
            self.entries[counter][1].insert(END, value)
            counter += 1

    def readform(self):

        """
        When specifying the size of rectangular ROI ('fixed' menu),
        read the specified values after clicking button 'accept'

        :return: nothing
        """
        # auxiliary boolean operation to enable storing of last
        # specified parameters of ROI
        self.object_arrays.acceptButtonIsAlreadyUsed = True
        # initialize data_array
        data_array = []
        # fill data_array with values of the form
        for entry in self.entries:
            data_array.append(entry[1].get())
        # pass values to self-variables to use them in the class
        self.fixed_roi_height = data_array[0]
        self.fixed_roi_width = data_array[1]
        # globalize variables to access them in other classes
        global fixed_roi_height
        fixed_roi_height = data_array[0]
        global fixed_roi_width
        fixed_roi_width = data_array[1]
        # destroy dialog window
        self.master_main_window.destroy()

    def readform_array_roi(self):

        """
        When specifying parameters of array ROIs,
        read the specified values after clicking button 'accept'

        :return: nothing
        """

        # delete all previously shown previewed rectangles from canvas
        if obj_gui.previewButtonIsAlreadyUsed:
            for rect in self.previewed_rect_list:
                obj_gui.background.delete(rect)
        # if the button "accept" has been already pressed
        self.object_arrays.acceptButtonIsAlreadyUsed = True
        # array for collecting data from entries
        data_array = []
        # get data from entries
        for entry in self.entries:
            data_array.append(entry[1].get())
        # assignment to self-variables
        self.fixed_roi_height = int(data_array[0])
        self.fixed_roi_width = int(data_array[1])
        self.position_x = int(data_array[2])
        self.position_y = int(data_array[3])
        self.number_x = int(data_array[4])
        self.number_y = int(data_array[5])
        self.distance_x = int(data_array[6])
        self.distance_y = int(data_array[7])
        # self.new_source = obj_gui.new_source
        self.background = obj_gui.background
        # self.px_width = self.object_arrays.im_width_dict[self.new_source]
        # self.px_height = self.object_arrays.im_height_dict[self.new_source]
        # store variables into JSON
        with open(self.name_of_json, 'w') as file_to_store_variables:
            dict_to_store = {'fixed_roi_height': self.fixed_roi_height,
                             'fixed_roi_width': self.fixed_roi_width,
                             'position_x': self.position_x,
                             'position_y': self.position_y,
                             'number_x': self.number_x,
                             'number_y': self.number_y,
                             'distance_x': self.distance_x,
                             'distance_y': self.distance_y,
                             }
            json.dump(dict_to_store, file_to_store_variables)

        # globalize variables to access them in other classes
        global fixed_roi_height
        fixed_roi_height = data_array[0]
        global fixed_roi_width
        fixed_roi_width = data_array[1]

        # build arrays of coordinates

        # then draw rectangles with fixed size
        rect_width = int(self.fixed_roi_width)
        rect_height = int(self.fixed_roi_height)
        # PhX insert pop up window

        l_up_corner_x = int(self.position_x)
        l_up_corner_y = int(self.position_y)

        # initialize position coordinates of link upper corner of first ROI
        x_pos = l_up_corner_x
        y_pos = l_up_corner_y

        # iterate over numbers of ROIs in x-direction (outer loop)
        # and in y-direction (inner loop)
        for x_i in range(self.number_x):
            for y_i in range(self.number_y):
                # specify coordinates of rectangle's diagonal corners
                begin_rect_x = x_pos  # for the scores matrix
                begin_x_im = int(begin_rect_x * obj_gui.background.winfo_width() / self.px_width)  # on the canvas
                end_rect_x = x_pos + rect_width
                end_x_im = int(end_rect_x * obj_gui.background.winfo_width() / self.px_width)
                begin_rect_y = y_pos
                begin_y_im = int(begin_rect_y * obj_gui.background.winfo_height() / self.px_height)
                end_rect_y = y_pos + rect_height
                end_y_im = int(end_rect_y * obj_gui.background.winfo_height() / self.px_height)
                # draw rectangle on canvas
                rect_sel = obj_gui.background.create_rectangle(begin_x_im, begin_y_im, end_x_im, end_y_im,
                                                               outline=self.color_rect_not_stored)
                # store coordinates of rectangle
                obj_gui.image_rect_coord.append((begin_rect_x,
                                                 begin_rect_y,
                                                 end_rect_x,
                                                 end_rect_y))
                obj_gui.image_rect_coord_record.append((begin_rect_x,
                                                        begin_rect_y,
                                                        end_rect_x,
                                                        end_rect_y))
                obj_gui.rect_coord_dict.update({obj_gui.basename_w_ext: obj_gui.image_rect_coord})
                # store the shown coordinates of rectangles
                obj_gui.image_rect_coord_im.append((begin_x_im,
                                                    begin_y_im,
                                                    end_x_im,
                                                    end_y_im))
                obj_gui.rect_coord_dict_im.update({obj_gui.basename_w_ext: obj_gui.image_rect_coord_im})
                # store the rectangle in the list
                obj_gui.image_rectangles.append(rect_sel)
                obj_gui.rectangles_dict.update({obj_gui.basename_w_ext: obj_gui.image_rectangles})
                # go to the next y_position of ROI
                y_pos += rect_height + self.distance_y
            # go to the next x_position of ROI
            x_pos += rect_width + self.distance_x
            # go to the start y_position of ROI
            y_pos = l_up_corner_y
        # destroy dialog window
        self.master_main_window.destroy()

    def readform_exclude_files(self):

        """
        When specifying number of files to be excluded from the beginning
        and the end of each series folder,
        read the specified values after clicking button 'accept'

        :return: nothing
        """

        # array for collecting data from entries
        data_array = []
        # get data from entries
        for entry in self.entries:
            data_array.append(entry[1].get())
        # assignment to self-variables
        self.num_files_to_exclude_start = int(data_array[0])
        self.num_files_to_exclude_end = int(data_array[1])

        with open(self.file_exclusion_json, 'w') as file_to_store_variables:
            dict_to_store = {'num_files_to_exclude_start': self.num_files_to_exclude_start,
                             'num_files_to_exclude_end': self.num_files_to_exclude_end,
                             }
            json.dump(dict_to_store, file_to_store_variables)

        self.master_main_window.destroy()

    def preview_array_rois(self):

        """
        Draw rectangles on the canvas for previewing after clicking
        button 'Preview'.

        :return:
        """

        # switch auxiliary boolean to True
        obj_gui.previewButtonIsAlreadyUsed = True
        # delete all previously previewed rectangles from canvas
        for rect in self.previewed_rect_list:
            obj_gui.background.delete(rect)
        # array for collecting data from entries
        data_array = []
        # get data from entries
        for entry in self.entries:
            data_array.append(entry[1].get())
        # assignment to self-variables
        self.fixed_roi_height = int(data_array[0])
        self.fixed_roi_width = int(data_array[1])
        self.position_x = int(data_array[2])
        self.position_y = int(data_array[3])
        self.number_x = int(data_array[4])
        self.number_y = int(data_array[5])
        self.distance_x = int(data_array[6])
        self.distance_y = int(data_array[7])

        global fixed_roi_height
        fixed_roi_height = data_array[0]
        global fixed_roi_width
        fixed_roi_width = data_array[1]

        # build arrays of coordinates

        # then draw rectangles with fixed size
        rect_width = int(self.fixed_roi_width)
        rect_height = int(self.fixed_roi_height)
        # PhX insert pop up window

        l_up_corner_x = int(self.position_x)
        l_up_corner_y = int(self.position_y)

        # initialize position coordinates of link upper corner of first ROI
        x_pos = l_up_corner_x
        y_pos = l_up_corner_y
        for x_i in range(self.number_x):
            for y_i in range(self.number_y):
                # specify coordinates of rectangle's diagonal corners
                begin_rect_x = x_pos  # for the scores matrix
                begin_x_im = int(begin_rect_x * obj_gui.background.winfo_width() / self.px_width)  # on the canvas
                end_rect_x = x_pos + rect_width
                end_x_im = int(end_rect_x * obj_gui.background.winfo_width() / self.px_width)
                begin_rect_y = y_pos
                begin_y_im = int(begin_rect_y * obj_gui.background.winfo_height() / self.px_height)
                end_rect_y = y_pos + rect_height
                end_y_im = int(end_rect_y * obj_gui.background.winfo_height() / self.px_height)
                # draw rectangle on canvas
                self.rect_preview = obj_gui.background.create_rectangle(begin_x_im, begin_y_im, end_x_im, end_y_im,
                                                                        outline=self.color_rect_not_stored)
                self.previewed_rect_list.append(self.rect_preview)

                y_pos += rect_height + self.distance_y
            x_pos += rect_width + self.distance_x
            y_pos = l_up_corner_y
        # destroy dialog window
        # self.master_main_window.destroy()