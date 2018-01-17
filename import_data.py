import sys
import os
import django
import xlrd
from PIL import Image
from datetime import datetime
import boto3

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tripitaka.settings")
django.setup()
from sutra.models import Tripitaka, Sutra, Reel, Page


def write_dict_into_db(tripitaka_dict):

    for t in tripitaka_dict.keys():
        tripitaka = list(Tripitaka.objects.filter(code=t))
        if not tripitaka:
            tripitaka = Tripitaka(code=t, name=t)
            tripitaka.save()
        else:
            tripitaka = tripitaka[0]
        for sutra_code in tripitaka_dict[t].keys():
            sutra = Sutra.objects.filter(tripitaka=tripitaka, code=sutra_code)
            if not sutra:
                sutra = Sutra(tripitaka=tripitaka, code=sutra_code, name=tripitaka_dict[t][sutra_code][0])
                sutra.save()
            else:
                sutra = sutra[0]
            reel_dict = tripitaka_dict[t][sutra_code][1]
            for r in reel_dict:
                reel = Reel(sutra=sutra, code=r, name=r)
                reel.save()
                page_lst = reel_dict[r]
                for p in page_lst:
                    page = Page(reel=reel, code=p[1], r_page_no=int(p[0]), img_path=p[2], v_no=p[3], v_page_no=p[4])
                    page.save()
                    print(page.img_path)


def import_glz(txt_path):
    txt = open(txt_path)
    tripitaka_dict = {}

    for i in txt.readlines():
        paras = i.split(' ')
        img_url = paras[0]
        sutra_name = paras[2].split('_')[2]
        img_url_paras = img_url.split('/')
        tripitaka_code = img_url_paras[0]
        if tripitaka_code not in tripitaka_dict.keys():
            tripitaka_dict[tripitaka_code] = {}
        sutra_code = img_url_paras[1]
        reel_code = img_url_paras[2]
        page_code = paras[1].split('_')[-1].replace('.jpg', '')
        if sutra_code not in tripitaka_dict[tripitaka_code].keys():
            tripitaka_dict[tripitaka_code][sutra_code] = (sutra_name, {})
        if reel_code not in tripitaka_dict[tripitaka_code][sutra_code][1].keys():
            tripitaka_dict[tripitaka_code][sutra_code][1][reel_code] = []
        tripitaka_dict[tripitaka_code][sutra_code][1][reel_code].append((page_code, img_url))
    write_dict_into_db(tripitaka_dict)

#import_glz('/home/buddhist/AI/tripitaka/高丽藏切字对应.txt')

def generate_img_url(start_v_no, end_v_no, start_p_no, end_p_no):
    if start_v_no == end_v_no:
        img_urls = []
        for p_no in range(start_p_no, stop=end_p_no):
            tmp = "V%03d/T%0"

def parseInt(word):
    if type(word) is str:
        if word.isdigit():
            return int(word)
        else:
            return int(float(word))
    elif type(word) is float:
        return int(word)
    else:
        return word

def import_xls_lqsutra(xls_path, lq_sutra):
    data_sheet = xlrd.open_workbook(xls_path).sheets()[0]
    tripitaka_dict = {}

    for row_no in range(data_sheet.nrows)[1:]:
        row = data_sheet.row_values(row_no)
        tripitaka_code = row[0]
        tripitaka_name = row[1]
        sutra_code = row[2][:2] + '0' + row[2][2:] + '0'
        sutra_name = row[3]
        reel_no = str(row[4]).replace('.0', '')
        print(reel_no)
        start_v_no = parseInt(row[5])
        start_p_no = parseInt(row[6])
        end_p_no = parseInt(row[7])
        if tripitaka_code not in tripitaka_dict.keys():
            tripitaka_dict[tripitaka_code] = {}
        if sutra_code not in tripitaka_dict[tripitaka_code].keys():
            tripitaka_dict[tripitaka_code][sutra_code] = (sutra_name, {})
        if reel_no not in tripitaka_dict[tripitaka_code][sutra_code][1].keys():
            tripitaka_dict[tripitaka_code][sutra_code][1][reel_no] = []
        for page_no in range(end_p_no - start_p_no + 1):
            r_page_no = (page_no + 1)
            v_no = int(start_v_no)
            v_page_no = start_p_no + page_no
            paras = [tripitaka_code, 'v%03d' % v_no, "p%04d" % v_page_no]
            page_code = ''.join(paras)
            img_url = '/'.join(paras[:2]) + '/' + ''.join(paras) + '.jpg'
            tripitaka_dict[tripitaka_code][sutra_code][1][reel_no].append((r_page_no, page_code, img_url, v_no, v_page_no))

    return tripitaka_dict


