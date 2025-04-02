from django.shortcuts import render, get_object_or_404
from django.views import View
from django.db import transaction
from django.core.paginator import Paginator
from .models import Card_summary, Card_detail, Pokedex
from .forms import CardCreateForm, CardUpdateForm
from app_folder.modules import common
import pandas as pd, glob
import math

# top ポートフォリオにかかわる初期設定周りで、その他便利そうなツールはこの画面に追加していく
# 
# Top1View class内分岐
# get 
#   DB_init_pokedex top_page.htmlから[btn_DBInit_pokedex]ボタンで返ってきた際の処理 DBの初期登録を行う
#   DB_init_card    top_page.htmlから[btn_DBInit_card]   ボタンで返ってきた際の処理 DBの初期登録を行う
# 　fetchNameE　     top_page.htmlから[btn_fetchNameE]ボタンで返ってきた際の処理 英語名のないレコードにpokedex テーブルから英語名を登録
# 　DB_reset 　      top_page.htmlから[btn_tables_reset]ボタンで返ってきた際の処理 アプリ内に関するレコードを全削除し,initialを再度実行できるようにする

class TopView(View):
    category_pokemon = 1 # カードカテゴリ1はポケモン
    ok_msg = [
        "pokedexテーブルの初期登録が完了しました!",
        "カード情報の初期登録が完了しました!",
        "レコードをすべて削除しました(1~3の再登録が可能となりました)",
    ]
    ng_msg = [
        "テーブルの初期登録は必要ありません",
        "現在、取得できるポケモン英語名はありません",
    ]

    def get(self, request, *args, **kwargs):
        # DBinit_pokedex_GET
        if (request.GET.get('btn_DBInit_pokedex')):
            print("__checkIn__ topview get DBinit_pokedex IN")
            context = {}

            file_pokedex = glob.glob(common.filedir_pokedex)
            csv_data_pokedex = pd.read_csv(file_pokedex[0], index_col=None, header=0)

            # pokedexのレコード数とcsvのレコード数を比べ、csvの方が多いときに実行する-後で状態保存テーブルから状態をとってきて初回だけ登録できる仕様に変える
            csv_pokedex_num = len(csv_data_pokedex)
            db_pokedex_num = Pokedex.objects.all().count()

            # DB追加処理
            if (csv_pokedex_num > db_pokedex_num):
                print("__checkIn__ topview get DBinit_pokedex try-create")
                with transaction.atomic():
                    pokedex_items=[]
                    for row in csv_data_pokedex.itertuples():
                        tmp = Pokedex(
                            pokedex_id=row.pokedex_id,
                            name_j=row.name_j,
                            name_e=row.name_e,
                        )
                        pokedex_items.append(tmp)
                    Pokedex.objects.bulk_create(pokedex_items)
                    context['complete_text'] = self.ok_msg[0]
            else:
                print("__checkIn__ topview get DBinit_pokedex non-create")
                context['ng_text'] = self.ng_msg[0]


            return render(request, 'app_folder/top_page.html', context=context)
        
        # DBinit_card_GET
        elif (request.GET.get('btn_DBInit_card')):
            print("__checkIn__ topview get DBinit_card IN")            
            # csvをsummary,detailに登録する
            context = {}

            file_card_sumarry = glob.glob(common.filedir_card_summary)
            file_card_detail  = glob.glob(common.filedir_card_detail)

            csv_data_card_summary = pd.read_csv(file_card_sumarry[0], index_col=None, header=0)
            csv_data_card_detail  = pd.read_csv(file_card_detail[0], index_col=None, header=0)

            csv_card_summary_num = len(csv_data_card_summary)
            db_card_summary_num = Card_summary.objects.all().count()

            # DB追加処理
            if (csv_card_summary_num > db_card_summary_num):
                print("__checkIn__ topview get DBinit_card_summary/detail try-create")
                with transaction.atomic():
                    if len(csv_data_card_summary) == len(csv_data_card_detail):# sumarryとdetailで同じ数になることを担保
                        # card_summaryリスト作成
                        card_summary_items=[]
                        for row in csv_data_card_summary.itertuples():
                            card_summary = Card_summary(
                                all_card_id   = row.all_card_id,
                                pack_code     = row.pack_code,
                                pack_card_id  = row.pack_card_id,
                                name          = row.name,
                                name_english  = "",
                                card_category = row.card_category,
                                card_class    = row.card_class,
                                rarity        = 0,
                            )
                            card_summary_items.append(card_summary)

                        Card_summary.objects.bulk_create(card_summary_items)

                        # card_detailリスト作成
                        card_detail_items=[]
                        for row in csv_data_card_detail.itertuples():
                            card_summary = Card_summary.objects.get(all_card_id=row.all_card)
                            card_detail = Card_detail(
                                all_card=card_summary,
                                ex = row.ex
                            )
                            if math.isnan(row.element)==False:# elementが0でないことを確認
                                card_detail.element = row.element
                            card_detail_items.append(card_detail)

                        Card_detail.objects.bulk_create(card_detail_items)

                        context['complete_text'] = self.ok_msg[1]
                    print("card create complete")
                    # elif:

            else:
                print("__checkIn__ topview get DBinit_pokedex non-create")
                context['ng_text'] = self.ng_msg[0]

            return render(request, 'app_folder/top_page.html', context=context)

        # fetchNameE_GET
        elif (request.GET.get('btn_fetchNameE')):
            print("__checkIn__ topview get fetchNameE IN")
            context = {}

            nameELess_Rcds = Card_summary.objects.order_by('all_card_id')
            nameELess_Rcds = nameELess_Rcds.filter(card_category = self.category_pokemon) 
            nameELess_Rcds = nameELess_Rcds.filter(name_english = "")
            num_rcds = len(nameELess_Rcds)

            # DB[card_summary.name_english] 更新処理
            if num_rcds > 0:
                print("__checkIn__ topview get fetchNameE try-update")
                # DB更新処理
                with transaction.atomic():
                    nameE_updateCount = 0
                    for i in range(num_rcds):
                        search_name = nameELess_Rcds[i].name
                        if "ex" in search_name:
                            search_name = search_name.replace('ex','').strip()
                        if "パルデア" in search_name:
                            search_name = search_name.replace('パルデア','').strip()

                        # 1.mysqlでカラカラ、ガラガラが同一とみなされてしまうため、回避策
                        # 2.また第8世代以降の英語名データがcsvにないため、pokedexにもない。カードサマリから得た検索ワードにヒットするレコードがpokedexテーブルに1あることを担保している
                        filter_count = Pokedex.objects.filter(name_j=search_name).count()   
                        if filter_count == 1:
                            pokedex = Pokedex.objects.get(name_j=search_name)
                            nameELess_Rcds[i].name_english = pokedex.name_e

                            nameE_updateCount = nameE_updateCount+1

                    Card_summary.objects.bulk_update(nameELess_Rcds, fields=["name_english"])
                    if nameE_updateCount == 0:
                        context['complete_text'] = self.ng_msg[1]
                    else:
                        context['complete_text'] = str(nameE_updateCount)+"件のポケモン英語名が新規取得されました!"
            else:
                print("__checkIn__ topview get fetchNameE non-Update")
                context['ng_text'] = self.ng_msg[1]

            return render(request, 'app_folder/top_page.html',context=context)

        # DB_reset_GET
        elif (request.GET.get('btn_tables_reset')):
            print("__checkIn__ topview get btn_tables_reset ")
            context = {}

            # アプリ内に関係するレコードを全削除し,リセットする処理
            with transaction.atomic():
                Card_detail.objects.all().delete()
                Card_summary.objects.all().delete()
                Pokedex.objects.all().delete()

            context['complete_text'] = self.ok_msg[2]
            return render(request, 'app_folder/top_page.html',context=context)

        # top 初期表示時 
        else:
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
#      delete modal_predelete.htmlからbtn_deleteで返ってきた際の処理

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

            # データ加工
            records = self.record_processing(page_obj)

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
             
        # Delete_POST
        elif "btn_delete" in request.POST:
            print("__checkIn__ app1view post EDIT IN")
            delete_id = request.POST['delete_id']

            delete_executed_flg = False
            # DB削除処理
            with transaction.atomic():
                # card_summary登録
                card_summary = get_object_or_404(Card_summary, all_card_id=delete_id)
                card_summary.delete() 
                # ondelete_cascade設定によりdetail tableのレコードも削除される
                delete_executed_flg = True

            page_num = 1
            context = self.index_context(page_num)
            context["delete_executed_flg"] = delete_executed_flg

            return render(request, self.template_app1_index, context=context)
            
    #--------------------------------
    # view内共通関数
    #--------------------------------

    # 全件取得のcontextを返す
    def index_context(self, page_num):
        #  データ取得(全件)
        result = Card_summary.objects.select_related("detail").order_by('all_card_id')

        # ページネーション
        paginator = Paginator(result, self.per_page_num, orphans=1, allow_empty_first_page=True)
        page_obj = paginator.page(page_num)

        # page_obj を Template用dataに加工/
        records = self.record_processing(page_obj)

        context = {
            'packnamedict'      : self.packnamedict,
            'card_categorydict' : self.card_categorydict,
            'card_classdict'    : self.card_classdict,
            'card_elementdict'  : self.card_elementdict,
            'records'  : records,
            'page_obj' : page_obj,
            }
        
        return context

    # page_objectをTemplate用データに加工
    # Template内でsqlクエリが回らないよう、このタイミングで取得データにアクセスしておく(N+1予防)
    def record_processing(self,page_obj):
        records = []
        for r in page_obj:
            rcd = {}
            rcd['all_card_id'] = r.all_card_id
            rcd['name'] = r.name
            rcd['name_english'] = r.name_english
            rcd['card_category'] = common.show_card_category(str(r.card_category))
            rcd['card_class']    = common.show_card_class(str(r.card_class))
            rcd['pack_name']     = common.packcode_To_Packname(r.pack_code)
            rcd['pack_card_id']  = r.pack_card_id
            rcd['rarity']        = r.rarity

            rcd['hp'] = r.detail.hp
            rcd['ability_name'] = r.detail.ability_name
            rcd['ability_txt'] = r.detail.ability_txt
            rcd['effect1_name'] = r.detail.effect1_name
            rcd['effect1_dmg'] = r.detail.effect1_dmg
            rcd['effect1_txt'] = r.detail.effect1_txt
            rcd['effect2_name'] = r.detail.effect2_name
            rcd['effect2_dmg'] = r.detail.effect2_dmg
            rcd['effect2_txt'] = r.detail.effect2_txt
            rcd['escape_cost'] = r.detail.escape_cost
            rcd['ex'] = r.detail.ex

            if rcd['card_category'] == 'ポケモン':
                rcd['element'] = common.show_card_element(str(r.detail.element))
                rcd['weakness'] = common.show_card_element(str(r.detail.weakness))
            if rcd['card_category'] == 'トレーナーズ':
                rcd['element'] = '-'
                rcd['hp'] = '-' if rcd['card_class'] != 'かせき' else '40'
            records.append(rcd)
        
        return records


class App2View(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'app_folder/app2_top.html')