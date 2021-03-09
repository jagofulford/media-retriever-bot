import abc

class result:
    def __init__(self, title, year, poster, overview, id, source):
        self.title = title
        self.year = year
        self.poster = poster
        self.overview = overview
        self.id = id
        self.source = source

class MediaRetriever( abc.ABC ) :
    @abc.abstractclassmethod
    def searchForMedia(self, search_term: str ) -> list[result]:
        pass

