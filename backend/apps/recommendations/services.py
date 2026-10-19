from . import schema


def top_recommendations(user, limit=0):
    return schema.top_for_user(user.pk)[:limit]
