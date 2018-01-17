import os
from django.shortcuts import render
from sutra.models import Tripitaka, Page, LQSutra
import json
import boto3
import io
import urllib
from PIL import Image
from django.http import HttpResponse
# Create your views here.


def sutra_index(request):
    tripitaka_lst = [{'name': i.name, 'code': i.code} for i in list(LQSutra.objects.all())]
    d = json.dumps(tripitaka_lst, default=lambda obj: obj.__dict__)
    return render(request, 'sutra/show.html', {'tripitaka': d})


def sutra_op(request):
    tripitaka_lst = [{'name': i.name, 'code': i.code} for i in list(LQSutra.objects.all())]
    d = json.dumps(tripitaka_lst, default=lambda obj: obj.__dict__)
    return render(request, 'sutra/operation.html', {'tripitaka': d})


def pic_show(request):
    img_dict ={}
    point_dict = {}
    for p in open('wentidata').readlines():
        if p[0]=='G':
            point_dict[p.split(' ')[0]] = [[int(z)*0.5 for z in i.split(',') if z.isdigit()] for i in p.split(' ')[1].split('!')[0].split(";")]
        else:
            point_dict[p.split(' ')[0]] = [[int(z) for z in i.split(',') if z.isdigit()] for i in p.split(' ')[1].split('!')[0].split(";")]
    for pic in os.listdir('/home/buddhist/AI/tripitaka/sutra/static/picked'):
        if pic.find('_L') == -1:
            key = pic
            if key not in img_dict.keys():
                img_dict[pic] = []
        else:
            key = "_".join(pic.split('_')[:-1])+'.jpg'
            if key not in img_dict.keys():
                img_dict[key] = ['/static/picked/'+pic]
            else:
                img_dict[key].append('/static/picked/'+pic)
        for key in img_dict:
            img_dict[key].sort()
            img_dict[key].reverse()
    d = json.dumps(img_dict)
    p = json.dumps(point_dict)
    return render(request, 'sutra/pic_cut_show.html', {'img_lst': d, 'point_lst': p})

s3 = boto3.client('s3')


def crop_img(img_url, crop_region, key):
    # 在线切列函数
    img = Image.open(io.BytesIO(urllib.request.urlopen(img_url).read()))
    image = img.crop(crop_region)
    buffer = io.BytesIO()
    image.save(buffer, format="jpg")
    b = io.BytesIO(buffer.getvalue())
    s3.upload_fileobj(b, 'lqcharacters-images', key)


def trans_code(img_name):
    name_list = img_name.split('_')
    new_name_list = ['GLZ']
    page_no = int(name_list[3].split('.')[0])
    suffix = name_list[3].split('.')[1]
    new_name_list.extend(['S%05d' % int(name_list[0]), 'R%03d' % int(name_list[1]), 'T%04d' % page_no])
    img_name = "_".join(new_name_list) + '.' + suffix
    img_url = '/'.join(new_name_list[:-1]) + '/' + img_name
    return img_url


def get_glz_data():
    wenti_txt = open('wenti_txt', 'a')
    for txt in os.listdir('/home/buddhist/文档/切分文件/glz_label/')[3:]:
        txt_data = open('/home/buddhist/文档/切分文件/glz_label/' + txt, 'r')
        for l in txt_data.readlines():
            name = l.split(' ')[0]
            if l.split(' ')[1] != '\n' and name.find('(') == -1:
                cut_data = l.split(' ')[1].split('!')[0]
                txt = l.split(' ')[1].split('!')[1]
                code = trans_code(name)
                ps = Page.objects.filter(img_path=code)
                if ps:
                    p = ps[0]
                    if p.txt == '':
                        p.cut_data = cut_data
                        p.txt = txt
                        p.save()
                    else:
                        continue
                else:
                    wenti_txt.write(code)
            else:
                wenti_txt.write(code)
        txt_data.close()


def get_glz(request):
    get_glz_data()
    return HttpResponse('ok')