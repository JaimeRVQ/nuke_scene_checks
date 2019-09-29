# -*- coding: UTF-8 -*-
'''
Author: Jaime Rivera
File: nuke_specifics.py
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

import re
import nuke


# -------------------------------- INFO FROM SCENE -------------------------------- #

def all_node_names():
    return sorted([node.name() for node in nuke.allNodes() if node.Class() != 'Viewer'])

def all_writes():
    return sorted([node.name() for node in nuke.allNodes('Write')])

# -------------------------------- CHECKS -------------------------------- #

def node_exists(node_name):
    return node_name in [n.name() for n in nuke.allNodes()]

def all_nodes_with_errors():
    error_nodes = []

    for node in nuke.allNodes():
        if node.hasError():
            error_nodes.append(node.name())

    return error_nodes

def regex_checks(regex_string):
    misnamed_nodes = []
    regex = re.compile(regex_string)

    for node in nuke.allNodes():
        if re.match(regex, node.name()):
            misnamed_nodes.append(node.name())

    return misnamed_nodes

def disconnected_reads():
    disconnected_reads = []
    for node in nuke.allNodes('Read'):
        if not node.dependent(2):
            disconnected_reads.append(node.name())

    return disconnected_reads

def forbidden_class_nodes(forbidden_class):
    invalid_nodes = []
    for node in nuke.allNodes():
        if node.Class() == forbidden_class:
            invalid_nodes.append(node.name())

    return invalid_nodes


# -------------------------------- WRITING -------------------------------- #

def write_path(origin_node, path, start_frame, end_frame, extra_nodes):

    wr = nuke.nodes.Write(name='WRITER')

    # Extra manipulations
    extra_names = []
    if extra_nodes:
        for n in extra_nodes:

            if n == 'Desaturation':
                cc = nuke.nodes.ColorCorrect(name='EXTRA_DESATURATION')
                cc['saturation'].setValue(0)
                extra_names.append('EXTRA_DESATURATION')

            if n == 'Flip':
                t = nuke.nodes.Transform(name='EXTRA_FLIP')
                t.setInput(0, nuke.toNode(origin_node))
                w, h = t.width()/2, t.height()/2
                t['center'].setValue(w, 0)
                t['center'].setValue(h, 1)
                t['scale'].setValue(-1, 0)
                t['scale'].setValue(1, 1)
                extra_names.append('EXTRA_FLIP')

        first_extra_node = nuke.toNode(extra_names[0])
        first_extra_node.setInput(0, nuke.toNode(origin_node))

        if len(extra_names) > 1:
            for i in range(len(extra_names) - 1):
                nuke.toNode(extra_names[i+1]).setInput(0, nuke.toNode(extra_names[i]))

        origin_node = extra_names[-1]

    # Execution
    wr['file'].setValue(path)
    wr.setInput(0, nuke.toNode(origin_node))
    nuke.execute(wr, start_frame, end_frame)

    # Cleanup
    nuke.delete(wr)
    for name in extra_names:
        nuke.delete(nuke.toNode(name))