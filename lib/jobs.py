#!/usr/bin/env python

from time import localtime, strftime

import yaml

instance_types = [
    {"name": "m1.tiny", 'CPUs': 1, "RAM": 2, "Storage": 8},
    {"name": "m1.small", 'CPUs': 2, "RAM": 4, "Storage": 20},
    {"name": "m1.medium", 'CPUs': 6, "RAM": 16, "Storage": 60},
    {"name": "m1.large", 'CPUs': 10, "RAM": 30, "Storage": 60},
    {"name": "m1.xlarge", 'CPUs': 24, "RAM": 60, "Storage": 60},
    {"name": "m1.xxlarge", 'CPUs': 44, "RAM": 120, "Storage": 60},
    #{"name": "s1.large", 'cPUs': 10, "RAM": 2, "Storage": 120},
    #{"name": "s1.xlarge", 'cPUs': 24, "RAM": 2, "Storage": 240},
    #{"name": "s1.xxlarge", 'cPUs': 44, "RAM": 2, "Storage": 480},
]

class Job(object):

    def __getitem__(self, key):
        """Dictionary-like lookup."""
        if key in self.__dict__:
            return self.__dict__[key]
        else:
            return None

    def __setitem__(self, key, value):
        """Dictionary-like value setting."""
        self.__dict__[key] = value
        return None
    
    def __init__(self, fname):
        self.CPUs = 1
        self.RAM = 1
        self.Storage = 1
        self.instance = None
        self.inputs = []
        self.outputs = []
        self.state = 'waiting_for_inputs'
        self.ID = strftime("%m-%d-%H-%M", localtime())
        self.script = None
        self.yaml = None
        data = yaml.load(open(fname))
        for key, value in data.iteritems():
            self[key] = value
        self.determine_instance()
        if self.script is None or self.yaml is None or self.instance is None:
            self.state = 'error'

    def determine_instance(self):
        for instance in instance_types:
            if (instance['CPUs'] >= self.CPUs and
                instance['RAM'] >= self.RAM and
                instance['Storage'] >= self.Storage):
                self.instance = instance
                break

    def update_state(self, file_dict):
        missing_in = False
        missing_out = False
        for file in self.inputs:
            if file_dict[file] is None:
                self.state = 'error'
                break
            elif not file_dict[file]:
                missing_in = True
        if self.state != 'error':
            for file in self.outputs:
                if file_dict[file] != True:
                    missing_out = True
            if not missing_in:
                if not missing_out:
                    self.state = 'finished'
                else:
                    self.state = 'ready'

    def score_job(self, resources):
        # score job requirements based on available resources to find best fit
        return self.score







