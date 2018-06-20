import string

USER_ID = 0
BEGIN_DAY = '7:00'
END_DAY = '22:00'

def check_input(input_string):
    '''проверка на неправильные символы при вводе'''
    allowed_characters = string.ascii_lowercase + string.ascii_uppercase + string.digits + '-' + '_'
    return bool(set(input_string).difference(allowed_characters)) # True если есть лищние символы

