import configparser
from twisted.internet import reactor
from twisted.protocols import ftp
from twisted.cred.portal import Portal
from twisted.cred.checkers import FilePasswordDB

conf = configparser.ConfigParser()
conf.read('./conf/default.conf')

class OnUpload(ftp.FTP):
    # store the username when given in case actions are dependent on it
    def ftp_USER(self, username):
        d = super(OnUpload, self).ftp_USER(username)
        self.user = username
        return d

    def ftp_STOR(self, path):
        d = super(OnUpload, self).ftp_STOR(path)
        d.addCallback( lambda status: self.onStorComplete(path, status) )
        return d

    def onStorComplete(self, path, status):
        
        if self.user == 'korkeasaari':
            print 'User ' + self.user + ' uploaded a file with name ' + path
            print 'I could be uploading it to S3 datastore bucket right now'

        return status

if __name__ == '__main__':
    #NB userHome path must contain a folder for each user
    #anonymousRoot has to be != None, even though we don't allow anon access
    p = Portal(ftp.FTPRealm(anonymousRoot='./', userHome=conf['DEFAULT']['homedir_basepath']),
            (FilePasswordDB(conf['DEFAULT']['credentials_file']),))

    f = ftp.FTPFactory( p )
    f.protocol = OnUpload

    reactor.listenTCP(int(conf['DEFAULT']['port']), f)
    reactor.run()
