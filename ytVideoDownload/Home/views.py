from django.shortcuts import render
from pytube import YouTube, Playlist
from django.http import HttpResponse, StreamingHttpResponse
import os
import requests

def has_audio(stream):
    return stream.audio_codec is not None and stream.audio_codec != ''

def get_size_in_mb(stream):
    try:
        size_in_bytes = stream.filesize
        size_in_mb = round(size_in_bytes / (1024 * 1024), 1)
        return size_in_mb
    except Exception as e:
        print("Error in get filesize: ",e)
        return 0

def get_mimetype(stream):
    return stream.mime_type.split('/')[-1]

def get_available_qualities_details(playlist_url):
    try:
        details = []
        playlist = Playlist(playlist_url)
        unique_details = set() 
        for video_url in playlist.video_urls:
            resolution, hasAudio, mimetype = "", False, ""
            yt = YouTube(video_url)
            video_streams = yt.streams.filter(type="video")
            for stream in video_streams:
                resolution = stream.resolution
                hasAudio = has_audio(stream)
                mimetype = get_mimetype(stream)
                unique_details.add((resolution, hasAudio, mimetype))
        for resolution, hasAudio, mimetype in unique_details:
            data = {'resolution': resolution, 'hasAudio': hasAudio, 'mimetype': mimetype}
            details.append(data)
        return details
    except Exception as e:
        print("Error retrieving video qualities:")
        print(e)

def index(request):
    if request.method == 'POST':
        try:
            video_url = request.POST['link']
            myVideo = YouTube(video_url)
            title = myVideo.title
            length = str(myVideo.length)
            thumbnail_url = myVideo.thumbnail_url
            myVideoStreams = list(myVideo.streams.filter(type='video'))
            allVideoStreams = []
            for stream in myVideoStreams:                
                data = {}
                data['audio'] = has_audio(stream)
                data['filesize'] = get_size_in_mb(stream)
                data['resolution'] = stream.resolution
                data['mime_type'] = stream.mime_type
                allVideoStreams.append(data)
            context = {'title':title, 'length': length, 'thumbnail_url': thumbnail_url,'video_url':video_url,'myVideoStreams':allVideoStreams}
            return render(request, 'Home/index.html', context=context)
        except Exception as e:
            print(e)
            context = {"error":"Could not find the video, Please provide valid video link."}
            return render(request, 'Home/index.html', context=context)            
    return render(request, 'Home/index.html')


def download_video(request, addPrefix, counter, video_url, resolution):
    yt = YouTube(video_url)
    selected_stream = yt.streams.filter(resolution=resolution).first()
    if addPrefix=="True" or addPrefix=="true":
        filename = f"{counter}.{yt.title}.{resolution}.mp4"
    else:
        filename = f"{yt.title}.{resolution}.mp4"
    if selected_stream:
        video_stream = requests.get(selected_stream.url, stream=True)
        response = StreamingHttpResponse(streaming_content=video_stream.iter_content(chunk_size=8192))
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
    else:
        return HttpResponse('Error: Video not found')

def playlist(request):
    if request.method == 'POST':
        try:
            playlist_link = request.POST['link']
            quality = request.POST['quality']
            addPrefix = True if 'addPrefix' in request.POST else False
            reduceQuality = True if 'reduceQuality' in request.POST else False
            playlist = Playlist(playlist_link)
            all_videoStreams = []
            video_qualities_details = get_available_qualities_details(playlist_link)
            for video_url in playlist.video_urls:
                myVideo = YouTube(video_url)
                title = myVideo.title
                length = str(myVideo.length)
                thumbnail_url = myVideo.thumbnail_url
                resolution=quality.split(' ')[1]
                file_extension=quality.split(' ')[0]
                print(f"resolution: {resolution}, file extension: {file_extension}")
                filtered_myVideoStreams = list(myVideo.streams.filter(type='video', resolution=resolution, file_extension=file_extension))
                myVideoStreams = []
                data = {'title':title, 'length': length, 'thumbnail_url': thumbnail_url,'video_url':video_url}
                for stream in filtered_myVideoStreams:
                    if has_audio(stream):
                        data['audio'] = has_audio(stream)
                        data['filesize'] = get_size_in_mb(stream)
                        data['resolution'] = resolution
                        data['mime_type'] = stream.mime_type
                        myVideoStreams.append(stream)
                        break
                if not myVideoStreams:
                    data['audio'] = has_audio(filtered_myVideoStreams[0])
                    data['filesize'] = get_size_in_mb(filtered_myVideoStreams[0])
                    data['resolution'] = resolution
                    data['mime_type'] = filtered_myVideoStreams[0].mime_type
                all_videoStreams.append(data)
            context = {'all_videoStreams': all_videoStreams, "video_qualities_details":video_qualities_details, "addPrefix":addPrefix}  
            return render(request, 'Home/playlist.html', context=context)
        except Exception as e:
            print(e)
            context = {"error":"Could not find the video"}
            return render(request, 'Home/playlist.html', context=context)
    return render(request, 'Home/playlist.html')

