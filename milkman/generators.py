import datetime
import errno
import os
import random
import string
import sys
import uuid

from django.core.files.storage import DefaultStorage
from django.utils import timezone

from PIL import Image, ImageDraw


DEFAULT_STRING_LENGTH = 8
DECIMAL_TEMPLATE = "%%d.%%0%dd"
EMAIL_TEMPLATE = "%s%%d@%s"
DATETIME_TEMPLATE = "%s %d:%d"


def loop(func):
    def loop_generator(*args, **kwargs):
        while 1:
            yield func(*args, **kwargs)
    return loop_generator


def sequence(func):
    def sequence_generator(*args, **kwargs):
        i = 0
        while 1:
            i += 1
            yield func(i, *args, **kwargs)
    return sequence_generator


def default_gen_maker(field):
    return loop(lambda: '')


def random_choice_iterator(choices=[''], size=1):
    for i in range(0, size):
        yield random.choice(choices)


def random_string_maker(field, chars=None):
    max_length = getattr(field, 'max_length', DEFAULT_STRING_LENGTH)
    return loop(lambda: random_string(max_length, chars))


def random_string(max_length=None, chars=None):
    if max_length is None:
        max_length = DEFAULT_STRING_LENGTH
    if chars is None:
        chars = (string.ascii_letters + string.digits)
    i = random_choice_iterator(chars, max_length)
    return ''.join(x for x in i)


def random_boolean_maker(field=None):
    return loop(lambda: random.choice((True, False)))


def random_null_boolean_maker(field=None):
    return loop(lambda: random.choice((None, True, False)))


def random_datetime(field):
    return loop(lambda: timezone.now() - datetime.timedelta(days=random.randint(0, 300)))


def random_date(field):
    return loop(lambda: (timezone.now() - datetime.timedelta(days=random.randint(0, 300)).date))


def random_date_string():
    y = random.randint(1900, 2020)
    m = random.randint(1, 12)
    d = random.randint(1, 28)
    return str(datetime.date(y, m, d))


def random_time_string():
    h = random.randint(0, 23)
    m = random.randint(0, 59)
    s = random.randint(0, 59)
    return str(datetime.time(h, m, s))


def random_date_string_maker(field):
    return loop(random_date_string)


def random_datetime_string():
    h = random.randint(1, 12)
    m = random.randint(0, 59)
    result = DATETIME_TEMPLATE % (random_date_string(), h, m)
    return result


def random_datetime_string_maker(field):
    return loop(random_datetime_string)


def random_decimal_maker(field):
    x = pow(10, field.max_digits - field.decimal_places) - 1
    y = pow(10, field.decimal_places) - 1
    fmt_string = DECIMAL_TEMPLATE % field.decimal_places

    def gen():
        return fmt_string % (random.randint(1, x), random.randint(1, y))

    return loop(gen)


def email_generator(addr, domain):
    template = EMAIL_TEMPLATE % (addr, domain)

    def email_gen_maker(field):
        return sequence(lambda i: template % i)

    return email_gen_maker


def random_integer_maker(field, low=-2147483647, high=2147483647):
    return loop(lambda: random.randint(low, high))


def random_big_integer_maker(field):
    return random_integer_maker(
        field,
        low=-9223372036854775808,
        high=9223372036854775807
    )


def random_small_integer_maker(field):
    return random_integer_maker(field, low=-1, high=1)


def random_small_positive_integer_maker(field):
    return random_integer_maker(field, low=0, high=1)


def random_positive_integer_maker(field):
    return random_integer_maker(field, low=0)


def random_float_maker(field):
    return loop(lambda: random_float())


def random_auto_field_maker(field):
    return loop(lambda: random.randint(1, 2147483647))


def random_float():
    return random.uniform(sys.float_info.min, sys.float_info.max)


def random_ipaddress_maker(field):
    return loop(lambda: "%s.%s.%s.%s" % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255))
    )


def random_comma_seperated_integer(max_length):
    if max_length is None:
        max_length = DEFAULT_STRING_LENGTH

    max_length = (int)(max_length / 2)
    chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    return reduce(
        lambda x, y: "%s,%s" % (x, y),
        random_string(max_length, chars)
    ).lstrip(',')


def random_comma_seperated_integer_maker(field):
    max_length = getattr(field, 'max_length', DEFAULT_STRING_LENGTH)
    return loop(lambda: random_comma_seperated_integer(max_length))


def random_time_string_maker(field):
    return loop(lambda: random_time_string())


def random_rgb():
    return (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )


def random_image(field):

    color1 = random_rgb()
    color2 = random_rgb()
    color3 = random_rgb()
    color4 = random_rgb()
    size = (random.randint(300, 900), random.randint(300, 900))

    im = Image.new("RGB", size)  # create the image
    draw = ImageDraw.Draw(im)    # create a drawing object that is
    draw.rectangle(
        [(0, 0), ((size[0] / 2), (size[1] / 2))],
        fill=color1
    )
    draw.rectangle(
        [((size[0] / 2), 0), ((size[1] / 2), size[0])],
        fill=color2
    )
    draw.rectangle(
        [(0, (size[1] / 2)), ((size[0] / 2), size[1])],
        fill=color3
    )
    draw.rectangle(
        [((size[0] / 2), (size[1] / 2)), (size[0], size[1])],
        fill=color4
    )

    filename = "%s.png" % uuid.uuid4().hex[:10]
    filename = field.generate_filename(None, filename)
    storage = DefaultStorage()
    full_path = storage.path(filename)
    directory = os.path.dirname(full_path)

    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    filehandle = storage.open(filename, mode="w")
    im.save(filehandle, "PNG")

    filehandle.close()

    return filename  # and we"re done!


def random_image_maker(field):
    return loop(lambda: random_image(field))
