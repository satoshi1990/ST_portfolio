from django.db import models

# Create your models here.
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
    
# カード詳細テーブルから
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

