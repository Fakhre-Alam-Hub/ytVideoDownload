from django.shortcuts import render
from pytube import YouTube
from django.http import HttpResponse
import os

# Create your views here.
def index(request):
    if request.method == 'POST':
        try:
            link = request.POST['link']
            print("Link: %s" % link)
            myVideo = YouTube(link)
            title = myVideo.title
            length = str(myVideo.length)
            thumbnail_url = myVideo.thumbnail_url
            myVideoStreams = myVideo.streams.filter(type='video')
            context = {'title':title, 'length': length, 'thumbnail_url': thumbnail_url,'video_url':link,'myVideoStreams':myVideoStreams}
            return render(request, 'Home/index.html', context=context)
        except Exception as e:
            print(e)
            context = {"error":"Could not find the video"}
            return render(request, 'Home/index.html', context=context)            
    return render(request, 'Home/index.html')

def download_video(request, video_url, resolution):
    yt = YouTube(video_url)
    selected_stream = yt.streams.filter(resolution=resolution).first()

    if selected_stream:
        video_data = selected_stream.download()
        response = HttpResponse(content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{yt.title+"."+resolution}.mp4"'
        with open(video_data, 'rb') as video_file:
            response.write(video_file.read())
        os.remove(video_data)
        return response
    else:
        return HttpResponse('Error: Video not found')
    
def about(request):
    return render(request, 'Home/about.html')

