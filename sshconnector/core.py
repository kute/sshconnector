#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
@version: 1.0
@ __author__: kute
@ __file__: sftp_downloader.py
@ __mtime__: 2016/10/19 17:12

ssh 公私钥密码认证，sftp下载

http://blog.csdn.net/kutejava/article/details/52880573

"""

import sys
import socket
import traceback
import paramiko
from paramiko import SSHException, AuthenticationException
from gevent.pool import Pool
from gevent import monkey
from multiprocessing import cpu_count

monkey.patch_all()
plat = sys.platform


class SSHConnector(object):

    def __init__(self, host=None, port=22, username=None, password=None, pub_key_file_path=None,
                 known_hosts_file_path=None):
        """
        :param pub_key_file_path
                on windows: pub_key_file_path should be openssh-format and passed with private_key,
                and passed 'password' parameter if your private_key need decipher with password.
                other platforms: just passed public_key
        """
        if not host or not port or not username:
            raise ValueError("Parameters illegal")
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.pub_key_file = pub_key_file_path
        self.knownhost = known_hosts_file_path
        self.hostkeys = self._load_host_keys()

        self.sshclient = self._connect()
        if self.sshclient:
            self.session = self.sshclient.get_transport().open_session()
        self.sftpclient = self._init_sftp_client()

    def _connect(self):
        try:
            client = paramiko.SSHClient()
            # client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if self.pub_key_file:
                if plat == "win32":
                    client.connect(hostname=self.host, port=self.port, username=self.username,
                                   password=self.password, key_filename=self.pub_key_file)
                else:
                    client.connect(hostname=self.host, port=self.port, username=self.username, key_filename=self.pub_key_file)
            else:
                client.connect(hostname=self.host, port=self.port, username=self.username, password=self.password)
            return client
        except AuthenticationException as e:
            raise AuthenticationException(self._error(e))
        except SSHException as e:
            raise SSHException(self._error(e))

    def _error(self, e):
        out, err = '', u"\n".join([e.strerror, traceback.format_exc()])
        return err

    def _load_host_keys(self):
        host_keys = {}
        if self.knownhost:
            try:
                host_keys = paramiko.util.load_host_keys(self.knownhost)
            except IOError as e:
                try:
                    # try ~/ssh/ too, because windows can't have a folder named ~/.ssh/
                    host_keys = paramiko.util.load_host_keys()
                except IOError as e:
                    raise IOError("Unable to open host keys file:{}".format(self.knownhost), self._error(e))
        return host_keys

    def _init_sftp_client(self):
        if self.sshclient:
            return self.sshclient.open_sftp()
        if self.host in self.hostkeys:
            hostkeytype = self.hostkeys[self.host].keys()[0]
            hostkey = self.hostkeys[self.host][hostkeytype]
            hostfqdn = socket.getfqdn(self.host)
            try:
                t = paramiko.Transport((self.host, self.port))
                t.connect(hostkey=hostkey, username=self.username, password=self.password,
                          gss_host=hostfqdn, gss_auth=True, gss_kex=True)
                sftp = paramiko.SFTPClient.from_transport(t, max_packet_size=1000 * 1000 * 10)
                return sftp
            except SSHException as e:
                traceback.print_exc()
                t.close()
                sys.exit(1)

    def execute_command(self, command="ls -l", timeout=3000):
        """execute command
        :param command:
        :param timeout:
        """
        stdin, stdout, stderr = self.session.exec_command(command)
        if stderr:
            raise SSHException(stderr)
        self.sshclient.close()
        return stdout

    def _sftp_operation(self, remotefile=None, localfile=None, op=None):
        """do some sftp operations like 'get', 'put', 'read', 'write' """
        if not remotefile or not localfile:
            raise ValueError("must special remote and dest file path")
        sftp = self.sshclient.open_sftp()
        if op == "get":
            sftp.get(remotefile, localfile)
        elif op == "put":
            sftp.put(localfile, remotefile)
        sftp.close()
        self.sshclient.close()

    def sftp_get(self, remotefile=None, destfile=None):
        """download file to remote server
        :param remotefile
                    like /home/app/server.txt
        :param destfile
                    like /mycomputer/save/local.txt
        """
        self._sftp_operation(remotefile, destfile, "get")

    def sftp_put(self, localfile=None, remotefile=None):
        """upload file from remote server"""
        self._sftp_operation(remotefile, localfile, "put")


class SFTPMutilthread(object):
    def __init__(self, server_source, remotefile=None, localfile=None, username=None, password=None, pub_key_file_path=None,
                 known_hosts_file_path=None):
        """
        :param server_source
                   like [(ip1, port1), (ip2, port2), ...]
        :param pub_key_file_path
                on windows: pub_key_file_path should be openssh-format and passed with private_key,
                and passed 'password' parameter if your private_key need decipher with password.
                other platforms: just passed public_key
        """
        self.serversource = server_source
        try:
            iter(self.serversource)
        except TypeError:
            raise TypeError("""supplied server source must be a list with tuple,
               not %s""" % server_source.__class__.__name__)
        self.remotefile = remotefile
        self.localfile = localfile
        self.username = username
        self.password = password
        self.pub_key_file = pub_key_file_path
        self.knownhost = known_hosts_file_path

    def _download_mutil(self, host, port):
        try:
            sshconnector = SSHConnector(host=host, port=int(port), username=self.username,
                                        password=self.password, pub_key_file_path=self.pub_key_file_path,
                                        known_hosts_file_path=self.known_hosts_file_path)
            sshconnector.sftp_get(self.remotefile, self.localfile)
        except SSHException as e:
            out, err = '', u"\n".join([e.strerror, traceback.format_exc()])
            raise SSHException(err)

    def start(self):
            """download same file with multi thread from multi server.
            """
            cpunum = cpu_count()
            pool = Pool(cpunum)
            pool.map(self._download_mutil, self.server_source)


def main():
    pass


if __name__ == "__main__":
    main()
