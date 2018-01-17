from django.db import models
import uuid
import urllib
import boto3
from datetime import datetime
import os
from PIL import Image
import json

s3c = boto3.client('s3')
my_bucket = 'lqcharacters-images'
s3 = boto3.resource('s3')
CHNAGE_NAME_LOGS = open('change_name_logs.txt', 'a')
UPLOAD_LOGS = open('upload_logs.txt', 'a')


class TripiMixin(object):
    def __str__(self):
        return self.name


class Batch(models.Model):
    sub_date = models.DateField('date submitted', blank=True, default=datetime.now)
    org = models.CharField(max_length=128, blank=False)
    des = models.CharField(max_length=512, blank=False)

    class Meta:
        verbose_name = '批次'
        verbose_name_plural = '批次'

    def __str__(self):
        return self.org +":" + str(self.sub_date)



class LQSutra(models.Model, TripiMixin):
    code = models.CharField(verbose_name='龙泉经目编码', max_length=8, primary_key=True)
    # （为"LQ"+ 经序号 + 别本号）
    name = models.CharField(verbose_name='龙泉经目名称', max_length=64, blank=False)
    total_reels = models.IntegerField(verbose_name='总卷数', blank=True, default=1)

    class Meta:
        verbose_name = u"龙泉经目"
        verbose_name_plural = u"龙泉经目管理"

    def __str__(self):
        return self.name


class Tripitaka(models.Model, TripiMixin):
    code = models.CharField(verbose_name='实体藏经版本编码', primary_key=True, max_length=4, blank=False)
    name = models.CharField(verbose_name='实体藏经名称', max_length=32, blank=False)

    class Meta:
        verbose_name = '实体藏经'
        verbose_name_plural = '实体藏经管理'

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class Sutra(models.Model, TripiMixin):
    sid = models.CharField(verbose_name='实体藏经|唯一经号编码', editable=True, max_length=32)  # 藏经版本编码 + 5位经序号+1位别本号
    tripitaka = models.ForeignKey(Tripitaka, related_name='sutras')
    code = models.CharField(verbose_name='实体经目编码', max_length=5, blank=False)
    variant_code = models.CharField(verbose_name='别本编码', max_length=1, default='0')
    name = models.CharField(verbose_name='实体经目名称', max_length=64, blank=True)
    lqsutra = models.ForeignKey(LQSutra, verbose_name='龙泉经目编码', null=True, blank=True)  # （为"LQ"+ 经序号 + 别本号）
    total_reels = models.IntegerField(verbose_name='总卷数', blank=True, default=1)


    class Meta:
        verbose_name = '实体经目'
        verbose_name_plural = '实体经目管理'

    def change_name(self):
        reels = self.reel_set.all()
        for reel in reels:
            reel.change_name()

    def __str__(self):
        return self.sid + self.name


class Reel(models.Model):
    sutra = models.ForeignKey(Sutra)
    sutra_code = models.CharField(verbose_name='实体经目编码', max_length=8, blank=True)
    code = models.CharField(max_length=128, blank=False)
    name = models.CharField(max_length=128, blank=False)
    ready = models.BooleanField(default=False)
    image_ready = models.BooleanField(default=False)
    #image_ready_no = models.SmallIntegerField(default=0)
    image_upload = models.BooleanField(default=False)
    txt_ready = models.BooleanField(default=False)
    cut_ready = models.BooleanField(default=False)
    column_ready = models.BooleanField(default=False)

    class Meta:
        verbose_name = '卷'
        verbose_name_plural = '卷'

    def __str__(self):
        return self.sutra.tripitaka.code+self.sutra.name + '第' + self.code + '卷'

    def change_name(self):
        pages = self.page_set.all()
        for page in pages:
            page.change_name()

    def check_image(self):
        pages = self.page_set.all()
        no = 0
        # 用百分比还是布尔值？

    def pdf_2_img(self, pdf_path):
        img_dir = '/'.join([self.sutra.tripitaka.code, self.sutra.sid[2:], 'v%03d' % int(self.code)])
        if not os.path.exists(img_dir):
            os.system('mkdir -p '+img_dir)
        trans_cmd = 'gs  -dQUIET -sDEVICE=jpeg -o ' + img_dir + '/test.jpg -r72  -dFirstPage=1 -dLastPage=1 ' + pdf_path
        os.system(trans_cmd)
        im = Image.open(img_dir + '/test.jpg')
        im.show(title="width:" + str(im.width))
        if im.width < 1200:
            n = 1600 / im.width * 72
        else:
            n = 72
        os.system('rm ' + img_dir + '/test.jpg')
        trans_cmd = 'gs  -dQUIET -sDEVICE=jpeg -o ' + img_dir + '/%04d.jpg -r' + str(int(n)) + ' ' + pdf_path
        os.system(trans_cmd)

    '''def upload_img(self, tripitaka_dir=''):
        pages = self.page_set.all()
        for p in pages:
            p.upload_img(tripitaka_dir)'''


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


