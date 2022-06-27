from imports_nps import *


class ProcessROI:
    """
    Calculate NPS and create files with results.

    Attributes
    ----------
    workbook_series : XlsxWriter's Workbook object
        Workbook containing NPS info for each image in current series.
        Each worksheet (except the last one) contains NPS info for current dcm-image.
        Last worksheet contains averaged NPS info ansd is called 'averaged'.
        Near description is to find in the manual.
    workbook_averaged : XlsxWriter's Workbook object
        Workbook containing all averaged worksheets of attributes workbook_series
        for current study.
        I.e. each worksheet contains averaged NPS info for current series.
    workbook_summary : openpyxl's Workbook object
        Workbook containing summarized information of averaged NPS xlsx-files.
    worksheet_averaged : XlsxWriter's Worksheet object
        Worksheet of attribute workbook_averaged.
    worksheet_summary : openpyxl'S Worksheet object
        Worksheet of attribute workbook_summary.
    col_number, col_folder, col_series, col_peak_freq,
    col_peak_value, col_left_dev, col_right_dev,
    col_area, col_ave_m_HU : strings
        Excel letters for each information column in workbook_summary.
    metadata_columns : list of strings
        List of Excel letetrs for columns containing metadata info in
        workbook_summary.
    all_roi_dict : dict of dict of lists of tuples
        (See attribute all_roi_dict of class GUI)
    sorted_all_roi_dict : dict of dicts
        Dict with same structure as attribute filedict of class StartClass.
        The lists of files in series folder are transformed into dictionaries:
        Keys : absolute path to image in current series folder
        Values : list of tuples with ROIs' diagonal coordinates:
            x0 - x coordinate of left upper corner
            y0 - y coordinate of left upper corner
            x1 - x coordinate of right lower corner
            y1 - y coordinate of right lower corner
    image_rect_coord : list
        (See attribute image_rect_coord of class GUI)
    image_rect_coord_record : list
        (See attribute image_rect_coord_record of class GUI)
    roi_image_mean_HU : list of floats
        List of mean HU for each ROI in current image.
    image_sd : list of floats
        List of standard deviation for each ROI in current image.
    all_mean_HU_dict : dict of lists of floats
        Dict of attributes roi_image_mean_HU for current series folder.
        Keys : paths to dcm-image file.
        Values : respective attribute roi_image_mean_HU
            (See description of roi_image_mean_HU above)
    all_SD_dict : dict of lists of floats
        Dict of attributes image_sd for current series folder.
        Keys : paths to dcm-image file.
        Values : respective attribute image_sd
            (See description of image_sd above)
    nps_image : list of dicts
        For current image.
        List of range_dict attributes for each ROI
        on current image.
        For each ROI on image, range_dict consists of:
            'values': interpolated NPS list of the ROI
            'frequencies': respective frequencies
            'AUC': area under not interpolated 1d-NPS profile
            'integral_of_2d_nps': integral of 2d NPS of teh ROI
                                    (not interpolated!!!)
    all_nps_dict : dict_ of lists of dicts
        For images in current series folder.
        Keys : paths to images in current series folder
        Values : nps_image attributes for respective image
    all_average_nps : dict of dicts
        For images in current series folder.
        Keys : absolute paths to images in current series folder.
            Values : dict
                Key : 'value'
                Value : NPS list of averaged ROIs' NPS lists for respective image.
                Key : 'frequencies'
                Value : list of respective frequencies.
    mean_of_averaged_nps_dict : dict
        For current series folder.
        'values' : NPS list averaged among all images in current series folder.
        'frequencies' : respective frequencies.
    peak_info_dict_ave : dict
        Peak information of NPS list averaged among images in current series folder.
        Keys : 'mean_value' (peak NPS value)
               'mean_freq' (peak NPS frequency)
               'left_dev' (freq distance between peak freq and freq, at which NPS
                           sinks under 60% of peak NPS value when moving to left)
               'right_dev' (freq distance between peak freq and freq, at which NPS
                            sinks under 60% of peak NPS value when moving to right)


    Methods
    -------

    """

    def __init__(self, *, obj_roi, obj_arr, fit_order,
                 crop_perc, useFitting, im_height_in_mm,
                 im_width_in_mm, extensions, trunc_percentage,
                 useCentralCropping, start_freq_range, end_freq_range, step,
                 useTruncation, multipleFiles, pixel_size_in_mm, first_data_set):

        """
        Start initialiazation and sorting of all_roi_dict.

        (See all_roi_dict attribute's description in class GUI).

        :param obj_roi: instance of class GUI
            Used to get access to its attributes:
            - all_roi_dict
            - master
            - image_rect_coord_record
            - array
        :param obj_arr: instance of class StartClass
            Used to get access to its attribute:
            - metadata_subdict
            and method create_base_array()
        :param fit_order: int (1 or 2)
            Order of 2d fit of image for background removal.
        :param crop_perc: float

        :param useFitting: boolean
            Choose method of background removal.
            True: 2d fitting is used (order is defined by attribute
                fit_order);
            False: mean value subtraction is used.
        :param im_height_in_mm: float or string 'undefined'
            Height of current dcm-image in mm.
        :param im_width_in_mm: float or string 'undefined'
            Width of current dcm-image in mm.
        :param extensions: list of strings
            Extensions of files to be searched for in selected order.
            (Probably not needed in this class).
        :param trunc_percentage: float
            Percentage of maximum value, under which NPS is truncated
            at higher frequencies.
            (Probably not needed in this class).
        :param x0: int
            For the mode 'Array_ROIs':
            absolute x coordinate of left upper corner of
            left upper ROI in ROIs array. (???)
        :param x1:
        :param y0:
        :param y1:
        :param useCentralCropping:
        :param start_freq_range: float
            Start frequency of interest. Specified in init_dict.
        :param end_freq_range: float
            End frequency of interest. Specified in init_dict.
        :param step: float
            Interval between frequency samples in freq array.
        :param useTruncation: boolean
            Whether use truncation as explained in description
            of attribute trunc_percentage.
        :param multipleFiles: not needed
        :param pixel_size_in_mm: float
            Default pixel size in mm. used when dealing with
            not-DICOMs.
        :param first_data_set: boolean
            Specify folder structure of dataset.
            Near description is to find in manual.
        """

        print('Constructor of class ProcessROI is being executed')

        # ************Initialization of attributes*********************

        # all xlsx-files
        self.all_xlsx_range = []
        self.all_xlsx = []
        # dictionary for averaged nps and freqs
        self.all_average_nps = {}
        # info about all averaged nps
        self.all_nps_peak_info = {}
        self.all_nps_peak_info_ave = {}
        # paths to all cropped images
        self.all_cropped_im = []
        # paths to all one d nps images
        self.all_1_d_nps = []
        # collect all mean HU for each ROI
        self.image_mean_HU = []
        # collect mean HU for each image
        self.all_mean_HU_dict = {}
        # collect all st dev in dictionary
        self.all_SD_dict = {}
        # dictionary for roi sizes in each image
        self.roi_size_dict = {}
        # dictionary for AUC
        self.auc_dict = {}
        # dictionary for integral of 2d NPS
        self.integral_2d_nps_dict = {}
        # whether central cropping should be applied
        self.useCentralCropping = useCentralCropping
        # whether lower nps should be deleted
        self.useTruncation = useTruncation
        # extensions of image files
        self.extensions = extensions
        # image measurements in mm
        self.im_height_in_mm = im_height_in_mm
        self.im_width_in_mm = im_width_in_mm
        # truncate lower nps
        self.trunc_percentage = trunc_percentage
        # maximal size of the image (height or width)
        self.max_size = max(im_height_in_mm, im_width_in_mm)
        # cropping percentage
        self.crop_perc = crop_perc
        # fitting order for 2d-fit
        self.fit_order = fit_order
        # whether fitting should be applied
        # or background removal should be used
        self.useFitting = useFitting
        # remove raw csv-files
        self.files_to_remove = []
        self.pixel_size_in_mm = pixel_size_in_mm
        self.multipleFiles = multipleFiles
        # declaring attributes, that are specified later
        self.nps = []
        self.new_dict = {}
        # type of data set
        self.first_data_set = first_data_set
        self.object_roi = obj_roi
        self.object_arr = obj_arr
        self.fit_order = fit_order
        self.all_roi = self.object_roi.all_roi_dict
        self.directories_dict = self.object_arr.filedict
        self.metadata_subdict = self.object_arr.metadata_subdict
        # list for paths to Excel-files
        self.xlsx_paths = []

        # numbers of rows and columns of ROI pixel array
        self.px_width = self.object_roi.array.shape[1]
        self.px_height = self.object_roi.array.shape[0]
        # self.arrays_dict = self.object_roi.arrays_dict
        self.all_roi_dict = self.object_roi.all_roi_dict
        self.image_rect_coord = self.object_roi.image_rect_coord
        self.image_rect_coord_record = self.object_roi.image_rect_coord_record

        # ************End of initialization*********************

        # get metadata and prepare for creating summary_info xlsx
        self.headers_list = ['Number', 'Folder', 'Series', 'peak_freq', 'peak_value',
                             'left_dev', 'right_dev', 'area', 'Integral',
                             'ave_m_HU', 'ave_SD']

        self.metadata_headers = [key for key in self.metadata_subdict]
        self.headers_list += self.metadata_headers

        # initialize start row (row of first series in current folder)
        self.start_row = 3

        # create xlsx-file, that will contain summary information
        self.name_workbook_summary = 'Summary_information.xlsx'
        self.workbook_summary = opxl.Workbook()

        # create single worksheet in this workbook
        self.worksheet_summary = self.workbook_summary.active

        # get column letters
        self.col_number = opxl.utils.get_column_letter(1)
        self.worksheet_summary.column_dimensions[self.col_number].width = 6.73
        self.col_folder = opxl.utils.get_column_letter(2)
        self.worksheet_summary.column_dimensions[self.col_folder].width = 30.00
        self.col_series = opxl.utils.get_column_letter(3)
        self.worksheet_summary.column_dimensions[self.col_series].width = 5.18
        self.col_peak_freq = opxl.utils.get_column_letter(4)
        self.worksheet_summary.column_dimensions[self.col_peak_freq].width = 9.09
        self.col_peak_value = opxl.utils.get_column_letter(5)
        self.worksheet_summary.column_dimensions[self.col_peak_value].width = 9.2
        self.col_left_dev = opxl.utils.get_column_letter(6)
        self.col_right_dev = opxl.utils.get_column_letter(7)
        self.col_area = opxl.utils.get_column_letter(8)
        self.col_int_2d_nps = opxl.utils.get_column_letter(9)
        self.col_ave_m_HU = opxl.utils.get_column_letter(10)
        self.worksheet_summary.column_dimensions[self.col_ave_m_HU].width = 10.00
        self.col_ave_SD = opxl.utils.get_column_letter(11)

        self.metadata_columns = [opxl.utils.get_column_letter(i + 12) for i
                                 in range(len(self.metadata_headers))]

        for col in self.metadata_columns:
            self.worksheet_summary.column_dimensions[col].width = 33.00

        # name of xlsx-file
        self.name_xlsx = 'NPS_ranged_GUI.xlsx'
        # letters as column names in excel
        self.letters_for_excel = ['A', 'B', 'C', 'D', 'E',
                                  'F', 'G', 'H', 'I', 'J',
                                  'K', 'L', 'M', 'N', 'O',
                                  'P', 'Q', 'R', 'S', 'T',
                                  'U', 'V', 'W', 'X', 'Y',
                                  'Z', 'AA', 'AB', 'AC', 'AD',
                                  'AE', 'AF', 'AG', 'AH', 'AI',
                                  'AJ', 'AK', 'AL']

        # freq range
        self.start_freq = start_freq_range
        self.end_freq = end_freq_range
        self.num_of_steps = int((self.end_freq - self.start_freq) // step + 1)
        self.freq_range = np.linspace(start=self.start_freq,
                                      stop=self.end_freq,
                                      num=self.num_of_steps)
        # sort all_roi_dict
        self.sorted_all_roi_dict = ProcessROI.sort_all_roi_dict(directories_dict=self.directories_dict,
                                                                all_roi_dict=self.all_roi)

        print('Constructor of class ProcessROI is done')

    def execute_calc_nps_sorted(self):

        """
        Main method of the class ProcessROI.

        Calculate NPS by iterating over pixel array of each ROI.
        Create xlsx-files with results.
        :return: nothing
        """

        ave_folder = GUI.create_aux_folder(cur_fold=os.getcwd(), folder_name='Only_averaged_sheets')

        # iterate over keys of the passed dict, i.e. folder paths
        for self.num_folder, self.folder in enumerate(self.sorted_all_roi_dict):
            # log the process
            print('\n\nFolder %s is been processed: %d of %d\n\n' % (os.path.basename(self.folder), self.num_folder + 1,
                                                                     len(self.sorted_all_roi_dict)))

            if self.first_data_set:
                self.folder_part = os.path.basename(self.folder)
            else:
                self.folder_part = ProcessROI.drop_part_of_name(
                    name=os.path.basename(self.folder),
                    pattern_of_dropped_part=r' \- \d+',
                    dropped_from_end=True)

            # create workbook for only averaged sheets
            name_averaged_workbook = ave_folder + '/' + self.folder_part + '.xlsx'
            self.workbook_averaged = xlsx.Workbook(name_averaged_workbook)

            # iterate over series
            for self.num_series, series in enumerate(self.sorted_all_roi_dict[self.folder]):

                global start_time_series
                start_time_series = time.time()

                if self.first_data_set:
                    self.serie_part = serie
                    self.folder_part = os.path.basename(self.folder)
                else:
                    self.serie_part = ProcessROI.drop_part_of_name(
                        name=series,
                        pattern_of_dropped_part=r'\w*\d*_',
                        dropped_from_end=False)[1:]
                    self.folder_part = ProcessROI.drop_part_of_name(
                        name=os.path.basename(self.folder),
                        pattern_of_dropped_part=r' \- \d+',
                        dropped_from_end=True)
                # log the process
                print('\nseries %s: %d of %d\nFolder %d of %d\n' % (
                series, self.num_series + 1, len(self.sorted_all_roi_dict[self.folder]),
                self.num_folder + 1,
                len(self.sorted_all_roi_dict)
                ))
                # if len(series) > 3:
                #     print('This is not a folder with images. Skip')
                #     continue
                # create folder Results
                # GUI.create_aux_folder(cur_fold=folder, folder_name='Results')

                GUI.create_aux_folder(cur_fold=self.folder, folder_name='Results_%s' % self.folder_part)

                # create worksheet to write averaged data into
                self.worksheet_averaged = self.workbook_averaged.add_worksheet(name=self.serie_part)

                name_for_xlsx = self.folder \
                                + '/Results_%s/' % (self.folder_part) \
                                + self.folder_part + \
                                self.serie_part + '.xlsx'
                # open new workbook in Excel
                self.workbook_series = xlsx.Workbook(name_for_xlsx)
                self.execute_nps_comp(all_roi_dict=self.sorted_all_roi_dict[self.folder][series])
                print('++++++++++\n'
                      'execution time per series: %f seconds\n' % (time.time() - start_time_series))
                # self.execute_nps_comp(all_roi_dict=self.sorted_all_roi_dict[self.folder][series])
                num_remaining_folders = len(self.sorted_all_roi_dict) - self.num_folder
                num_rem_series_in_folder = len(self.sorted_all_roi_dict[self.folder]) - self.num_series - 1
                time_for_one_series = time.time() - start_time_series
                remaining_time = ((num_remaining_folders - 1) * len(self.sorted_all_roi_dict[self.folder]) +
                                  num_rem_series_in_folder) * time_for_one_series
                remaining_hours = remaining_time // 3600
                remaining_minutes = (remaining_time - remaining_hours * 3600) // 60
                remaining_seconds = remaining_time - remaining_minutes * 60
                print(
                    '%d hours, %d minutes, %f seconds remain' % (remaining_hours, remaining_minutes, remaining_seconds))
            self.workbook_averaged.close()
            # increment start row for summary workbook
            self.start_row += self.num_series + 2
        self.workbook_summary.save(self.name_workbook_summary)
        if init_dict['destroy_main_window']:
            self.object_roi.master.destroy()

    def execute_nps_comp(self, all_roi_dict):

        """
        Calculate NPS and side variables inside series folder loop.

        :param all_roi_dict: dict
            (See attribute sorted_all_roi_dict)
        :return: nothing
        """
        # flush dict of ave nps for the current serie
        self.all_average_nps = {}
        # dictionary to store nps for each image
        self.all_nps_dict = {}

        # flush dictionaries
        self.all_mean_HU_dict = {}
        self.all_SD_dict = {}
        self.integral_2d_nps_dict = {}
        self.auc_dict = {}
        # iterate through all images
        for num_of_image, self.key_image in enumerate(all_roi_dict):

            # initialize list of image ROIs' AUC
            image_auc_list = []
            # initialize list of image ROI's integral of 2d NPS
            image_integral_2d_nps_list = []

            data_from_dicom = self.object_arr.create_base_array(self.key_image)
            metadata_from_dicom = data_from_dicom['whole_dcm']
            try:
                pixel_spacing = [float(i) for i in metadata_from_dicom['0x0028', '0x0030'].value]
            except ValueError:
                pixel_spacing = self.pixel_size_in_mm
                print('There is no property \'Pixel Spacing\'')
            except TypeError:
                pixel_spacing = [0.378, 0.378]
            pixel_array_image = data_from_dicom['base_array']

            # if new series begins
            if num_of_image == 0:
                self.metadata = data_from_dicom['metadata_subdict']

            # build dict of mean HU and SD

            self.build_all_mean_HU_SD_dict(array_to_operate=pixel_array_image,
                                           all_roi_dict=all_roi_dict,
                                           key=self.key_image)
            print('ROIs on image %s are being processed: %d of %d; '
                  'Folder %d of %d; '
                  'series %d of %d ' % (os.path.basename(self.key_image),
                                        num_of_image + 1,
                                        len(all_roi_dict),
                                        self.num_folder + 1,
                                        len(self.sorted_all_roi_dict),
                                        self.num_series + 1,
                                        len(self.sorted_all_roi_dict[self.folder])))
            # counter_roi_inside_image = 0
            # list to store all nps for current image
            self.nps_image = []
            # collect lengths of one d nps of rois in image
            self.lengths = []
            self.image_roi_sizes = []
            # iterate through all rois inside one image
            for num_of_roi, self.item_roi in enumerate(all_roi_dict[self.key_image]):
                subarray = pixel_array_image[self.item_roi[1]:self.item_roi[3], self.item_roi[0]:self.item_roi[2]]
                # print progress
                print('ROI is being processed: %d of %d' % (num_of_roi + 1, len(all_roi_dict[self.key_image])))
                # basename of image without extensions
                self.basename = os.path.basename(self.key_image)[:-4]
                # basename of image with extension
                self.basename_w_ext = os.path.basename(self.key_image)
                # array from the image
                array_to_operate = subarray
                # get shape of the ROI
                shape_of_roi = array_to_operate.shape
                # store the shape in list
                self.image_roi_sizes.append(shape_of_roi)
                # # apply fitting of the image
                # self.create_pol_fit(array_to_operate)
                # create dictionary of nps and respective frequencies (unranged)
                dict = self.compute_nps(array=array_to_operate, pixel_spacing=pixel_spacing)
                AUC = dict['AUC']
                integral_of_2d_NPS = dict['integral_of_2d_NPS']
                # append ROI's AUC und integral of 2d NPS to resp. lists
                image_auc_list.append(dict['AUC'])
                image_integral_2d_nps_list.append(dict['integral_of_2d_NPS'])
                if self.useTruncation:  # setting in init_dict
                    # truncate lower nps and respective frequencies
                    self.new_dict = self.truncate_nps_freq(dict=dict)
                else:
                    # use nps_dict as it is
                    self.new_dict = dict
                # create raw csv-file (with empty rows between data)
                # self.all_xlsx.append(self.create_xlsx_file_nps(dict=self.new_dict, prefix='One_D_NPS_'))
                # create nps range

                # get equations of lines connecting each two points of nps array
                eqs_prop = ProcessROI.nps_equation(self.new_dict['values'])
                # initialize empty list for ranged NPS (with specified s´distance
                # between samples)
                nps_range = []
                # we need this array because freq_range is restricted through
                # size of ROI, frequencies beyond the last available freq
                # should be truncated (dropped)
                new_freq_range = []
                # iterate through frequencies in freq_range
                for item_freq in self.freq_range:
                    try:
                        nps_range.append(self.get_current_nps(freq_array=self.new_dict['frequencies'],
                                                              freq_value=item_freq))
                        new_freq_range.append(item_freq)
                    except ValueError:
                        # if there are no more frequencies available
                        # print('finished')
                        # print('nps range: ', len(nps_range))
                        break
                # nps_range = list(map(fut.partial(self.get_current_nps, freq_array=self.new_dict['frequencies'],
                #                                                            eqs=eqs_prop), self.freq_range))
                range_dict = {'values': nps_range,
                              'frequencies': new_freq_range,
                              'AUC': AUC,
                              'integral_of_2d_NPS': integral_of_2d_NPS}

                # store ranged nps and resp. freq in a list
                self.nps_image.append(range_dict)
                assert len(nps_range) == len(new_freq_range)
                self.lengths.append(len(range_dict['values']))
                # print('continued:  ', self.lengths)

            # update dict for AUC and integral of 2d NPS
            self.auc_dict.update({self.key_image: image_auc_list})
            self.integral_2d_nps_dict.update({self.key_image: image_integral_2d_nps_list})

            # average stored nps
            averaged_dict = self.average_roi_nps(list_of_dict=self.nps_image)
            self.all_average_nps.update({self.key_image: averaged_dict})
            self.roi_size_dict.update({self.key_image: self.image_roi_sizes})

            # recognize all peaks in nps-array
            peaks = ProcessROI.collect_all_max_peaks_nps(averaged_dict)
            # handle peak info
            peak_info_dict = self.handle_peak_info(peak_dict=peaks,
                                                   all_val_arr=averaged_dict['values'],
                                                   all_freq_arr=averaged_dict['frequencies'])
            self.all_nps_peak_info.update({self.key_image: peak_info_dict})

            self.all_nps_dict.update({self.key_image: self.nps_image})
        # create mean HU and SD info dictionaries
        # self.build_all_mean_HU_SD_dict(all_roi_dict=all_roi_dict)
        # self.build_all_sd_dict(all_roi_dict=all_roi_dict,
        #                        all_mean_dict=self.all_mean_HU_dict)
        # print('SD:  ', self.all_SD_dict)
        # print('mean HU:  ', self.all_mean_HU_dict)
        # calculate mean of averaged nps
        self.mean_of_averaged_nps_dict = ProcessROI.mean_of_ave_nps(all_average_nps=self.all_average_nps)
        # recognize all peaks in nps-array
        peaks_ave = ProcessROI.collect_all_max_peaks_nps(self.mean_of_averaged_nps_dict)
        # handle peak info
        self.peak_info_dict_ave = self.handle_peak_info(peak_dict=peaks_ave,
                                                        all_val_arr=self.mean_of_averaged_nps_dict['values'],
                                                        all_freq_arr=self.mean_of_averaged_nps_dict['frequencies'])
        # self.all_nps_peak_info_ave.update({self.key_image: self.peak_info_dict_ave})
        # calculate SD of mean HU
        self.sd_of_mean_HU_dict = ProcessROI.sd_of_dictionary(dict=self.all_mean_HU_dict)
        # calculate SD of SD
        self.sd_of_sd_dict = ProcessROI.sd_of_dictionary(dict=self.all_SD_dict)
        # get total mean values for mean_HU and SD
        self.total_mean_HU = ProcessROI.mean_of_mean(all_values_dict=self.all_mean_HU_dict)
        self.total_mean_sd = ProcessROI.mean_of_mean(all_values_dict=self.all_SD_dict)
        # create workbook for displaying results
        # self.workbook_series = xlsx.Workbook(self.name_xlsx)
        self.create_xlsx_file_nps(all_nps_dict=self.all_nps_dict)
        self.workbook_series.close()
        pass
        return

    @staticmethod
    def sort_all_roi_dict(directories_dict, all_roi_dict):
        """
        Sort passed all_roi_dict to reproduce
        directory structure of dcm-images data set
        (see description below).

        :param directories_dict: dict of dicts of lists of strings
            (See description of attribute filedict of class StartClass)
        :param all_roi_dict: dict of lists of tuples
            (See decription of attribute all_roi_dict of class GUI)
        :return: sorted all_roi_dict
            Keys : paths to study folder
            Values : dicts
                Keys : paths to series folders
                Values : dict
                    Keys : paths to image file
                    Values : lists of tuples containing coordinates of ROIs:
                        - x coordinate of upper left corner
                        - y coordinate of upper left corner
                        - x coordinate of lower right corner
                        - y coordinate of lower right corner

        """

        print('sort_all_roi_dict is being executed')
        # empty dict for sorted ROIs
        sorted_all_roi_dict = {}
        total_files = len(all_roi_dict.keys())
        # iterate over keys of all_roi_dict, i.e. file names
        for numf, file_name_prim in enumerate(natsorted(all_roi_dict.keys(), key=lambda f: f.split('_')[-1])):
            local_start_time = time.time()
            print('Progress: file %d of %d' % ((numf + 1), total_files))
            # iterate over the keys of directories_dict
            for classdirname in natsorted(directories_dict.keys(), key=lambda f: f.split('_')[-1]):
                # update dict
                # sorted_all_roi_dict.update({classdirname: {}})
                # iterate over keys of subdict
                subdict = directories_dict[classdirname]
                for serie_name in natsorted(subdict.keys(), key=lambda f: f.split('_')[-1]):
                    # update dict
                    # sorted_all_roi_dict[classdirname].update({serie_name: {}})
                    # iterate over the files in file list
                    for file_name_second in subdict[serie_name]:
                        # compare key of all_roi_dict and filename
                        if file_name_prim in file_name_second:
                            try:
                                temp_dict_prim = sorted_all_roi_dict[classdirname]
                            except KeyError:
                                sorted_all_roi_dict.update({classdirname: {}})
                                temp_dict_prim = sorted_all_roi_dict[classdirname]

                            try:
                                temp_dict = temp_dict_prim[serie_name]
                            except KeyError:
                                temp_dict_prim.update({serie_name: {}})
                                temp_dict = temp_dict_prim[serie_name]

                            temp_dict.update({file_name_prim: all_roi_dict[file_name_prim]})
                            sorted_all_roi_dict[classdirname].update({serie_name: temp_dict})
            duration_for_loop = time.time() - local_start_time
        print('sort_all_roi_dict is done')

        return sorted_all_roi_dict

    def build_all_mean_HU_SD_dict(self, all_roi_dict, array_to_operate, key):

        """
        Calculate mean HU and standard deviation for each ROI
        on the current image and update respective dictionaries
        all_mean_HU_dict and all_SD_dict (See description in class' docs)

        :param all_roi_dict: dict
            (See description of attribute sorted_all_roi_dict).
        :param array_to_operate: ndarray (2d)
            Current ROI's pixel array.
        :param key: string
            Path to current dcm-image file.
        :return: nothing
        """

        # all mean HU for the current image
        roi_image_mean_HU = []
        # all mean sd for current image
        image_sd = []
        # iterate through all rois in image
        for coord in all_roi_dict[key]:
            # get pixel array of current roi
            roi_array = array_to_operate[coord[1]:coord[3], coord[0]:coord[2]]

            # calculate mean HU
            mean_HU = np.mean(roi_array)
            roi_image_mean_HU.append(mean_HU)

            # calculate SD
            # build homogen mean matrix
            mean_matrix = np.ones(shape=np.array(roi_array).shape) * mean_HU
            # calculate difference between roi image and mean image
            diff_matrix = roi_array - mean_matrix
            # flatten diff matrix to access all its elements easier
            diff_flattened = diff_matrix.ravel()
            # calculate SD for current ROI
            sd_roi = np.sqrt(np.mean([i ** 2 for i in diff_flattened]))
            image_sd.append(sd_roi)
        self.all_mean_HU_dict.update({key: roi_image_mean_HU})
        self.all_SD_dict.update({key: image_sd})

        pass

    @staticmethod
    def mean_of_ave_nps(all_average_nps):
        """
        Averaging of passed nps values dict
        among all images in current series folder.
        :param all_average_nps: dict of lists of dicts
            Keys : paths to images in current series folder.
            Values : list range_dict attribute for each ROI.
                (See attribute range_dict)
        :return: dict
            (Key :) 'values' : (Value :) nps list averaged
        """
        averaged_nps_as_list = []
        for key in all_average_nps:
            averaged_nps_as_list.append(all_average_nps[key]['values'])
            frequens = all_average_nps[key]['frequencies']
        mean_of_averaged_nps = np.mean(np.array(averaged_nps_as_list), axis=0)
        mean_of_averaged_nps_dict = {'values': mean_of_averaged_nps,
                                     'frequencies': frequens}
        return mean_of_averaged_nps_dict

    @staticmethod
    def sd_of_dictionary(dict):
        """
        Calculate standard deviation of list values of given dict.

        :param dict: dict
            Keys : whatever keys;
            Values : lists of numeric values;
        :return: dict
            Keys : the same keys as of dict argument;
            Values : sd value of respective list.
        """

        # build array from dictionary
        sd_dict = {}
        for key in dict:
            one_d_array = dict[key]
            mean_value = np.mean(one_d_array)
            squared_diff_list = []
            for item in one_d_array:
                squared_diff = (item - mean_value) ** 2
                squared_diff_list.append(squared_diff)
            sd = np.sqrt(np.mean(squared_diff_list))
            sd_dict.update({key: sd})

        return sd_dict

    def average_roi_nps(self, list_of_dict):
        """
        Build dictionary of nps lists averaged among ROIs in each image.

        :param list_of_dict: list_of_dict
            (See attribute nps_image)
        :return: dict of dicts
            Keys : absolute paths to images in current series folder.
            Values : dict
                Key : 'value'
                Value : NPS list of averaged ROIs' NPS lists for respective image.
                Key : 'frequencies'
                Value : list of respective frequencies.
        """

        # initialize lists for nps and resp freqs
        values_to_average = []
        resp_freq_to_average = []
        # get max length of roi nps and its index
        max_length = max(self.lengths)
        max_length_idx = np.argmax(self.lengths)
        # iterate through all rois nps in image
        for roi_item_dict in list_of_dict:
            values = roi_item_dict['values']
            frequencies = roi_item_dict['frequencies']

            # fill lacking items with zeros

            # length difference with the longest nps
            len_diff = max_length - len(values)
            # convert values und freqs to python lists
            values = list(values)
            frequencies = list(frequencies)
            values += [0] * len_diff
            frequencies += [0] * len_diff
            # store transformed nps values and freqs in lists
            values_to_average.append(values)
            resp_freq_to_average.append(frequencies)
        # get mean array of value arrays
        averaged_nps = np.mean(values_to_average, axis=0)
        # max_length_idx tells us, which ROI has the largest NPS range
        # then the frequencies array of this ROI is retrieved from nps_image
        averaged_freqs = list_of_dict[max_length_idx]['frequencies']
        # store averaged value and frequencies in one dictionary
        averaged_dict = {'values': averaged_nps,
                         'frequencies': averaged_freqs}
        return averaged_dict

    # method is used to get total average values from all_mean_HU_dict and all_sd_dict
    @staticmethod
    def mean_of_mean(all_values_dict):

        """
        Build mean value of numerical values of given dictionary.
        :param all_values_dict: dict
            Keys : Any
            Values : single numerical values
        :return: mean value of the values
        """

        mean_of_mean_list = []
        for key in all_values_dict:
            mean_of_mean_list.append(np.mean(all_values_dict[key]))
        mean_of_mean_value = np.mean(mean_of_mean_list)
        return mean_of_mean_value

    def compute_nps(self, array, pixel_spacing):

        """
        Compute 2d and 1d NPS of given pixel array.

        :param array: ndarray (2d)
            Pixel array of current ROI.
        :param pixel_spacing: tuple of two floats
            Pixel spacing of dcm-image in y and
            x direction.
        :return: dict
            Keys : 'values' - 1d NPS of ROI (not interpolated),
                   'frequencies' - respective frequencies,
                   'AUC' - area under 1d NPS profile,
                   'integral_of_2d_nps' - as in the name.
        """

        # if image measurements in mm are undefined
        # the default image sizing is applied
        if self.im_width_in_mm == 'undefined':
            self.im_width_in_mm = self.px_width * self.pixel_size_in_mm
        if self.im_height_in_mm == 'undefined':
            self.im_height_in_mm = self.px_height * self.pixel_size_in_mm
        # mean pixel value of whole image
        mean_value = np.mean(array)
        # transform list into numpy array
        # to access the array's properties
        np_arr = np.array(array)
        # get ROI size
        roi_width = np_arr.shape[0]
        roi_height = np_arr.shape[1]
        # maximal size of the array (height or width)
        max_size = max(np_arr.shape)
        # building mean value array (background)
        mean_arr = mean_value * np.ones(np_arr.shape)
        # if 2d fitting should be used
        if self.useFitting:
            # self.polyfit is the 2d-fit of the image
            detrended_arr = array - self.pol_fit
        else:
            detrended_arr = array - mean_arr
        # create file of detrended image
        # StartClass.create_image_from_2d_array(arr_2d=detrended_arr,
        #                             filename='09.Detrended_images/Detrended_image__' +
        #                                      self.basename + '__.png')
        # apply FFT to detrended image
        DFT_list = np.fft.fftshift(np.fft.fft2(detrended_arr))
        # calculate 2d-NPS
        # nps = 1 / self.px_width / self.px_height * np.abs(DFT_list)**2
        # nps = (self.pixel_size_in_mm ** 2) / self.px_width / self.px_height * np.abs(DFT_list) ** 2
        nps = 1 / roi_height ** 2 / roi_width ** 2 * np.abs(DFT_list) ** 2
        integral_of_2d_NPS = np.sum(nps)

        # create file of 2d-NPS-image
        StartClass.create_image_from_2d_array(arr_2d=nps,
                                              filename='01.2d_NPS_images/NPS_2D__' +
                                                       self.basename + '__.jpg')
        # building 1d-NPS from 2d_NPS using radial average
        nps_1d = ProcessROI.radial_mean(nps)
        AUC = np.sum(nps_1d)
        # self.nps_norm = self.norm_array(arr_to_normalize=nps_1d,
        #                                 all_val_array=nps_1d)
        # freqs = np.fft.fftfreq(max_size, self.im_width_in_mm/10/self.px_width)[:max_size // 2]
        # calculate respective frequencies (line pairs per cm)
        # freqs = np.fft.fftfreq(max_size, self.im_width_in_mm/10/self.px_width)[:max_size // 2]
        freqs = np.fft.fftfreq(max_size, pixel_spacing[0] / 10)[:max_size // 2]
        # dictionary with all NPS- and freq-values, that will be
        # truncated afterwards
        nps_dict = {'values': nps_1d,
                    'frequencies': freqs,
                    'integral_of_2d_NPS': integral_of_2d_NPS,
                    'AUC': AUC}
        return nps_dict

    @staticmethod
    def drop_part_of_name(name, pattern_of_dropped_part, dropped_from_end):

        """
        Recognize part of name and drop it.

        :param name: string
            String to be truncated.
        :param pattern_of_dropped_part: raw string
            RegEx-pattern of part to be dropped.
        :param dropped_from_end: boolean
            True: if dropped part is at the left end of string.
            False: if dropped part is at the right end of string.
        :return: string
            Truncated string.
        """

        # DEBUG_dropped_part = re.findall(pattern=pattern_of_dropped_part, string=name)
        dropped_part = re.findall(pattern=pattern_of_dropped_part, string=name)[0]
        if dropped_from_end:
            used_part = name[:-(len(dropped_part))]
        else:
            used_part = name[(len(dropped_part) - 1):]
        return used_part

    def create_xlsx_file_nps(self, all_nps_dict):

        """
        Create several xlsx-files with results:

            - <foldername_seriesname>.xlsx (for each series folder;
                                            with info on all ROIs' NPS-values, ended with 'averaged'-worksheet
                                            saved in folder 'Results' inside each study-folder)
            - <foldername>.xlsx (for each study;
                                 with all collected averaged-worksheets from previous files
                                 saved in executive file's dir in dir 'Only_averaged_worksheets')
            - Summary_information.xlsx (with summarized information from foldername.xlsx-files
                                        saved in executive file's dir)

        :param all_nps_dict: dict
            Dictionary containing NPS info for each ROI in each image. Has following
            structure:

            {'path_to_image_0': [roi_0 = {'values': [],
                                        'frequencies' [],
                                        'AUC': ...,
                                        'integral_of_2d_NPS':...},
                                roi_1 = {'values': [],
                                        'frequencies' [],
                                        'AUC': ...,
                                        'integral_of_2d_NPS':...},
                            ...],
            'path_to_image_1': ...}

        :return: nothing
        """

        # iterate through all images
        for num_of_image, image_key in enumerate(all_nps_dict):
            # print progress
            print('Writing worksheets in xlsx-file: %d of %d' % (num_of_image + 1, len(all_nps_dict)))
            # counter for roi in image multiplied by 2
            counter_roi = 0
            worksheet = self.workbook_series.add_worksheet(os.path.basename(image_key)[:-4])
            for item_nps_dict in all_nps_dict[image_key]:
                val_arr = item_nps_dict['values']
                freq_arr = item_nps_dict['frequencies']

                # initialization of cells in worksheet
                row = 2
                col = counter_roi

                # headers of the table
                worksheet.write(1, counter_roi, 'Lp')
                worksheet.write(1, counter_roi + 1, 'NPS')
                worksheet.write(0, counter_roi, 'ROI_%d' % (counter_roi // 2 + 1))
                worksheet.write(0, counter_roi + 1, '%dx%d px' % (self.roi_size_dict[image_key][counter_roi // 2][0],
                                                                  self.roi_size_dict[image_key][counter_roi // 2][1]))

                for frequency, value_nps in zip(freq_arr, val_arr):
                    worksheet.write(row, col, frequency)
                    worksheet.write(row, col + 1, value_nps)
                    row += 1  # next row

                counter_roi += 2
            # retrieve mean of AUC and integral of 2d NPS for the current image
            AUC = np.mean(self.auc_dict[image_key])
            integral_of_2d_NPS = np.mean(self.integral_2d_nps_dict[image_key])

            row_ave = 2
            col_ave = counter_roi + 1
            # averaged nps data
            worksheet.write(row_ave - 2, col_ave, 'averaged')
            worksheet.write(row_ave - 1, col_ave, 'Lp')
            worksheet.write(row_ave - 1, col_ave + 1, 'NPS')
            for frequency, value_nps in zip(self.all_average_nps[image_key]['frequencies'],
                                            self.all_average_nps[image_key]['values']):
                worksheet.write(row_ave, col_ave, frequency)
                worksheet.write(row_ave, col_ave + 1, value_nps)
                row_ave += 1  # next row

            # create a new Chart object
            chart = self.workbook_series.add_chart({'type': 'line'})
            # configure the chart
            chart.add_series({'values': '=%s!$%s$3:$%s$%d' % (os.path.basename(image_key)[:-4],
                                                              self.letters_for_excel[counter_roi + 2],
                                                              self.letters_for_excel[counter_roi + 2],
                                                              len(self.all_average_nps[image_key]['frequencies']) + 2),
                              'categories': '%s!$%s$3:$%s$%d' % (os.path.basename(image_key)[:-4],
                                                                 self.letters_for_excel[counter_roi + 1],
                                                                 self.letters_for_excel[counter_roi + 1],
                                                                 len(self.all_average_nps[image_key][
                                                                         'frequencies']) + 2),
                              'name': os.path.basename(image_key),
                              'legend': False,
                              'trendline': {'type': 'polynomial',
                                            'order': 3,
                                            'line': {
                                                'color': 'red',
                                                'width': 1,
                                                'dash_type': 'long_dash',
                                            },
                                            'display_equation': True,
                                            }})
            chart.set_x_axis({'name': 'Line pairs per cm'})
            chart.set_y_axis({'name': 'NPS_1D_averaged'})
            # Insert the chart into the worksheet.
            worksheet.insert_chart('%s1' % self.letters_for_excel[counter_roi + 3], chart)

            # additional information about size of cropped image
            # and characteristics of nps curve

            worksheet.write(19, counter_roi + 4, 'max_peak_nps')
            worksheet.write(20, counter_roi + 4, 'max_peak_freq')
            worksheet.write(19, counter_roi + 5, self.all_nps_peak_info[image_key]['mean_value'])
            worksheet.write(20, counter_roi + 5, self.all_nps_peak_info[image_key]['mean_freq'])
            worksheet.write(21, counter_roi + 4, 'left_dev')
            worksheet.write(22, counter_roi + 4, 'right_dev')
            worksheet.write(21, counter_roi + 5, self.all_nps_peak_info[image_key]['left_dev'])
            worksheet.write(22, counter_roi + 5, self.all_nps_peak_info[image_key]['right_dev'])

            # area under NPS-curve
            worksheet.write(24, counter_roi + 4, 'area')
            worksheet.write(24, counter_roi + 5, AUC)

            # integral of 2d NPS
            worksheet.write(25, counter_roi + 4, 'Integral_2d_NPS')
            worksheet.write(25, counter_roi + 5, integral_of_2d_NPS)

            # fitting info
            if self.useFitting:
                worksheet.write(17, counter_roi + 4, 'Fitting')
                worksheet.write(17, counter_roi + 5, self.fit_order)
            else:
                worksheet.write(17, counter_roi + 4, 'BG_remove')
            # make column wider
            worksheet.set_column(first_col=counter_roi + 4, last_col=counter_roi + 4, width=20)

            # write info about mean HU and standard deviation
            row_mean_HU_SD_info = 19
            col_mean_HU_SD_info_header = counter_roi + 7
            col_mean_HU = col_mean_HU_SD_info_header + 1
            col_SD = col_mean_HU + 1
            col_x_coord = col_SD + 1
            col_y_coord = col_x_coord + 1
            for mean_HU, SD, coord in zip(self.all_mean_HU_dict[image_key],
                                          self.all_SD_dict[image_key],
                                          self.image_rect_coord_record):
                worksheet.write(row_mean_HU_SD_info, col_mean_HU_SD_info_header,
                                'ROI_%d' % (row_mean_HU_SD_info - 18))
                worksheet.write(row_mean_HU_SD_info, col_mean_HU, mean_HU)
                worksheet.write(row_mean_HU_SD_info, col_SD, SD)
                worksheet.write(row_mean_HU_SD_info, col_x_coord, coord[0])
                worksheet.write(row_mean_HU_SD_info, col_y_coord, coord[1])
                row_mean_HU_SD_info += 1
            worksheet.write(18, counter_roi + 8, 'Mean_HU')
            worksheet.write(18, counter_roi + 9, 'SD')
            worksheet.write(18, counter_roi + 10, 'x_coord')
            worksheet.write(18, counter_roi + 11, 'y_coord')

            worksheet.write(27, counter_roi + 4, 'averaged_Mean_HU')
            worksheet.write(28, counter_roi + 4, 'averaged_SD')
            worksheet.write(29, counter_roi + 4, 'SD_of_Mean_HU')
            worksheet.write(30, counter_roi + 4, 'SD_of_SD')

            worksheet.write(row_mean_HU_SD_info + 1, col_mean_HU_SD_info_header,
                            'averaged')
            worksheet.write(row_mean_HU_SD_info + 2, col_mean_HU_SD_info_header,
                            'SD')
            worksheet.write(row_mean_HU_SD_info + 1, col_mean_HU,
                            np.mean(self.all_mean_HU_dict[image_key]))
            worksheet.write(row_mean_HU_SD_info + 1, col_SD,
                            np.mean(self.all_SD_dict[image_key]))

            worksheet.write(27, counter_roi + 5, np.mean(self.all_mean_HU_dict[image_key]))
            worksheet.write(28, counter_roi + 5, np.mean(self.all_SD_dict[image_key]))
            worksheet.write(29, counter_roi + 5, np.mean(self.sd_of_mean_HU_dict[image_key]))
            worksheet.write(30, counter_roi + 5, np.mean(self.sd_of_sd_dict[image_key]))

            # write sd of mean HU and SD
            worksheet.write(row_mean_HU_SD_info + 2, col_mean_HU,
                            np.mean(self.sd_of_mean_HU_dict[image_key]))
            worksheet.write(row_mean_HU_SD_info + 2, col_SD,
                            np.mean(self.sd_of_sd_dict[image_key]))
        worksheet_ave = self.workbook_series.add_worksheet('averaged')
        val_arr = self.mean_of_averaged_nps_dict['values']
        freq_arr = self.mean_of_averaged_nps_dict['frequencies']

        # initialization of cells in worksheet
        row = 2
        col = 0

        # headers of the table
        worksheet_ave.write(0, 0, 'Total average')
        worksheet_ave.write(1, 0, 'Lp')
        worksheet_ave.write(1, 0 + 1, 'NPS')

        self.worksheet_averaged.write(0, 0, 'Total average')
        self.worksheet_averaged.write(1, 0, 'Lp')
        self.worksheet_averaged.write(1, 0 + 1, 'NPS')
        # worksheet.write(0, 1, 'ROI_%d' % (1 // 2 + 1))
        # worksheet.write(0, 1 + 1,
        #                 '%dx%d px' % (self.roi_size_dict[image_key][1 // 2][0],
        #                               self.roi_size_dict[image_key][1 // 2][1]))

        for frequency, value_nps in zip(freq_arr, val_arr):
            worksheet_ave.write(row, col, frequency)
            worksheet_ave.write(row, col + 1, value_nps)

            self.worksheet_averaged.write(row, col, frequency)
            self.worksheet_averaged.write(row, col + 1, value_nps)
            row += 1  # next row

        # additional information about size of cropped image
        # and characteristics of nps curve

        worksheet_ave.write(19 - 4, 1 + 3, 'max_peak_nps')
        worksheet_ave.write(20 - 4, 1 + 3, 'max_peak_freq')
        worksheet_ave.write(19 - 4, 1 + 4, self.peak_info_dict_ave['mean_value'])
        worksheet_ave.write(20 - 4, 1 + 4, self.peak_info_dict_ave['mean_freq'])
        worksheet_ave.write(21 - 4, 1 + 3, 'left_dev')
        worksheet_ave.write(22 - 4, 1 + 3, 'right_dev')
        worksheet_ave.write(21 - 4, 1 + 4, self.peak_info_dict_ave['left_dev'])
        worksheet_ave.write(22 - 4, 1 + 4, self.peak_info_dict_ave['right_dev'])

        self.worksheet_averaged.write(19 - 4, 1 + 3, 'max_peak_nps')
        self.worksheet_averaged.write(20 - 4, 1 + 3, 'max_peak_freq')
        self.worksheet_averaged.write(19 - 4, 1 + 4, self.peak_info_dict_ave['mean_value'])
        self.worksheet_averaged.write(20 - 4, 1 + 4, self.peak_info_dict_ave['mean_freq'])
        self.worksheet_averaged.write(21 - 4, 1 + 3, 'left_dev')
        self.worksheet_averaged.write(22 - 4, 1 + 3, 'right_dev')
        self.worksheet_averaged.write(21 - 4, 1 + 4, self.peak_info_dict_ave['left_dev'])
        self.worksheet_averaged.write(22 - 4, 1 + 4, self.peak_info_dict_ave['right_dev'])

        # writing info averaged Mean_HU, averaged SD, and area
        worksheet_ave.write(24 - 4, 1 + 3, 'Int of 2d-NPS')
        worksheet_ave.write(26 - 4, 1 + 3, 'averaged Mean_HU')
        worksheet_ave.write(27 - 4, 1 + 3, 'averaged SD')

        worksheet_ave.write(24 - 4, 1 + 4, np.mean(
            [self.integral_2d_nps_dict[key] for key in self.integral_2d_nps_dict]
        ))
        worksheet_ave.write(26 - 4, 1 + 4, self.total_mean_HU)
        worksheet_ave.write(27 - 4, 1 + 4, self.total_mean_sd)

        self.worksheet_averaged.write(24 - 4, 1 + 3, 'Int of 2d-NPS')
        self.worksheet_averaged.write(26 - 4, 1 + 3, 'averaged Mean_HU')
        self.worksheet_averaged.write(27 - 4, 1 + 3, 'averaged SD')

        self.worksheet_averaged.write(24 - 4, 1 + 4, np.mean(
            [self.integral_2d_nps_dict[key] for key in self.integral_2d_nps_dict]
        ))
        self.worksheet_averaged.write(26 - 4, 1 + 4, self.total_mean_HU)
        self.worksheet_averaged.write(27 - 4, 1 + 4, self.total_mean_sd)

        # make column wider
        worksheet_ave.set_column(first_col=4, last_col=4, width=20)
        self.worksheet_averaged.set_column(first_col=4, last_col=4, width=20)

        # info about averaged mean_HU and SD
        worksheet_ave.write(19 - 4, 1 + 7, 'mean_HU')
        worksheet_ave.write(19 - 4, 1 + 8, 'SD')
        worksheet_ave.write(20 - 4, 1 + 6, 'averaged')
        worksheet_ave.write(20 - 4, 1 + 7, self.total_mean_HU)
        worksheet_ave.write(20 - 4, 1 + 8, self.total_mean_sd)

        self.worksheet_averaged.write(19 - 4, 1 + 7, 'mean_HU')
        self.worksheet_averaged.write(19 - 4, 1 + 8, 'SD')
        self.worksheet_averaged.write(20 - 4, 1 + 6, 'averaged')
        self.worksheet_averaged.write(20 - 4, 1 + 7, self.total_mean_HU)
        self.worksheet_averaged.write(20 - 4, 1 + 8, self.total_mean_sd)

        # create a new Chart object
        chart_ave = self.workbook_series.add_chart({'type': 'line'})
        chart_averaged = self.workbook_averaged.add_chart({'type': 'line'})
        # configure the chart
        chart_ave.add_series({'values': '=%s!$%s$3:$%s$%d' % ('averaged',
                                                              'B',
                                                              'B',
                                                              len(self.mean_of_averaged_nps_dict['frequencies']) + 2),
                              'categories': '%s!$%s$3:$%s$%d' % ('averaged',
                                                                 'A',
                                                                 'A',
                                                                 len(self.mean_of_averaged_nps_dict[
                                                                         'frequencies']) + 2),
                              'name': 'Total Average',
                              'legend': False,
                              'trendline': {'type': 'polynomial',
                                            'order': 3,
                                            'line': {
                                                'color': 'red',
                                                'width': 1,
                                                'dash_type': 'long_dash',
                                            },
                                            'display_equation': False,
                                            }})

        chart_averaged.add_series({'values': '=%s!$%s$3:$%s$%d' % (self.serie_part,
                                                                   'B',
                                                                   'B',
                                                                   len(self.mean_of_averaged_nps_dict['frequencies']) +
                                                                   2),
                                   'categories': '%s!$%s$3:$%s$%d' % (self.serie_part,
                                                                      'A',
                                                                      'A',
                                                                      len(self.mean_of_averaged_nps_dict[
                                                                              'frequencies']) + 2),
                                   'name': 'Total Average',
                                   'legend': False,
                                   })

        chart_ave.set_x_axis({'name': 'Line pairs per cm'})
        chart_ave.set_y_axis({'name': 'NPS_1D_averaged'})
        # Insert the chart into the worksheet.
        worksheet_ave.insert_chart('C1', chart_ave)

        chart_averaged.set_x_axis({'name': 'Line pairs per cm'})
        chart_averaged.set_y_axis({'name': 'NPS_1D_averaged'})
        # Insert the chart into the worksheet.
        self.worksheet_averaged.insert_chart('C1', chart_averaged)

        # create summary info xlsx

        # write headers to worksheet
        for num_header, header_name in enumerate(self.headers_list):
            self.worksheet_summary['%s1' % opxl.utils.get_column_letter(num_header + 1)] = header_name

        # row to write
        row_to_write = self.start_row + self.num_series
        # get worksheet's name
        name_of_folder = self.folder_part
        name_of_series = self.serie_part
        # write information from worksheet
        self.worksheet_summary['%s%d' % (self.col_number, row_to_write)] = self.num_folder + 1
        self.worksheet_summary['%s%d' % (self.col_folder, row_to_write)] = name_of_folder
        self.worksheet_summary['%s%d' % (self.col_series, row_to_write)] = name_of_series
        self.worksheet_summary['%s%d' % (self.col_peak_freq, row_to_write)] = self.peak_info_dict_ave['mean_freq']
        self.worksheet_summary['%s%d' % (self.col_peak_value, row_to_write)] = self.peak_info_dict_ave['mean_value']
        self.worksheet_summary['%s%d' % (self.col_left_dev, row_to_write)] = self.peak_info_dict_ave['left_dev']
        self.worksheet_summary['%s%d' % (self.col_right_dev, row_to_write)] = self.peak_info_dict_ave['right_dev']
        self.worksheet_summary['%s%d' % (self.col_area, row_to_write)] = np.mean(
            [self.auc_dict[key] for key in self.auc_dict]
        )
        self.worksheet_summary['%s%d' % (self.col_int_2d_nps, row_to_write)] = np.mean(
            [self.integral_2d_nps_dict[key] for key in self.integral_2d_nps_dict]
        )
        self.worksheet_summary['%s%d' % (self.col_ave_m_HU, row_to_write)] = self.total_mean_HU
        self.worksheet_summary['%s%d' % (self.col_ave_SD, row_to_write)] = self.total_mean_sd

        for num_metadata, (metadata_tag, col_metadata) in enumerate(
                zip(self.metadata_headers, self.metadata_columns)
        ):
            self.worksheet_summary['%s%d' % (col_metadata, row_to_write)] = self.metadata[metadata_tag]

    @staticmethod
    def radial_mean(array):

        """
        Build radial mean of 2d-array. In our case: 2d-NPS.


        :param array: ndarray (2d)
            Two-dimensional NPS of current ROI.
        :return: ndarray (1d)
            Radial mean of the 2d-NPS.
        """

        image = array
        image_height = array.shape[0]
        image_width = array.shape[1]
        center_x = image_width // 2
        center_y = image_height // 2
        max_size = max(image_height, image_width)
        # create array of radii
        x, y = np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))
        R = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)

        # calculate the mean
        f = lambda r: image[(R >= r - .5) & (R < r + .5)].mean()
        # r = np.linspace(1, 302, num=302)
        r = np.linspace(0, max_size // 2, num=max_size // 2 + 1)
        mean = np.vectorize(f)(r)
        mean = [array[center_y][center_x]] + mean
        return mean

    def polyfit2d(self, x, y, z):
        """2d-fitting of 2d-array. Used for background extraction"""
        size_x = np.array(x).shape[0]
        size_y = np.array(y).shape[0]
        if size_x > size_y:
            y = np.concatenate((y, [y[-1]] * (size_x - size_y)))
        else:
            x = np.concatenate((x, [x[-1]] * (size_y - size_x)))
        order = self.fit_order
        ncols = (order + 1) ** 2
        G = np.zeros((x.size, ncols))
        ij = itertools.product(range(order + 1), range(order + 1))
        for k, (i, j) in enumerate(ij):
            G[:, k] = x ** i * y ** j
        try:
            m, _, _, _ = np.linalg.lstsq(G, z, rcond=None)
        except:
            print('There is a problem in file (fitting):   ', file)
        return m

    @staticmethod
    def polyval2d(self, x, y, m):
        """Auxiliar function for 2d-fitting"""
        size_x = np.array(x).shape[0]
        size_y = np.array(y).shape[0]
        if size_x > size_y:
            y = np.concatenate((y, [y[-1]] * (size_x - size_y)))
        else:
            x = np.concatenate((x, [x[-1]] * (size_y - size_x)))
        order = int(np.sqrt(len(m))) - 1
        ij = itertools.product(range(order + 1), range(order + 1))
        z = np.zeros_like(x)
        for a, (i, j) in zip(m, ij):
            z += a * x ** i * y ** j
        return z

    def prepare_f_1(self, xy, a, b, c, d):
        """Auxiliar function for 2d-fitting"""
        i = xy // self.image_width_1  # reconstruct y coordinates
        j = xy % self.image_width_1  # reconstruct x coordinates
        out = i * a + j * b + i * j * c + d
        return out

    @staticmethod
    def nps_equation(nps_array):
        """Input: not ranged nps array (with larger distance between
        samples). Return list of tuples, containing slope and bias of
        line connecting each two points of nps array"""
        line_equations = []
        for s in range(len(nps_array) - 1):
            line_equations.append(ProcessROI.determine_line_equation(point_index_1=s,
                                                                     point_index_2=s + 1,
                                                                     point_val_1=nps_array[s],
                                                                     point_val_2=nps_array[s + 1]))
        return line_equations

    def get_current_nps(self, freq_value, freq_array):

        """
        Get NPS value respective to frequency in freq range.

        :param freq_value: float
            Current frequency value of freq_range.
        :param freq_array: list of floats
            Not interpolated list of NPS frequencies.
        :return: float
            Interpolated value of NPS respective to given freq_value.
        """

        """
        using equations of lines between points of unranged NPS array"""
        # all frequencies, that less than freq_value
        less_values = [i for i in freq_array if i <= freq_value]
        # all frequencies, that greater than freq_value
        greater_values = [i for i in freq_array if i >= freq_value]
        # lower boundary freq value
        min_bound_val = max(less_values)
        # upper boundary freq value
        max_bound_val = min(greater_values)
        # lower boundary index
        min_bound_idx = list(freq_array).index(min_bound_val)
        max_bound_idx = list(freq_array).index(max_bound_val)
        line_prop = ProcessROI.determine_line_equation(point_index_1=min_bound_val,
                                                       point_index_2=max_bound_val,
                                                       point_val_1=self.new_dict['values'][min_bound_idx],
                                                       point_val_2=self.new_dict['values'][max_bound_idx])
        if min_bound_val == max_bound_val:
            current_nps = self.new_dict['values'][min_bound_idx]
        else:
            current_nps = line_prop[0] * freq_value + line_prop[1]
        # print('min bound value: ', self.new_dict['values'][min_bound_idx],
        #       '  freq_value:  ', self.new_dict['values'][max_bound_idx],
        #       'min bound index: ', min_bound_idx, '\n',
        #       'max bound value: ', max_bound_val, 'max bound index:  ', max_bound_idx)
        if current_nps < 0:
            current_nps = 0
        return current_nps

    def prepare_f_2(self, xy, a, b, c, d, e, f, g, h, k):
        """Auxiliar function for 2d-fitting"""
        i = xy // self.image_width_1  # reconstruct y coordinates
        j = xy % self.image_width_1  # reconstruct x coordinates
        out = i * a + j * b + i * j * c + i * j ** 2 * d + \
              i ** 2 * j * e + i ** 2 * j ** 2 * f + \
              i ** 2 * g + j ** 2 * h + k
        return out

    def create_pol_fit(self, array):

        """
        Create 2d fit of current ROI, either of first or of second order.

        :param array: ndarray (2d)
            Pixel array of current ROI.
        :return: ndarray (2d)
            Fitted pixel array.
        """

        self.pol_fit = []
        self.image_width_1 = array.shape[1]
        self.image_height_1 = array.shape[0]
        x = np.linspace(0, self.image_width_1 - 1, num=self.image_width_1)
        y = np.linspace(0, self.image_height_1 - 1, num=self.image_height_1)
        z = array[0: self.image_height_1, 0: self.image_width_1]
        xy = np.arange(z.size)
        if self.fit_order == 1:
            mvfs = np.ravel(z)
            res = opt.curve_fit(self.prepare_f_1, xy, np.ravel(z))
            z_est = self.prepare_f_1(xy, *res[0])
        else:
            mvfs = np.ravel(z)
            res = opt.curve_fit(self.prepare_f_2, xy, np.ravel(z))
            z_est = self.prepare_f_2(xy, *res[0])

        self.pol_fit = z_est.reshape(self.image_height_1, self.image_width_1)
        # self.fitting = np.array(self.polyfit2d(x, y, z))
        # for item_fit_ind in range(self.fitting.shape[1]):
        #     self.pol_fit_sub = self.polyval2d(x, y, self.fitting[:, item_fit_ind])
        #     self.pol_fit.append(self.pol_fit_sub)
        return self.pol_fit

    def truncate_nps_freq(self, *, dict):

        """
        Truncate low NPS values at higher frequencies.

        :param dict: dict
            See return value of method compute_nps.

        :return: dict
            Dict truncated NPS values and respective frequencies.
            Keys : 'values', 'frequencies'.
        """

        """Takes as parameter dict: raw NPS-dict.
        Truncate higher frequencies with small respective NPS-values"""
        # select element greater than 10**(-4)
        truncated_nps = []
        for i in dict['values']:
            if i > self.trunc_percentage / 100 * np.max(dict['values']):
                truncated_nps.append(i)
            else:
                break
        # difference of length between normal and truncated NPS-lists
        # = last index of freq-list
        tr_idx = len(truncated_nps)
        # truncate freq-list
        truncated_freqs = dict['frequencies'][: tr_idx]
        new_dict = {'values': truncated_nps,
                    'frequencies': truncated_freqs}
        return new_dict

    @staticmethod
    def determine_line_equation(*,
                                point_val_1,
                                point_index_1,
                                point_val_2,
                                point_index_2):

        """
        Find slope and bias (shift) of the line containing two passed points.

        :param point_val_1: float
            y value of first point.
        :param point_index_1: float
            x value of first point.
        :param point_val_2: float
            y value of second point.
        :param point_index_2: float
            x value of second point.
        :return: tuple of floats
            Slope and bias of the aforementioned line.
        """

        # determination of line equation
        # based on two points of the line
        if point_index_1 == point_index_2:
            slope = 1
            shift = 0
        else:
            slope = (point_val_2 - point_val_1) / (point_index_2 - point_index_1)
            shift = point_val_1 - slope * point_index_1

        return slope, shift

    @staticmethod
    def collect_all_max_peaks_nps(dict):

        """
        Find all peak values and their indices and respective frequencies in passed 1d-list.

        :param dict: dict
            Keys : 'values', 'frequencies', 'AUC', 'Integral_of_2d_NPS'.
            Values : resp.: 1d-NPS values of current ROI, respective frequencies,
                            area under 1d-NPS profile, integral of 2d-NPS.
        :return: dict
            Dict with all peaks info.
            Keys : 'values', 'indices', frequencies'
            Values : resp. list of peak values,
                           list of respective indices,
                           list of respective frequencies.
        """

        val_arr = dict['values']
        freq_arr = dict['frequencies']
        # counter for nps array items
        counter = 0
        # initialize max value - first threshold level
        max_value = 0
        # list to store all peaks values
        max_peaks_array = []
        # list to store all peaks indices
        max_ind_array = []
        # list to store respective frequencies
        resp_freq_max = []
        # auxiliary boolean variable
        switcher = True
        # initialize max index
        max_index = 0
        for item in val_arr:
            # if the next item has larger value than the previous
            # and if its value is more than the threshold level
            if item >= max_value:
                max_value = item
                max_index = counter
                # ability to store max value in the list
                switcher = True
            # if the next item is less than the previous (peak condition)
            elif switcher:
                max_peaks_array.append(max_value)
                max_ind_array.append(max_index)
                resp_freq_max.append(freq_arr[max_index])
                # prevent storing not peaks values
                switcher = False
            else:
                max_value = item
            counter += 1
        return {'values': max_peaks_array,  # [1:],
                'indices': max_ind_array,  # [1:],
                'frequencies': resp_freq_max}  # [1:]}

    def handle_peak_info(self, peak_dict, all_val_arr, all_freq_arr):

        """
        Extract peak information from peak_dict.

        :param peak_dict: dict
            (See return value of static method collect_all_max_peaks_nps)
        :param all_val_arr: list
            List of values from which peak_dict has been built.
        :param all_freq_arr: list
            List of respective frequencies.
        :return: dict
         Dict with peak information:
            Keys : 'mean_value' - peak NPS value,
                   'mean_freq' - peak NPS frequency,
                   'left_dev' - frequency distance between peak freq. and
                                freq. at which NPS value falls under 60% of max value
                                to left side from peak.
                   'right_dev' - frequency distance between peak freq. and
                                 freq. at which NPS value falls under 60% of max value
                                 to right side from peak.
        """

        """Extract following info from peak_dict:
        - mean_value (i.e. absolute max peak value);
        - mean_freq (i.e. absolute max peak freq);
        - left deviation (freq, at which NPS-value falls underneath
                          the 60% of max value to the left side)
        - right deviation (the same, but to the right side)"""
        peak_val_arr = peak_dict['values']
        freq_arr = peak_dict['frequencies']
        left_dev = 'undefined'
        right_dev = 'undefined'
        # indices = peak_dict['indices']
        # if there are peaks
        no_peaks = False
        if len(peak_val_arr) > 0:
            only_right_dev = False
            # define max value and whether there is only right deviation
            try:
                if max(peak_val_arr) < max(all_val_arr) * 0.1:
                    mean_distr = max(all_val_arr)
                    index_max = list(all_val_arr).index(mean_distr)
                    only_right_dev = True
                else:
                    mean_distr = max(peak_val_arr)
                    index_max = list(all_val_arr).index(mean_distr)
                    if all([i > 0.6 * mean_distr for i in all_val_arr[:index_max]]):
                        only_right_dev = True
            except ValueError:
                print('peak dict: ', peak_dict)
                print('all values: ', all_val_arr)
                print('file: ', self.basename)
        else:
            mean_distr = max(all_val_arr)
            index_max = list(all_val_arr).index(mean_distr)
            only_right_dev = True
            no_peaks = True

        # collect nps information
        if not no_peaks:
            try:
                # index_max_peak = peak_val_arr.index(mean_distr)
                mean_freq = all_freq_arr[list(all_val_arr).index(mean_distr)]
            except ValueError:
                print('file:  ', self.basename)
                print('peak dict: ', peak_dict)
                print('mean:   ', mean_distr)
        else:
            # index_max_peak = 0
            mean_freq = self.start_freq

        # right deviation
        for item in all_val_arr[index_max:]:
            if item < 0.6 * mean_distr:
                r_dev_value = item
                resp_idx = list(all_val_arr).index(item)
                r_dev_freq = all_freq_arr[resp_idx]
                right_dev = r_dev_freq - mean_freq
                break
        # left deviation
        if only_right_dev:
            l_dev_value = 'undefined'
            l_dev_freq = 'undefined'
            left_dev = 'undefined'
        else:
            for item in all_val_arr[:index_max]:
                if item > 0.6 * mean_distr:
                    l_dev_value = item
                    resp_idx = list(all_val_arr).index(item)
                    l_dev_freq = all_freq_arr[resp_idx]
                    left_dev = mean_freq - l_dev_freq
                    break
        peak_info_dict = {'mean_value': mean_distr,
                          'mean_freq': mean_freq,
                          'left_dev': left_dev,
                          'right_dev': right_dev
                          }
        return peak_info_dict