def import_xls(xls_path, tripitaka_code):
    data_sheet = xlrd.open_workbook(xls_path).sheets()[0]
    tripitaka_dict = {}
    if tripitaka_code not in tripitaka_dict.keys():
        tripitaka_dict[tripitaka_code] = {}
    for row_no in range(data_sheet.nrows)[2:]:
        row = data_sheet.row_values(row_no)
        sutra_code = '0'+row[0][-4:]+'0'
        sutra_name = row[1]
        reel_no = str(row[2]).replace('.0', '')

        start_v_no = parseInt(row[3])
        start_p_no = parseInt(row[4])
        end_p_no = parseInt(row[5])

        if sutra_code not in tripitaka_dict[tripitaka_code].keys():
            tripitaka_dict[tripitaka_code][sutra_code] = (sutra_name, {})
        if reel_no not in tripitaka_dict[tripitaka_code][sutra_code][1].keys():
            tripitaka_dict[tripitaka_code][sutra_code][1][reel_no] = []
        for page_no in range(end_p_no-start_p_no+1):
            r_page_no = (page_no+1)
            v_no = int(start_v_no)
            v_page_no = start_p_no + page_no
            paras = [tripitaka_code, 'v%03d' % v_no, "p%04d0" % v_page_no]
            page_code = ''.join(paras)
            img_url = '/'.join(paras[:2])+'/'+''.join(paras)+'.jpg'
            tripitaka_dict[tripitaka_code][sutra_code][1][reel_no].append((r_page_no, page_code, img_url, v_no, v_page_no))
    return tripitaka_dict

#write_dict_into_db(import_xls('/home/buddhist/文档/项目文档/藏经目录/乾隆大藏经详目20170605.xlsx', 'QL'))
#write_dict_into_db(import_xls('/home/buddhist/文档/项目文档/藏经目录/三層永樂北藏詳目.xlsx', 'YB'))
write_dict_into_db(import_xls_lqsutra('/home/buddhist/文档/项目文档/60华严/六十华严目录.xlsx', 'LQ0310'))


def cut_into_col(img_url, pos_data, dest_path, record_txt):
    pos = pos_data.split('!')[0]
    # txt = pos_data.split('!')[1]
    pos_lines = pos.split(';')
    pos_lines.reverse()
    line_region_dict = {}
    neibor_x = 1200
    if len(pos) < 4:
        pass
    else:
        for line_no, line in enumerate(pos_lines):
            left_x = 2400
            left_y = 2400
            right_x = 0
            right_y = 0
            for d_no, data in enumerate(line.split(',')):
                d_no += 1
                #print(data)
                data = int(float(data) * 0.5)
                if d_no % 5 == 1:
                    if data < left_x:
                        left_x = data
                if d_no % 5 == 2:
                    if data < left_y:
                        left_y = data
                if d_no % 5 == 3:
                    if data > right_x:
                        right_x = data
                if d_no % 5 == 4:
                    if data > right_y:
                        right_y = data
            if right_x < neibor_x:
                right_x = neibor_x
            neibor_x = left_x
            line_region_dict[line_no + 1] = [left_x, 0, right_x, 780]
        line_region_dict[len(pos_lines)][0] = 0
        #ori_im = Image.open(img_url)
        for line_no in line_region_dict.keys():
            new_img_url = (img_url.split('.')[0].split('/')[-1] + "_L%02d" % line_no) + ".jpg"
            #if not os.path.exists(dest_path + new_img_url):
                #crop_im = ori_im.crop(line_region_dict[line_no])
                #crop_im.save(dest_path + new_img_url)
            record_txt.write(new_img_url+" "+str(line_region_dict[line_no][0])+",0\n")
        #ori_im.close()
        # 问题：最后一列可能会出现切窄，但是又没有足够的范围来画框
        # 问题：最后一列之后可能还会有字，但是没切到
        # 解决方案：最后一列和第一列都直接到两边


def cut_glz(cut_data, record_txt):
    a = datetime.now()
    for d in cut_data.readlines():
        img_name = d.split(' ')[0]
        if img_name.find('(') > -1:
            print(img_name)
        else:
            name_list = img_name.split('_')
            new_name_list = ['GLZ']
            page_no = int(name_list[3].split('.')[0])
            suffix = name_list[3].split('.')[1]
            new_name_list.extend(['S%05d' % int(name_list[0]), 'R%03d' % int(name_list[1]), 'T%04d' % page_no])
            img_name = "_".join(new_name_list) + '.jpg'
            img_url = '/media/buddhist/大藏经（三）/1200/GLZ_1200/' + '/'.join(new_name_list[1:-1]) + '/' + img_name
            pos_data = d.split(' ')[1].split('!')[0]
            dest_path = '/home/buddhist/cut_col/GLZ/' + '/'.join(new_name_list[1:-1]) + '/'
            if not os.path.exists(dest_path):
                os.system('mkdir -p '+dest_path)
            cut_into_col(img_url=img_url, pos_data=pos_data, dest_path=dest_path, record_txt=record_txt)
    b = datetime.now()
    return (b-a).seconds


def generate_key(name):
    return "/".join(name.split('_')[:3]) + '/' + name

s3 = boto3.resource('s3')


