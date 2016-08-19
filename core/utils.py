def jwt_response_payload_handler(token, user, request, *args, **kwargs):
    data = {
        "token": token,
        "user": "{}".format(user.id),
        "userid": user.id,
        "active": user.is_active
    }
    return data
