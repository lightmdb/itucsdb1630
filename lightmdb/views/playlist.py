from flask import Blueprint, abort, redirect, url_for, render_template, current_app, request
from flask_login import login_required, current_user
from lightmdb.models import Playlist
from lightmdb.forms import PlaylistForm

playlist = Blueprint('playlist', __name__)


@playlist.route("/new/", methods = ["GET","POST"])
@login_required
def add_playlist():
    form = PlaylistForm(request.form)
    if request.method == 'POST' and form.validate():
        is_public = False
        if form.privacy.data == "Public":
           is_public = True
        _playlist = Playlist(name=form.name.data,user_id=current_user.pk,is_public = is_public)
        _playlist = _playlist.save()
        return redirect(url_for('.playlists', pk=_playlist.pk))
    return render_template('playlist/add.html',form=form)

@playlist.route("/<pk>",methods = ["GET","POST"])
def playlists(pk):
    _playlist = Playlist.get(pk)
    if not _playlist:
        abort(404,{'message':'Playlist not found.'})
    if _playlist:
        _movies = _playlist.get_movies()
    return render_template('playlist/playlist.html', movies = _movies, playlist = _playlist)

