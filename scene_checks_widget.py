# -*- coding: UTF-8 -*-
'''
Author: Jaime Rivera
File: scene_checks_widget.py
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
from PySide2 import QtGui
from PySide2 import QtCore
import os

import node_classes
import custom_widgets
import abstract_stream


class SceneChecks(QtWidgets.QWidget):

    def __init__(self):

        QtWidgets.QWidget.__init__(self)
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path).replace('\\', '/') + '/'
        self.ICONS_PATH = dir_path + '/Icons/'

        # STYLE
        self.zoom = 1
        self.setMinimumWidth(850)
        self.setMinimumHeight(500)
        self.resize(1550, 850)
        self.setWindowTitle('Scene checks / write')

        # FEEDBACK
        self.the_process_window = QtWidgets.QTextEdit()
        self.the_process_window.setReadOnly(True)
        self.the_process_window.setWindowTitle('Stream execution feedback')

        # LAYOUT
        self.grid = QtWidgets.QGridLayout(self)

        # ELEMENTS
        self.nodes_tree = QtWidgets.QTreeWidget()
        self.nodes_tree.setHeaderLabel('Available nodes')
        self.nodes_tree.setMinimumWidth(260)
        self.nodes_tree.setFont(QtGui.QFont('arial', 14))
        self.nodes_tree.setDragEnabled(True)
        self.grid.addWidget(self.nodes_tree, 0, 0, 1, 1)

        self.save_network_btn = QtWidgets.QPushButton('Save network')
        self.save_network_btn.setFixedHeight(35)
        self.grid.addWidget(self.save_network_btn, 1, 0, 1, 1)

        self.load_network_btn = QtWidgets.QPushButton('Load network')
        self.load_network_btn.setFixedHeight(35)
        self.grid.addWidget(self.load_network_btn, 2, 0, 1, 1)

        self.gs = custom_widgets.CustomScene()
        self.gs.setSceneRect(-20000, -20000, 20000, 20000)

        self.gw = custom_widgets.CustomGW()
        self.gw.setScene(self.gs)
        self.gs.setParent(self.gw)
        self.grid.addWidget(self.gw, 0, 1, 3, 3)

        self.visualize_streams_btn = QtWidgets.QPushButton('Visualize Streams')
        self.visualize_streams_btn.setFixedHeight(50)
        self.grid.addWidget(self.visualize_streams_btn, 3, 2, 1, 1)

        self.run_btn = QtWidgets.QPushButton('Run All')
        self.run_btn.setFixedHeight(50)
        self.grid.addWidget(self.run_btn, 3, 3, 1, 1)

        # CONNECTIONS
        self.save_network_btn.clicked.connect(self.save_network)
        self.load_network_btn.clicked.connect(self.load_network)
        self.visualize_streams_btn.clicked.connect(self.visualize_all_streams)
        self.run_btn.clicked.connect(self.run_all_streams)

        # INITIALIZE
        self.populate_tree()
        self.show()


    def populate_tree(self):

        used_nice_superclasses = []

        for c in node_classes.ALL_NODES_LIST:

            if c.node_superclass_nice_name not in used_nice_superclasses:
                nodes_group = QtWidgets.QTreeWidgetItem(self.nodes_tree)
                nodes_group.setText(0, c.node_superclass_nice_name)
                self.nodes_tree.addTopLevelItem(nodes_group)
                used_nice_superclasses.append(c.node_superclass_nice_name)

            child_action = QtWidgets.QTreeWidgetItem()
            child_action.setText(0, ' ' + c.node_class_nice_name)
            child_action.setIcon(0, QtGui.QIcon(self.ICONS_PATH + c.node_class + '.png'))
            top_item = self.nodes_tree.findItems(c.node_superclass_nice_name, QtCore.Qt.MatchExactly)[0]
            top_item.addChild(child_action)

        self.nodes_tree.expandAll()

    def save_network(self):
        self.gs.save_to_file()

    def load_network(self):
        self.gs.load_from_file()

    def visualize_all_streams(self):
        self.gs.color_streams()

    def run_all_streams(self):
        self.the_process_window.clear()
        self.the_process_window.resize(950,700)
        self.the_process_window.show()

        for node in self.gs.all_nodes:
            if node.node_class == 'Start':
                for stream in node.streams:
                    abstract_stream.AbstactStream(stream, self.the_process_window)