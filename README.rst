sshconnector: Python Ssh Server Easy API..
======================================

Simple API for connect server with `ssh` by password or public-key authentication.
You can do:

- connect server by ssh and execute command on remote server
- upload and download file from remote server by the sftp


**Note:**

- on windows: if connected with public-key, you should pass the `openssh` private key, password for decrypting if nessesary.


Usage
-----

`SSHConnector` is the main class, `SFTPMutilthread` is for downloading file with `Coroutine`(`gevent`), .

connect server by public-key

    >>> import sshconnector
    >>> sshconnector = SSHConnector(host="192.168.157.2", port=22, username="root", password="root",
                                    pub_key_file_path="/path/of/my-private-openssh-key")

exec command

    >>> sshconnector.execute_command(command="ls -l")

upload file from local server

    >>> sshconnector.sftp_put("/home/my/local/file", "/remote/server/save/file")

download file from remote server

    >>> sshconnector.sftp_get("/remote/server/save/file", "/home/my/local/file")

download file from remote server with multi thread

    >>> import SFTPMutilthread
    >>> serverdatasource = [("192.168.157.1", 22), ("192.168.157.2", 22), ("192.168.157.3", 22), ]
    >>> remotefile = "/remote/file"
    >>> localfile = "E:/save/local/file"
    >>> mutilhelper = SFTPMutilthread(serverdatasource, remotefile, localfile, "root", "root", "/path/of/my-private-openssh-key")
    >>> mutilhelper.start()

Very stupid!