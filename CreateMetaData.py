from imports_nps import *


class CreateFormMetaData(tk.Frame):

    """
    Create dialog window for user input of metadata tag numbers.

    Attributes
    ----------
    name_of_json_metadata_settings : string
        Relative path to JSON (txt-file) containing string with metadata
        tags' numbers. Used to fill the form with recent settings.
    json_exists_settings : boolean
        Whether JSON (txt-file) containing string with metadata
        tags' numbers already exists.
    text : tkinter's Text object
        Widget containing user input of metadata settings. Is filled
        initially with either values from init_dict if JSON with settings
        does not exist yet, or with recent settings otherwise.
    ok_button_is_created : boolean
        Auxiliary boolean.
        True: Dialog window can be destroyed and program execution continued.

    Methods
    -------
    make_form()
        Create necessary widgets (Label, Text and Button)
        for the dialog window.
    fill_form(value)
        Fill Text widget with value
        (See parameter value of init of class CreateForMetadata).
    read_form()
        Read user input from text widget.
        Save settings to JSON.
        Destroy dialog window (necessary to continue
        the program execution).
    """

    def __init__(self, title, value, master_main_window):

        """

        :param title: string
            Title of dialog window.
        :param value: string or list of hexstrings
            string : Default string of hexnumbers for metadata_tags_list
                defined in init_dict. The variable is of this type if JSON
                with settings does not exist yet.
            list : If the JSON already exists, the settings string of JSON
                is scanned with RegEx and yields list of hexstrings denoting
                needed metadata tag numbers.
        :param master_main_window: tkinter's Tk object
            Master of dialog window.

        """

        # initial arrangements
        super().__init__(master_main_window)
        self.value = value
        self.title = title
        self.master_main_window = master_main_window

        # initialize names for JSONs
        # they will contain settings information
        # and result of program execution (metadata_dictionary)
        self.name_of_json_metadata_settings = 'meta_data_settings.txt'

        # boolean to check if the files already exist
        self.json_exists_settings = os.path.isfile(self.name_of_json_metadata_settings)

        # if JSON with settings already exists, rewrite default value
        if self.json_exists_settings:
            with open(self.name_of_json_metadata_settings, 'r') as file_to_read_info:
                self.value = file_to_read_info.read()

        # auxiliary boolean for destroying main_window
        # i.e. program can be executed after entering tag numbers
        self.ok_button_is_created = False

        # make form of dialog window
        self.make_form()
        # fill the form with default values
        self.fill_form(self.value)

        pass

    def make_form(self):

        """
        Create necessary widgets (Label, Text and Button)
        for the dialog window.

        :return: nothing
        """

        text_for_label = 'Please, enter your desired tags as described bellow:\n\n' \
                         '1) Enter tag pair splitting it by comma\n' \
                         '2) Separate adjacent tag pairs by entering new line\n' \
                         '3) If you wish to reach the subtags\' information,\n' \
                         '   just write parent tag pair followed by child tag pairs\n\n' \
                         'Example:\n' \
                         '        \'0x0040, 0x0275, 0x0032, 0x1060\' (press enter)\n' \
                         '        \'0x7005, 0x1002\' (press enter)\n' \
                         '        \'0x0905, 0x1030\' (press enter)\n' \
                         '         (click on button OK)'

        lab = tk.Label(width=50, text=text_for_label, anchor='w', justify='left')
        lab.pack()
        self.text = tk.Text(self.master_main_window, width=50, height=10)
        self.text.tag_configure("left", justify='left')
        self.text.pack()

        accept_button = tk.Button(master=self.master_main_window, text='OK',
                                  command=self.read_form, anchor='w')
        accept_button.pack()
        self.ok_button_is_created = True

    def fill_form(self, value):

        """
        Fill Text widget with value
        (See parameter value of init of class CreateForMetadata).
        :param value: string or list of hexstrings
            (See parameter value of init of class CreateForMetadata)
        :return: type of variable value
        """

        type_of_value = type(value)
        print(type_of_value)
        if type(value) is list:
            for item in value:
                for sub_item in item:
                    self.text.insert(END, hex(int(sub_item))+', ')
                self.text.insert(END, '\n')
        else:
            list_of_indices = StartClass.recognize_hex_numbers_in_string(settings_string=value)
            list_of_indices = [i for i in list_of_indices if len(i) > 0]
            for prop_index in list_of_indices:
                for tag_element in prop_index:
                    self.text.insert(END, tag_element + ', ')
                self.text.insert(END, '\n')
        return type_of_value

    def read_form(self):

        """
        Read user input from text widget.
        Save settings to JSON.
        Destroy dialog window (necessary to continue
        the program execution).
        :return: string
            (See attribute settings_string of class CreateFormMetadata)
        """

        self.settings_string = self.text.get(1.0, END)
        # write data into JSON

        if self.ok_button_is_created:
            with open(self.name_of_json_metadata_settings, 'w') as json_settings_file:
                json_settings_file.write(self.settings_string)
            self.master_main_window.destroy()

        return self.settings_string