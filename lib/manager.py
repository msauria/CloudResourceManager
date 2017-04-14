#!/usr/bin/env python

import os
import glob
from time import sleep

import yaml

from .jobs import Job
from .cloudutils import Instance

class Manager(object):

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
    
    def __init__(self, config_fname):
        # need to create object store or connect to object store up front. How do we know whether an object store exists?
        self.staging = {}
        self.queue = {}
        self.finished = {}
        self.errored = {}
        self.running = {}
        self.files = {}
        self.outdir = './'
        self.instances = {}
        self.queues = {'waiting_on_inputs': self.staging, 'ready': self.queue,
                  'finished': self.finished, 'error': self.errored, 'running': self.running}
        data = yaml.load(open(config_fname))
        for key, value in data.iteritems():
            self[key] = value
        yaml_fnames = glob.glob(self.pattern)
        for fname in yaml_fnames:
            job = Job(fname)
            for file in job.inputs:
                self.files[file] = False
            for file in job.outputs:
                self.files[file] = False
            self.staging[job.ID] = job
        self.load_instances()
        for file in self.files.keys():
            self.files[file] = self.check_file_status(file)
        for ID, job in self.staging.iteritems():
            if job.state == 'error':
                for file in self.outputs:
                    if self.files[file] != True:
                        self.files[file] = None
            self.errored
        self.update_job_states()

    def load_instances(self):
        if self.instance_log is None:
            return None
        for line in open(self.instance_log):
            ip, instance_type = line.rstrip('\n').split('\t')
            self.instances[ip] = Instance(instance_type, ip=ip)

    def check_file_status(self, file):
        # need to be able to check whether file exists on object store
        return os.path.exists("%s/%s" % (self.outdir, file))

    def run_jobs(self):
        while len(self.queue) > 0:
            best_score = 999999
            while best_score > 0:
                best_score = 0
                best_ID = None
                for ID, job in self.queue.iteritems():
                    if job.score_job(self.resources) > best_score:
                        best_score = job.score
                        best_ID = ID
                if best_ID is None:
                    break
                job = self.queue.pop(best_ID)
                instance = self.find_available_instance(job.instance)
                if instance is None:
                    instance = Instance(job.instance)
                    self.instances[instance.ip] = instance
                instance.job = job
                self.running[job.ID] = job
                instance.run_job()
            self.clean_unused_instances()
            while self.monitor_jobs():
                sleep(180)
            self.update_job_states()


    def clean_unused_instances(self):
        for key, instance in self.instances.iteritems():
            if instance.job is None:
                instance.delete()
                del self.instances[key]

    def monitor_jobs(self):
        finished = False
        for key, instance in self.instances.iteritems():
            finished = finished | self.resolve_instance_job(instance)
        return finished

    def update_job_states(self):
        for ID, job in self.staging:
            job.update_state(self.files)
            if job.state != 'waiting_for_inputs':
                job = self.staging.pop(ID)
                self.queues[job.state][ID] = job
        for ID, job in self.queue:
            job.update_state(self.files)
            if job.state != 'ready':
                job = self.queue.pop(ID)
                self.queues[job.state][ID] = job

    def resolve_instance_job(self, instance):
        finished = False
        if instance.job_finished():
            job = instance.job
            self.running.pop(job.ID)
            instance.job = None
            finished = True
            missing = False
            for file in job.outputs:
                if not self.check_file_status(file):
                    self.files[file] = None
                    missing = True
            if missing:
                job.state = 'error'
                self.errored[job.ID] = job
            else:
                job.state = 'finished'
                self.finished[job.ID] = job
        return finished










