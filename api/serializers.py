from sutra.models import Sutra, Reel, Page, OCut, OImg
from rest_framework import serializers


class SutraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sutra
        fields = '__all__'

        class Meta:
            depth = 2


class ReelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reel
        fields = '__all__'

        class Meta:
            depth = 2


class OCutSerializer(serializers.ModelSerializer):
    class Meta:
        model = OCut
        exclude = ['id', 'v_no', 'v_page_no', 'cut_ori', 'cut_json', 'col_json', 'column_ready']
        #fields = '__all__'


class OImgSerializer(serializers.ModelSerializer):
    class Meta:
        model = OImg
        exclude = ['id', 'v_no', 'v_page_no']
        #fields = '__all__'


class PageSerializer(serializers.ModelSerializer):
    cut = serializers.SerializerMethodField()
    img = serializers.SerializerMethodField()

    def get_cut(self, obj):
        try:
            cut = obj.o_cut
            return OCutSerializer(cut, read_only=True).data
        except Exception as e:
            return {}

    def get_img(self, obj):
        try:
            img = obj.o_img
            return OImgSerializer(img, read_only=True).data
        except Exception as e:
            return {}

    class Meta:
        model = Page
        fields = ['id', 'v_no', 'code', 'r_page_no', 'img_path', 'cut', 'img']

        class Meta:
            depth = 2
