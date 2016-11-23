from django.contrib.contenttypes.models import ContentType
from django.dispatch import Signal

from .models import Feed


feed_item = Signal(
    providing_args=['verb', 'action', 'target', 'affected_users'])


def new_feed_item(sender, **kwargs):
    kwargs.pop('signal', None)
    affected_users = kwargs.pop('affected_users', None)
    verb = kwargs.pop("verb")

    if affected_users is not None:
        for user in affected_users:
            new_item = Feed(
                verb=verb,
                sender_content_type=ContentType.objects.get_for_model(sender),
                sender_object_id=sender.id,
            )
            for option in ("target", "action"):
                try:
                    obj = kwargs[option]
                    if obj is not None:
                        setattr(new_item, "{0}_content_type".format(option),
                                ContentType.objects.get_for_model(obj))
                        setattr(new_item, "{0}_object_id".format(option),
                                obj.id)
                except:
                    pass
            new_item.save()
    else:
        new_item = Feed(
            verb=verb,
            sender_content_type=ContentType.objects.get_for_model(sender),
            sender_object_id=sender.id,
        )
        for option in ("target", "action"):
            obj = kwargs.pop(option, None)
            if obj is not None:
                setattr(new_item, "{0}_content_type".format(option),
                        ContentType.objects.get_for_model(obj))
                setattr(new_item, "{0}_object_id".format(option), obj.id)
        new_item.save()


feed_item.connect(new_feed_item)
