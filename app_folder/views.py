from django.shortcuts import render, get_object_or_404
from django.views import View
from django.db import transaction
from django.core.paginator import Paginator
from .models import Card_summary, Card_detail
from .forms import CardRegisterForm, CardCreateForm, CardUpdateForm
from app_folder.modules import common

class TopView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'app_folder/top_page.html')


# app1 ポケポケDB(基本的なCRUD)
# 
# App1View class内分岐
# get create app1_index.htmlから新規登録リンクで返ってきた際の処理
#     edit   app1_index.htmlから編集リンクで返ってきた際の処理
#     search app1_index.htmlからbtn_searchで返ってきた際の処理
#     index  'app_folder/app1_index/'にgetプロパティ無しで入った場合の処理
#
# post create app1_form.htmlからbtn_createボタンで返ってきた際の処理
#      edit   app1_form.htmlからbtn_editボタンで返ってきた際の処理

class App1View(View):

    template_app1_form  = 'app_folder/app1_form.html'
    template_app1_index = 'app_folder/app1_index.html'

    per_page_num      = common.per_page_num  # ページ内表示レコード数
    packnamedict      = common.packNameDict  # パックコードとパック名の対照dict
    card_categorydict = common.cardCategoryDict # カードカテゴリ番号とカテゴリ名の対照dict
    card_classdict    = common.cardClassDict    # カードクラス番号とクラス名の対照dict
    card_elementdict  = common.cardElementDict  # 属性番号と属性名の対照dict
    category_trainers = 2 # カードカテゴリ2はトレーナーズカード

    def get(self, request, *args, **kwargs):
        # Create_GET
        if (request.GET.get('create')):
            print("__checkIn__ app1view get CREATE IN")
            
            last_rcd = Card_summary.objects.order_by('all_card_id').last()
            create_id = last_rcd.all_card_id+1

            form = CardCreateForm(initial={"all_card_id":create_id})
            context = {
                'create_all_card_id':create_id,
                'form':form,
               }

            return render(request, self.template_app1_form, context=context)

        # Edit_GET
        elif (request.GET.get('edit')):
            print("__checkIn__ app1view get EDIT IN")
            edit_all_card_id = int(request.GET.get('edit'))
            form = CardUpdateForm(initial={"all_card_id":edit_all_card_id})

            result = get_object_or_404(Card_summary, all_card_id=edit_all_card_id)

            # form.fields['all_card_id'].initial   = result.all_card_id
            form.fields['name'].initial          = result.name
            form.fields['name_english'].initial  = result.name_english
            form.fields['pack_code'].initial     = result.pack_code
            form.fields['pack_card_id'].initial  = result.pack_card_id
            form.fields['card_category'].initial = result.card_category
            form.fields['card_class'].initial    = result.card_class
            form.fields['ex'].initial            = result.detail.ex
            if result.card_category == self.category_trainers:
                form.fields['element'].initial       = ""
            else:
                form.fields['element'].initial       = result.detail.element

            context = {
                'edit_all_card_id':edit_all_card_id,
                'form':form,
            }
            return render(request, self.template_app1_form, context)

        # Search (検索ボタン押下またはその続きで遷移してきた場合
        elif (request.GET.get('btn_search')):
            print("__checkIn__ app1view get SEARCH IN")

            # 入力データ受け取り
            input_id        = request.GET.get('input_id')
            input_name      = request.GET.get('input_name')
            input_pack_code = request.GET.get('input_pack_code')
            input_element       = request.GET.get('input_element')
            input_card_category = request.GET.get('input_card_category')
            input_card_class    = request.GET.get('input_card_class')
            input_ex            = request.GET.get('input_ex')

            # 並び替え条件はID,タイプ
            # sort_order = request.POST['sort_order'] # id,elementのいずれかが入る(カラム名)

            # データ取得
            result = Card_summary.objects.select_related("detail").order_by('all_card_id')

            if input_name:
                result = result.filter(name__icontains=input_name)
            if input_pack_code:
                result = result.filter(pack_code=input_pack_code)
            if input_element:
                result = result.filter(detail__element=input_element)
            if input_card_category:
                result = result.filter(card_category=input_card_category)
            if input_card_class:
                result = result.filter(card_class=input_card_class)
            if input_ex == "on":
                result = result.filter(detail__ex=True)

            # ページネーション
            paginator = Paginator(result, self.per_page_num, orphans=1, allow_empty_first_page=True)
            page_num = int(request.GET.get('page', 1))
            page_obj = paginator.page(page_num)

            # データ加工後表示
            records = []
            for r in page_obj:
                rcd = {}
                rcd['all_card_id'] = r.all_card_id
                rcd['name'] = r.name
                rcd['card_category'] = common.show_card_category(str(r.card_category))
                rcd['card_class'] = common.show_card_class(str(r.card_class))
                rcd['pack_name'] = common.packcode_To_Packname(r.pack_code)
                rcd['pack_card_id'] = r.pack_card_id
                rcd['ex'] = r.detail.ex
                # print("TEST")
                # print(r.detail.ex)
                rcd['rarity'] = r.rarity

                if rcd['card_category'] == 'ポケモン':
                    rcd['element'] = common.show_card_element(str(r.detail.element))
                elif rcd['card_category'] == 'トレーナーズ':
                    rcd['element'] = '-'
                    rcd['hp'] = '-' if rcd['card_class'] != 'かせき' else '40'

                records.append(rcd)

            context = {
                'packnamedict'      : self.packnamedict,      # 検索ボックス用
                'card_categorydict' : self.card_categorydict, # 検索ボックス用
                'card_classdict'    : self.card_classdict,    # 検索ボックス用
                'card_elementdict'  : self.card_elementdict,  # 検索ボックス用
                'records'  : records,
                'page_obj' : page_obj,

                }
            return render(request, self.template_app1_index, context=context)
        
        # Index (検索ボタン以外(searchのgetパラメータ無し)で遷移してきた場合‗初回など
        else:
            print("__checkIn__ app1view get INDEX IN")
            
            page_num = int(request.GET.get('page', 1))
            context = self.index_context(page_num)

            return render(request, self.template_app1_index, context=context)
    
    def post(self, request, *args, **kwargs):
        print("__checkIn__ app1view post IN")
    
        # Create_POST
        if "btn_create" in request.POST:
            print("__checkIn__ app1view post CREATE IN")
            
            last_rcd = Card_summary.objects.order_by('all_card_id').last()
            create_id = last_rcd.all_card_id+1

            form = CardCreateForm(request.POST,initial={"all_card_id":create_id})

            # バリデーション(新規作成時)
            if form.is_valid():
                print("__checkIn__ app1view post CREATE valid_Ok IN")

                pack_code     = form.cleaned_data.get('pack_code')
                pack_card_id  = int(form.cleaned_data.get('pack_card_id'))
                name          = form.cleaned_data.get('name')
                name_english  = form.cleaned_data.get('name_english')
                card_category = int(form.cleaned_data.get('card_category'))
                card_class    = int(form.cleaned_data.get('card_class'))
                element       = int(form.cleaned_data.get('element'))
                ex            = form.cleaned_data.get('ex')

                # DB登録処理
                with transaction.atomic():
                    # card_summary登録
                    # card_summary = Card_summary(**form.cleaned_data)
                    card_summary = Card_summary(
                        all_card_id   = create_id,
                        pack_code     = pack_code,
                        pack_card_id  = pack_card_id,
                        name          = name,
                        name_english  = name_english,
                        card_category = card_category,
                        card_class    = card_class,
                        rarity        = 0,
                    )
                    card_summary.save()

                    # card_detail登録
                    card_deatil = Card_detail(all_card=card_summary)
                    card_deatil.ex = ex
                    if element:# elementが0でないことを確認
                        card_deatil.element = element

                    card_deatil.save()

                page_num = int(request.GET.get('page', 1))
                context = self.index_context(page_num)
                return render(request, self.template_app1_index, context=context)
                # return render(request, self.template_app1_form, context={ 'form':form ,'create_all_card_id':create_id}) # バリデーションテスト用
        
            else:
                print("__checkIn__ app1view post CREATE valid_No IN")

                return render(request, self.template_app1_form, context={ 'form':form ,'create_all_card_id':create_id})
 
        # Edit_POST
        elif "btn_edit" in request.POST:
            print("__checkIn__ app1view post EDIT IN")
            edit_id = request.POST['all_card_id']

            form = CardUpdateForm(request.POST, initial={"all_card_id":edit_id})
            # form.fields['all_card_id'].initial   = edit_id

            # バリデーション(更新時)
            if form.is_valid():
                print("__checkIn__ app1view post EDIT valid_Ok IN")

                pack_code     = form.cleaned_data.get('pack_code')
                pack_card_id  = int(form.cleaned_data.get('pack_card_id'))
                name          = form.cleaned_data.get('name')
                name_english  = form.cleaned_data.get('name_english')
                card_category = int(form.cleaned_data.get('card_category'))
                card_class    = int(form.cleaned_data.get('card_class'))
                element       = int(form.cleaned_data.get('element'))
                ex            = form.cleaned_data.get('ex')

                # DB更新処理
                with transaction.atomic():
                    # card_summary登録
                    card_summary = get_object_or_404(Card_summary, all_card_id=edit_id)
                    card_summary.pack_code     = pack_code
                    card_summary.pack_card_id  = pack_card_id
                    card_summary.name          = name
                    card_summary.name_english  = name_english
                    card_summary.card_category = card_category
                    card_summary.card_class    = card_class
                    card_summary.save()

                    # card_detail登録
                    card_detail = get_object_or_404(Card_detail, all_card=edit_id)
                    card_detail.ex = ex
                    if element: # elementが0でないことを確認
                        card_detail.element = element
                    card_detail.save()

                page_num = int(request.GET.get('page', 1))
                context = self.index_context(page_num)
                return render(request, self.template_app1_index, context=context)
                # return render(request, self.template_app1_form, context={ 'form':form ,'edit_all_card_id':edit_id})  # バリデーションテスト用

            else:
                print("__checkIn__ app1view post EDIT valid_No IN")

                return render(request, self.template_app1_form, context={ 'form':form ,'edit_all_card_id':edit_id})
            
    # view共通関数
    # 
    def index_context(self, page_num):
            #  データ取得(全件)
            result = Card_summary.objects.select_related("detail").order_by('all_card_id')

            # ページネーション
            paginator = Paginator(result, self.per_page_num, orphans=1, allow_empty_first_page=True)
            page_obj = paginator.page(page_num)

            #DBデータを編集
            records = []
            for r in page_obj:
                rcd = {}
                rcd['all_card_id'] = r.all_card_id
                rcd['name'] = r.name
                rcd['card_category'] = common.show_card_category(str(r.card_category))
                rcd['card_class'] = common.show_card_class(str(r.card_class))
                rcd['pack_name'] = common.packcode_To_Packname(r.pack_code)
                rcd['pack_card_id'] = r.pack_card_id
                rcd['ex'] = r.detail.ex
                rcd['rarity'] = r.rarity

                if rcd['card_category'] == 'ポケモン':
                    rcd['element'] = common.show_card_element(str(r.detail.element))
                if rcd['card_category'] == 'トレーナーズ':
                    rcd['element'] = '-'
                    rcd['hp'] = '-' if rcd['card_class'] != 'かせき' else '40'

                records.append(rcd)

            context = {
                'packnamedict'      : self.packnamedict,
                'card_categorydict' : self.card_categorydict,
                'card_classdict'    : self.card_classdict,
                'card_elementdict'  : self.card_elementdict,
                'records'  : records,
                'page_obj' : page_obj,
                }
            return context

