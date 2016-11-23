from django.contrib.contenttypes.models import ContentType
from django.dispatch import Signal

from .models import Notification


notify = Signal(
    providing_args=['recipient', 'verb', 'action', 'target', 'affected_users'])


def new_notification(sender, **kwargs):
    kwargs.pop('signal', None)
    affected_users = kwargs.pop('affected_users', None)
    recipient = kwargs.pop("recipient")
    verb = kwargs.pop("verb")

    if recipient != sender:
        if affected_users is not None:
            for user in affected_users:
                new_note = Notification(
                    recipient=user,
                    verb=verb,
                    sender_content_type=ContentType.objects.get_for_model(sender),
                    sender_object_id=sender.id,
                )
                for option in ("target", "action"):
                    try:
                        obj = kwargs[option]
                        if obj is not None:
                            setattr(new_note, "{}_content_type".format(option),
                                    ContentType.objects.get_for_model(obj))
                            setattr(new_note, "{}_object_id".format(option),
                                    obj.id)
                    except:
                        pass
                new_note.save()
        else:
            new_note = Notification(
                recipient=recipient,
                verb=verb,
                sender_content_type=ContentType.objects.get_for_model(sender),
                sender_object_id=sender.id,
            )
            for option in ("target", "action"):
                obj = kwargs.pop(option, None)
                if obj is not None:
                    setattr(new_note, "{0}_content_type".format(option),
                            ContentType.objects.get_for_model(obj))
                    setattr(new_note, "{0}_object_id".format(option), obj.id)
            new_note.save()


notify.connect(new_notification)
