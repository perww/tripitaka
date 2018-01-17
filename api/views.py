from rest_framework import viewsets
from .serializers import SutraSerializer, ReelSerializer, PageSerializer
from sutra.models import Sutra, Reel, Page, OCut, OImg, Batch
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import django_filters
from rest_framework.pagination import PageNumberPagination
import os
from PIL import Image
import boto3
from datetime import datetime
from rest_framework.decorators import detail_route, list_route
import json
import io
import urllib.request
import traceback
from struct import unpack

s3c = boto3.client('s3')
my_bucket = 'lqcharacters-images'
s3 = boto3.resource('s3')
CHNAGE_NAME_LOGS = open('change_name_logs.txt', 'a')
UPLOAD_LOGS = open('upload_logs.txt', 'a')
ROOT_DIR = '/home/buddhist/AI/tripitaka_data/'
CUT_ORI_DIR = ROOT_DIR + 'cut_origin/'
CUT_DAT_DIR = ROOT_DIR + 'cut_json/'
COL_DAT_DIR = ROOT_DIR + 'col_json/'
S3_CUT_DIR = ROOT_DIR + 'cut_s3/'
S3_COL_DIR = ROOT_DIR + 'col_s3/'
IMG_1200_DIR = '/home/buddhist/AI/tripitaka_data/img_1200/'
PDF_DIR = ''
BIG_IMG_DIR = ''


def jpegsize(filename):
    '''gets the width and height (in pixels) of a JPEG file'''
    stream = open(filename, 'rb')
    x, y = 0, 0
    # Dummy read to skip header ID
    stream.read(2)
    while 1:
        # Extract the segment header.
        (marker, code, length) = unpack('!BBH', stream.read(4))
        # Verify that it's a valid segment.
        if marker != 0xFF:
            # Was it there?
            raise ValueError('JPEG marker not found')
        elif code >= 0xC0 and code <= 0xC3:
            # Segments that contain size info
            (y, x) = unpack('!xHH', stream.read(5))
            break
        else:
            # Dummy read to skip over data
            stream.read(length - 2)
    if x == 0 or y == 0:
        raise ValueError('could not determine JPEG size')
    return x, y


def gather_img_info(p):
    tripitaka = p.code[:2]
    if tripitaka in ['GL', 'LC']:
        sutra = p.code[2:8]
        dir_path = os.path.join(IMG_1200_DIR, tripitaka, sutra)
    else:
        dir_path = os.path.join(IMG_1200_DIR, tripitaka)
    if not os.path.exists(dir_path):
        return "图片目录%s不存在！" % dir_path
    else:
        v_no = p.v_no
        v_page_no = p.v_page_no
        img_path = os.path.join(dir_path, '%03d/%04d.jpg' % (v_no, v_page_no))
        if not os.path.exists(img_path):
            return "图片%s不存在！" % img_path
        else:
            width, height = jpegsize(img_path)
            img_code = '%sv%03dp%04d0' % (tripitaka, v_no, v_page_no)
            try:
                o = OImg.objects.get(img_code=img_code)
                o.width, o.height = width, height
            except Exception as e:
                o = OImg(img_code=img_code, v_no=v_no, v_page_no=v_page_no, img_path=img_path, big_image=False, img_1200=True, img_s3=True, img_cropped=False, width=width, height=height)
            finally:
                o.save()
                p.o_img = o
                p.save()
                return "%s gathered!" % img_path


