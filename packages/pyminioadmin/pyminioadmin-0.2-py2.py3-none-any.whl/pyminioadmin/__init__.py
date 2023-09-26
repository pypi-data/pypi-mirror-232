import subprocess
from typing import Any

class MinioAdminClient:
    def __init__(self, endpoint: str, access_key: Any = None, secret_key: Any = None, secure: bool = True, cert_check: bool = True):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure
        self.cert_check = cert_check
        self.set_alias()

    def set_alias(self):
        protocol = ''
        if self.secure == True:
            protocol = "https://"
        elif self.secure == False:
            protocol = "http://"
        command = ''
        if self.cert_check == True:
            command = f"mc alias set mcadminclient {protocol}{self.endpoint} {self.access_key} {self.secret_key}"
        else:
            command = f"mc alias set mcadminclient {protocol}{self.endpoint} {self.access_key} {self.secret_key} --insecure"
        subprocess.run(command, shell=True)

    def create_user(self, access_key: str, secret_key: str):
        if self.cert_check == True:
            full_command = f"mc admin user add mcadminclient {access_key} {secret_key}"
        else:
            full_command = f"mc admin user add mcadminclient {access_key} {secret_key} --insecure"
        process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            return f"An error occurred: {stderr.decode()}"
        return stdout.decode()
    
    def delete_user(self, access_key: str):
        if self.cert_check == True:
            full_command = f"mc admin user rm mcadminclient {access_key}"
        else:
            full_command = f"mc admin user rm mcadminclient {access_key} --insecure"
        process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            return f"An error occurred: {stderr.decode()}"
        return stdout.decode()

    def disable_user(self, access_key: str):
        if self.cert_check == True:
            full_command = f"mc admin user disable mcadminclient {access_key}"
        else:
            full_command = f"mc admin user disable mcadminclient {access_key} --insecure"
        process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            return f"An error occurred: {stderr.decode()}"
        return stdout.decode()
    
    def enable_user(self, access_key: str):
        if self.cert_check == True:
            full_command = f"mc admin user enable mcadminclient {access_key}"
        else:
            full_command = f"mc admin user enable mcadminclient {access_key} --insecure"
        process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            return f"An error occurred: {stderr.decode()}"
        return stdout.decode()
    
    def list_groups(self):
        if self.cert_check == True:
            full_command = f"mc admin group ls mcadminclient"
        else:
            full_command = f"mc admin group ls mcadminclient --insecure"
        process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            return f"An error occurred: {stderr.decode()}"
        return stdout.decode()

    def add_members_to_group(self, group_name: str, members: list):
        members_str = ' '.join(members)
        if self.cert_check == True:
            full_command = f"mc admin group add mcadminclient {group_name} {members_str}"
        else:
            full_command = f"mc admin group add mcadminclient {group_name} {members_str} --insecure"
        process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            return f"An error occurred: {stderr.decode()}"
        return stdout.decode()
    
    def delete_group(self, group_name: str):
        if self.cert_check == True:
            full_command = f"mc admin group rm mcadminclient {group_name}"
        else:
            full_command = f"mc admin group rm mcadminclient {group_name} --insecure"
        process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            return f"An error occurred: {stderr.decode()}"
        return stdout.decode()
    
    def add_bucket_quota(self, bucket_name: str, size: str):
        """
        Suffixes available: k = KB, m = MB, g = GB, t = TB, ki or kib = KiB, mi or mib = MiB, gi or gib = GiB, ti or tib = TiB.
        size(str): should contain a number and one of the suffixes, example: 10g.
        """
        if self.cert_check == True:
            full_command = f"mc quota set mcadminclient/{bucket_name} --size {size}"
        else:
            full_command = f"mc quota set mcadminclient/{bucket_name} --size {size} --insecure"
        process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            return f"An error occurred: {stderr.decode()}"
        return stdout.decode()
    
    def attach_policy(self, type:str, policy: str, value: str):
        """
        type (str): type should be either user or group.
        policy(str): policy should be one of the following: readonly, readwrite, diagnostics, writeonly.
        value(str): value is either the name of the user or the name of the group.
        """
        allowed_types = ['user', 'group']
        allowed_policies = ['readonly', 'readwrite', 'diagnostics', 'writeonly']
        if type not in allowed_types:
            raise ValueError(f"Invalid type {type}. Allowed types are {allowed_types}")
        if policy not in allowed_policies:
            raise ValueError(f"Invalid policy {policy}. Allowed policies are {allowed_policies}")
        if self.cert_check == True:
            full_command = f"mc admin policy attach mcadminclient {policy} --{type} {value}"
        else:
            full_command = f"mc admin policy attach mcadminclient {policy} --{type} {value} --insecure"
        process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            return f"An error occurred: {stderr.decode()}"
        return stdout.decode()