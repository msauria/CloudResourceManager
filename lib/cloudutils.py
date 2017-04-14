"""Launch an instance on Jetstream."""
from time import localtime, strftime, sleep

from cloudbridge.cloud.factory import CloudProviderFactory, ProviderList
import fabric


class Instance(object):

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
    
    def __init__(self, instance_type, ip=None, name=None, volume=None):
        self.job = None
        self.instance_type = instance_type.strip().lower()
        self.subnet_id = '890be584-9ff8-4dc8-a746-47c331cb7ea3'  # CloudBridgeSubnet
        self.sgs = ['CloudLaunch']
        self.kp_name = "cloudman_key_pair"
        self.img_id = '0df49222-8014-4a7a-9933-e7383a09678f'
        if name is None and ip is None:
            self.launch(volume)
        elif name is None:
            self.ip = ip
            self.find_name()
        else:
            self.name = name
            self.find_ip()

    def launch(self, volume=None):
        """Initiate an instance launch."""
        provider = self.get_provider()  # Ubuntu 16.04 with Docker
        self.name = 'dckr-{0}'.format(strftime("%m-%d-%H-%M", localtime()))

        print("Launching...")
        i = provider.compute.instances.create(
            self.name, self.img_id, self.instance_type, security_groups=self.sgs, key_pair=self.kp_name,
            subnet=self.subnet_id)
        try:
            print("Waiting for instance {0} to launch...".format(self.name))
            i.wait_till_ready()
        except AttributeError:
            sleep(2)
            print("Still waiting for the instance to launch...")
            i.wait_till_ready()

        # Attach a volume
        # for v in provider.block_store.volumes.list():
        #     if v.state == 'available':
        #         v.attach(i.id, '/dev/sdb')
        #         print(i.private_ips[0])
        #         break

        # Attach a floating IP to the instance
        self.fip = None
        fips = provider.network.floating_ips()
        for ip in fips:
            if not ip.in_use():
                self.fip = ip
        if self.fip:
            i.add_floating_ip(self.fip.public_ip)
            print("Launched inst {0} with IP {1}".format(self.name, self.fip.public_ip))
        else:
            raise("No available floating IP found for instance {0}.".format(self.name))

    def get_provider(self):
        """Return a connection object for a cloud provider."""
        os_username = "username"
        os_password = "pwd"
        os_project_name = "TG-CCR160022"

        js_config = {"os_username": os_username,
                     "os_password": os_password,
                     "os_auth_url": "https://jblb.jetstream-cloud.org:35357/v3",
                     "os_user_domain_name": "tacc",
                     "os_project_domain_name": "tacc",
                     "os_project_name": os_project_name}
        return CloudProviderFactory().create_provider(ProviderList.OPENSTACK,
                                                      js_config)

    def find_ip(self):
        """Delete an instance with a given IP address."""
        provider = self.get_provider()
        for inst in provider.compute.instances.list():
            if inst.name == self.name:
                self.ip = inst.public_ips[0]

    def find_name(self):
        """Delete an instance with a given IP address."""
        provider = self.get_provider()
        for inst in provider.compute.instances.list():
            if inst.public_ips[0] == self.ip:
                self.name = inst.name

    def delete(self):
        """Delete an instance with a given IP address."""
        provider = self.get_provider()
        for inst in provider.compute.instances.list():
            if inst.public_ips[0] == self.ip:
                inst.terminate()
                print("{0}, {1}".format(inst.name, self.ip))

    def run_job(self):
        #launch job as bg process on instance

    def job_finished(self):
        # check in with job and return True if job has finished

