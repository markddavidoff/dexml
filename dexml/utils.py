"""

dexml.utils:  misc utils
=====================================================

"""

def strptime_ISO_8601(time_str):
    """

    An implementation of parsing ISO_8601 strings that should work on all
    systems.

    ISO_8601 is defined in RFC 3339
    Because RFC 3339 allows many variations of optional colons and dashes
    being present, basically CCYY-MM-DDThh:mm:ss[Z|(+|-)hh:mm].
    If you want to use strptime, you need to strip out those variations first.

    __author__ = "markddavidoff"

    :param time_str: ISO_8601 format string
    :return: utc timezone datetime.dateimte object
    """

    # this regex removes all colons and all
    # dashes EXCEPT for the dash indicating + or - utc offset for the timezone
    conformed_timestamp = re.sub(r"[:]|([-](?!((\d{2}[:]\d{2})|(\d{4}))$))", '', time_str)

    # split on the offset to remove it. use a capture group to keep the delimiter
    split_timestamp = re.split(r"[+|-]",conformed_timestamp)
    main_timestamp = split_timestamp[0]
    if len(split_timestamp) == 3:
        sign = split_timestamp[1]
        offset = split_timestamp[2]
    else:
        sign = None
        offset = None

    # manually do the offset here as
    # Python <3 did not consistently support %z
    # generate the datetime object without the offset at UTC time

    output_datetime = datetime.datetime.strptime(main_timestamp +"Z", "%Y%m%dT%H%M%S.%fZ" )
    if offset:
        # create timedelta based on offset
        offset_delta = datetime.timedelta(hours=int(sign+offset[:-2]), minutes=int(sign+offset[-2:]))
        # offset datetime with timedelta
        output_datetime = output_datetime + offset_delta

    return output_datetime