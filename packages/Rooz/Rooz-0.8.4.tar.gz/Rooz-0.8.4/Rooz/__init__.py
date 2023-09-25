import requests , yt_dlp
from user_agent import generate_user_agent
import json , re
from yt_dlp import *
from os import system

class Download:
    def __init__(self, link):
        self.link = link
       

    def DownThreads(self):
        url = f"https://api.threadsphotodownloader.com/v2/media?url={self.link}"
        head = {'User-Agent':generate_user_agent()}
        dat={"url":f'{self.link}'}
        re=requests.get(url, headers=head, data=dat).json()
        return re


    def hi(self):
        return 'hi'
    
    def DownTikTok(self):
        Url = 'https://www.veed.io/video-downloader-ap/api/download-content'

        data = {"url":self.link }

        req = requests.post(Url , data ).json()

        daa = json.loads(json.dumps(req))
        vid = daa["media"][0]["url"]
        vidurl = f'https://www.veed.io{vid}'
        title = daa["title"]
        username = daa["username"]
        author_url = f'https://tiktok/@{username}'

        dmj = {
            'Video_Url': f'{vidurl}',
            'Title': f'{title}',
            'Author_Url': f'{author_url}'}

        return dmj
        #print(dmj)
    def DownSoundCloud(self):
        url = 'https://www.klickaud.co/download.php'
        data = {'value': self.link,
        'afae4540b697beca72538dccafd46ea2ce84bec29b359a83751f62fc662d908a':'2106439ef3318091a603bfb1623e0774a6db38ca6579dae63bcbb57253d2199e'}
        req = requests.post(url , data).text
        linnk = re.findall(r'href="(https://cf-media.sndcdn.com/[^"]+)', req)[0]
        photo = re.findall(r'<img src="(https://i1.sndcdn.com[^"]+)', req)[0]
        dmmj  =  {
        'Audio_link':linnk,
        'Thumbnail_link':photo}
        return dmmj

    def DownPinterest(self):
        li = self.link
        rep = li.replace('https://pin.it/', '')


        url = 'https://pintodown.com/wp-admin/admin-ajax.php'

        data = {'action': 'pinterest_action',
        'pinterest': f'is_private_video=&pinterest_video_url=https%3A%2F%2Fpin.it%2F{rep}'}

        req = requests.post(url , data).json()

        Op = req['data']
        return Op

    def DownFaceBook(self):
        url = 'https://www.getfvid.com/downloader'

        data = {'url': self.link}

        req = requests.post(url , data).text

        linkv = re.findall(r'<a href="([^"]+)', req)[4]
        dmj={'Video_Url':linkv}
        return dmj

    def DownFromVodu(self):
        url = self.link

        id = url.replace('https://movie.vodu.me/index.php?do=view&type=post&id=','')

        #print(id)
        data = {'do':'view',
        'type':'post',
        'id':id}

        req = requests.get(url , data).text

        title = re.findall(r'data-title="([^"]+)', req)

        vidl=re.findall(r'data-url="([^"]+)', req)

        p = re.findall(r'<img src="([^"]+)' , req)[1]
        pt = f'https://movie.vodu.me/{p}'
        #print(pt)

        for i in range(len(vidl)):
            dmj = {'title':title[i],
            'video_link':vidl[i],
            'poster':pt}
            return dmj
        return '\n\n' 