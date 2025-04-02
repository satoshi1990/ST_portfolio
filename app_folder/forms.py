from django import forms
from app_folder.modules import common
# from django.core.exceptions import ValidationError
# from django.utils.translation import gettext_lazy as _
from .models import Card_summary


packnamedict = common.packNameDict  # パックコードとパック名の対照dict
card_categorydict = common.cardCategoryDict # カードカテゴリ番号とカテゴリ名の対照dict
card_classdict    = common.cardClassDict    # カードクラス番号とクラス名の対照dict
card_elementdict  = common.cardElementDict  # 属性番号と属性名の対照dict
card_elementdict['0'] = "---"

class CardRegisterForm(forms.Form):
    name          = forms.CharField(label='カード名', max_length=50, empty_value="", strip=True ) # 必須
    name_english  = forms.CharField(label='英語名', max_length=50, required=False, empty_value="", strip=True )
    pack_code     = forms.ChoiceField(label="パック名", widget=forms.widgets.Select, choices=(packnamedict), ) # 必須
    pack_card_id  = forms.IntegerField(label='パック内カードID', min_value=1, max_value=9999) # 必須
    card_category = forms.ChoiceField(label='カードカテゴリ', widget=forms.widgets.Select, choices=(card_categorydict), ) # 必須
    card_class    = forms.ChoiceField(label='カードクラス',   widget=forms.widgets.Select, choices=(card_classdict), ) # 必須
    element       = forms.ChoiceField(label="属性", widget=forms.widgets.Select, choices=(card_elementdict), required=False, ) # 必須
    ex            = forms.BooleanField(label="ex", widget=forms.widgets.CheckboxInput, required=False,)
    all_card_id  = forms.IntegerField(label='全体カードID', widget=forms.widgets.NumberInput, min_value=1, max_value=9999, ) # 必須

    category_pokemon  = common.category_pokemon
    category_trainers = common.category_trainers
    class_pokemon     = common.class_pokemon
    class_trainers    = common.class_trainers
    non_element = 0

    #--------------------------------
    # バリデーション(フィールド個別)
    #--------------------------------
    
    # card_class
    # クラス カテゴリがポケモン[1]の時はクラスでグッズ等[456]は選べない,
    # トレーナーズ[2]の時は逆にたねや進化[123]は選べない
    def clean_card_class(self):
        print("IN clean_card_class")
        card_category = int(self.cleaned_data["card_category"])
        card_class = int(self.cleaned_data["card_class"])

        if card_category == self.category_trainers:
            if card_class in self.class_pokemon:
                self.add_error('card_class', "カードカテゴリがトレーナーズの際、クラスは[サポート,グッズ,かせき]から選択してください")

        elif card_category == self.category_pokemon:
            if card_class in self.class_trainers:
                self.add_error('card_class', "カテゴリがトレーナーズの時、クラスは[たね,1進化,2進化]から選択してください")
        return card_class

    # element
    # カテゴリがトレーナーズ[2]の時はエレメントは選べない
    def clean_element(self):
        print("IN clean_element")
        card_category = int(self.cleaned_data["card_category"])
        element = int(self.cleaned_data["element"])

        if card_category == self.category_trainers:
            if element:
                self.add_error('element', "カードカテゴリがトレーナーズの際、属性は選択できません")

        elif card_category == self.category_pokemon:
            if element is self.non_element:
                self.add_error('element', "カードカテゴリがポケモンの際、属性は必須です")
        return element

    # ex
    # カテゴリがトレーナーズ[2]の時exは選択できない
    def clean_ex(self):
        print("IN clean_ex")
        card_category = int(self.cleaned_data["card_category"])
        ex = self.cleaned_data["ex"]

        if card_category == self.category_trainers:
            if ex:
                self.add_error('ex', "カードカテゴリがトレーナーズの際、exは選択できません")
        return ex

# 新規作成フォーム
class CardCreateForm(CardRegisterForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['all_card_id'].disabled = True
    
    # pack_card_id
    # パック名+パックIDがユニークにならない場合はエラー(DBに組み合わせ制約あり)
    def clean_pack_card_id(self):    
        print("IN clean_pack_card_id")
        pack_code = self.cleaned_data["pack_code"]
        pack_card_id = int(self.cleaned_data["pack_card_id"])

        result = Card_summary.objects.select_related("detail").order_by('all_card_id')
        result = result.filter(pack_code=pack_code)
        result = result.filter(pack_card_id=pack_card_id)

        if result:
            self.add_error('pack_card_id', "指定されたパック名+パックIDの組み合わせは既に登録されています")
        return pack_card_id
    
    #--------------------------------
    # バリデーション(all_card_idが不正に操作されていた場合でall_card_idが既に存在している場合)
    # クライアントからの値は表示のみで全て無信用のため、不要となった(都度IDのMAX値+1を取得する方針)
    #--------------------------------
    # def clean_all_card_id(self):
    #     print("IN clean all_card_id")
    #     all_card_id = int(self.cleaned_data["all_card_id"])

    #     result = Card_summary.objects.filter(all_card_id=all_card_id).exists()
        
    #     if result:
    #         self.add_error('all_card_id', "全体カードIDが不正です")
    #         # raise forms.ValidationError('全体カードIDが既に存在しています')
    #     return all_card_id

# アップデートフォーム
class CardUpdateForm(CardRegisterForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['all_card_id'].widget.attrs['readonly']  = 'readonly'
        self.fields['all_card_id'].widget.attrs['class']     = 'form-control'

    #--------------------------------
    # バリデーション(個別)
    #--------------------------------
    # all_card_idが不正に操作されていた場合
    # 存在しないレコードにアップデートをかけないために実施、
    def clean_all_card_id(self):
        print("IN clean all_card_id update")
        all_card_id = int(self.cleaned_data["all_card_id"])

        result = Card_summary.objects.filter(all_card_id=all_card_id).exists()

        if not result:
            self.add_error('all_card_id', "全体カードIDが不正です")
        return all_card_id
    
    # pack_card_id
    # 登録時、入力されたパック名+パックIDが重複した場合はエラー 
    # だが、重複したレコードのall_card_idが、編集しているformの同fieldのinitialと同じ場合 は問題ない
    def clean_pack_card_id(self):    
        print("IN clean_pack_card_id")
        pack_code = self.cleaned_data["pack_code"]
        pack_card_id = int(self.cleaned_data["pack_card_id"])

        result = Card_summary.objects.filter(pack_code=pack_code, pack_card_id=pack_card_id).exists()

        if result:
            result2 = Card_summary.objects.get(pack_code=pack_code, pack_card_id=pack_card_id)
            if result2.all_card_id != int(self['all_card_id'].initial):
                self.add_error('pack_card_id', "指定されたパック名+パックIDの組み合わせは既に登録されています")
        return pack_card_id
