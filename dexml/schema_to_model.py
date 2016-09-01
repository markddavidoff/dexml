from abc import ABCMeta, abstractmethod
from datetime import datetime
import dexml as dexml
import re


class XSD_DeXML_FieldModel:
    __metaclass__ = ABCMeta

    def __init__(self, xsd_element):
        self.xsd_element = xsd_element

    @property
    def nullable(self):
        self.xsd_element

def strptime_ISO_8601(time_str):
    """

    An implementation of parsing ISO_8601 strings that should work on all
    systems.

    ISO_8601 is defined in RFC 3339
    Because RFC 3339 allows many variations of optional colons and dashes
    being present, basically CCYY-MM-DDThh:mm:ss[Z|(+|-)hh:mm].
    If you want to use strptime, you need to strip out those variations first.

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

class deXML_DateTime(dexml.fields.Value):
    """
    This datatype describes instances identified by the combination of a date
    and a time. Its value space is described as a combination of date and
    time of day in Chapter 5.4 of ISO 8601. Its lexical space is the
    extended format:

    [-]CCYY-MM-DDThh:mm:ss[Z|(+|-)hh:mm]
    """
    def parse_value(self, val):
        # wtf is negative datetime? the xml spec specifies an optional [-]
        # but lets just ignore that for now...

        return strptime_ISO_8601(val if val[0] == '-' else val[1:])


class FieldFactory(object):
    """
    Create dexml Field Models based on xsd elements
    """
    _type_map ={
        'xs:string': dexml.fields.String,
        'xs:long': dexml.fields.Integer,
        'xs:int': dexml.fields.Integer,
        'xs:boolean': dexml.fields.Boolean,
        'xs:dateTime': deXML_DateTime,
        'xs:decimal': dexml.fields.Float
    }

    def __init__(self, custom_type_mappings):
        """
        :param custom_type_mappings: dict of {element type: field model class}
        mappings to map element types (type='x' attribute) to field models.
        default types (e.g. xs:string) are already mapped, if you wish to
        add custom mappings for them you can provide them in this dict to
        override the defaults
        """

        self._type_map.update(custom_type_mappings)

    def from_xsd_element(self, xsd_element):
        if 'type' not in xsd_element.keys():
            raise ValueError('FieldFactory: XSD element provided does not have a "type" attribute')
        type_attr = xsd_element.get('type')
        return