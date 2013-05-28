# Author: Arnaud Dartois
# URL: http://code.google.com/p/sickbeard/
#
# This file is part of Sick Beard.
#
# Sick Beard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sick Beard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sick Beard.  If not, see <http://www.gnu.org/licenses/>.
import time
import os
import sickbeard
import ftplib as ftp
import glob

from sickbeard import logger

class SentFTPChecker():
    def __init__(self):
        self.todoWanted = []
        self.todoBacklog = []

    def run(self):
        if sickbeard.USE_TORRENT_FTP:
            # upload all torrent file to remote FTP
            logger.log("Sending torrent file to FTP", logger.DEBUG)
            self._sendToFTP("*.torrent", sickbeard.TORRENT_DIR)

    def _sendToFTP(filter, dir):
        """
        Send all torrent of the specified filter (eg "*.torrent") to the appropriate FTP.

        """

        # Connect to the FTP server
        logger.log(u"Initializing FTP Session", logger.DEBUG)
        session = ftp.FTP_Host(sickbeard.FTP_HOST, sickbeard.FTP_LOGIN, sickbeard.FTP_PASSWORD)

        # Assign FTP Port
        logger.log(u"Assign FTP Port", logger.DEBUG)
        ftp.FTP_PORT = sickbeard.FTP_PORT

        # Assign passive mode
        logger.log(u"Assign Session Passive Mode", logger.DEBUG)
        session.set_pasv(sickbeard.FTP_PASSIVE)

        # get welcome message
        welcome = session.getwelcome()
        if welcome != '':
            logger(u"If a welcome message is detected, we log it :" + session.welcome, logger.DEBUG)

        # change remote directory
        logger(u"Set Remote Directory : " + sickbeard.FTP_DIR, logger.DEBUG)
        session.chdir(sickbeard.FTP_DIR)

        os.chdir(dir)

        for fileName in glob.glob(filter):

            # Send the file
            logger(u"Send local file : " + fileName, logger.DEBUG)
            session.upload(fileName, os.path.basename(fileName), "b")

            # delete local file
            logger(u"Deleting local file : " + fileName, logger.DEBUG)
            os.remove(fileName)

        # Close FTP session
        logger.log(u"Close FTP Session", logger.DEBUG)
        session.quit()

        logger(u"It's working ... hop a beer !", logger.DEBUG)