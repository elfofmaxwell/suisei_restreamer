import time

from flask import Blueprint, g, redirect, render_template, request, url_for

from restreamer import rebroadcast_funcs
from restreamer.auth import login_required

bp = Blueprint('restreamer', __name__)

@bp.route('/', methods=('POST', 'GET'))
@login_required
def index(): 
    if request.method == 'POST': 
        source_url = request.form.get('sourceUrl')
        stream_server = request.form.get('streamServer')
        stream_key = request.form.get('streamKey')
        g.stream_server = stream_server
        if not rebroadcast_funcs.check_lock(): 
            best_m3u8 = rebroadcast_funcs.extract_best_m3u8(source_url)
            print(best_m3u8)
            rebroadcast_funcs.push_stream(best_m3u8, stream_server, stream_key)
            time.sleep(0.5)
        return redirect(url_for('restreamer.index'))
    else: 
        if g.stream_server: 
            history_server = g.stream_server
        else: 
            history_server = ''
        return render_template('index.html', stream_lock=rebroadcast_funcs.check_lock(), history_server=history_server)

@bp.route('/kill')
@login_required
def kill(): 
    rebroadcast_funcs.kill_streamer()
    time.sleep(0.5)
    return redirect(url_for('restreamer.index'))
