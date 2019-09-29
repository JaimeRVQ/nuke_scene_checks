# -*- coding: UTF-8 -*-
'''
Author: Jaime Rivera
File: abstract_stream.py
Date: 2019.08.03
Revision: 2019.08.03
Copyright: Copyright Jaime Rivera 2019 | www.jaimervq.com
           The program(s) herein may be used, modified and/or distributed in accordance with the terms and conditions
           stipulated in the Creative Commons license under which the program(s) have been registered. (CC BY-SA 4.0)

Brief:

'''

__author__ = 'Jaime Rivera <jaime.rvq@gmail.com>'
__copyright__ = 'Copyright 2019, Jaime Rivera'
__credits__ = []
__license__ = 'Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)'
__maintainer__ = 'Jaime Rivera'
__email__ = 'jaime.rvq@gmail.com'
__status__ = 'Testing'


import datetime

import nuke_specifics

# -------------------------------- CONSTANTS -------------------------------- #

NO_WRITING_INFO = 0
ORIGIN_INFO = 1
FILEPATH_INFO = 2
COMMENT_INFO = 3
PADDING_INFO = 4
VERSION_INFO = 5
FRAMEESTART_INFO = 6
FRAMEEND_INFO = 7
EXTENSION_INFO = 8


# -------------------------------- CLASS -------------------------------- #

class AbstactStream(object):

    def __init__(self, start_stream, parent_feedback_window):

        # Window to output feedback
        self.window = parent_feedback_window

        # Write infos
        self.origin_node_name = ''
        self.file_path = ''
        self.comment = ''
        self.start_frame = None
        self.end_frame = None
        self.extension = ''

        # Extra information
        self.padding = '#####'
        self.version = ''

        # CAN THIS STREAM BE WRITTEN?
        self.all_write_fields = True
        self.all_checks_good = True

        # Extra manipulations
        self.manipulation_nodes = set()

        # Execute
        if start_stream.output_stream:
            self.execute(start_stream)

    def execute(self, stream):

        if stream.parent_node.node_class == 'Start':
            self.append_to_log('Started execution of Stream<font size=4> (Stream number: {} | From node with ID:{})'
                               ''.format(stream.index, stream.parent_node.id), 6, 'lime')

        else:
            response = stream.parent_node.run_node()

            # RESPONSE
            response_superclass = response[0]
            response_class = response[1]
            response_id = response[2]

            response_writing_info = response[3]
            response_message = response[4]
            response_completion = response[5]

            if response_completion:
                self.append_to_log('Executed node of type: {0}  (Node ID: {1})<br>Result: {2}'
                                   ''.format(response_class, response_id, response_message), 4)    
                
                if response_superclass == 'WritingNodes':
                    if response_writing_info == ORIGIN_INFO:
                        self.origin_node_name = response_message
                    elif response_writing_info == FILEPATH_INFO:
                        self.file_path = response_message
                    elif response_writing_info == COMMENT_INFO:
                        self.comment = response_message
                    elif response_writing_info == PADDING_INFO:
                        self.padding = '_' + response_message
                    elif response_writing_info == VERSION_INFO:
                        self.version = '_' + response_message
                    elif response_writing_info == FRAMEESTART_INFO:
                        self.start_frame = response_message
                    elif response_writing_info == FRAMEEND_INFO:
                        self.end_frame = response_message
                    elif response_writing_info == EXTENSION_INFO:
                        self.extension = response_message
                        
            else:
                self.append_to_log('Executed node of type: {0}  (Node ID: {1})<br>Result: {2}'
                                   ''.format(response_class, response_id, response_message), 4, 'red')
                
                if response_superclass == 'CheckNodes':
                    self.all_checks_good = False

            if response_superclass == 'Manipulation':
                self.manipulation_nodes.add(response_class)

        # JUMP TO NEXT STREAM
        next_stream = stream.output_stream
        if next_stream:
            self.execute(next_stream)
        else:
            self.final_checks()

    def append_to_log(self, message, size, color='white'):
        time = datetime.datetime.now()
        formatted_time = time.strftime('%Y-%m-%d %H:%M:%S')
        self.window.insertHtml("<font color='{0}' size={1}>[{2}] {3}<br>".format(color, size, formatted_time, message))

    def final_checks(self):

        # Check for all the elements needed for rendering
        if not self.origin_node_name:
            self.all_write_fields = False
            self.append_to_log('There was no origin node detected in this stream', 4, 'orange')

        if not self.file_path:
            self.all_write_fields = False
            self.append_to_log('There was no filepath detected in this stream', 4, 'orange')

        if not self.comment:
            self.all_write_fields = False
            self.append_to_log('There was no comment detected in this stream', 4, 'orange')

        if self.start_frame is None:
            self.all_write_fields = False
            self.append_to_log('There was no start frame detected in this stream', 4, 'orange')

        if self.end_frame is None:
            self.all_write_fields = False
            self.append_to_log('There was no end frame detected in this stream', 4, 'orange')

        if not self.extension:
            self.all_write_fields = False
            self.append_to_log('There was no valid file extension detected in this stream', 4, 'orange')


        # Warning that the stream cannot render
        if not self.all_checks_good:
            self.append_to_log('<b>[!]</b> Some of the check nodes in the stream have failed, it will not be rendered',
                               4, 'red')
        if not self.all_write_fields:
            self.append_to_log('<b>[!]</b> Some of the elements needed for rendering have not been found. Please note '
                               'that this stream and its checks have been run but it will not have a rendered output',
                               4, 'red')

        # Send to be written if all info needed is present
        if self.all_checks_good and self.all_write_fields:
            self.send_to_write()

        self.append_to_log('Finished execution of stream<br>', 5, 'lime')

    def send_to_write(self):
        self.append_to_log('Starting to write the output for this stream', 4, 'magenta')

        # Correct format for paths
        path = self.file_path.replace('\\', '/')
        path = path + '/' if not path.endswith('/') else path
        complete_file_value = path + self.comment + self.padding + self.version + self.extension

        # Send to write
        nuke_specifics.write_path(self.origin_node_name, complete_file_value,
                                  self.start_frame, self.end_frame, self.manipulation_nodes)

        self.append_to_log('Finished writing the output for this stream', 4, 'magenta')