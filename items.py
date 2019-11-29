from mongoengine import *
from datetime import datetime
import random

class Proxy(Document):
    proxy_url = StringField(required=True)
    last_used = DateTimeField(required=True, default=datetime.utcnow)
    is_using = BooleanField(required=True, default=False)
    dead = BooleanField(required=True, default=False)

    def __repr__(self):
        return f"{self.proxy_url} used at {self.last_used}"
    def __str__(self):
        return self.proxy_url


class Key(Document):
    kw = StringField(required=True)
    scraped = BooleanField(required=True)

    def __repr__(self):
        return self.kw
    def __str__(self):
        return self.kw

class GoogleResult(Document):
    keyword = StringField(required=True)
    html = StringField(required=True)
    time = StringField(required=True)

    def __repr__(self):
        return self.keyword
    def __str__(self):
        return self.keyword

class Storage:
    def __init__(self):
        self.db = connect('crawl_storage', username='crawlstorage', password='mangto535')

    def add_kw(self, kw):
        return Key(kw=kw, scraped=False).save()

    def get_10(self, string=False):
        kw_obj = Key.objects(scraped=False)[:10]
        for key in kw_obj:
            key.update(scraped=True)
        if string:
            return [x.kw for x in kw_obj]
        return kw_obj
    
    def get_all_queue(self):
        kw_obj = Key.objects(scraped=False)
        return kw_obj

    def change_status(self, kw, scraped=True):
        return Key.objects(kw=kw).first().update(scraped=scraped)

    def empty(self):
        indicator = Key.objects(scraped=False).first()
        if indicator:
            return True
        else:
            return False

# PROXIES
    def get_proxy(self):
        """
        Get alive, non-abused proxy from DB, also marks it "is_using"
        """
        current_proxy = random.choice(Proxy.objects(is_using=False, dead=False))
        if self.proxy_usable_check(current_proxy):
            current_proxy.update(is_using=True)
            return current_proxy
        else:
            current_proxy.update(is_using=True)
            return self.get_proxy()

    def proxy_usable_check(self, proxy_instance):
        if (datetime.utcnow()-proxy_instance.last_used).seconds > 5:
            return True
        return False

    def mark_proxy_last_used(self, proxy_instance):
        return proxy_instance.update(last_used=datetime.utcnow())
    def mark_proxy_idle(self, proxy_instance):
        return proxy_instance.update(is_using=False)
    def mark_proxy_dead(self, proxy_instance):
        return proxy_instance.update(dead=True)

# END PROXIES

class Keyword:
    def __init__(self, keyword, url_template, proxy):
        self.keyword = keyword
        self.url = url_template.format(keyword)
        self.proxy = proxy
        self.scraped_result = ''

    def __repr__(self):
        return self.keyword
    def __str__(self):
        return self.keyword
        
class KeywordBatch:
    def __init__(self, kwlist, url_template, proxy):
        self.keyword_list = self.gen_kwlist(kwlist, url_template, proxy)
        self.proxy = proxy
    
    @staticmethod
    def gen_kwlist(kwlist, url_template, proxy):
        for kw in kwlist:
            yield Keyword(kw,url_template,proxy)

    def get_keywords(self):
        return self.keyword_list