def gather_cut_info(p):
    tripitaka = p.code[:2]
    if tripitaka in ['GL', 'LC']:
        sutra = p.code[2:8]
        dir_path = os.path.join(CUT_DAT_DIR, tripitaka, sutra)
    else:
        dir_path = os.path.join(CUT_DAT_DIR, tripitaka)
    if not os.path.exists(dir_path):
        return "切分原始数据目录%s不存在！" % dir_path
    else:
        batch = Batch.objects.get(id=1)
        v_no = p.v_no
        v_page_no = p.v_page_no
        cut_path = os.path.join(dir_path, '%03d/%04d.jpg' % (v_no, v_page_no))
        if not os.path.exists(cut_path):
            return "切分文件%s不存在！" % cut_path
        else:
            cut_code = '%sv%03dp%04d0' % (tripitaka, v_no, v_page_no)
            try:
                o = OCut.objects.get(cut_code=cut_code)
            except Exception as e:
                o = OCut(batch=batch, cut_code=cut_code, v_no=v_no, v_page_no=v_page_no, cut_json=cut_path, cut_gened=False)
            finally:
                o.save()
                p.o_cut = o
                p.save()
                return "%s gathered!" % cut_path


def get_page_txt(page_dict):
    txt = {}
    for c in page_dict['char_data']:
        col_no = int(c['char_id'][18:20])
        char_no = int(c['char_id'][21:])
        char = c['char']
        if col_no in txt.keys():
            txt[col_no][char_no] = char
        else:
            txt[col_no] = {char_no: char}
    for col_no in txt.keys():
        col_txt = sorted(txt[col_no].items(), key=lambda a: a[0], reverse=False)
        txt[col_no] = ''.join(list(zip(*col_txt))[1])
    p_txts = sorted(txt.items(), key=lambda a: a[0], reverse=False)
    p_txt = list(zip(*p_txts))[1]
    return p_txt


def get_file(dat_dir, page, suffix):
    file_url = dat_dir + '/' + page.code[:2] + '/' + page.code + suffix
    if not os.path.exists(file_url):
        file_url = dat_dir + '/' + page.code[:2] + '/%03d/' % int(page.v_no) + page.code.replace(page.reel.sutra.sid[2:], '') + suffix
    try:
        file_content = open(file_url, 'r')
    except Exception as e:
        traceback.print_exc()
        return ' '.join([str(datetime.now()), '%s' % format(e)])
    return file_content


def upload_img(p):
    try:
        oimg = p.o_img
    except Exception as e:
        return '图片数据未就绪！'
    if oimg.img_s3:
        return "图片已上传!"
    else:
        msg = 'success!'
    try:
        s3c.get_object_acl(Bucket=my_bucket, Key=p.img_path)
        oimg.img_s3 = True
        oimg.save()
        return '图片已上传！'
    except Exception as e:
        if oimg.img_1200:
            try:
                s3.meta.client.upload_file(oimg.img_path, my_bucket, p.img_path)
                oimg.img_s3 = True
                oimg.save()
            except Exception as e:
                msg = ' '.join([str(datetime.now()), oimg.img_path, 'upload failed!%s' % format(e)])
        else:
            return '请先生成1200图！'
    return msg


def generate_cut(page):
    try:
        o_cut = page.o_cut
    except Exception as e:
        return '切分数据未就绪！'
    try:
        oimg = page.o_img
    except Exception as e:
        return '图片数据未就绪！'
    if o_cut.cut_gened:
        return "Cut generated!"
    else:
        msg = 'success!'
        page_dict = {
            'page_code': page.code,
            'reel_no': page.reel.sutra.sid + "r%03d" % int(page.reel.code),
            'char_data': []
        }
        cut_file = get_file(CUT_DAT_DIR, page, '.cut')
        if type(cut_file) is str:
            return cut_file
        try:
            cut_dict = json.loads(cut_file.readlines()[0])
            w_ratio = oimg.width / cut_dict['width']
            h_ratio = oimg.height / cut_dict['height']
            for d_no, data_line in enumerate(cut_dict['char_data']):
                line_dict = dict()
                if data_line == " : : \n":
                    break
                elif len(data_line.split(':')[0]) == len('GL000790v001p0001001n01'):
                    line_dict['char_id'] = data_line.split(':')[0]
                else:
                    line_dict['char_id'] = data_line.split(':')[0].replace('sid', page.reel.sutra.sid)
                line_dict['char'] = data_line.split(':')[1]
                char_cut_data = data_line.split(':')[2].split(',')
                line_dict['x'] = int(char_cut_data[0]) * w_ratio
                line_dict['y'] = int(char_cut_data[1]) * h_ratio
                line_dict['w'] = int(char_cut_data[2]) * w_ratio
                line_dict['h'] = int(char_cut_data[3]) * h_ratio
                line_dict['wcc'] = float(char_cut_data[4])
                line_dict['cc'] = float(char_cut_data[4])
                page_dict['char_data'].append(line_dict)
            result = json.dumps(page_dict)
            v_dir = S3_CUT_DIR + page.reel.sutra.sid + '/%03d/' % page.v_no
            if not os.path.exists(v_dir):
                os.system('mkdir -p ' + v_dir)
            result_file = open(v_dir + page.code + '.cut', 'w')
            result_file.write(result)
            result_file.close()
            key = '/'.join([page.reel.sutra.sid[:2], page.reel.sutra.sid[2:], 'v%03d' % int(page.v_no), page.code + '.cut'])
            s3.meta.client.upload_file(v_dir + page.code + '.cut', my_bucket, key)
            o_cut.cut_gened = True
            o_cut.save()
        except Exception as e:
            return ' '.join([str(datetime.now()), '%s' % format(e)])
    return msg


