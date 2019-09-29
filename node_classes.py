# -*- coding: UTF-8 -*-
'''
Author: Jaime Rivera
File: node_classes.py
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


from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
import os

import nuke_specifics
import abstract_stream


# -------------------------------- CONSTANTS -------------------------------- #
# --------------------------------------------------------------------------- #

# Node style
HEADER_HEIGHT = 27
STRIPE_HEIGHT = 20

# Connector style
SQUARE_DIAGONAL = 8   #(more precisely, half-diagonal)
CONNECTOR_AVAILABLE_COLOR = QtCore.Qt.darkYellow
CONNECTOR_USED_COLOR = QtCore.Qt.green


# -------------------------------- NODE-RELATED CLASSES -------------------------------- #
# -------------------------------------------------------------------------------------- #

class GeneralNode(QtWidgets.QGraphicsPathItem):

    # CLASS COUNTER
    id_counter = 0

    # BASIC PROPERTIES (To be overriden)
    node_superclass = 'Base'
    node_class = 'General'
    stream_class = None
    can_have_input = True
    can_have_output = True

    # VISUAL PROPERTIES (To be overriden)
    node_width = 120
    r, g, b = (112, 112, 112)

    # NICE NAMES (To be overriden)
    node_superclass_nice_name = 'Base'
    node_class_nice_name = 'General'

    # NODE HELP (To be overriden)
    help_text = ''


    def __init__(self):

        # ID OF THE NODE
        GeneralNode.id_counter += 1
        self.id = GeneralNode.id_counter

        # BASIC NODE PROPERTIES
        self.extra_header = 0
        self.widget = None
        self.max_streams = 16
        self.is_selected = False

        # STREAMS
        self.stream_count = 0
        self.streams = []

        # GRAPHICS OF THE NODE
        QtWidgets.QGraphicsPathItem.__init__(self)
        self.setFlags(QtWidgets.QGraphicsPathItem.ItemIsMovable)

        self.id_text = QtWidgets.QGraphicsSimpleTextItem(parent=self)
        self.proxy_add_btn = QtWidgets.QGraphicsProxyWidget(parent=self)
        self.proxy_remove_btn = QtWidgets.QGraphicsProxyWidget(parent=self)

        self.marquee = QtWidgets.QGraphicsPathItem(parent=self)

        # SETUP
        self.setup_node()
        self.add_stream()
        self.setup_widget()

    @property
    def node_height(self):
        return  HEADER_HEIGHT + self.extra_header + (self.stream_count + 1) * STRIPE_HEIGHT

    def setup_node(self):

        if self.stream_class:
            self.extra_header = 30
            self.widget = self.stream_class(parent=None)

        # BASIC SHAPE
        self.reconstruct_shape()
        self.setPen(QtGui.QPen(QtCore.Qt.black))

        # NODE NAME
        class_text = QtWidgets.QGraphicsSimpleTextItem(self.node_class, parent=self)
        node_class_font = QtGui.QFont('arial', 12)
        node_class_font.setUnderline(True)
        class_text.setFont(node_class_font)
        class_text.setPos(8, 6)

        # NODE WIDGET
        if self.stream_class:
            self.widget.setFixedSize(self.node_width - 10, HEADER_HEIGHT - 6)
            proxy = QtWidgets.QGraphicsProxyWidget(parent=self)
            proxy.setWidget(self.widget)
            proxy.moveBy(5, HEADER_HEIGHT + 3)
            proxy.setZValue(20)

        # HELP
        help_btn = QtWidgets.QPushButton(parent=None)
        help_btn.setFixedSize(16, 16)
        help_btn.setText('i')
        help_btn.setFont(QtGui.QFont('Monotype Corsiva', 10))
        help_btn.clicked.connect(self.show_help)
        proxy = QtWidgets.QGraphicsProxyWidget(parent=self)
        proxy.setWidget(help_btn)
        proxy.moveBy(self.node_width - 25, 7)

        # NODE ID
        self.id_text.setText('ID: {}'.format(self.id))
        node_id_font = QtGui.QFont('arial', 8)
        self.id_text.setFont(node_id_font)

        # ADD / DELETE STREAMS BUTTONS
        add_btn = QtWidgets.QPushButton(parent=None)
        add_btn.setFixedSize(16, 16)
        add_btn.setText('+')
        add_btn.setStyleSheet('color:lime')
        add_btn.setFont(QtGui.QFont('Impact', 11))
        add_btn.clicked.connect(self.add_stream)
        self.proxy_add_btn.setWidget(add_btn)

        remove_btn = QtWidgets.QPushButton(parent=None)
        remove_btn.setFixedSize(16, 16)
        remove_btn.setText('-')
        remove_btn.setStyleSheet('color:red')
        remove_btn.setFont(QtGui.QFont('Impact', 11))
        remove_btn.clicked.connect(self.remove_stream)
        self.proxy_remove_btn.setWidget(remove_btn)

    def reconstruct_shape(self):
        # BASIC SHAPE
        new_path = QtGui.QPainterPath()
        new_path.addRoundedRect(QtCore.QRect(0, 0, self.node_width, self.node_height), 10, 10)
        self.setPath(new_path)

        # ID MOVEMENT
        self.id_text.setPos(10, self.node_height - STRIPE_HEIGHT / 2 - 8)

        # BUTTON MOVEMENT
        self.proxy_add_btn.setPos(self.node_width - 40, self.node_height - STRIPE_HEIGHT / 2 - 8)
        self.proxy_remove_btn.setPos(self.node_width - 25, self.node_height - STRIPE_HEIGHT / 2 - 8)

        # MARQUEE
        new_path = QtGui.QPainterPath()
        new_path.addRoundedRect(QtCore.QRect(0, 0, self.node_width, self.node_height), 10, 10)
        self.marquee.setPath(new_path)
        self.marquee.setZValue(10)

        # FILLING
        grad = QtGui.QLinearGradient(0, 0, 0, self.node_height)
        grad.setColorAt(0.5, QtGui.QColor(self.r, self.g, self.b))
        lighter_color = QtGui.QColor(self.r + 20, self.g + 20, self.b + 20)
        grad.setColorAt(1.0, lighter_color)
        self.setBrush(grad)

    def add_stream(self):
        if self.stream_count == self.max_streams:
            return

        if self.stream_count % 2 == 0:
            new_stream = Stream(self.stream_count, self.node_width, 'light', self)
        else:
            new_stream = Stream(self.stream_count, self.node_width, 'dark', self)

        new_stream.moveBy(0,self.node_height - STRIPE_HEIGHT)
        new_stream.setParentItem(self)
        new_stream.setZValue(5)

        self.stream_count += 1
        self.streams.append(new_stream)

        self.reconstruct_shape()

    def remove_stream(self):
        if self.stream_count == 1:
            return

        stream_to_delete = self.streams[-1]
        stream_to_delete.clear_connections()
        self.streams.remove(stream_to_delete)
        self.scene().removeItem(stream_to_delete)
        del stream_to_delete

        self.stream_count -= 1

        self.reconstruct_shape()

    def set_selected(self, selected):

        if selected:
            self.is_selected = True
            self.marquee.setPen(QtGui.QPen(CONNECTOR_USED_COLOR, 2))
        else:
            self.is_selected = False
            self.marquee.setPen(QtGui.QPen(QtCore.Qt.black, 1))

        self.marquee.setZValue(10)

    def relabel_id(self, new_id):
        self.id = new_id
        self.id_text.setText('ID: {}'.format(self.id))

        if new_id > GeneralNode.id_counter:
            GeneralNode.id_counter = new_id

    def show_help(self):

        help_text = '<b><font size = 5>' + self.node_class +\
                    '</b><br><font size = 4>' + self.help_text + '<font size = 3> ' + \
                    '<hr>Node properties:<br>  <b>- SUPERCLASS:</b> {}<br>  <b>- CLASS:</b> {}' \
                    ''.format(self.node_superclass, self.node_class)


        help_text += '<hr><b>HOTKEYS:</b>' \
                     '<br>[<font color = yellow><b>+</b></font>] Adds new stream' \
                     '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[<font color = yellow><b>F</b></font>] Focuses on this node' \
                     '<br>[<font color = yellow><b>-</b></font>] Deletes last stream' \
                     '&nbsp;&nbsp;&nbsp;&nbsp;[<font color = yellow><b>Supr</b></font>] Deletes this node'

        info_window = QtWidgets.QMessageBox()
        info_window.setText(help_text)
        info_window.setWindowTitle("Help")
        info_window.setIcon(QtWidgets.QMessageBox.Information)
        info_window.exec_()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.set_selected(True)
            self.scene().establish_selected_node(self)

        QtWidgets.QGraphicsPathItem.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.is_selected:
            self.redraw_lines()

        QtWidgets.QGraphicsPathItem.mouseMoveEvent(self, event)

    def redraw_lines(self):
        for stream in self.streams:

            if stream.input_line:
                line = stream.input_line

                p1 = line.path().pointAtPercent(0)
                p2 = stream.input_connector.center_point
                new_path = QtGui.QPainterPath(p1)
                c_p1 = QtCore.QPoint(((p2.x() + p1.x()) / 2) + 10, p1.y())
                c_p2 = QtCore.QPoint(((p2.x() + p1.x()) / 2) - 10, p2.y())
                new_path.cubicTo(c_p1, c_p2, p2)

                line.setPath(new_path)

            if stream.output_line:
                line = stream.output_line

                p1 = stream.output_connector.center_point
                p2 = line.path().pointAtPercent(1)
                new_path = QtGui.QPainterPath(p1)
                c_p1 = QtCore.QPoint(((p2.x() + p1.x()) / 2) + 10, p1.y())
                c_p2 = QtCore.QPoint(((p2.x() + p1.x()) / 2) - 10, p2.y())
                new_path.cubicTo(c_p1, c_p2, p2)

                line.setPath(new_path)

    def setup_widget(self):
        pass

    def run_node(self):
        pass

    def get_widget_value(self):
        if self.stream_class is None:
            return None

        # STREAM CLASSES
        if self.stream_class == QtWidgets.QComboBox:
            return str(self.widget.currentText())
        elif self.stream_class == QtWidgets.QLineEdit:
            return str(self.widget.text())
        elif self.stream_class == QtWidgets.QSpinBox:
            return self.widget.value()

    def set_widget_value(self, new_value):
        if self.stream_class is None:
            return

        # STREAM CLASSES
        if self.stream_class == QtWidgets.QComboBox:
            self.widget.setCurrentText(new_value)
        elif self.stream_class == QtWidgets.QLineEdit:
            self.widget.setText(new_value)
        elif self.stream_class == QtWidgets.QSpinBox:
            self.widget.setValue(new_value)

    def __str__(self):
        return self.node_class + '_' + str(self.id)

# ------- STREAM CONTROL NODES ------- #
class EmptyNode(GeneralNode):

    # BASIC PROPERTIES (Overriden from general class)
    node_superclass = 'StreamControlNodes'
    node_class = 'Empty'
    stream_class = None

    # VISUAL PROPERTIES (Overriden from general class)
    node_width = 150
    r, g, b = (112, 112, 112)

    # NICE NAMES (Overriden from general class)
    node_superclass_nice_name = 'Stream Control'
    node_class_nice_name = 'Empty'

    # NODE HELP (Overriden from general class)
    help_text = 'Empty node for testing purposes.'

    def run_node(self):
        return [self.node_superclass, self.node_class, self.id,
                abstract_stream.NO_WRITING_INFO, 'Empty nodes do not return any result!', True]


class StartNode(GeneralNode):

    # BASIC PROPERTIES (Overriden from general class)
    node_superclass = 'StreamControlNodes'
    node_class = 'Start'
    stream_class = None
    can_have_input = False

    # VISUAL PROPERTIES (Overriden from general class)
    node_width = 150
    r, g, b = (82, 142, 19)

    # NICE NAMES (Overriden from general class)
    node_superclass_nice_name = 'Stream Control'
    node_class_nice_name = 'Start'

    # NODE HELP (Overriden from general class)
    help_text = 'Starts the execution of every stream. Only the streams that begin at a Start node' \
                'will be executed (or visualized through the <i>Visualize Streams</i> button)'

# ------- WRITING NODES ------- #
class OriginNode(GeneralNode):

    # BASIC PROPERTIES (Overriden from general class)
    node_superclass = 'WritingNodes'
    node_class = 'Origin'
    stream_class = QtWidgets.QComboBox

    # VISUAL PROPERTIES (Overriden from general class)
    node_width = 145
    r, g, b = (19, 178, 120)

    # NICE NAMES (Overriden from general class)
    node_superclass_nice_name = 'Writing'
    node_class_nice_name = 'Origin'

    # NODE HELP (Overriden from general class)
    help_text = "Defines which Nuke's scene node to be rendered."

    def setup_widget(self):
        for name in nuke_specifics.all_node_names():
            self.widget.addItem(name)

    def run_node(self):
        origin = str(self.widget.currentText())
        return [self.node_superclass, self.node_class, self.id,
                abstract_stream.ORIGIN_INFO, origin, True]


class OriginFromNameNode(GeneralNode):

    # BASIC PROPERTIES (Overriden from general class)
    node_superclass = 'WritingNodes'
    node_class = 'OriginFromName'
    stream_class = QtWidgets.QLineEdit

    # VISUAL PROPERTIES (Overriden from general class)
    node_width = 155
    r, g, b = (19, 178, 120)

    # NICE NAMES (Overriden from general class)
    node_superclass_nice_name = 'Writing'
    node_class_nice_name = 'Origin (from name)'

    # NODE HELP (Overriden from general class)
    help_text = "Chooses any node (by name) as origin to be renderized"

    def setup_widget(self):
        self.widget.setPlaceholderText('Enter node name')

    def run_node(self):
        origin_node = str(self.widget.text())
        if not nuke_specifics.node_exists(origin_node):
            return [self.node_superclass, self.node_class, self.id,
                    abstract_stream.ORIGIN_INFO, 'The node of name {} does not exist'.format(origin_node), False]

        return [self.node_superclass, self.node_class, self.id,
                abstract_stream.ORIGIN_INFO, origin_node, True]


class FilePathNode(GeneralNode):

    # BASIC PROPERTIES (Overriden from general class)
    node_superclass = 'WritingNodes'
    node_class = 'FilePath'
    stream_class = QtWidgets.QLineEdit

    # VISUAL PROPERTIES (Overriden from general class)
    node_width = 200
    r, g, b = (198, 185, 0)

    # NICE NAMES (Overriden from general class)
    node_superclass_nice_name = 'Writing'
    node_class_nice_name = 'File Path'

    # NODE HELP (Overriden from general class)
    help_text = 'Takes a filepath as input, where the output of the stream will be rendered to. ' \
                'Note that any text will be accepted as input, but the stream will not be correctly' \
                'rendered if the filepath does not exist.'

    def setup_widget(self):
        self.widget.setPlaceholderText('Enter file path')

    def run_node(self):
        filepath = str(self.widget.text())

        if not filepath:
            return [self.node_superclass, self.node_class, self.id,
                    abstract_stream.FILEPATH_INFO, 'No filepath was provided', False]
        if not os.path.exists(filepath):
            return [self.node_superclass, self.node_class, self.id,
                    abstract_stream.FILEPATH_INFO, 'The filepath does not exist', False]

        return [self.node_superclass, self.node_class, self.id,
                abstract_stream.FILEPATH_INFO, filepath, True]


class CommentNode(GeneralNode):

    # BASIC PROPERTIES (Overriden from general class)
    node_superclass = 'WritingNodes'
    node_class = 'Comment'
    stream_class = QtWidgets.QLineEdit

    # VISUAL PROPERTIES (Overriden from general class)
    node_width = 170
    r, g, b = (17, 173, 147)

    # NICE NAMES (Overriden from general class)
    node_superclass_nice_name = 'Writing'
    node_class_nice_name = 'Comment'

    # NODE HELP (Overriden from general class)
    help_text = 'Comment for the writing output. Must be written all in lowercaps, ' \
                'with the option to add underscores.'

    def setup_widget(self):
        self.widget.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("^[a-z]+[a-z0-9_]*")))
        self.widget.setPlaceholderText('only_lowkey_comments')
        self.widget.cursorPositionChanged.connect(lambda: self.scene().establish_selected_node(None))

    def run_node(self):
        comment = str(self.widget.text())

        if not comment:
            return [self.node_superclass, self.node_class, self.id,
                    abstract_stream.COMMENT_INFO, 'No comment was provided', False]

        return [self.node_superclass, self.node_class, self.id,
                abstract_stream.COMMENT_INFO, comment, True]


class FrameStartNode(GeneralNode):

    # BASIC PROPERTIES (Overriden from general class)
    node_superclass = 'WritingNodes'
    node_class = 'FrameStart'
    stream_class = QtWidgets.QSpinBox

    # VISUAL PROPERTIES (Overriden from general class)
    node_width = 120
    r, g, b = (150, 24, 178)

    # NICE NAMES (Overriden from general class)
    node_superclass_nice_name = 'Writing'
    node_class_nice_name = 'Frame start'

    # NODE HELP (Overriden from general class)
    help_text = 'Frame to start rendering from.'

    def setup_widget(self):
        self.widget.setMaximum(9999)

    def run_node(self):
        frame = self.widget.value()
        return [self.node_superclass, self.node_class, self.id,
                abstract_stream.FRAMEESTART_INFO, frame, True]


class FrameEndNode(GeneralNode):

    # BASIC PROPERTIES (Overriden from general class)
    node_superclass = 'WritingNodes'
    node_class = 'FrameEnd'
    stream_class = QtWidgets.QSpinBox

    # VISUAL PROPERTIES (Overriden from general class)
    node_width = 120
    r, g, b = (150, 24, 178)

    # NICE NAMES (Overriden from general class)
    node_superclass_nice_name = 'Writing'
    node_class_nice_name = 'Frame end'

    # NODE HELP (Overriden from general class)
    help_text = 'Frame at which the rendering will stop.'

    def setup_widget(self):
        self.widget.setMaximum(9999)

    def run_node(self):
        frame = self.widget.value()
        return [self.node_superclass, self.node_class, self.id,
                abstract_stream.FRAMEEND_INFO, frame, True]


class ExtensionNode(GeneralNode):

    # BASIC PROPERTIES (Overriden from general class)
    node_superclass = 'WritingNodes'
    node_class = 'Extension'
    stream_class = QtWidgets.QComboBox

    # VISUAL PROPERTIES (Overriden from general class)
    node_width = 110
    r, g, b = (93, 40, 191)

    # NICE NAMES (Overriden from general class)
    node_superclass_nice_name = 'Writing'
    node_class_nice_name = 'Extension'

    # NODE HELP (Overriden from general class)
    help_text = 'Image extension for the output of the stream.'

    def setup_widget(self):
        self.widget.addItems(['.exr', '.png', '.jpeg', '.tiff'])

    def run_node(self):
        ext = self.widget.currentText()
        return [self.node_superclass, self.node_class, self.id,
                abstract_stream.EXTENSION_INFO, ext, True]

# ------- ADDITIONAL INFO NODES ------- #
class VersionNode(GeneralNode):
    
    # BASIC PROPERTIES (Overriden from general class)
    node_superclass = 'InfoNodes'
    node_class = 'Version'
    stream_class = QtWidgets.QSpinBox

    # VISUAL PROPERTIES (Overriden from general class)
    node_width = 120
    r, g, b = (100, 80, 19)

    # NICE NAMES (Overriden from general class)
    node_superclass_nice_name = 'Information'
    node_class_nice_name = 'Version'

    # NODE HELP (Overriden from general class)
    help_text = 'To add information of version'

    def setup_widget(self):
        self.widget.setPrefix('v.')
        self.widget.setMinimum(0)
        self.widget.setMaximum(100)

    def run_node(self):
        version = 'v.' + str(self.widget.value()).zfill(4)
        return [self.node_superclass, self.node_class, self.id,
                abstract_stream.VERSION_INFO, version, True]

class PaddingNode(GeneralNode):
    # BASIC PROPERTIES (Overriden from general class)
    node_superclass = 'InfoNodes'
    node_class = 'Padding'
    stream_class = QtWidgets.QLineEdit

    # VISUAL PROPERTIES (Overriden from general class)
    node_width = 100
    r, g, b = (80, 170, 191)

    # NICE NAMES (Overriden from general class)
    node_superclass_nice_name = 'Information'
    node_class_nice_name = 'Padding'

    # NODE HELP (Overriden from general class)
    help_text = 'Output frames padding'

    def setup_widget(self):
        self.widget.setText('####')
        self.widget.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('#+')))

    def run_node(self):
        padding = str(self.widget.text())
        if not padding:
            return [self.node_superclass, self.node_class, self.id,
                    abstract_stream.PADDING_INFO, '####', True]

        return [self.node_superclass, self.node_class, self.id,
                abstract_stream.PADDING_INFO, padding, True]


# ------- CHECK NODES ------- #
class ErrorsNode(GeneralNode):

    # BASIC PROPERTIES (Overriden from general class)
    node_superclass = 'CheckNodes'
    node_class = 'Errors'
    stream_class = None

    # VISUAL PROPERTIES (Overriden from general class)
    node_width = 105
    r, g, b = (142, 19, 19)

    # NICE NAMES (Overriden from general class)
    node_superclass_nice_name = 'Checks'
    node_class_nice_name = 'Errors'

    # NODE HELP (Overriden from general class)
    help_text = 'Checks for common errors in all nodes (<i>node.hasError()</i>)'

    def run_node(self):
        error_nodes = nuke_specifics.all_nodes_with_errors()

        if error_nodes:
            return [self.node_superclass, self.node_class, self.id, abstract_stream.NO_WRITING_INFO,
                    'The following nodes contain some kind of error: ' + str(error_nodes), False]
        
        return [self.node_superclass, self.node_class, self.id, abstract_stream.NO_WRITING_INFO,
                'No nodes with errors have been found', True]


class RegexNamingNode(GeneralNode):

    # BASIC PROPERTIES (Overriden from general class)
    node_superclass = 'CheckNodes'
    node_class = 'RegexNaming'
    stream_class = QtWidgets.QLineEdit

    # VISUAL PROPERTIES (Overriden from general class)
    node_width = 180
    r, g, b = (124, 155, 31)

    # NICE NAMES (Overriden from general class)
    node_superclass_nice_name = 'Checks'
    node_class_nice_name = 'Regex naming'

    # NODE HELP (Overriden from general class)
    help_text = 'Will check that no node has a name that matches the Regular Expression provided as input.'

    def setup_widget(self):
        self.widget.setPlaceholderText('Enter RegEx here')

    def run_node(self):
        misnamed_nodes = nuke_specifics.regex_checks(str(self.widget.text()))

        if misnamed_nodes:
            return [self.node_superclass, self.node_class, self.id, abstract_stream.NO_WRITING_INFO,
                    'The following nodes matched the provided Regular Expression: ' + str(misnamed_nodes), False]

        return [self.node_superclass, self.node_class, self.id, abstract_stream.NO_WRITING_INFO,
                'All nodes are properly named', True]


class DisconnectedReadsNode(GeneralNode):

    # BASIC PROPERTIES (Overriden from general class)
    node_superclass = 'CheckNodes'
    node_class = 'DisconnectedReads'
    stream_class = None

    # VISUAL PROPERTIES (Overriden from general class)
    node_width = 200
    r, g, b = (191, 112, 17)

    # NICE NAMES (Overriden from general class)
    node_superclass_nice_name = 'Checks'
    node_class_nice_name = 'Disconnected Reads'

    # NODE HELP (Overriden from general class)
    help_text = 'Will check that all Read nodes in the scene have their output connected to another node.'

    def run_node(self):
        disconnected_reads = nuke_specifics.disconnected_reads()

        if disconnected_reads:
            return [self.node_superclass, self.node_class, self.id, abstract_stream.NO_WRITING_INFO,
                    'The following Read nodes were not connected to anything: ' + str(disconnected_reads), False]

        return [self.node_superclass, self.node_class, self.id, abstract_stream.NO_WRITING_INFO,
                'All Read nodes have output', True]


class ClassFilterNode(GeneralNode):

    # BASIC PROPERTIES (Overriden from general class)
    node_superclass = 'CheckNodes'
    node_class = 'ClassFilter'
    stream_class = QtWidgets.QLineEdit

    # VISUAL PROPERTIES (Overriden from general class)
    node_width = 160
    r, g, b = (178, 94, 46)

    # NICE NAMES (Overriden from general class)
    node_superclass_nice_name = 'Checks'
    node_class_nice_name = 'Class filter'

    # NODE HELP (Overriden from general class)
    help_text = 'Will check that no nodes match the class provided as input (i.e. NoOp)'

    def setup_widget(self):
        self.widget.setPlaceholderText('Enter class to filter')

    def run_node(self):
        invalid_nodes = nuke_specifics.forbidden_class_nodes(str(self.widget.text()))

        if invalid_nodes:
            return [self.node_superclass, self.node_class, self.id, abstract_stream.NO_WRITING_INFO,
                    'The following nodes belong to the specified class: ' + str(invalid_nodes), False]

        return [self.node_superclass, self.node_class, self.id,
                abstract_stream.NO_WRITING_INFO, 'No nodes match the specified class', True]


# ------- MANIPULATION NODES ------- #
class DesaturationNode(GeneralNode):

    # BASIC PROPERTIES (Overriden from general class)
    node_superclass = 'Manipulation'
    node_class = 'Desaturation'
    stream_class = None

    # VISUAL PROPERTIES (Overriden from general class)
    node_width = 130
    r, g, b = (112, 112, 112)

    # NICE NAMES (Overriden from general class)
    node_superclass_nice_name = 'Manipulation'
    node_class_nice_name = 'Desaturation'

    # NODE HELP (Overriden from general class)
    help_text = 'Desaturates the output image, leaving it in shades of gray.'

    def run_node(self):
        return [self.node_superclass, self.node_class, self.id,
                abstract_stream.NO_WRITING_INFO, 'The output result for this stream will be desaturated', True]


class FlipNode(GeneralNode):

    # BASIC PROPERTIES (Overriden from general class)
    node_superclass = 'Manipulation'
    node_class = 'Flip'
    stream_class = None

    # VISUAL PROPERTIES (Overriden from general class)
    node_width = 120
    r, g, b = (130, 50, 106)

    # NICE NAMES (Overriden from general class)
    node_superclass_nice_name = 'Manipulation'
    node_class_nice_name = 'Flip'

    # NODE HELP (Overriden from general class)
    help_text = 'Flips the image horizontally.'

    def run_node(self):
        return [self.node_superclass, self.node_class, self.id,
                abstract_stream.NO_WRITING_INFO, 'The output result for this stream will be flipped', True]


# ------- ALL NODES LIST ------- #

ALL_NODES_LIST = [StartNode, EmptyNode,

                  ErrorsNode, RegexNamingNode, DisconnectedReadsNode, ClassFilterNode,

                  DesaturationNode, FlipNode,

                  OriginNode, OriginFromNameNode, FilePathNode, CommentNode, FrameStartNode,
                  FrameEndNode, ExtensionNode,

                  VersionNode, PaddingNode]


# -------------------------------- STREAMS -------------------------------- #
# ------------------------------------------------------------------------- #

class Stream(QtWidgets.QGraphicsRectItem):

    def __init__(self, stream_index, width, colortype, parent_node):
        QtWidgets.QGraphicsRectItem.__init__(self, 0, 0, width, STRIPE_HEIGHT, parent=parent_node)

        # BASIC VISUAL PROPERTIES
        self.width = width

        # BASIC PROPERTIES
        self.parent_node = parent_node
        self.parent_class = parent_node.node_class
        self.index = stream_index

        self.input_stream = None
        self.input_line = None
        self.output_stream = None
        self.output_line = None

        # COLOR STYLE
        r, g, b = parent_node.r, parent_node.g, parent_node.b
        if colortype == 'light':
            r, g, b = r + 20, g + 20, b + 20
        grad = QtGui.QLinearGradient(0, 0, 0, STRIPE_HEIGHT)
        grad.setColorAt(0.0, QtGui.QColor(r, g, b))
        lighter_color = QtGui.QColor(r + 10, g + 10, b + 10)
        grad.setColorAt(1.0, lighter_color)
        self.setBrush(grad)

        # CONNECTORS
        self.input_connector = Connector('input', self, self.width) if self.parent_node.can_have_input else None
        self.output_connector = Connector('output', self, self.width) if self.parent_node.can_have_output else None

        # STREAM TEXTS
        stream_text = QtWidgets.QGraphicsSimpleTextItem('>> Stream {} >>'.format(self.index), parent=self)
        stream_text.moveBy(width / 2 - 48, 3)

    @property
    def parent_id(self):
        return self.parent_node.id

    def clear_connections(self):

        if self.input_stream:
            self.input_stream.output_connector.toggle_connection(restore=True)
            self.input_stream = None
            self.scene().removeItem(self.input_line)
            self.input_line = None

        if self.output_stream:
            self.output_stream.input_connector.toggle_connection(restore=True)
            self.output_stream = None
            self.scene().removeItem(self.output_line)
            self.output_line = None


# -------------------------------- CONNECTORS -------------------------------- #
# ---------------------------------------------------------------------------- #

class Connector(QtWidgets.QGraphicsPolygonItem):

    def __init__(self, c_type, parent, separation):
        QtWidgets.QGraphicsPolygonItem.__init__(self, parent=parent)

        # BASIC PROPERTIES
        self.parent_stream = parent
        self.type = c_type
        self.can_recieve_connection = True

        # CONNECTIONS
        self.connected_to = None
        self.line = None

        # VISUAL PROPERTIES
        self.separation = separation

        # SETUP
        self.setup_polygons()

    @property
    def parent_node(self):
        return self.parent_stream.parent_node

    @property
    def index(self):
        return self.parent_stream.stream_index

    @property
    def x(self):
        return self.scenePos().x()

    @property
    def center_point(self):
        return self.scenePos()

    def setup_polygons(self):
        polygon = QtGui.QPolygon([QtCore.QPoint(-SQUARE_DIAGONAL, 0), QtCore.QPoint(0, SQUARE_DIAGONAL),
                                  QtCore.QPoint(SQUARE_DIAGONAL, 0), QtCore.QPoint(0, -SQUARE_DIAGONAL)])
        self.setPolygon(polygon)
        self.setBrush(CONNECTOR_AVAILABLE_COLOR)

        if self.type == 'input':
            self.moveBy(-SQUARE_DIAGONAL, STRIPE_HEIGHT / 2)
        elif self.type == 'output':
            self.moveBy(self.separation + SQUARE_DIAGONAL, STRIPE_HEIGHT / 2)

    def toggle_connection(self, restore=False):
        if not restore:
            self.can_recieve_connection = not self.can_recieve_connection
        else:
            self.can_recieve_connection = True
            self.connected_to = None
            self.line = None

            if self.type == 'input':
                self.parent_stream.input_stream = None
                self.parent_stream.input_line = None
            elif self.type == 'output':
                self.parent_stream.output_stream = None
                self.parent_stream.output_line = None

        # Appearance
        if self.can_recieve_connection:
            self.setBrush(CONNECTOR_AVAILABLE_COLOR)
        else:
            self.setBrush(CONNECTOR_USED_COLOR)

    def register_connection(self, other_connector, line):

        self.toggle_connection()

        self.connected_to = other_connector
        self.line = line

        if self.type == 'input':
            self.parent_stream.input_stream = other_connector.parent_stream
            self.parent_stream.input_line = line
        elif self.type == 'output':
            self.parent_stream.output_stream = other_connector.parent_stream
            self.parent_stream.output_line = line
