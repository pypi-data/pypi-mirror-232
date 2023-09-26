import datetime
import time
from typing import Optional
from mongoengine import *
from operator import itemgetter


def handler(event):
    """Signal decorator to allow use of callback functions as class decorators."""

    def decorator(fn):
        def apply(cls):
            event.connect(fn, sender=cls)
            return cls

        fn.apply = apply
        return fn

    return decorator


@handler(signals.pre_save)
def update_date_tracking(sender, document):
    document.update_date = datetime.datetime.utcnow()


class ListQuerySet(QuerySet):
    def get_items(self, search: Optional[str], sort_by: str = 'id', sort_desc: bool = False, skip: int = 0, limit: int = 10):
        query = self.search_text(search).order_by(
            f"{'-' if sort_desc else '+'}{sort_by}")[skip:limit]
        return query.count(), query


class ItemFrequenciesQuerySet(QuerySet):
    def get_field_frequencies(self, field: str, search: Optional[str], sort_desc: bool = True, skip: int = 0, limit: int = 100):
        frqus = self.item_frequencies(field)
        if search is not None and len(search) > 0:
            frqus = {k: v for k, v in frqus.items() if search in str(k)}
        frqus_list = sorted(frqus.items(), key=itemgetter(1),
                            reverse=sort_desc)[skip:limit]
        return len(frqus_list), frqus_list


class ListableDocument(Document):
    meta: {'allow_inheritance': True, 'queryset_class': ListQuerySet}

    @queryset_manager
    def get_items(doc_cls, queryset: QuerySet, search: Optional[str], sort_by: str = 'id', sort_desc: bool = False, skip: int = 0, limit: int = 100):
        return queryset.get_items(search, sort_by, sort_desc, skip, limit)


class Role(ListableDocument):
    meta: {'allow_inheritance': True, 'queryset_class': ItemFrequenciesQuerySet}

    name = StringField(required=True)
    scopes = ListField(StringField())

    @queryset_manager
    def get_scopes(doc_cls, queryset: QuerySet, search: Optional[str], sort_desc: bool = True, skip: int = 0, limit: int = 100):
        queryset.get_field_frequencies(
            'scopes', search, sort_desc, skip, limit)