def crop_col_img(page):
    if page.img_cropped:
        return "Already cropped!"
    else:
        msg = 'success!'
        img = Image.open(io.BytesIO(urllib.request.urlopen("https://s3.cn-north-1.amazonaws.com.cn/lqcharacters-images/%s" % page.img_path).read()))
        col_file = get_file(COL_DAT_DIR, page, '.col')
        if type(col_file) is str:
            return col_file
        oimg = page.oimg
        col_dict = json.loads(col_file.readlines()[0])
        w_ratio = oimg.width / col_dict['width']
        h_ratio = oimg.height / col_dict['height']
        col_lines = col_dict['col_pos']
        for d_no, data_line in enumerate(col_lines):
            if len(data_line.split(':')[0]) == len('GZ000790v001p0001001'):
                col_id = data_line.split(':')[0]
            else:
                col_id = data_line.split(':')[0].replace('sid', page.reel.sutra.sid)
            col_cut_data = data_line.split(':')[1].split(',')
            x = int(col_cut_data[0]) * w_ratio
            y = int(col_cut_data[1]) * h_ratio
            x1 = int(col_cut_data[2]) * w_ratio
            y1 = int(col_cut_data[3]) * h_ratio
            key = '/'.join([page.reel.sutra.sid[:2], page.reel.sutra.sid[2:], 'v%03d' % int(page.v_no), col_id + '.jpg'])
            try:
                image = img.crop((x, y, x1, y1))
                buffer = io.BytesIO()
                image.save(buffer, format="jpeg")
                b = io.BytesIO(buffer.getvalue())
                s3c.upload_fileobj(b, my_bucket, key)
            except Exception as e:
                msg = ' '.join([str(datetime.now()), '%s' % format(e)])
                traceback.print_exc()
    if msg == 'success!':
        page.cut_ready = True
        page.save()
    return msg


