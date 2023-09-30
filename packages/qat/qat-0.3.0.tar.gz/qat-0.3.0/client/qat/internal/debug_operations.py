# -*- coding: utf-8 -*-
# (c) Copyright 2023, Qat’s Authors

"""
Functions used for development and debugging purposes
"""

from qat.internal.application_context import ApplicationContext


def activate_picker(app_context: ApplicationContext):
    """
    Activate the object picker
    """
    command = {}
    command['command'] = 'action'
    command['attribute'] = 'picker'
    command['args'] = 'enable'

    return app_context.send_command(command)


def deactivate_picker(app_context: ApplicationContext):
    """
    Deactivate the object picker
    """
    command = {}
    command['command'] = 'action'
    command['attribute'] = 'picker'
    command['args'] = 'disable'

    return app_context.send_command(command)