def about(request):
    return render(request, 'Home/about.html')

# Create your views here.
# def index(request):
#     if request.method == 'POST':
#         try:
#             linkType = request.POST['linkType']
#             link = request.POST['link']
#             quality = request.POST['quality']
#             print("quality: ",quality)
#             addPrefix = True if 'addPrefix' in request.POST else False
#             reduceQuality = True if 'reduceQuality' in request.POST else False
#             if linkType == "video":
#                 try:
#                     myVideo = YouTube(link)
#                     title = myVideo.title
#                     length = str(myVideo.length)
#                     thumbnail_url = myVideo.thumbnail_url
#                     myVideoStreams = list(myVideo.streams.filter(type='video'))
#                     video_qualities_details = get_available_qualities_details(myVideoStreams)
#                     resolution=quality.split(' ')[1]
#                     file_extension=quality.split(' ')[0]
#                     print(f"resolution: {resolution}, file extension: {file_extension}")
#                     myVideoStreams = list(myVideo.streams.filter(type='video', resolution=resolution, file_extension=file_extension))
#                     for stream in myVideoStreams:
#                         stream.audio = has_audio(stream)
#                     context = {'title':title, 'length': length, 'thumbnail_url': thumbnail_url,'video_url':link,'myVideoStreams':myVideoStreams,"video_qualities_details":video_qualities_details}
#                     return render(request, 'Home/index.html', context=context)
#                 except Exception as e:
#                     print(e)
#                     context = {"error":"Could not find the video"}
#                     return render(request, 'Home/index.html', context=context)
#             elif linkType == "playlist":
#                 try:
#                     print("link: ",link)
#                     playlist = Playlist(link)                    
#                     # for url in playlist.videos:
#                     #     print(url.title)
#                     #     print(url.thumbnail_url)
#                     print(" ")
#                     for url in playlist.video_urls:
#                         print("url: ",url)
#                         myVideo = YouTube(url)
#                         title = myVideo.title
#                         length = str(myVideo.length)
#                         thumbnail_url = myVideo.thumbnail_url
#                         myVideoStreams = list(myVideo.streams.filter(type='video'))
#                         video_qualities_details = get_available_qualities_details(myVideoStreams)
#                         resolution=quality.split(' ')[1]
#                         file_extension=quality.split(' ')[0]
#                         print(f"resolution: {resolution}, file extension: {file_extension}")
#                         myVideoStreams = list(myVideo.streams.filter(type='video', resolution=resolution, file_extension=file_extension))
#                         for stream in myVideoStreams:
#                             stream.audio = has_audio(stream)
#                         context = {'title':title, 'length': length, 'thumbnail_url': thumbnail_url,'video_url':link,'myVideoStreams':myVideoStreams,"video_qualities_details":video_qualities_details}
#                         break
#                     return render(request, 'Home/index.html', context=context)
#                 except Exception as e:
#                     print(e)
#                     context = {"error":"Could not find the playlist."}
#                     return render(request, 'Home/index.html', context=context)
#             else:
#                 context = {"error":"Please provide valid video link or playlist link"}
#                 return render(request, 'Home/index.html', context=context)
#         except Exception as e:
#             print(e)
#             context = {"error":"Could not find the video"}
#             return render(request, 'Home/index.html', context=context)            
#     return render(request, 'Home/index.html')
