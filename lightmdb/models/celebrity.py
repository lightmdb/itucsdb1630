from flask import current_app
from collections import OrderedDict


def get_database():
    from lightmdb import get_db
    return get_db(current_app)


class Celebrity(object):
    """Celebrity Model."""
    TABLE_NAME = 'celebrities'

    def __init__(self, pk=None, name=None, birthday=None, imdb_pk=None):
        self.pk = pk
        self.name = name
        self.birthday = birthday
        self.imdb_pk = imdb_pk

    def get_id(self):
        return str(self.pk)

    def values(self):
        data = OrderedDict([
            ('pk', self.pk),
            ('name',self.name),
            ('birthday',self.birthday),
            ('imdb_pk', self.imdb_pk)
        ])
        return data

    @classmethod
    def get(cls, pk=None, imdb_pk=None):
        """Get celebrity by identifier.

        Usage: Celebrity.get(title)
        :rtype: Celebrity object or None
        """
        db = get_database()
        cursor = db.cursor
        if pk:
            cursor.execute(
                "SELECT * FROM {table} WHERE id=%(id)s".format(table=cls.TABLE_NAME),
                {'id': pk}
            )
        elif imdb_pk:
            cursor.execute(
                "SELECT * FROM {table} WHERE imdb_pk=%(imdb_pk)s".format(table=cls.TABLE_NAME),
                {'imdb_pk': imdb_pk}
            )
        else:
            return None
        celebrity = db.fetch_execution(cursor)
        if celebrity:
            return Celebrity(**celebrity[0])
        return None

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
        celebs = db.fetch_execution(cursor)
        result = []
        for celebrity in celebs:
            result.append(Celebrity(**celebrity))
        return result

    def delete(self):
        if not self.pk:
            raise ValueError("Celebrity is not saved yet.")
        db = get_database()
        cursor = db.cursor
        query = "DELETE FROM {table} WHERE id=%(id)s".format(table=self.TABLE_NAME)
        cursor.execute(query, {'id': self.pk})
        db.commit()

    def save(self, return_obj=True):
        db = get_database()
        data = self.values()
        celebrity = None
        if self.pk:
            celebrity = self.get(pk=self.pk)
        elif self.imdb_pk:
            celebrity = self.get(imdb_pk=self.imdb_pk)
        if celebrity:
            # update old celebrity
            old_data = celebrity.values()
            diffkeys = [key for key in data if data[key] != old_data[key]]
            if not diffkeys:
                # Nothing changed
                return celebrity
            filters = {}
            for key in diffkeys:
                filters[key] = self.values()[key]
            query = "UPDATE {table} SET ".format(table=self.TABLE_NAME)
            for key in filters:
                query += key + ' = %(' + key + ')s, '
            # Remove last comma
            query = query.rstrip(', ') + ' '
            # Add filter
            query += "WHERE id={pk}".format(pk=celebrity.pk)
            db.cursor.execute(query, filters)
            db.commit()
            # Return saved celebrity
            return self.get(pk=celebrity.pk)
        # new celebrity
        del data['pk']
        query = "INSERT INTO {table} (name, birthday, imdb_pk) VALUES (%(name)s, %(birthday)s, %(imdb_pk)s)".format(table=self.TABLE_NAME)
        if return_obj:
            query += " RETURNING id"
        cursor = db.cursor
        cursor.execute(query, dict(data))
        # db.commit()
        if return_obj:
            new_row_pk = cursor.fetchone()[0]
            return self.get(pk=new_row_pk)
        return True
