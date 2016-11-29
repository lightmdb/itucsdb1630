from flask import current_app
from collections import OrderedDict
from lightmdb.models import Movie, User

def get_database():
    from lightmdb import get_db
    return get_db(current_app)


class Playlist(object):
    """Playlist Model."""
	PLAYLIST_MOVIES= 'playlist_movies'
	MOVIES_TABLE = 'movies'
    TABLE_NAME = 'playlists'

    def __init__(self, pk=None, name=None, is_public=False, user=None):
        self.pk = pk
        self.name = name
		self.user = user
		self.is_public = is_public

    def get_id(self):
        return str(self.pk)

    def values(self):
        data = OrderedDict([
            ('pk', self.pk),
            ('name', self.name),
            ('is_public', self.is_public),
            ('user', self.user),
        ])
        return data

    @classmethod
    def get(cls, pk=None, name=None):
        """Get playlist by identifier.

        Usage: Playlist.get(title)
        :rtype: Playlist object or None
        """
        db = get_database()
        cursor = db.cursor
        if pk:
            cursor.execute(
                "SELECT * FROM {table} WHERE id=%(id)s".format(table=cls.TABLE_NAME),
                {'id': pk}
            )
        elif title:
            cursor.execute(
                "SELECT * FROM {table} WHERE name=%(name)s".format(table=cls.TABLE_NAME),
                {'name': name}
            )
        else:
            return None
        playlist = db.fetch_execution(cursor)
        if playlist:
            return Playlist(**playlist[0])
        return None
    
    @classmethod
    def append(title):
        _movie = Movie.get(title)
        if not _movie:
            abort(404,{'message':'Movie Title not found.'})
        db = get_database()
        cursor = db.cursor
        query = "INSERT INTO {table} " \
                "(name, " + str(_movie.pk)  +  "  , ordering) " \
                "VALUES" \
                "(%(name)s, %(movie_id)s, %(ordering)s".format(table=self.PLAYLIST_MOVIES)
        db.cursor.execute(query, dict(data))
        db.commit()
        return self.get(pk=self.pk)

	@classmethod
	def get_movies():
		movie_ids = []
        db = get_database()
        cursor = db.cursor
        cursor.execute(
            "SELECT movie_id FROM {table} WHERE playlist_id=%(playlist_id)s ORDER BY ORDERING ASC".format(table=cls.PLAYLIST_MOVIES), {'playlist_id': pk} 
        )  
        movie_ids = db.fetch_execution(cursor)
        movies = []
        for item in movie_ids:
            movies.append(Movie.get(item))
		return movies


    @classmethod
    def filter(cls, **kwargs):
        db = get_database()
        cursor = db.cursor
        filter_data = {}
        query = "SELECT * FROM " + cls.TABLE_NAME
        if kwargs:
            filter_query, filter_data = db.where_builder(kwargs)
            query += " WHERE " + filter_query
        cursor.execute(query, filter_data)
        playlists = db.fetch_execution(cursor)
        result = []
        for playlist in playlists:
            result.append(Playlist(**playlist))
        return result

    def delete(self):
        if not self.pk:
            raise ValueError("Playlist is not saved yet.")
        db = get_database()
        cursor = db.cursor
        query = "DELETE FROM {table} WHERE id=%(id)s".format(table=self.TABLE_NAME)
        cursor.execute(query, {'id': self.pk})
        db.commit()

    def save(self):
        db = get_database()
        data = self.values()
        if self.pk:
            playlist = self.get(pk=self.pk)
        else:
            playlist = self.get(title=self.title)
        if playlist:
            # update old playlist
            old_data = playlist.values()
            diffkeys = [key for key in data if data[key] != old_data[key]]
            if not diffkeys:
                # Nothing changed
                return playlist
            filters = {}
            for key in diffkeys:
                filters[key] = self.values()[key]
            query = "UPDATE {table} SET ".format(table=self.TABLE_NAME)
            for key in filters:
                query += key + ' = %(' + key + ')s, '
            # Remove last comma
            query = query.rstrip(', ') + ' '
            # Add filter
            query += "WHERE id={pk}".format(pk=playlist.pk)
            db.cursor.execute(query, filters)
            db.commit()
            # Return saved playlist
            return self.get(pk=playlist.pk)
        # new playlist
        del data['pk']
        query = "INSERT INTO {table} " \
                "(name, is_public, user) " \
                "VALUES" \
                "(%(name)s, %(is_public)s, %(user_id)s".format(table=self.TABLE_NAME)
        db.cursor.execute(query, dict(data))
        db.commit()
        return self.get(title=self.title)