def generate_col(page):
    try:
        o_cut = page.o_cut
    except Exception as e:
        return '切分数据未就绪！'
    try:
        oimg = page.o_img
    except Exception as e:
        return '图片数据未就绪！'
    if o_cut.col_gened:
        return "Col already generated!"
    else:
        msg = 'success!'
        page_dict = {
            'page_code': page.code,
            'reel_no': page.reel.sutra.sid + "r%03d" % int(page.reel.code),
            'col_data': []
        }
        col_file = get_file(COL_DAT_DIR, page, '.col')
        if type(col_file) is str:
            return col_file
        try:
            col_dict = json.loads(col_file.readlines()[0])
            w_ratio = oimg.width / col_dict['width']
            h_ratio = oimg.height / col_dict['height']
            col_lines = col_dict['col_pos']
            o_cut.col_no = len(col_lines)
            o_cut.save()
            for d_no, data_line in enumerate(col_lines):
                line_dict = dict()
                if len(data_line.split(':')[0]) == len('GZ000790v001p0001001'):
                    line_dict['col_id'] = data_line.split(':')[0]
                else:
                    line_dict['col_id'] = data_line.split(':')[0].replace('sid', page.reel.sutra.sid)
                col_cut_data = data_line.split(':')[1].split(',')
                line_dict['x'] = int(int(col_cut_data[0]) * w_ratio)
                line_dict['y'] = int(int(col_cut_data[1]) * h_ratio)
                line_dict['x1'] = int(int(col_cut_data[2]) * w_ratio)
                line_dict['y1'] = int(int(col_cut_data[3]) * h_ratio)
                page_dict['col_data'].append(line_dict)
            result = json.dumps(page_dict)
            v_dir = S3_COL_DIR + page.reel.sutra.sid + '/%03d/' % page.v_no
            if not os.path.exists(v_dir):
                os.system('mkdir -p ' + v_dir)
            result_file = open(v_dir + page.code + '.col', 'w')
            result_file.write(result)
            result_file.close()
            s3.meta.client.upload_file(v_dir + page.code + '.col', my_bucket, '/'.join([page.reel.sutra.sid[:2], page.reel.sutra.sid[2:], 'v%03d' % int(page.v_no), page.code + '.col']))
            o_cut.col_gened = True
            o_cut.save()
        except Exception as e:
            msg = ' '.join([str(datetime.now()), '%s' % format(e)])
        return msg


def sutra_operation(func, ob):
    sid = ob.request.query_params.get('sid', None)
    msg = {}
    if sid is not None:
        s = Sutra.objects.get(sid=sid)
    else:
        s = Sutra.objects.get(id=pk)
    reels = s.reel_set.all()
    for r in reels:
        for p in r.page_set.all():
            msg[p.code] = func(p)
    return msg


class SutraViewSet(viewsets.ModelViewSet):
    serializer_class = SutraSerializer
    queryset = Sutra.objects.all()
    permission_classes = (AllowAny,)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fileds = ('code', 'tripitaka', 'id')

    def get_queryset(self):
        queryset = Sutra.objects.all()
        code = self.request.query_params.get('code', None)
        tripitaka = self.request.query_params.get('tripitaka', None)
        if code is not None:
            queryset = queryset.filter(code=code)
        if tripitaka is not None:
            queryset = queryset.filter(lqsutra__code=tripitaka)
        return queryset

    @detail_route(methods=['post', 'get'])
    def upload_img(self, request, pk):
        a = 's'
        s = Sutra.objects.get(id=pk)
        reels = s.reel_set.all()
        tripitaka_dir = self.request.query_params.get('tripitaka_dir', None)
        for r in reels:
            pages = r.page_set.all()
            for p in pages:
                if not p.image_ready:
                    b = upload_p_img(p, tripitaka_dir)
        return Response(a)

    @list_route(methods=['post', 'get'])
    def generate_cut(self, request):
        return Response(sutra_operation(generate_cut, self))

    @list_route(methods=['post', 'get'])
    def generate_col(self, request):
        return Response(sutra_operation(generate_col, self))

    @detail_route(methods=['post', 'get'])
    def crop_col_img(self, request, pk):
        return Response(sutra_operation(crop_col_img, self))

    @list_route(methods=['post', 'get'])
    def gather_img_info(self, request):
        return Response(sutra_operation(gather_img_info, self))

    @list_route(methods=['post', 'get'])
    def gather_cut_info(self, request):
        return Response(sutra_operation(gather_cut_info, self))

    @list_route(methods=['post', 'get'])
    def upload_img(self, request):
        return Response(sutra_operation(upload_img, self))


def reel_operation(func, ob, pk):
    msg = {}
    r = Reel.objects.get(id=pk)
    pages = r.page_set.all()
    for p in pages:
        msg[p.code] = func(p)
    return msg


