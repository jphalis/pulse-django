def jwt_response_payload_handler(token, user=None, request=None):
    return {
        "token": token,
        "user": str(user.email),
        "userid": str(user.id),
        "active": user.is_active
    }


def readable_number(value, short=False):
    """
    Returns an abbreviated value for numbers over 1,000.
    """
    powers = [10 ** x for x in (3, 6, 9, 12, 18)]
    human_powers = ('thousand', 'million', 'billion', 'trillion',
                    'quadrillion')
    human_powers_short = ('k', 'm', 'b', 'T', 'QD')

    try:
        value = int(value)
    except (TypeError, ValueError):
        return value

    if value < powers[0]:
        return str(value)
    for ordinal, power in enumerate(powers[1:], 1):
        if value < power:
            chopped = value / float(powers[ordinal - 1])
            chopped = format(chopped, '.1f')
            if not short:
                return '{}{}'.format(chopped, human_powers[ordinal - 1])
            return '{}{}'.format(chopped, human_powers_short[ordinal - 1])
