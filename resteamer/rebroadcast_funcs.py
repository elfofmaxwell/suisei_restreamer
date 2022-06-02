import os
import subprocess
import sys

import psutil


def extract_best_m3u8(video_link: str, cookies: str='') -> str: 
    yt_dlp_args = [
        'yt-dlp', 
        '-f', 'b', 
        '-g', 
        video_link
    ]

    #if os.path.isfile(cookies): 
    #    yt_dlp_args.insert(-2, '--cookies')
    #    yt_dlp_args.insert(-2, cookies)

    get_m3u8 = subprocess.run(yt_dlp_args, capture_output=True)
    m3u8 = get_m3u8.stdout.decode('utf-8')
    if m3u8: 
        return m3u8
    else:
        raise ValueError('Fail to get m3u8!')
    

def push_stream(m3u8: str, stream_server: str, stream_key: str): 
    ffmpeg_args = [
        'ffmpeg', 
        '-re',
        '-i', 
        m3u8.strip(), 
        '-c:v', 'copy', 
        '-c:a', 'aac', 
        '-ar', '44100', 
        '-ab', '128k', 
        '-ac', '2', 
        '-strict', '-2', 
        '-flags', '+global_header', 
        '-bsf:a', 
        'aac_adtstoasc', 
        '-bufsize', '6400k',
        '-f', 'flv', 
        '/'.join((stream_server.strip(), stream_key.strip()))
    ]
    print(' '.join(ffmpeg_args))

    try: 
        streamer = subprocess.Popen(ffmpeg_args)
        with open('streamer.lock', 'w') as f: 
            f.write(str(streamer.pid))
    except: 
        if os.path.isfile('streamer.lock'): 
            with open("streamer.lock") as f: 
                pid_str = f.readline()
            if pid_str: 
                pid = int(pid_str)
                p = psutil.Process(pid)
                p.terminate()
                os.remove("streamer.lock")

def kill_streamer(): 
    if os.path.isfile('streamer.lock'): 
        with open("streamer.lock") as f: 
            pid_str = f.readline()
        if pid_str: 
            pid = int(pid_str)
            p = psutil.Process(pid)
            p.terminate()
        os.remove("streamer.lock")
        

if __name__ == "__main__": 
    if len(sys.argv)>1: 
        if sys.argv[1] == 'kill': 
            kill_streamer()
    else: 
        video_url = input('video url: \n')
        stream_server = input('stream server: \n')
        strem_key = input('stream key: \n')
        m3u8 = extract_best_m3u8(video_url)
        print(m3u8)
        push_stream(m3u8, stream_server, strem_key)

    
