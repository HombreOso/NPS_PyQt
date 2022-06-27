from imports_nps import *


class GUI(tk.Frame):

    """
    Create GUI to show dcm-images and select ROIs.

    Attributes
    ----------
    horiz : int
        Absolute x coordinate of mouse pointer on the image.
        If image has been resized, x position is got as if
        the image has not been resized.
    vert : int
        Absolute y coordinate of mouse pointer on the image.
        If image has been resized, x position is got as if
        the image has not been resized.
    slice_number : int
        Current image number. Got from Slider widget.
    slided_rectangles_list : list of tkinter's Rectangle objects
        If rectangles have been drawn on some image, and then the
        Slider widget was used to slide images, the Rectangle objects
        of previous image are stored in this list.
    slided_rectangles_dict : dict of lists
        Key : current dcm-image file name (not path).
        Value : respective list slided_rectangles_list
            (See the attribute's description in class GUI).
    new_source : string
        Absolute path to current slided dcm-image.
    basename_w_ext : string
        Base name of attribute new_source.
    new_show_im_source : string
        Absolute path to png image respective to currently shown
        dcm-image.
    new_image : PIL.PngImagePlugin.PngImageFile object
        This object is yielded from current png image file
        using Pillow.
    new_img_copy : PIL.PngImagePlugin.PngImageFile object
        Copy of attribute new_image.
        Copy is created to be resized later.
    image : PIL.PngImagePlugin.PngImageFile object
        Attribute new_img_copy resized to actual size of Canvas.
    slice_img : tkinter's PhotoImage object
        This object is finally loaded on canvas widget of main window.
    array : ndarray (2d)
        Pixel array of currently shown dcm-image.
    px_height : int
        Number of rows in attribute array.
    px_width : int
        Number of columns in attribute array.
    slider : tkinter's Slider object
        Slider to slide through images. Connected with method slide_images().
    label_name : tkinter's Label object
        Label containing name of current dcm-image
    label_position : tkinter's Label object
        Label containing absolute x and y position of mouse pointer.
        (See also attributes horiz and vert of class GUI)
    background : tkinter's Canvas object
        Canvas on which the images are displayed.
    menu : tkinter's Menu object
        Menu containing user GUI commands.
        Submenus: Edit, Tools, Final.
    file : tkinter's Menu object
        Submenu of attribute Menu.
        Command: 'Save ROIs and create XLSX'
    image_rect_coord_record : list of tuples of int
        Each tuple for each ROI. Items of each tuple:
            absolute x coordinate of left upper corner of ROI,
            absolute y coordinate of left upper corner of ROI,
            absolute x coordinate of right lower corner of ROI,
            absolute y coordinate of right lower corner of ROI.
    rect_coord_dict : dict of lists of tuples of int
        Keys : base name of dcm-image file
        Values : respective attribute image_rect_coord_record
            (See the attribute's description)
    image_rect_coord_im : list of tuples of int
        Each tuple for each ROI. Items of each tuple:
                shown x coordinate of left upper corner of ROI,
                shown y coordinate of left upper corner of ROI,
                shown x coordinate of right lower corner of ROI,
                shown y coordinate of right lower corner of ROI.
    rect_coord_dict_im : dict of lists of tuples of int
        Keys : base name of dcm-image file
        Values : respective attribute image_rect_coord_im
            (See the attribute's description)
    image_rectangles : list of tkinter's Rectangle objects
        Rectangle objects drawn on current image.
    rectangles_dict : dict of lists of tkinter'S Rectangle objects
        Keys : base name of dcm-image file
        Values : respective attribute image_rectangles
            (See the attribute's description)
    x_coord : int
        Absolute x coordinate of mouse pointer at clicking on
        left mouse button.
    y_coord : int
        Absolute y coordinate of mouse pointer at clicking on
        left mouse button.
    all_roi_dict : dict of lists of tuples
        Keys : absolute paths to dcm-images
        Values : lists of tuples containing coordinates of
            left upper (x and y) and right lower (x and y)
            corners of ROIs. Each tuple for each ROI.
            (See attribute image_rect_coord_record)
    form : instance of class CreateForm
        Object containing information needed in mode 'Fixed_ROIs'
        about size of fixed ROI.

    Methods
    -------
    motion(self, event)
        Get absolute mouse pointer coordinates, when moving it.
        Update mouse pointer position label's text.
    slide_images(self, event)
        Slide shown images with Slider widget.
    create_widgets(self)
        Create necessary widgets (Labels, Canvas, Slider, Menu)
        for main window.
    _resize_image(self, event)
        Adjust shown image size, canvas size and
        slider width to resized main window.
    create_bindings(self)
        Connect events to methods.
    draw(self, event)
        Select ROIs depending on selecting mode:
        'Fixed_ROI' or 'Draw_Diagonal'.
        Draw rectangles on canvas.
        Store their absolute coordinates in self.image_rect_coord.
        Store their resized coordinates in self.image_rect_coord_im.
        Store Rectangle objects in self.rectangles_dict.
    erase_last(self)
        Erase last ROI drawn on canvas.
    update_roi_dict(self)
        Update attribute all_roi_dict, when choosing
        menu 'Save ROIs and create XLSX-file'.
    choose_whole_image(self)
        Select whole images as ROIs and store their pixel arrays
        into all_roi_dict.
    minimal_shape(self, dict_of_2d_arrays)
        minimal_shape(self, dict_of_2d_arrays).
    choose_fixed(self)
        Select 'Fixed_ROIs' mode.
        Create form for choosing fixed ROI's size.
    choose_array_rois(self)
        Select 'Array_ROIs' mode.
        Create form for choosing parameters of array of ROIs.
    choose_diagonal(self)
        Select mode 'Draw_Diagonal'
    build_initial_coord(self, event)
        Store absolute coordinates of mouse pointer
        when clicking on left mouse button.
    """

    def __init__(self, *, master, obj_arrays, crop_perc, fit_order, useFitting, im_height_in_mm,
                 im_width_in_mm, extensions, trunc_percentage,
                 useCentralCropping, start_freq_range, end_freq_range, step,
                 useTruncation, multipleFiles, pixel_size_in_mm, equal_ROIs_for_each_image,
                 main_window_width, main_window_height):

        """

        :param master: tkinter's Tk object
            Master of window with shown images.
        :param obj_arrays: instance of class StartClass
            Used to retrieve its attributes: acceptButtonIsAlreadyUsed,
            filelist, filedict, all_images; and method create_base_array().
        :param crop_perc:
        :param fit_order: int (1 or 2)
            If attribute useFitting is True, the order of fitting of dcm-image.
            Specified in init_dict.
        :param useFitting:
            True: 1st or 2nd order fit of dcm images is executed as a method of
                background removal.
            False: Mean value subtraction is used as background removal.
            This attribute is specified in init_dict.
        :param im_height_in_mm: float
            Height of FOV (Field-Of-View) in mm. Specified in init_dict.
        :param im_width_in_mm:
            Width of FOV in mm. Specified in init_dict.
        :param extensions: list of strings
            List of extensions to be searched for in selected directory.
            Specified in init_dict.
        :param trunc_percentage: float
            Under this per cent value the NPS is truncated at
            the end of NPS-values list. Specified in init_dict.
        :param x0: int
            x-coordinate of mouse pointer when clicking on left mouse
            button.
        :param x1: int
            x-coordinate of mouse pointer when releasing left mouse
            button.
        :param y0:
            y-coordinate of mouse pointer when clicking on left mouse
            button.
        :param y1:
            y-coordinate of mouse pointer when releasing left mouse
            button.
        :param useCentralCropping: boolean
            Whether the ROI should be a central crop of the dcm-images.
            True: central part of the image is cropped.
                Percentage of the cropping is specified by attribute
                crop_percentage of class GUI.
            Specified in init_dict.
        :param start_freq_range: float
            Start of frequency range (maybe not needed in this class)
        :param end_freq_range: float
            End of frequency range (maybe not needed in this class)
        :param step: float
            Step of frequency range (maybe not needed in this class)
        :param useTruncation: boolean
            Whether truncation of low valued NPS at higher frequencies
            should be used. Specified in init_dict.
        :param multipleFiles: (not needed in this class)
        :param pixel_size_in_mm: float
            Default pixel size in mm. (If metadata PixelSpacing
            is not known). Specified in init_dict.
        :param equal_ROIs_for_each_image: boolean
            Whether there should be equal ROIs selected in all images.
            Specified in init_dict.
        :param main_window_width: int
            Width of main window (showing images, labels, slider, etc.)
            in pixels. Specified in init_dict.
        :param main_window_height: int
            Height of main window (showing images, labels, slider, etc.)
            in pixels. Specified in init_dict.
        """

        print('Constructor of the class GUI is being executed')


        self.master = master
        super().__init__(master)  # master frame
        self.grid()  # packing of master frame on grid
        # get base arrays as dict from another class
        self.obj_arrays = obj_arrays

        # initialize attributes

        # defined in self.motion()
        self.horiz = 0
        self.vert = 0
        # defined in self.slide_images()
        self.slice_number = 0
        self.basename_w_ext = ''
        self.new_image = ''
        self.new_img_copy = ''
        self.image = ''
        self.slice_img = ''
        # defined in create_widgets()
        self.slider = 0
        self.label_name = 0
        self.label_position = 0
        self.background = 0
        # defined in choose_fixed()
        self.form = 0
        self.dialog_window = 0











        self.freq = []
        # self.arrays_dict = self.obj_arrays.arrays_dict
        # slider's height
        self.slider_height = 15
        # height of label
        self.label_height = 57
        # aux boolean
        self.already_resized = False
        self.counter_pass = 0
        # color of rectangles (not stored)
        self.color_rect_not_stored = '#0000FF'
        # color of rectangles (not stored)
        self.color_rect_slided = '#FF0000'
        # color of rectangles (stored)
        self.color_rect_stored = '#00FF00'
        # color of resized rectangles
        self.color_rect_resized = '#0000FF'
        # color of active button
        self.color_button_active = '#9FFF80'
        # color of inactive button
        self.color_button_inactive = '#E6E6E6'
        # field names and initial values for dialog frame
        self.fields = ['height_px', 'width_px']
        # size of main window
        self.main_window_height = main_window_height
        self.main_window_width = main_window_width
        self.size_of_main_window = max(self.main_window_width, self.main_window_height)
        if self.obj_arrays.acceptButtonIsAlreadyUsed:
            self.values = [int(fixed_roi_height), int(fixed_roi_width)]
        else:
            self.values = [128, 128]
        # field names for array rois selection
        self.fields_array_rois = ['height',
                                  'width',
                                  'left_upper_x',
                                  'left_upper_y',
                                  'number_roi_x',
                                  'number_roi_y',
                                  'distance_x',
                                  'dictance_y']
        if os.path.isfile('variables_info.txt'):
            with open('variables_info.txt', 'r') as file_to_read_info:
                read_dict = json.load(file_to_read_info)
            list_of_variables = [read_dict[key] for key in read_dict]
            self.values_array_rois = list_of_variables
        else:
            self.values_array_rois = [64,
                                      64,
                                      10,
                                      10,
                                      1,
                                      1,
                                      5,
                                      5]
        # auxuliary boolean to destroy perviewed rectangles
        self.previewButtonIsAlreadyUsed = False
        # size of dialog window
        self.dialog_window_height = 110
        self.dialog_window_width = 160
        self.dialog_window_x = 200
        self.dialog_window_y = 20

        # for array of ROIs
        self.dialog_window_height_arr_roi = 400
        self.dialog_window_width_arr_roi = 190
        self.dialog_window_x_arr_roi = 200
        self.dialog_window_y_arr_roi = 20
        # pixel size
        self.pixel_size_in_mm = pixel_size_in_mm
        # whether there are equal ROIs for each image
        self.equalROIs = equal_ROIs_for_each_image
        # whether it should be one or multiple excel-files
        self.multipleFiles = multipleFiles
        # all rectangles
        self.all_rect = []
        # dictionary for rectangles on each image
        self.all_rect_dict = {}
        # dictionary for rectangle coordinates
        self.rect_coord_dict = {}
        self.rect_coord_dict_im = {}
        self.image_rect_coord = []
        self.image_rect_coord_record = []
        self.image_rect_coord_im = []
        # dictionary for rectangles in slided images
        self.slided_rectangles_dict = {}
        # list of slided rectangles in current image
        self.slided_rectangles_list = []
        # list for rectangles created by resizing

        # dictionary for rectangle objects on each image
        self.rectangles_dict = {}
        self.image_rectangles = []
        # ROIs for current image
        self.image_roi = []
        # dictionary for ROIs of all images
        self.all_roi_dict = {}
        # collect all recorded rectangles
        self.all_rect_record = []
        # all xlsx-files
        self.all_xlsx_range = []
        self.all_xlsx = []
        # paths to all cropped images
        self.all_cropped_im = []
        # paths to all one d nps images
        self.all_1_d_nps = []
        # whether central cropping should be applied
        self.useCentralCropping = useCentralCropping
        # whether lower nps should be deleted
        self.useTruncation = useTruncation
        # extensions of image files
        self.extensions = extensions
        # image measurements in mm
        # self.im_height_in_mm = im_height_in_mm
        # self.im_width_in_mm = im_width_in_mm
        # truncate lower nps
        self.trunc_percentage = trunc_percentage
        # maximal size of the image (height or width)
        # self.max_size = max(im_height_in_mm, im_width_in_mm)
        # cropping percentage
        self.crop_perc = crop_perc
        # fitting order for 2d-fit
        self.fit_order = fit_order
        # whether fitting should be applied
        # or background removal should be used
        self.useFitting = useFitting

        # freq range parameters
        self.start_freq = start_freq_range
        self.end_freq = end_freq_range
        self.num_of_steps = int((self.end_freq - self.start_freq) // step + 1)
        self.freq_range = np.linspace(start=self.start_freq,
                                      stop=self.end_freq,
                                      num=self.num_of_steps)

        # get the duration of program's execution
        self.start_timer = time.time()
        # create list of image files (paths to them)
        self.file_list = self.obj_arrays.filelist
        self.filedict = self.obj_arrays.filedict
        # initialize empty dictionary for rois
        print('creation of all_roi_dict is being executed')
        for path_to_file in self.file_list:
            key = path_to_file
            self.all_roi_dict.update({key: []})
        print('creation of all_roi_dict is done')


        # initial image array
        self.array = self.obj_arrays.create_base_array(self.file_list[0])['base_array']
        # initial label name
        self.new_source = self.file_list[0]
        # initial image for canvas
        self.new_show_im_source = self.obj_arrays.all_images[0]
        # initial image height and width
        # image measurements
        self.px_height = self.array.shape[0]
        self.px_width = self.array.shape[1]
        self.new_im_size = max(self.px_width, self.px_height)
        self.resize_coef = 1
        # initial tool_index
        self.tool_index = 'diagonal'
        # create widgets
        self.create_widgets()
        # create bindings
        self.create_bindings()

        print('Constructor of the class GUI is done')


    def motion(self, event):
        """
        Get absolute mouse pointer coordinates, when moving it.
        Update mouse pointer position label's text.

        If the main window is resized self.vert and self.horiz
        define absolute position of mouse pointer as if the image was not resized.

        :param event: tkinter's event object
            Mouse event Motion.
        :return: nothing
        """
        try:
            # horiz. mouse pointer position in the changed frame
            self.horiz = int(self.px_width * event.x / self.background.winfo_width())
            # vert. mouse pointer position in the changed frame
            self.vert = int(self.px_height * event.y / self.background.winfo_height())
            # update label's text
            self.label_position["text"] = 'x: ' + str(self.horiz) + '| y: ' + str(self.vert)
        except NameError:
            pass
        except AttributeError:
            pass

    def slide_images(self, event):

        """
        Slide shown images with Slider widget.
        :param event: tkinter's event object
            Slider Movement object.
        :return: nothing
        """
        # clear the list of slided rectangles
        self.slided_rectangles_list = []
        # get image number from slider
        self.slice_number = self.slider.get() - 1
        # path to file containing pixel data
        self.new_source = self.file_list[self.slice_number]
        self.basename_w_ext = os.path.basename(self.new_source)
        # path to new png image
        self.new_show_im_source = self.obj_arrays.all_images[self.slice_number]
        # create Pillow image object
        self.new_image = Image.open(self.new_show_im_source)
        # copy object of new image
        self.new_img_copy = self.new_image.copy()
        # resize the copy to new size specified by user
        self.image = self.new_img_copy.resize((self.new_im_size, self.new_im_size))
        # create PhotoImage object for canvas (self.background) from the resized image
        self.background.new_background_image = ImageTk.PhotoImage(self.image)
        # load the object PhotoImage on the Canvas
        self.slice_img = self.background.create_image(0, 0, anchor=NW, image=self.background.new_background_image)
        # draw rectangles selected in previous images
        # and store the respective Rectangle objects in a list
        try:
            for coord in self.image_rect_coord_im:
                self.slided_rectangles_list.append(
                    self.background.create_rectangle(
                        coord[0],  # * self.resize_coef,
                        coord[1],  # * self.resize_coef,
                        coord[2],  # * self.resize_coef,
                        coord[3],  # * self.resize_coef,
                        outline=self.color_rect_slided))
        except KeyError:
            pass

        # update dict of slided rectangles
        self.slided_rectangles_dict.update({self.basename_w_ext: self.slided_rectangles_list})
        # print('slided_rectangles:  ', self.slided_rectangles_dict)

        # change title of main window according to new image file
        self.master.title(os.path.basename(self.new_source))
        # create array for current image
        self.array = self.obj_arrays.create_base_array(self.new_source)['base_array']

        # image measurements
        self.px_height = self.array.shape[0]
        self.px_width = self.array.shape[1]

        # self.px_width = self.obj_arrays.im_width_dict[self.new_source]
        # self.px_height = self.obj_arrays.im_height_dict[self.new_source]
        # change label name

        # update name label's text
        self.label_name["text"] = os.path.basename(self.new_source)

    def create_widgets(self):
        """
        Create necessary widgets (Labels, Canvas, Slider, Menu)
        for main window.
        :return: nothing
        """
        # slider
        self.slider = Scale(master=self.master, from_=1, to=2, length=self.px_width,
                            orient=HORIZONTAL, highlightthickness=0, bd=0, width=self.slider_height,
                            command=self.slide_images)
        self.slider.grid(row=4)

        # label for base name of current image file
        self.label_name = tk.Label(self, highlightthickness=0, bd=0)  # create the demonstration label
        self.label_name.grid(row=1, column=0)

        # label for position of mouse pointer on the image
        self.label_position = tk.Label(self, highlightthickness=0, bd=0)  # create the demonstration label
        self.label_position.grid(row=2, column=0)
        # passing the initial text
        self.label_name["text"] = os.path.basename(self.new_source)
        self.label_position["text"] = 'set pointer on the image'

        # canvas with image of slice
        self.background = Canvas(self, highlightthickness=0, borderwidth=0, width=self.px_width,
                                 height=self.px_height)
        self.background.grid(row=3)
        imp = Image.open(self.new_show_im_source)
        self.background.image = ImageTk.PhotoImage(imp)
        self.slice_img = self.background.create_image(0, 0, anchor=NW, image=self.background.image)

        # create menubar
        self.menu = tk.Menu(self.master)
        self.master.config(menu=self.menu)

        # add file menu
        self.file = tk.Menu(self.menu)
        self.file.add_command(label='Save ROIs and create XLSX-file', command=self.update_roi_dict)
        # self.file.add_command(label='Create XLSX', command=self.command_for_create_xlsx_button)
        # self.menu.add_cascade(label='File', menu=self.file)

        # add edit menu
        edit = tk.Menu(self.menu)
        edit.add_command(label='Erase Last ROI', command=self.erase_last)
        self.menu.add_cascade(label='Edit', menu=edit)

        # add tools menu
        tools = tk.Menu(self.menu)
        tools.add_command(label='Fixed Rectangle', command=self.choose_fixed)
        tools.add_command(label='Draw Diagonal', command=self.choose_diagonal)
        tools.add_command(label='Array of ROIs', command=self.choose_array_rois)
        tools.add_command(label='Whole Images', command=self.choose_whole_image)
        self.menu.add_cascade(label='Tools', menu=tools)

    def _resize_image(self, event):
        """
        Adjust shown image size, canvas size and
        slider width to resized main window.
        :param event: tkinter's event object
            Configure event.
        :return: nothing
        """
        # store previous size of window
        if self.already_resized:
            self.previous_size = min(self.new_height, self.new_width)
        # get new width and height of window
        self.new_width = self.master.winfo_width()  # actual width of main window
        self.new_height = self.master.winfo_height()  # actual height of main window
        # condition that checks whether window has been resized
        if self.already_resized:
            if np.abs(self.previous_size - min(self.new_height, self.new_width)) < 5:
                # print('pass %d' % self.counter_pass)
                self.counter_pass += 1
                pass
        self.already_resized = True
        # new size of the image
        if self.new_width < self.new_height - (self.slider_height + self.label_height):
            self.new_im_size = self.new_width
        else:
            self.new_im_size = self.new_height - (self.slider_height + self.label_height)
        # resizing coefficient
        self.resize_coef = min(self.new_height, self.new_width) / self.size_of_main_window

        self.size_of_main_window = min(self.new_height, self.new_width)
        self.image_heigth = self.background.winfo_height()  # actual height of slice image
        # position of slider
        self.z = self.slider.get() - 1
        # source of the shown image
        self.new_show_im_source = self.obj_arrays.all_images[self.z - 1]
        # open image with PIL
        self.new_image = Image.open(self.new_show_im_source)
        # make copy of the opened image
        self.new_img_copy = self.new_image.copy()
        # resize image copy according to actual main window size
        self.image = self.new_img_copy.resize((self.new_im_size, self.new_im_size))
        # put the resized image on canvas
        self.background.new_background_image = ImageTk.PhotoImage(self.image)
        self.background.itemconfig(self.slice_img, image=self.background.new_background_image)
        # resize canvas
        self.background.configure(width=self.new_im_size)
        self.background.configure(height=self.new_im_size)
        # resize the length of the slider
        self.slider['length'] = self.new_width

    def create_bindings(self):

        """
        Connect events to methods.
        :return: nothing.
        """
        # resize image method
        self.master.bind('<Configure>', self._resize_image)
        # click on left mouse button
        self.background.bind('<Button-1>', self.build_initial_coord)
        # release of left mouse button
        self.background.bind('<ButtonRelease-1>', self.draw)
        # bind motion event to display coordinates of mouse pointer
        self.background.bind('<Motion>', self.motion)

    def draw(self, event):
        """
        Select ROIs depending on selecting mode:
        'Fixed_ROI' or 'Draw_Diagonal'.
        Draw rectangles on canvas.
        Store their absolute coordinates in self.image_rect_coord.
        Store their resized coordinates in self.image_rect_coord_im.
        Store Rectangle objects in self.rectangles_dict.
        :param event: tkinter's event object
            <'ButtonRelease-1'> event.
        :return: nothing.
        """
        # the words 'absolute size, height, width etc.' mean size of ROI, image etc.
        # before resizing
        if self.tool_index == 'fixed':
            # then draw rectangles with fixed size (absolute size)
            rect_width = int(self.form.fixed_roi_width)  # absolute width of rectangle
            rect_height = int(self.form.fixed_roi_height)  # absolute height of rectangle
            # define coordinates of the left upper corner of rectangle (absolute values)
            l_up_corner_x = int(event.x * self.px_width / self.background.winfo_width())
            l_up_corner_y = int(event.y * self.px_height / self.background.winfo_height())
            # specify coordinates of rectangle's diagonal corners
            begin_rect_x = l_up_corner_x  # for the scores matrix
            begin_x_im = int(begin_rect_x * self.background.winfo_width() / self.px_width)  # on the canvas
            end_rect_x = l_up_corner_x + rect_width
            end_x_im = int(end_rect_x * self.background.winfo_width() / self.px_width)
            begin_rect_y = l_up_corner_y
            begin_y_im = int(begin_rect_y * self.background.winfo_height() / self.px_height)
            end_rect_y = l_up_corner_y + rect_height
            end_y_im = int(end_rect_y * self.background.winfo_height() / self.px_height)
            # draw rectangle on canvas
            rect_sel = self.background.create_rectangle(begin_x_im, begin_y_im, end_x_im, end_y_im,
                                                             outline=self.color_rect_not_stored)
            # store absolute coordinates of rectangle
            self.image_rect_coord.append((begin_rect_x,
                                          begin_rect_y,
                                          end_rect_x,
                                          end_rect_y))
            self.image_rect_coord_record.append((begin_rect_x,
                                          begin_rect_y,
                                          end_rect_x,
                                          end_rect_y))
            self.rect_coord_dict.update({self.basename_w_ext: self.image_rect_coord})
            # store the shown coordinates of rectangles
            self.image_rect_coord_im.append((begin_x_im,
                                          begin_y_im,
                                          end_x_im,
                                          end_y_im))
            self.rect_coord_dict_im.update({self.basename_w_ext: self.image_rect_coord_im})
            # store the rectangle in the list
            self.image_rectangles.append(rect_sel)
            self.rectangles_dict.update({self.basename_w_ext: self.image_rectangles})
            # subarray for roi
            # for key, path_to_image in zip(self.all_roi_dict, self.arrays_dict):
            #     self.current_array = self.arrays_dict[path_to_image]
            #     self.subarray_roi = self.current_array[l_up_corner_y : l_up_corner_y + rect_height,
            #                         l_up_corner_x: l_up_corner_x + rect_width]
            #     image_roi = self.all_roi_dict[key]
            #     image_roi.append(self.subarray_roi)
            #     print('shape_of_image_roi', np.array(image_roi).shape)
            #     self.all_roi_dict.update({key: image_roi})
                # image_roi = []
            # delete event coordinates
            del self.x_coord
            del self.y_coord
            # print('shape_of_image_roi_total', np.array(image_roi).shape)

        elif self.tool_index == 'diagonal':
            # coordinates are normalized to window size
            self.x_coord.append(event.x * self.px_width / self.background.winfo_width())
            self.y_coord.append(event.y * self.px_height / self.background.winfo_height())

            # get current slice
            self.z = self.slider.get() - 1  # "-1" because the first slice has number zero

            # specify coordinates of rectangle's diagonal corners
            begin_rect_x = int(self.x_coord[0])  # for the scores matrix
            begin_x_im = int(begin_rect_x * self.background.winfo_width() / self.px_width)  # on the canvas
            end_rect_x = int(self.x_coord[1])
            end_x_im = int(end_rect_x * self.background.winfo_width() / self.px_width)
            begin_rect_y = int(self.y_coord[0])
            begin_y_im = int(begin_rect_y * self.background.winfo_height() / self.px_height)
            end_rect_y = int(self.y_coord[1])
            end_y_im = int(end_rect_y * self.background.winfo_height() / self.px_height)
            # draw rectangle on canvas
            rect_sel = self.background.create_rectangle(begin_x_im, begin_y_im, end_x_im, end_y_im,
                                                             outline=self.color_rect_not_stored)
            # store the rectangle in the list
            self.image_rectangles.append(rect_sel)
            self.rectangles_dict.update({self.basename_w_ext: self.image_rectangles})
            # make possible to draw rectangle from all directions
            if begin_rect_x < end_rect_x:
                x0 = begin_rect_x
                x0_im = begin_x_im
                x1 = end_rect_x
                x1_im = end_x_im
            else:
                x1 = begin_rect_x
                x1_im = begin_x_im
                x0 = end_rect_x
                x0_im = end_x_im

            if begin_rect_y < end_rect_y:
                y0 = begin_rect_y
                y0_im = begin_y_im
                y1 = end_rect_y
                y1_im = end_y_im
            else:
                y1 = begin_rect_y
                y1_im = begin_y_im
                y0 = end_rect_y
                y0_im = end_y_im
            # set minimal size of ROI 5x5px
            if (x1 - x0) < 5:
                x1 = x0 + 5
            if (y1 - y0) < 5:
                y1 = y0 + 5
            self.subarray_roi = self.array[y0:y1, x0:x1]
            if len(self.subarray_roi) == 0:  # DEBUG
                print('x0: ', x0)
                print('x1: ', x1)
                print('y0: ', y0)
                print('y1: ', y1)
            # delete event coordinates
            del self.x_coord
            del self.y_coord
            # store coordinates of rectangle
            self.image_rect_coord.append((x0,
                                          y0,
                                          x1,
                                          y1))
            self.image_rect_coord_record.append((x0,
                                                 y0,
                                                 x1,
                                                 y1))
            self.rect_coord_dict.update({self.basename_w_ext: self.image_rect_coord})
            # store the shown coordinates of rectangles
            self.image_rect_coord_im.append((x0_im,
                                             y0_im,
                                             x1_im,
                                             y1_im))
            self.rect_coord_dict_im.update({self.basename_w_ext: self.image_rect_coord_im})
            # store the rectangle in the list
            self.image_rectangles.append(rect_sel)
            self.rectangles_dict.update({self.basename_w_ext: self.image_rectangles})
        # elif self.tool_index == 'array_roi':

    def erase_last(self):
        """
        Erase last ROI drawn on canvas.
        :return: nothing.
        """
        print('Last ROI has been deleted')
        try:
            # delete the last drawn rectangle from canvas
            self.background.delete(self.image_rectangles[-1])
            del self.image_rectangles[-1]
        except IndexError:
            pass
        try:
            # delete rectangle if it has been drawn on another image
            # and is shown as slided rectangle
            self.background.delete(self.slided_rectangles_list[-1])
            # delete last item of slided_rectangles_list
            del self.slided_rectangles_list[-1]
        except IndexError:
            pass
        try:
            # delete last roi coordinates from roi dictionary
            for key in self.all_roi_dict:
                roi_arr = self.all_roi_dict[key]
                del roi_arr[-1]
                self.all_roi_dict.update({key: roi_arr})
            print('im_roi:    ', np.array(roi_arr).shape)  # DEBUG
        except IndexError:
            pass

        try:
            # delete coordinates of rectangles
            del self.image_rect_coord_im[-1]
        except IndexError:
            pass

        try:
            del self.image_rect_coord[-1]
        except IndexError:
            pass
        print('%d ROIs remain' % (len(self.image_rectangles)))  # DEBUG

    def store_ROIs(self, *args):
        self.image_roi.append(self.subarray_roi)
        print(np.array(self.image_roi).shape)

    def update_roi_dict(self):
        """
        Update attribute all_roi_dict, when choosing
        menu 'Save ROIs and create XLSX-file'.
        :return: nothing.
        """
        print('ROIs are being saved. It can take some minutes')
        for coord in self.image_rect_coord:
            for key, path_to_file in zip(self.all_roi_dict, self.file_list):
                roi_arr = self.all_roi_dict[key]
                roi_arr.append(coord)
                self.all_roi_dict.update({key: roi_arr})
        for rect in self.image_rectangles:
            self.background.itemconfig(rect, outline=self.color_rect_stored)
        # change the color of resized rectangles
        self.color_rect_resized = '#00FF00'
        # clear rect coord array to not duplicate ROIs
        self.image_rect_coord = []
        # print(self.all_roi_dict)
        print('ROIs have been saved')
        global roi_processing_start_time
        roi_processing_start_time = time.time()
        obj_process_roi.execute_calc_nps_sorted()

    def choose_whole_image(self):
        """
        Select whole images as ROIs and store their pixel arrays
        into all_roi_dict.
        :return: nothing
        """
        # get minimal shape of images
        # minimal_shape = self.minimal_shape(dict_of_2d_arrays=self.arrays_dict)
        # min_rows = minimal_shape['rows']
        # min_columns = minimal_shape['columns']
        # iterate over all images
        for key_path in self.file_list:
            # update all_roi_dict
            key_image = os.path.basename(key_path)
            # self.all_roi_dict.update({key_image: np.array([
            #     self.arrays_dict[key_path][:min_rows][:min_columns]])})
            self.all_roi_dict.update({key_image: np.array([
                self.obj_arrays.create_base_array(key_path)['base_array']])})

    def minimal_shape(self, dict_of_2d_arrays):
        """
        Return minimal shape of 2d_arrays.
        :param dict_of_2d_arrays: dict of nd_arrays (2d)
        :return: dict with keys 'columns' and 'rows'
        """
        # initialize minimal shape
        min_rows = 10**10
        min_columns = 10**10
        # iterate over all keys of dictionary
        for key in dict_of_2d_arrays:
            # get 2d array in variable
            array_2d = dict_of_2d_arrays[key]
            num_of_columns = array_2d.shape[1]
            num_of_rows = array_2d.shape[0]
            # update minimal shape values
            if min_columns > num_of_columns:
                min_columns = num_of_columns
            if min_rows > num_of_rows:
                min_rows = num_of_rows
        return_dictionary = {'columns': min_columns,
                             'rows': min_rows}
        return return_dictionary

    def choose_fixed(self):
        """
        Select 'Fixed_ROIs' mode.
        Create form for choosing fixed ROI's size.
        :return: nothing
        """
        self.tool_index = 'fixed'
        self.dialog_window = tk.Toplevel(master=self.master)
        self.dialog_window.geometry('%dx%d+%d+%d' % (self.dialog_window_width,
                                                     self.dialog_window_height,
                                                     self.dialog_window_x,
                                                     self.dialog_window_y))
        self.dialog_window.title('Initial Data')
        self.form = CreateForm(master_main_window=self.dialog_window,
                               fields=self.fields,
                               values=self.values,
                               object_arrays=self.obj_arrays,
                               object_gui=obj_gui)
        pass

    def choose_array_rois(self):
        """
        Select 'Array_ROIs' mode.
        Create form for choosing parameters of array of ROIs.
        :return: nothing
        """
        self.tool_index = 'array_rois'
        self.dialog_window = tk.Toplevel(master=self.master)
        self.dialog_window.geometry('%dx%d+%d+%d' % (self.dialog_window_width_arr_roi,
                                                     self.dialog_window_height_arr_roi,
                                                     self.dialog_window_x_arr_roi,
                                                     self.dialog_window_y_arr_roi))
        self.dialog_window.title('Initial Data For Array Of ROIs')
        # if the variables have already been stored in JSON-file, read them from it
        if os.path.isfile('variables_info.txt'):
            with open('variables_info.txt', 'r') as file_to_read_info:
                read_dict = json.load(file_to_read_info)
            list_of_variables = [read_dict[key] for key in read_dict]
            self.values_array_rois = list_of_variables
        self.form_array_roi = CreateForm(master_main_window=self.dialog_window,
                               fields=self.fields_array_rois,
                               values=self.values_array_rois,
                               object_arrays=self.obj_arrays,
                               object_gui=obj_gui)
        pass

    def choose_diagonal(self):
        """
        Select mode 'Draw_Diagonal'
        :return: nothing
        """
        self.tool_index = 'diagonal'

    def build_initial_coord(self, event):
        """
        Store absolute coordinates of mouse pointer
        when clicking on left mouse button.
        :param event: tkinter's event object
             <'Button-1'> event.
        :return: nothing
        """
        self.x_coord = []
        self.y_coord = []
        self.x_coord.append(event.x * self.px_width / self.background.winfo_width())
        self.y_coord.append(event.y * self.px_height / self.background.winfo_height())
        return

    @staticmethod
    def create_aux_folder(folder_name, cur_fold=None):

        """
        Create auxiliary folder in the directory with executable py-file.

        :param folder_name: string
            Name of folder to be created (not path to it!)
        :param cur_fold: string
            Path to initial folder, where the new folder is to be created.
            If None (by default), the new folder is created in the same
            directory with this py-file.
        :return: string
            Absolute path to the created (or already existing) folder.
        """

        # current folder with py-file
        if cur_fold is None:
            cur_fold = os.path.dirname(os.path.abspath(__file__))
        # path to auxiliary folder
        aux_folder = cur_fold + '/' + folder_name
        # if the folder does not exist yet, create it
        if not os.path.exists(aux_folder):
            os.mkdir(aux_folder)
        # return path to folder
        return aux_folder