def upload_glz(upload_dir):
    a = datetime.now()
    for i, j, k in os.walk(upload_dir):
        for l in k:
            s3.meta.client.upload_file(os.path.join(i, l), 'lqcharacters-images', generate_key(l))
    b = datetime.now()
    return (b-a).seconds

    for cut_data_file in os.listdir('/home/buddhist/文档/切分文件/glz_label/'):
        #if cut_data_file not in ['18.txt', '22.txt', '0.txt', '6.txt', '12.txt', '30.txt']:
        run_time = cut_glz(open('/home/buddhist/文档/切分文件/glz_label/' + cut_data_file), open('切列坐标数据', 'w'))
        print(cut_data_file+":", end='')
        print(run_time)
#run_time = upload_glz('/media/buddhist/大藏经（三）/cut_col/GLZ/S00001/R005/')
#print(run_time)


def cut_into_coldata(img_url, pos_data):
    pos = pos_data.split('!')[0]
    txt = pos_data.split('!')[1]
    txt_lines = txt.replace("\n", "").split(';')
    txt_lines.reverse()
    pos_lines = pos.split(';')
    pos_lines.reverse()
    line_region_lst = []
    neibor_x = 1200
    for line_no, line in enumerate(pos_lines):
        left_x = 2400
        left_y = 2400
        right_x = 0
        right_y = 0
        for d_no, data in enumerate(line.split(',')):
            d_no += 1
            data = int(float(data) * 0.5)
            if d_no % 5 == 1:
                if data < left_x:
                    left_x = data
            if d_no % 5 == 2:
                if data < left_y:
                    left_y = data
            if d_no % 5 == 3:
                if data > right_x:
                    right_x = data
            if d_no % 5 == 4:
                if data > right_y:
                    right_y = data
        if right_x < neibor_x:
            right_x = neibor_x
        neibor_x = left_x
        line_region_lst.append(str(line_no + 1) + "," + str(left_x) + ',' + str(right_x) + "," + txt_lines[line_no])
    return img_url + " " + ";".join(line_region_lst)


'''for g in open('test_cut_col').readlines():
    img_url, pos_data = g.split(' ')
    print(cut_into_coldata(img_url, pos_data))
    sys.stdout.flush()'''


def print_point(l):
    if len(l.split(":")[0].split(',')) == 4:
        x, y, w, h = [int(i) for i in l.split(":")[0].split(',')]
        print(",".join([str(i) for i in [x, y, x+w, y+h]]), end=',')
    if not l:
        print(';', end='')
        sys.stdout.flush()


def print_col(l):
    if len(l.split(":")[0].split(','))==8:
        print(l.split(":")[0], end=";")
        sys.stdout.flush()

    ylbz_106 = open('106/Img-143.ocrtext')
    for line in ylbz_106.readlines():
        l = line.replace('\n', '')
        #print_point(l)
        print_col(l)


def cut_ylbz(col_pos_data='868,183,868,383,830,383,830,183;804,140,800,714,756,714,759,140;759,141,753,715,706,715,712,141;710,140,708,717,659,717,660,140;657,144,657,716,608,716,608,144;605,140,607,713,560,713,559,140;529,136,531,710,482,710,480,136;476,135,482,711,436,711,430,135;427,135,434,708,388,708,381,135;378,135,387,707,340,707,330,135;327,137,337,705,294,706,284,137;870,535,868,719,832,719,834,535;796,743,791,1316,745,1316,750,743;752,744,746,1316,699,1316,705,744;698,744,695,1315,649,1315,651,744;648,742,650,1315,603,1315,601,742;597,745,599,1316,552,1316,550,745;532,741,537,1314,491,1314,486,741;484,741,484,1314,438,1314,438,741;432,741,438,1312,392,1312,386,741;381,742,387,1311,344,1311,338,742;332,741,339,1308,295,1308,288,741;868,1060,868,1247,831,1247,831,1060;'):
    line_region_dict = {}
    pos_lines = col_pos_data.split(';')
    for line_no, pos_line in enumerate(pos_lines):
        left_x = 2400
        left_y = 2400
        right_x = 0
        right_y = 0
        cord_set = line.split(',')
        left_x = min(cord_set)
        for d_no, data in enumerate(line.split(',')):
            d_no += 1
            data = int(float(data) * 0.5)
            if d_no % 5 == 1:
                if data < left_x:
                    left_x = data
            if d_no % 5 == 2:
                if data < left_y:
                    left_y = data
            if d_no % 5 == 3:
                if data > right_x:
                    right_x = data
            if d_no % 5 == 4:
                if data > right_y:
                    right_y = data
        print(str(right_x) + "," + str(left_x) + " ", end="")
        if right_x < neibor_x:
            right_x = neibor_x
        neibor_x = left_x
        print(str(right_x) + "," + str(left_x))
        line_region_dict[line_no + 1] = [left_x, 0, right_x, 780]
    line_region_dict[len(pos_lines)][0] = 0