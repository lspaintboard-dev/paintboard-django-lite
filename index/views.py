from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.views.decorators.gzip import gzip_page
from PIL import Image
import base64
import io
from index.models import *


import time
import uuid
# import json
# import requests
import index.config as cg
mapp = []
lstsavebd = 0.0
tokenlist = {}
reqip_a = {}
reqip_g = {}
ip_address = {}


def initbd():
    for x in range(0, 600):
        mapp.append([])
        for y in range(0, 1000):
            mapp[x].append((255, 255, 255))


initbd()

# init_dict()


def save_board():
    try:
        pass

    except Exception as e:
        print("Errorrrrrrrrrrrrrrrrrrrrrrrrrrr", str(e))


# IpSpeed_g.objects.all().delete()
# IpSpeed_a.objects.all().delete()

save_board()


getboard_need_update = 1

# what getboard last save
getboard_last_return = ""

# what time getboard last save
getboard_last_save = 0


def mklog(data, request):
    id = request.path
    ipt = {}
    if request.method == 'POST':
        ipt = str(dict(request.POST.items()))
    else:
        ipt = str(dict(request.GET.items()))
    print("["+id+"]", ipt, "->", str(data)[:150])


def mkret(status, data, request):
    if (status == 203):
        mklog("", request)
        # 0, status=status)  # , content_type='image/gif')
        return HttpResponse(data)
    elif (status == 204):
        mklog("", request)
        return HttpResponse(data, content_type='image/png')  # status=203
    else:
        retl = {"status": status, "time": time.time(), "data": data}
        mklog(retl, request)
        return JsonResponse(retl, status=status)
    # if (status == 200):
    #     ret = str('\x00')
    # elif (status == 201):
    #     ret = str('\x01')+str(data)
    # elif (status == 203):
    #     ret = str(data)
    # else:
    #     ret = str(chr(status-400+16))
    # return HttpResponse(ret, status=status)



@gzip_page
def getboard(request):
    # mklog("",request)
    global getboard_need_update
    global getboard_last_return
    global getboard_last_save
    if (getboard_need_update):
        ret = "\x01"
        for y in range(0, 1000):
            for x in range(0, 600):
                ret += chr(mapp[x][y][0])+chr(mapp[x][y][1])+chr(mapp[x][y][2])
        # ret=ret.replace("\x00","\x01")
        getboard_need_update = 0
        getboard_last_return = ret
        if (time.time()-getboard_last_save >= cg.save_to_db_cd):
            save_board()
        getboard_last_save = time.time()

    else:
        ret = getboard_last_return
    # if(time.time()-lstsavebd>3):
    #     with open("/save/"+str(time.time())+".txt", "w") as fp:
    #         fp.write(ret)
    # print(ret)

    return mkret(203, ret, request)


def checktoken(uid, token):
    return True