class ReelViewSet(viewsets.ModelViewSet):
    serializer_class = ReelSerializer
    queryset = Reel.objects.all()
    permission_classes = (AllowAny,)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fileds = ('code', 'sutra')

    def get_queryset(self):
        queryset = Reel.objects.all()
        code = self.request.query_params.get('code', None)
        sutra = self.request.query_params.get('sutra', None)
        if code is not None:
            queryset = queryset.filter(code=code)
        if sutra is not None:
            # queryset = queryset.filter(sutra__code=sutra)
            queryset = queryset.filter(sutra__id=sutra)
        return queryset

    @detail_route(methods=['post', 'get'])
    def upload_img(self, request, pk):
        msg = ''
        r = Reel.objects.get(id=pk)
        tripitaka_dir = self.request.query_params.get('tripitaka_dir', None)
        pages = r.page_set.all()
        for p in pages:
            if not p.image_ready:
                upload_p_img(p, tripitaka_dir)
        return Response(msg)

    @detail_route(methods=['post', 'get'])
    def generate_cut(self, request, pk):
        msg = reel_operation(generate_col, self, pk)
        return Response(msg)

    @detail_route(methods=['post', 'get'])
    def generate_col(self, request, pk):
        msg = reel_operation(generate_col, self, pk)
        return Response(msg)

    @detail_route(methods=['post', 'get'])
    def crop_col_img(self, request, pk):
        msg = reel_operation(crop_col_img, self, pk)
        return Response(msg)

    @detail_route(methods=['post', 'get'])
    def gather_img_info(self, request, pk):
        msg = reel_operation(gather_img_info, self, pk)
        return Response(msg)

    @detail_route(methods=['post', 'get'])
    def gather_cut_info(self, request, pk):
        msg = reel_operation(gather_cut_info, self, pk)
        return Response(msg)

    def upload_img(self, request, pk):
        msg = reel_operation(upload_img, self, pk)
        return Response(msg)


def page_operation(func, ob, pk):
    try:
        p = Page.objects.get(id=pk)
    except Exception as e:
        pass
    return {p.code : func(p)}


class PageViewSet(viewsets.ModelViewSet):
    serializer_class = PageSerializer
    queryset = Page.objects.all()
    permission_classes = (AllowAny,)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fileds = ('code', 'reel')
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = Page.objects.all()
        reel = self.request.query_params.get('reel', None)
        if reel is not None:
            queryset = queryset.filter(reel__id=reel)
        return queryset

    @detail_route(methods=['post', 'get'])
    def upload_img(self, request, pk):
        return Response(page_operation(upload_img, self, pk))

    @detail_route(methods=['post', 'get'])
    def generate_cut(self, request, pk):
        return Response(page_operation(generate_cut, self, pk))

    @detail_route(methods=['post', 'get'])
    def generate_col(self, request, pk):
        return Response(page_operation(generate_col, self, pk))

    @detail_route(methods=['post', 'get'])
    def crop_col_img(self, request, pk):
        return Response(page_operation(crop_col_img, self, pk))

    @detail_route(methods=['get'])
    def get_cut_data(self, request, pk):
        p = Page.objects.get(id=pk)
        try:
            cut_path = "https://s3.cn-north-1.amazonaws.com.cn/lqcharacters-images/" + p.img_path.replace('.jpg', '.cut')
            cut_dict = json.loads(urllib.request.urlopen(cut_path).readlines()[0])
            ps = get_page_txt(cut_dict)
            cut_dict['ps'] = ps
            return Response(cut_dict)
        except Exception as e:
            msg = ' '.join([str(datetime.now()), '%s' % format(e)])
            return Response({'char_data': []})

    @detail_route(methods=['post', 'get'])
    def gather_img_info(self, request, pk):
        return Response(page_operation(gather_img_info, self, pk))

    @detail_route(methods=['post', 'get'])
    def gather_cut_info(self, request, pk):
        return Response(page_operation(gather_cut_info, self, pk))
