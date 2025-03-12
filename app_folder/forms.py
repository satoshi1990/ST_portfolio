from django import forms
from app_folder.modules import common
# from django.core.exceptions import ValidationError
# from django.utils.translation import gettext_lazy as _
from .models import Card_summary


packnamedict = common.packNameDict  # パックコードとパック名の対照dict
card_categorydict = common.cardCategoryDict # カードカテゴリ番号とカテゴリ名の対照dict
card_classdict    = common.cardClassDict    # カードクラス番号とクラス名の対照dict
card_elementdict  = common.cardElementDict  # 属性番号と属性名の対照dict
card_elementdict[''] = "---"

category_pokemon = 1
category_trainers = 2
class_pokemon = [1,2,3]
class_trainers = [4,5,6]


class CardRegisterForm(forms.Form):
    name          = forms.CharField(label='カード名', max_length=50, empty_value="", strip=True ) # 必須
    name_english  = forms.CharField(label='英語名', max_length=50, required=False, empty_value="", strip=True )
    pack_name     = forms.ChoiceField(label="パック名", widget=forms.widgets.Select, choices=(packnamedict), ) # 必須
    pack_card_id  = forms.IntegerField(label='パック内カードID', min_value=0, max_value=999) # 必須
    card_category = forms.ChoiceField(label='カードカテゴリ', widget=forms.widgets.Select, choices=(card_categorydict), ) # 必須
    card_class    = forms.ChoiceField(label='カードクラス',   widget=forms.widgets.Select, choices=(card_classdict), ) # 必須
    element       = forms.ChoiceField(label="属性", widget=forms.widgets.Select, choices=(card_elementdict), required=False, ) # 必須
    ex            = forms.BooleanField(label="ex", widget=forms.widgets.CheckboxInput, required=False,)


    #--------------------------------
    #バリデーション(全体)
    #--------------------------------
    # def clean(self):
    #     print("IN clean")
    #     cleaned_data = super().clean()
    #     card_category = cleaned_data["card_category"]
    #     element = cleaned_data["element"]

    #     if card_category == category_trainers:
    #         if element:
    #             self.add_error('element', "カードカテゴリがトレーナーズの際、属性は選択できません0")
    #             raise forms.ValidationError('Y')
    #     return cleaned_data

    #--------------------------------
    # バリデーション(フィールド個別)
    #--------------------------------
    
    # pack_card_id
    # パック名+パックIDがユニークにならない場合はエラー
    def clean_pack_card_id(self):    
        print("IN clean_pack_card_id")
        pack_code = self.cleaned_data["pack_name"]
        pack_card_id = self.cleaned_data["pack_card_id"]

        result = Card_summary.objects.select_related("detail").order_by('all_card_id')
        result = result.filter(pack_code=pack_code)
        result = result.filter(pack_card_id=pack_card_id)

        if result:
            self.add_error('pack_card_id', "指定されたパック名+パックIDの組み合わせは既に登録されています")
        return pack_card_id
    
    # card_class
    # クラス カテゴリがポケモン[1]の時はクラスでグッズ等[456]は選べない,
    # トレーナーズ[2]の時は逆にたねや進化[123]は選べない
    def clean_card_class(self):
        print("IN clean_card_class")
        card_category = int(self.cleaned_data["card_category"])
        card_class = int(self.cleaned_data["card_class"])

        print(card_class in class_trainers)

        if card_category == category_trainers:
            if card_class in class_pokemon:
                self.add_error('card_class', "カードカテゴリがトレーナーズの際、このカードクラスは選択できません")
                # raise forms.ValidationError("カードカテゴリがトレーナーズの際、このカードクラスは選択できません")

        elif card_category == category_pokemon:
            print("clean_class TEST2")
            if card_class in class_trainers:
                # self.add_error('card_class', "カードカテゴリがポケモンの際、このカードクラスは選択できません")
                raise forms.ValidationError("カードカテゴリがトレーナーズの際、このカードクラスは選択できません")
        return card_class

    # element
    # カテゴリがトレーナーズ[2]の時はエレメントは選べない
    def clean_element(self):
        print("IN clean_element")
        card_category = int(self.cleaned_data["card_category"])
        element = self.cleaned_data["element"]

        if card_category == category_trainers:
            if element:
                self.add_error('element', "カードカテゴリがトレーナーズの際、属性は選択できません")
                # raise forms.ValidationError('メールアドレスが不正です')
        return element

    # ex
    # カテゴリがトレーナーズ[2]の時exは選択できない
    def clean_ex(self):    
        print("IN clean_ex")
        card_category = int(self.cleaned_data["card_category"])
        ex = self.cleaned_data["ex"]

        if card_category == category_trainers:
            if ex:
                self.add_error('ex', "カードカテゴリがトレーナーズの際、exは選択できません")
        return ex

