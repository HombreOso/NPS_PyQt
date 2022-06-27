from imports_nps import *


class StartClass:
    """
    Start of the program.

    Create auxiliary folders;
    Create file list and file dict;
    Create window for specifying metadata to be extracted;
    Define static method create_base_array;
    Create PNG-images of dicoms to be shown in GUI.

    Attributes
        ----------
        acceptButtonIsAlreadyUsed : boolean
            Auxiliary boolean
            True: auto-fill of 'fixed'-tool dialog window with last
            set size of rectangular ROI;
            False: use values defined in GUI class' init (by default: 128x128)

        program_start : boolean
            Auxiliary boolean
            True: when creating an object of class CreateForm, the form for
            file exclusion is created;
            False: other forms are created depending on the value of tool_index
            attribute of an object of class GUI

        aux_folder_names : list of strings
            Names of auxiliary folders to be created at the start of the program:
                '01.2d_NPS_images': folder with 2d_NPS images (.png) of the last calculated ROIs;
                '02.One_D_NPS': matplotlib charts of 1d-NPS profiles saved as .png;
                '03.PNG_images': Dicoms that are transformed in .png-format, to be shown in GUI.

        whole_paths : list of strings
            Absolute paths to created auxiliary folders.

        file_exclusion_json : string
            Name of JSON containing last settings for file exclusion.

        im_height_dict : dict
            Keys : absolute paths to dcm-images;
            Values : the heights (in pixels) of the respective images.

        im_width_dict : dict
            Keys : absolute paths to dcm-images;
            Values : the widths (in pixels) of the respective images.

        metadata_tags_list : list of lists of hexstrings
            Each inner list contains even number of elements defining either tag (two elements) or
            tag and subtags (four and more elements). Each element is string of a hexadecimal number.
            For example: [['0x0008', '0x1030'], ['0x0040', '0x0275', '0x0032', '0x1060']] defines two tags:
            the second one is the subtag of tag ['0x0040']['0x0275']

        metadata_subdict : dict
            Dictionary based on metadata tag list, retrieving specified metadata from dicoms
            Keys : tag names;
            Values : values of tags.

        metadata_dict : dict of dicts
            Keys : absolute paths to dcm_images;
            Values : respective metadata_subdict.

        folder_with_images : string
            Absolute path to folder with all dicoms to be analyzed.

        filelist : list of strings
            Absolute paths to all images to be analyzed.

        filedict : dict of dicts
            Dict for sorting the attribute filelist.
            Outer dict:
                Keys : absolute paths to studies' folders;
                Values : inner dicts.
            Inner dict:
                Keys : absolute paths to series' folders;
                Values : list of files that are in respective series' folder.

        new_files : dict of dicts
            Dict containing filelist and filedict attributes.

        num_files_to_exclude_start : int
            Number of files to be excluded from the beginning of each series' folder.

        num_files_to_exclude_end : int
            Number of files to be excluded from the end of each series' folder.

        all_images : list of strings
            Absolute paths to all png-images of dicoms.

        Methods
        -------
        select_folder(self, title)
            Create dialog window for selecting folder with all images
            to be analyzed. Used to build attribute folder_with_images.

        create_dataset_dictionary(list_of_indices, dataset_dicom)
            Retrieve metadata from current dicom-file. Used to build attribute metadata_subdict.

        create_filelist(self, pathtoFiles, suffix_array)
            Search for files with specified extensions and build list of them.

        create_filedict(self, pathtoFiles, suffix_array)
            Search for files with specified extensions and build
            sorting dict of files to be analyzed.

        exclude_files(self, file_dict, file_list,
                      num_files_to_exclude_start,
                      num_files_to_exclude_end)
            Exclude specified number of files from each series folder
            and perform changes in filedict and filelist attributes
            of class StartClass.

        create_base_array(self, image_file)
            Read current dicom file and retrieve pixel array.
            Retrieve part of meta data and update attribute metadata_dict.

        rgb2gray(self, rgb)
            If we handle with RGB-image, convert it to grayscale.

        @staticmethod
        norm_2d_array(arr_2d, value_min, value_max)
            Normalize 2d-array to values between value_min and value_max.

        create_image_from_2d_array(self, arr_2d, filename)
            Normalize passed 2d_array between values 0 and 255 and create
            image saved as filename.

        create_png_image(self, key)
            Create .png-image from current dicom-file.

        @staticmethod
        create_aux_folder(folder_name)
            Create auxiliary folder in the directory with executable py-file.

        @staticmethod
        recognize_hex_numbers_in_string(settings_string)
            Recognize hexadecimal numbers in given string.



       """

    def __init__(self, suffixes, list_of_indices_raw):
        """
        :param suffixes: list of strings
            Suffixes of files to be found in selected directory
            (DICOMs or image files)
        :param list_of_indices_raw: list of strings
            Default list of tags of metadata to be extracted from DICOMs
            Specified in init_dict


        """

        print('Constructor of the class StartClass is being executed')
        # extensions of files to be found
        self.suffixes = suffixes
        # default list of tags for metadata
        self.list_of_indices_raw = list_of_indices_raw

        # auxiliary booleans
        # global acceptButtonIsAlreadyUsed
        # acceptButtonIsAlreadyUsed = False
        self.acceptButtonIsAlreadyUsed = False
        self.program_start = True

        # create auxiliary folders
        self.aux_folders_names = ['01.2d_NPS_images',
                                  '02.One_D_NPS',
                                  '03.PNG_images']
        self.whole_paths = list(map(StartClass.create_aux_folder, self.aux_folders_names))

        # name for json-file containing previous settings
        self.file_exclusion_json = 'file_exclusion_settings.txt'
        # dictionary for measurements of each image
        self.im_height_dict = {}
        self.im_width_dict = {}
        # initialize dictionary containing meta data
        # keys: paths to dicoms
        # values: part dictionaries with meta data
        self.metadata_dict = {}
        # collect all images in png-format
        self.all_images = []

        # create dialog window to specify part of meta data to be retrieved
        # creating dialog window for entering tag numbers
        dialog_window = tk.Tk()
        dialog_window.geometry('%dx%d+%d+%d' % (init_dict['main_window_width_md'],
                                                init_dict['main_window_height_md'],
                                                init_dict['left_upper_corner_x_md'],
                                                init_dict['left_upper_corner_y_md']
                                                ))
        # instantiate object of class CreateFormMetaData
        obj_create_form = CreateFormMetaData(title='Tag Numbers',
                                             value=init_dict['list_of_indices_raw'],
                                             master_main_window=dialog_window)
        dialog_window.mainloop()

        # recognize tag numbers
        self.metadata_tags_list = StartClass.recognize_hex_numbers_in_string(
            settings_string=obj_create_form.settings_string)

        # select folder with images
        self.folder_with_images = self.select_folder(
            title='Select folder with images')
        # create list of found images
        self.filelist = self.create_filelist(pathtoFiles=self.folder_with_images,
                                             suffix_array=self.suffixes)

        self.filedict = self.create_filedict(pathtoFiles=self.folder_with_images,
                                             suffix_array=self.suffixes)

        # create dialog window to exclude some files from folders
        fields = ['remove_begin', 'remove_end']
        values = [3, 3]
        if os.path.isfile(os.path.join(os.getcwd(), self.file_exclusion_json)):
            with open(self.file_exclusion_json, 'r') as file_to_read_info:
                read_dict = json.load(file_to_read_info)
            list_of_variables = [read_dict[key] for key in read_dict]
            values = list_of_variables

        main_window = tk.Tk()
        obj_exclude = CreateForm(master_main_window=main_window, object_gui=None,
                                 object_arrays=None, fields=fields,
                                 values=values, program_start=self.program_start)
        main_window.mainloop()
        self.num_files_to_exclude_start = obj_exclude.num_files_to_exclude_start
        self.num_files_to_exclude_end = obj_exclude.num_files_to_exclude_end
        self.program_start = False

        # exclude files from folders

        self.new_files = self.exclude_files(file_list=self.filelist, file_dict=self.filedict,
                                            num_files_to_exclude_start=self.num_files_to_exclude_start,
                                            num_files_to_exclude_end=self.num_files_to_exclude_end)
        self.filelist = self.new_files['file_list']
        self.filedict = self.new_files['file_dict']

        # self.create_image_arrays(filelist=self.filelist)
        # create png-images
        for num, key in enumerate(self.filelist):
            if num > 1:
                break
            self.all_images.append(self.create_png_image(key=key))

        print('Constructor of the class StartClass is done')

        pass

    @staticmethod
    def recognize_hex_numbers_in_string(settings_string):
        """
        Recognize hexadecimal numbers in given string.
        Used to build attribute metadata_tags_list.
        :param settings_string: string
            User input of tag numbers in dialog window.
        :return: list of hexadecimal strings
            (See attribute metadata_tags_list of class StartClass)
        """
        # initialize list for tag numbers
        list_of_indices = []
        # pattern for recognizing hex numbers using RegEx
        pattern = r'0x[\d\w]+'
        # iterate over lines in settings_string
        for string_line in settings_string.split('\n'):
            list_of_indices.append(re.findall(pattern=pattern,
                                              string=string_line))
        return list_of_indices

    @staticmethod
    def create_dataset_dictionary(list_of_indices, dataset_dicom):
        """
        Retrieve specified metadata from dicom-file.

        :param list_of_indices: list of hexstrings
            Tags' hexadecimal numbers. Attribute metadata_tags_list is a value
            of this parameter (see init of class StartClass).
        :param dataset_dicom: Dataset object
            Dataset object of current dicom-file
        :return: dataset_dict : dict
            (See attribute metadata_subdict in init of class StartClass).
        """

        # initialize dataset_dictionary
        dataset_dictionary = {}
        # iterate over indices in the passed list
        for prop_index in list_of_indices:
            if len(prop_index) < 2:
                continue
            first_index = prop_index[0]
            second_index = prop_index[1]
            # retrieve DataElement object
            try:
                d_element = dataset_dicom[first_index, second_index]
                # if sub indices are used
                if len(prop_index) > 2:
                    # iterate over indices in prop_index
                    for num_index, sub_index in enumerate(prop_index[2:]):
                        # iterate only over even indices of prop_index
                        if num_index % 2 != 0:
                            continue
                        d_element = d_element[0][sub_index,
                                                 prop_index[num_index + 3]]

                # get value of property
                value_of_property = d_element.value
                # get the name of property
                try:
                    name_of_property = d_element.name
                except IndexError:
                    name_of_property = ''
                    print('problem with: ', d_element)
                dataset_dictionary.update({name_of_property: value_of_property})
            except KeyError:
                dataset_dictionary.update({'undefined_tag': 'undefined'})
        return dataset_dictionary

    def select_folder(self, title):
        """
        Create dialog window for selecting folder with all images
        to be analyzed.
        :param title: titlle of dialog window;
        :return:
        Absolute path to folder with all images to be analyzed
        (See attribute folder_with_images of class StartClass)
        """
        root_2 = tk.Tk()
        selected_folder = askdirectory(master=root_2, title=title)
        root_2.destroy()
        root_2.mainloop()
        return selected_folder

    def create_filelist(self, pathtoFiles, suffix_array):
        """
        Search for files with specified extensions and build list of files to be analyzed.
        :param pathtoFiles: string
            Path to folder with all images to be analyzed
        :param suffix_array: list of strings
            Extensions of files to be searched for.
        :return: list of strings
            List of paths to all found images
        """

        print('create_filelist is being executed')
        # list of paths to all found files
        lstFiles = []
        # find out how many files found
        counter_files = 0
        sorted_file_names = []
        # list of all directories with found files
        all_dir_names = []
        # empty dict to sort files in directories
        directories_dict = {}
        # subdict = {}
        # search for files with certain extensions
        for dirName, subdirList, fileList in os.walk(pathtoFiles):
            for filename in fileList:
                # if any of extensions are present in filename
                if any(suffix.lower() in filename.lower() for suffix in suffix_array):
                    lstFiles.append(os.path.join(dirName, filename))
                    filepath = os.path.join(dirName, filename)
                    # base name of current directory with file
                    basedirname = os.path.basename(dirName)
                    classdirname = os.path.dirname(os.path.dirname(dirName))
                    try:  # update dict if the key-value-pair already exists
                        temp_dict = directories_dict[classdirname]
                    except KeyError:
                        sub_dict = {}
                        directories_dict.update({classdirname: sub_dict})
                        temp_dict = directories_dict[classdirname]
                    try:
                        temp_list = temp_dict[basedirname]
                        temp_list.append(filepath)
                        temp_dict.update({basedirname: temp_list})
                        directories_dict.update({classdirname: temp_dict})
                    except KeyError:
                        # or create key-value pair

                        # get subdict
                        temp_subdict = directories_dict[classdirname]
                        temp_subdict.update({basedirname: [filepath]})
                        directories_dict.update({classdirname: temp_subdict})

        # create array of only file names, sorted generally (based on whole path)
        for fnamepath in natsorted(lstFiles, alg=ns.IGNORECASE):
            sorted_file_names.append(os.path.basename(fnamepath))
        # create array of only folder names, sorted generally (based on whole path)
        for fdir in natsorted(lstFiles, alg=ns.IGNORECASE):
            all_dir_names.append(os.path.basename(os.path.dirname(fdir)))
        # print base names of found files
        for q in natsorted(lstFiles, alg=ns.IGNORECASE):
            print(os.path.basename(q))
        # print the number of found files
        print('%d files have been found' % len(lstFiles))
        print('create_filelist is done')
        return natsorted(lstFiles, alg=ns.IGNORECASE, key=lambda x: x.split('_')[-1])

    def create_filedict(self, pathtoFiles, suffix_array):

        """
        Search for files with specified extensions and build
        sorting dict of files to be analyzed.
        :param pathtoFiles: string
            Path to folder with all images to be analyzed
        :param suffix_array: list of strings
            Extensions of files to be searched for.
        :return: dict of dicts
            (See attribute filedict of class StartClass)
        """

        print('create_filedict is being executed')

        # list of paths to all found files
        lstFiles = []
        # find out how many files found
        counter_files = 0
        sorted_file_names = []
        # list of all directories with found files
        all_dir_names = []
        # empty dict to sort files in directories
        directories_dict = {}
        # subdict = {}
        # search for files with certain extensions
        for dirName, subdirList, fileList in os.walk(pathtoFiles):
            for filename in fileList:
                # # counter used to exclude files from the start of the list
                # counter_exclude_start = 1
                # # counter used to exclude file from the end of the list
                # counter_exclude_end = len(fileList)
                # if any of extensions are present in filename
                if any(suffix.lower() in filename.lower() for suffix in suffix_array):
                    lstFiles.append(os.path.join(dirName, filename))
                    filepath = os.path.join(dirName, filename)
                    # base name of current directory with file
                    basedirname = os.path.basename(dirName)
                    classdirname = os.path.dirname(dirName)
                    try:  # update dict if the key-value-pair already exists
                        temp_dict = directories_dict[classdirname]
                    except KeyError:
                        sub_dict = {}
                        directories_dict.update({classdirname: sub_dict})
                        temp_dict = directories_dict[classdirname]
                    try:
                        temp_list = temp_dict[basedirname]
                        temp_list.append(filepath)
                        temp_dict.update({basedirname: temp_list})
                        directories_dict.update({classdirname: temp_dict})
                    except KeyError:
                        # or create key-value-pair

                        # get subdict
                        temp_subdict = directories_dict[classdirname]
                        temp_subdict.update({basedirname: [filepath]})
                        directories_dict.update({classdirname: temp_subdict})

        # create array of only file names, sorted generally (based on whole path)
        for fnamepath in natsorted(lstFiles, alg=ns.IGNORECASE):
            sorted_file_names.append(os.path.basename(fnamepath))
        # create array of only folder names, sorted generally (based on whole path)
        for fdir in natsorted(lstFiles, alg=ns.IGNORECASE):
            all_dir_names.append(os.path.basename(os.path.dirname(fdir)))
        # print base names of found files
        # for q in natsorted(lstFiles, alg=ns.IGNORECASE):
        #     print(os.path.basename(q))
        # # print the number of found files
        # print('%d files have been found' % len(lstFiles))
        print('create_filedict is done')

        return directories_dict

    def exclude_files(self, file_dict, file_list,
                      num_files_to_exclude_start,
                      num_files_to_exclude_end):

        """
        Exclude specified number of files from each series folder
        and perform changes in filedict and filelist attributes
        of class StartClass.
        :param file_dict: dict of dict
            Attribute filedict before the exclusion of files.
        :param file_list: list of strings
            Attribute filelist before the exclusion of files.
        :param num_files_to_exclude_start: int
            (See attribute with the same name of class StartClass)
        :param num_files_to_exclude_end:
            (See attribute with the same name of class StartClass)
        :return: dict
            (See attribute new_files of class StartClass)
        """

        print('exclude_files is being executed')

        if num_files_to_exclude_end == 0 and num_files_to_exclude_start == 0:
            ret_dict = {'file_list': file_list,
                        'file_dict': file_dict}

            print('exclude_files is done')

            return ret_dict

        # empty list for files to exclude
        files_to_exclude = []

        # drop files in file_dict

        # iterate over folders
        for folder in natsorted(file_dict.keys(), key=lambda f: f.split('_')[-1]):
            temp_dict = file_dict[folder]
            # iterate over series
            for series in natsorted(temp_dict.keys(), key=lambda f: f.split('_')[-1]):
                # get list of files in series
                temp_list = temp_dict[series]
                # drop files
                try:
                    new_temp_list = temp_list[num_files_to_exclude_start: -num_files_to_exclude_end]
                    files_to_exclude += temp_list[:num_files_to_exclude_start]
                    files_to_exclude += temp_list[-num_files_to_exclude_end:]
                    temp_dict.update({series: new_temp_list})
                except IndexError:
                    print('There less files in the folder %s/%s, than attempted to exclude' % (folder, series))
            file_dict.update({folder: temp_dict})

        # get rid of repeated file names
        files_to_exclude = set(files_to_exclude)
        files_to_exclude = list(files_to_exclude)

        for file_to_remove in files_to_exclude:
            file_list.remove(file_to_remove)

        file_list = natsorted(file_list, alg=ns.IGNORECASE)

        ret_dict = {'file_list': file_list,
                    'file_dict': file_dict}

        print('exclude_files is done')

        return ret_dict

    def create_base_array(self, image_file):

        """
        Read current dicom file and retrieve pixel array.
        Retrieve part of meta data
        and update attribute metadata_dict
        :param image_file: string
            Absolute path to current image.
        :return: dict
            Key: 'base_array' : Value: pixel array of current image;
            Key: 'meatdata_subdict' : Value: dict of specified metadata;
            Key: 'whole_dcm' : Value: Dataset object of current dicom.
        """

        print('create_base_array is being executed')

        # if we handle with dicom-file
        if os.path.basename(image_file)[-4:] == '.dcm':
            try:
                # create data element object from dicom
                image_dcm = pydicom.dcmread(image_file, force=True)
            except:
                print('\n\n\nThere is a problem with the file: ')
                print(image_file)
            gc.collect()
            self.array = image_dcm.pixel_array
            self.metadata_subdict = StartClass.create_dataset_dictionary(
                list_of_indices=self.metadata_tags_list,
                dataset_dicom=image_dcm
            )
            metadata_subdict = self.metadata_subdict
            self.metadata_dict.update({image_file: self.metadata_subdict})

        # if we handle file with another file-extension
        else:
            # read image as list with PIL-library
            img = Image.open(image_file)
            # convert list into numpy-array
            self.array = np.array(img)
            # if we have colored image
            if len(self.array.shape) > 2:
                self.array = self.rgb2gray(self.array)
            self.metadata_subdict = {'undefined': 'undefined'}
            metadata_subdict = {'undefined': 'undefined'}

            # if the image is not a dicom, store 'undefined' in metadata_dict
            self.metadata_dict.update({image_file: {'undefined_tag': 'undefined'}})
            image_dcm = ''
        # image measurements
        self.px_height = self.array.shape[0]
        self.px_width = self.array.shape[1]
        # image file base name without extension
        self.basename = os.path.basename(image_file)[:-4]
        # image file base name with extension
        self.basename_w_ext = os.path.basename(image_file)

        ret_dict = {'base_array': self.array.astype(np.int16),
                    'metadata_subdict': metadata_subdict,
                    'whole_dcm': image_dcm}

        print('create_base_array is done')

        return ret_dict

    def rgb2gray(self, rgb):

        """
        If we handle with RGB-image, convert it to grayscale.
        :param rgb: ndarray
            ndarray (3d) of image to be transformed.
        :return: ndarray
            ndarray (2d) of the converted image
        """

        print('rgb2gray is being executed')

        # formula for converting of colored image to grayscale

        print('rgb2gray is done')

        return np.dot(rgb[..., :3], [0.299, 0.587, 0.114])

    @staticmethod
    def norm_2d_array(arr_2d, value_min, value_max):

        """
        Normalize 2d-array to values between value_min and value_max.
        :param arr_2d: ndarray (2d)
            Array to be normalized.
        :param value_min: int or float
            Minimal value of normalized array.
        :param value_max: int or float
            Maximal value of normalized array.
        :return: ndarray (2d)
            Noirmalized array.
        """

        print('norm_2d_array is being executed')

        max_value = np.max(arr_2d)
        min_value = np.min(arr_2d)
        normalized_2d_array = value_min + (np.array(arr_2d) - min_value) / (max_value - min_value) * value_max

        print('norm_2d_array is done')

        return normalized_2d_array

    @staticmethod
    def create_image_from_2d_array(arr_2d, filename):

        """
        Normalize passed 2d_array between values 0 and 255 and create image saved as filename.

        :param arr_2d: ndarray (2d)
            Array the image to be created from.
        :param filename: string
            Absolute path to created image.
        :return: string
            filename
        """

        print('create_image_from_2d_array is being executed')

        image_array = np.array(StartClass.norm_2d_array(arr_2d=arr_2d,
                                                        value_min=0,
                                                        value_max=255))
        cv2.imwrite(filename=filename, img=image_array)

        print('create_image_from_2d_array is done')

        return filename

    def create_png_image(self, key):

        """
        Create .png-image from current dicom-file.
        :param key: string
            Absolute path to dicom file
        :return: string
            Absolute path to created image.
        """

        print('create_png_image is being executed')

        # pixel array for current image
        curr_array = self.create_base_array(key)['base_array']
        # name of image file without extension
        name_of_file_without_extension = os.path.basename(key)[:-4]
        # create png-image
        png_image_path = StartClass.create_image_from_2d_array(arr_2d=curr_array,
                                                               filename='03.PNG_images/%s.png' %
                                                                        name_of_file_without_extension)
        # store path to png image in list
        # self.all_images.append(png_image_path)
        # return self.all_images

        print('create_png_image is done')

        return png_image_path

    @staticmethod
    def create_aux_folder(folder_name):

        """
        Create auxiliary folder in the directory with executable py-file.
        :param folder_name: string
            Name of folder to be created (not path to it!)
        :return: string
            Absolute path to the created folder.
        """
        # current folder with py-file
        cur_fold = os.path.dirname(os.path.abspath(__file__))
        # path to auxiliary folder
        aux_folder = cur_fold + '/' + folder_name
        # if the folder does not exist yet, create it
        if not os.path.exists(aux_folder):
            os.mkdir(aux_folder)
        # return path to folder
        return aux_folder