from django.conf import settings


### 定数 ###
 
# ページ内表示レコード数
per_page_num = 50

# 各データセットディレクトリ
filedir_pokedex = "./dataset/pokedex/*.csv" 
filedir_card_summary = "./dataset/card_summary/*.csv" 
filedir_card_detail = "./dataset/card_detail/*.csv" 

# パックコードとパック名の対照
packNameDict = {
    'A1common' : '最強の遺伝子 共通',
    'A1m' : '最強の遺伝子 ミュウツー',
    'A1r' : '最強の遺伝子 リザードン',
    'A1p' : '最強の遺伝子 ピカチュウ',
    'promoA' : 'プロモーションA',
    'A1a' : '幻のいる島',
    'A2common' : '時空の激闘 共通',
    'A2d' : '時空の激闘 ディアルガ',
    'A2p' : '時空の激闘 パルキア',
    'A2a' : '超克の光',
    'A2b' : 'シャイニングハイ',
}

# カードカテゴリ番号とカテゴリ名の対照
cardCategoryDict = {
    '1' : 'ポケモン',
    '2' : 'トレーナーズ',
}

# カードクラス番号とクラス名の対照
cardClassDict = {
    '1' : 'たね',
    '2' : '1進化',
    '3' : '2進化',
    '4' : 'サポート',
    '5' : 'グッズ',
    '6' : 'かせき',
}

# 属性番号と属性名の対照
cardElementDict = {
    "1" : "草",
    "2" : "炎",
    "3" : "水",
    "4" : "雷",
    "5" : "超",
    "6" : "闘",
    "7" : "悪",
    "8" : "鋼",
    "9" : "ドラゴン",
    "10" : "無",
}

### メソッド ###

# パックコードを渡すとパック名を返す
def packcode_To_Packname(packcode):
    ans =''
    if packcode in packNameDict :
        ans = packNameDict[packcode]
    else:
        ans = 'ERR'

    return (ans)

# カードカテゴリ番号を渡すとカテゴリ名を返す
def show_card_category(num):
    ans =''
    if num in cardCategoryDict :
        ans = cardCategoryDict[num]
    else:
        ans = 'ERR'

    return (ans)

# カードクラス番号を渡すとクラス名を返す
def show_card_class(num):
    ans =''
    if num in cardClassDict :
        ans = cardClassDict[num]
    else:
        ans = 'ERR'

    return (ans)

# 属性番号を渡すと属性名を返す
def show_card_element(num):
    ans =''
    if num in cardElementDict :
        ans = cardElementDict[num]
    else:
        ans = 'ERR'

    return (ans)

