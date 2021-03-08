import abc

class result:
    def __init__(self, title, year, poster, overview):
        self.title = title
        self.year = year
        self.poster = poster
        self.overview = overview

class MediaRetriever( abc.ABC ) :
    @abc.abstractclassmethod
    def searchForMedia(self, search_term: str ):
        pass