class Volume(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tripitaka = models.ForeignKey(Tripitaka)
    pdf_path = models.CharField(max_length=128, blank=False)
    v_no = models.SmallIntegerField(blank=True, default=0)
    pdf_page_offset = models.SmallIntegerField(blank=True, default=0)
    total_page_no = models.SmallIntegerField(blank=True, default=0)

    class Meta:
        verbose_name = '册'
        verbose_name_plural = '册'


class OImg(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    img_code = models.CharField(verbose_name='图片编码', max_length=20, blank=True)
    # GZ000790v001p00010 or QLv001p00010
    v_no = models.SmallIntegerField(verbose_name='册号', blank=True, default=0)
    v_page_no = models.SmallIntegerField(verbose_name='正文页码', blank=True, default=0)

    img_path = models.CharField(verbose_name='图片本地路径', max_length=128, blank=False)
    # 本地路径
    big_image = models.BooleanField(verbose_name='大图', default=False)
    img_1200 = models.BooleanField(verbose_name='1200图', default=False)
    img_s3 = models.BooleanField(verbose_name='上传到s3', default=False)
    img_cropped = models.BooleanField(verbose_name='图片切列', default=False)

    width = models.SmallIntegerField(verbose_name='图片宽度', blank=True, default=1200)
    height = models.SmallIntegerField(verbose_name='图片高度', blank=True, default=780)

    class Meta:
        verbose_name = '图片'
        verbose_name_plural = '图片'

    def __str__(self):
        return self.img_code


class OCut(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch = models.ForeignKey(Batch, blank=True, default=1, verbose_name='所属批次')
    cut_code = models.CharField(verbose_name='切分编码', max_length=20, blank=True)
    # GZ000790v001p00010 or QLv001p00010
    v_no = models.SmallIntegerField(verbose_name='册号', blank=True, default=0)
    v_page_no = models.SmallIntegerField(verbose_name='正文页码', blank=True, default=0)

    cut_ori = models.CharField(verbose_name='切分源文件', max_length=200, blank=True)
    cut_json = models.CharField(verbose_name='切分标准文件', max_length=200, blank=True)
    cut_gened = models.BooleanField(verbose_name='输出', default=False)

    col_json = models.CharField(verbose_name='列标准文件', max_length=200, blank=True)
    col_gened = models.BooleanField(verbose_name='列输出', default=False)
    column_ready = models.BooleanField(default=False)
    col_no = models.SmallIntegerField(verbose_name='列数', blank=True, default=1)

    class Meta:
        verbose_name = '切分数据'
        verbose_name_plural = '切分数据'

    def __str__(self):
        return self.cut_code


class Page(models.Model):
    reel = models.ForeignKey(Reel)
    code = models.CharField(verbose_name='编码', max_length=128, blank=False)
    v_no = models.SmallIntegerField(verbose_name='册号', blank=True, default=0)
    v_page_no = models.SmallIntegerField(verbose_name='页码', blank=True, default=1)
    r_page_no = models.SmallIntegerField(verbose_name='卷页码', blank=True, default=1)
    img_path = models.CharField(verbose_name='s3图片路径', max_length=128, blank=False)
    o_img = models.ForeignKey(OImg, blank=True, verbose_name='图片')
    o_cut = models.ForeignKey(OCut, blank=True, verbose_name='切分')
    #ready = models.BooleanField(default=False)
    image_ready = models.BooleanField(default=False)
    txt_ready = models.BooleanField(default=False)
    cut_ready = models.BooleanField(default=False)

    class Meta:
        verbose_name = '页'
        verbose_name_plural = '页'

    def __str__(self):
        return self.code

    @property
    def cut_data(self):
        try:
            cut_path = "https://s3.cn-north-1.amazonaws.com.cn/lqcharacters-images/" + self.img_path.replace('.jpg', '.cut')
            cut_dict = json.loads(urllib.request.urlopen(cut_path).readlines()[0])
            ps = get_page_txt(cut_dict)
            cut_dict['ps'] = ps
            return cut_dict
        except Exception as e:
            msg = ' '.join([str(datetime.now()), '%s' % format(e)])
            return {}

    def generate_line(self):
        pass

    def get_real_path(self):
        return "https://s3.cn-north-1.amazonaws.com.cn/lqcharacters-images/" + self.img_path

    def change_name(self):
        if len(self.code) != len('QL000010v001p00180'):
            sid = self.reel.sutra.sid
            self.code = sid + 'v%03d' % self.v_no + 'p%04d0' % self.v_page_no
            self.img_path = '/'.join([sid[:2], sid[2:], 'v%03d' % self.v_no, self.code + '.jpg'])
            self.save()


class Column(models.Model):
    page = models.ForeignKey(Page)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=128, blank=False)
    img_path = models.CharField(max_length=128, blank=False)

    def get_real_path(self):
        return "https://s3.cn-north-1.amazonaws.com.cn/lqcharacters-images/" + self.img_path


class OTxt(models.Model):
    page = models.ForeignKey(Page)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=128, blank=False)
    txt = models.TextField(blank=True)



'''
class Line(models.Model):
    page = models.ForeignKey(Page)
    code = models.CharField(max_length=128, blank=False)
    img_path = models.CharField(max_length=128, blank=False)
    txt = models.TextField(blank=True)

    class Meta:
        verbose_name = '列'
        verbose_name_plural = '列'

    def get_real_path(self):
        return "https://s3.cn-north-1.amazonaws.com.cn/lqcharacters-images/" + self.img_path


class BatchVersion(models.Model):
    class Meta:
        db_table = 'rect_batch'


class Opage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=64)
    s3_inset = models.CharField(max_length=100)

    class Meta:
        db_table = 'rect_opage'


class Ocolumn(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=64)
    s3_inset = models.CharField(max_length=256)
    location = models.CharField(max_length=64)
    opage = models.ForeignKey(Opage)

    class Meta:
        db_table = 'rect_ocolumn'


class RectPage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=64)
    line_count = models.SmallIntegerField()
    column_count = models.SmallIntegerField()
    rect_set = models.TextField()
    create_date = models.DateField()
    batch = models.ForeignKey(BatchVersion)

    class Meta:
        db_table = 'rect_pagerect'
'''
