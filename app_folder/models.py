from django.db import models

# カード概要テーブル
class Card_summary(models.Model):
    class Meta:
        db_table = 'app1_card_summary'
        ordering = ['all_card_id']
        verbose_name_plural = 'card_summary'
        constraints = [
            models.UniqueConstraint(
                fields=["pack_code", "pack_card_id"],
                name="pack_unique_id",
            ),
        ]

    all_card_id   = models.IntegerField('全体カードID',null=False, blank=False, primary_key=True)
    pack_code     = models.CharField('パックコード', max_length=10, null=True, blank=True)
    pack_card_id  = models.IntegerField('パック内カードID', null=True, blank=True)
    name          = models.CharField('カード名', max_length=50, null=True, blank=False)
    name_english  = models.CharField('英語名', max_length=50, null=True, blank=True)
    card_category = models.IntegerField('カードカテゴリ', null=True, blank=True)
    card_class    = models.IntegerField('カードクラス', null=True, blank=True)
    rarity        = models.IntegerField('レア度', null=True, blank=True)

    def __str__(self):
        ans = str(self.all_card_id) + ' / ' + self.name
        return ans
    
# カード詳細テーブル
class Card_detail(models.Model):
    class Meta:
        db_table = 'app1_card_detail'
        # ordering = ['all_card']
        verbose_name_plural = 'card_detail'

    all_card     = models.OneToOneField(Card_summary, on_delete=models.CASCADE, related_name='detail', null=True)
    # card_summary = models.OneToOneField(Card_summary, on_delete=models.CASCADE) #こちらが本来の形?
    element      = models.IntegerField('タイプ',null=True, blank=True)
    hp           = models.IntegerField('HP',null=True, blank=True)
    ability_name = models.CharField('特性名前', max_length=50, null=True, blank=True)
    ability_txt  = models.CharField('特性効果文', max_length=255 ,null=True, blank=True)
    effect1_name = models.CharField('技1名前', max_length=50,null=True, blank=True)
    effect1_dmg  = models.IntegerField('技1ダメージ',null=True, blank=True)
    effect1_txt  = models.CharField('技1効果文', max_length=255 ,null=True, blank=True)
    effect2_name = models.CharField('技2名前', max_length=50,null=True, blank=True)
    effect2_dmg  = models.IntegerField('技2ダメージ',null=True, blank=True)
    effect2_txt  = models.CharField('技2効果文', max_length=255 ,null=True, blank=True)
    weakness     = models.IntegerField('弱点',null=True, blank=True)
    escape_cost  = models.IntegerField('逃げる',null=True, blank=True)
    ex           = models.BooleanField('ex', null=True, blank=True) #, default=False



# pokedex テーブル
class Pokedex(models.Model):
    class Meta:
        db_table = 'app1_pokedex'
        ordering = ['pokedex_id']
        verbose_name_plural = 'pokedex'

    pokedex_id    = models.IntegerField('全国ポケモン図鑑ID', null=False, blank=False, primary_key=True)
    name_j        = models.CharField('ポケモン名_日本語', max_length=50, null=True, blank=False)
    name_e        = models.CharField('ポケモン名_英語', max_length=50, null=True, blank=True)

    def __str__(self):
        ans = str(self.pokedex_id) + ' / ' + self.name_j
        return ans
    
# common テーブル
class Common_ST(models.Model):
    class Meta:
        db_table = 'ST_common'
        ordering = ['id']
        verbose_name_plural = 'common_STPortfolio'

    id           = models.IntegerField('ID', null=False, blank=False, primary_key=True)
    key          = models.CharField('キー', max_length=50, null=True, blank=True)
    value        = models.CharField('値', max_length=50, null=True, blank=True)

    def __str__(self):
        ans = str(self.id) + ' / ' + self.key + ' : '+ self.value 
        return ans
    