def paintboard(request):
    global getboard_last_return
    try:
        nowt = time.time()
        if 1:
            if request.method == 'POST':
                uid = request.POST.get('uid', None)
                y = request.POST.get('y', None)
                x = request.POST.get('x', None)
                color = request.POST.get('color', None)
            else:
                uid = request.GET.get('uid', None)
                y = request.GET.get('y', None)
                x = request.GET.get('x', None)
                color = request.GET.get('color', None)
            uid = int(uid)
            tt = tokenlist[uid]
            if ((not (uid in cg.root)) and (nowt-float(tt['time']) < cg.cd)):
                return mkret(402, {"error": "Paint too fast"}, request)
            # y = request.POST.get('y', None)
            if (y == None):
                return mkret(403, {"error": "Where is your 'y'?"}, request)
            try:
                y = int(y)
            except Exception:
                return mkret(403, {"error": "y incorrect"}, request)
            if (y > 599 or y < 0):
                return mkret(403, {"error": "y incorrect"}, request)
            # x = request.POST.get('x', None)
            if (x == None):
                return mkret(403, {"error": "Where is your 'x'?"}, request)
            try:
                x = int(x)
            except Exception:
                return mkret(403, {"error": "x incorrect"}, request)
            if (x > 999 or x < 0):
                return mkret(403, {"error": "x incorrect"}, request)
            if (color == None):
                return mkret(403, {"error": "Where is your 'color'?"}, request)
            try:
                color_ = int(color[0:2], 16), int(
                    color[2:4], 16), int(color[4:6], 16)
            except Exception:
                return mkret(403, {"error": "color incorrect"}, request)
            mapp[y][x] = color_
            getboard_last_return = getboard_last_return[:y*1800+x*3+1:y*1800+x*3+1] + chr(
                color_[0])+chr(color_[1])+chr(color_[2])+getboard_last_return[y*1800+x*3+1:y*1800+x*3+3]
            # Tokenlist.objects.filter(id=uid).update(time=nowt)
            tokenlist[uid]["time"] = nowt
            print(uid, "paint", color, "at", x, y)
            global getboard_need_update
            getboard_need_update = 1
            return mkret(200, {"result": "Done"}, request)
            # return HttpResponse(request.POST['uid'] + " paint " + request.POST['color'] + " at " + request.POST['x'] + " " + request.POST['y'])
        else:
            pass
    except Exception as e:
        return mkret(500, {"error": str(e)}, request)


def fill(request):
    if request.method == 'GET':
        uid = request.GET.get('uid', -1)
        token = request.GET.get('token', -1)
        x1 = request.GET.get('x1', -1)
        x2 = request.GET.get('x2', -1)
        y1 = request.GET.get('y1', -1)
        y2 = request.GET.get('y2', -1)
        color = request.GET.get('color', -1)
    else:
        uid = request.POST.get('uid', -1)
        token = request.POST.get('token', -1)
        x1 = request.POST.get('x1', -1)
        x2 = request.POST.get('x2', -1)
        y1 = request.POST.get('y1', -1)
        y2 = request.POST.get('y2', -1)
        color = request.POST.get('color', -1)
    if ((not int(uid) in cg.root) or (not checktoken(uid, token))):
        return mkret(400, {"error": "Token Error"}, request)
    R, G, B = int(color[0:2], 16), int(
        color[2:4], 16), int(color[4:6], 16)
    for x in range(int(x1), int(x2)):
        for y in range(int(y1), int(y2)):
            mapp[y][x] = (R, G, B)
    global getboard_need_update
    global getboard_last_save
    getboard_need_update = 1
    getboard_last_save = 0
    return mkret(200, {"result": "Done"}, request)


def fillimg(request):
    try:
        if request.method == 'GET':
            uid = request.GET.get('uid', -1)
            token = request.GET.get('token', -1)
            img = request.GET.get('img', -1)
            x = int(request.GET.get('x', -1))
            y = int(request.GET.get('y', -1))
        else:
            uid = request.POST.get('uid', -1)
            token = request.POST.get('token', -1)
            img = request.POST.get('img', -1)
            x = int(request.POST.get('x', -1))
            y = int(request.POST.get('y', -1))
        checkres = (checktoken(uid, token))
        if ((not checkres) or (not int(uid) in cg.root)):
            return mkret(400, {"error": "Token Error"}, request)
        img = base64.b64decode(img)
        img = Image.open(io.BytesIO(img))
        sizzz = img.size
        for xx in range(x, x+sizzz[0]):
            for yy in range(y, y+sizzz[1]):
                if (xx >= 1000):
                    break
                if (yy >= 600):
                    break
                mapp[yy][xx] = img.getpixel((xx-x, yy-y))
        global getboard_need_update
        global getboard_last_save
        getboard_need_update = 1
        getboard_last_save = 0
        return mkret(200, {"result": "Done"}, request)
    except Exception as e:
        return mkret(500, {"error": str(e)}, request)


def index(request):
    mklog("", request)
    return render(request, "index.html")
