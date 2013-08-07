# Author: Nic Wolfe <nic@wolfeden.ca>
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

import datetime
import operator

import sickbeard

from sickbeard import db
from sickbeard import helpers, logger, show_name_helpers
from sickbeard import providers
from sickbeard import search
from sickbeard import history

from sickbeard.common import DOWNLOADED, SNATCHED, SNATCHED_FRENCH, Quality

from lib.tvdb_api import tvdb_api, tvdb_exceptions

from name_parser.parser import NameParser, InvalidNameException


class FrenchFinder():

    def __init__(self, force=None, show=None):

        #TODOif not sickbeard.DOWNLOAD_FRENCH:
        #    return
        if sickbeard.showList==None:
            return
        logger.log(u"Beginning the search for french episodes")
       
        frenchlist=[]
        #get list of english episodes that we want to search in french
        myDB = db.DBConnection()
        if show:
            frenchsql=myDB.select("SELECT showid, season, episode from tv_episodes where audio_langs='en' and tv_episodes.showid =?",[show]) 
        else:
            frenchsql=myDB.select("SELECT showid, season, episode from tv_episodes, tv_shows where audio_langs='en' and tv_episodes.showid = tv_shows.tvdb_id and tv_shows.frenchsearch = 1")
        #make the episodes objects
        for episode in frenchsql:
            showObj = helpers.findCertainShow(sickbeard.showList, episode[0])
            epObj = showObj.getEpisode(episode[1], episode[2])
            frenchlist.append(epObj)
        
        #for each episode in frenchlist fire a search in french
        for frepisode in frenchlist:
            result=[]
            for curProvider in providers.sortedProviderList():

                if not curProvider.isActive():
                    continue

                logger.log(u"Searching for french episodes on "+curProvider.name +" for " +frepisode.show.name +" season "+str(frepisode.season)+" episode "+str(frepisode.episode))
                curfrench = curProvider.findFrench(frepisode, manualSearch=True)
                for x in curfrench:
                    result.append(x)
            best = search.pickBestResult(result, episode = epObj.episode, season = epObj.season)
            if best:
                best.name=best.name + ' snatchedfr'
                logger.log(u"Found french episode for " +frepisode.show.name +" season "+str(frepisode.season)+" episode "+str(frepisode.episode))
                search.snatchEpisode(best, SNATCHED_FRENCH)
            else:
                logger.log(u"No french episodes found for " +frepisode.show.name +" season "+str(frepisode.season)+" episode "+str(frepisode.episode))
        