import tnkeeh

text = tnkeeh._remove_special_chars('كيف حالكم ، يا أشقاء')
expected = 'كيف حالكم   يا أشقاء'

if text == expected:
    print('success')
else:
    print('failed')

text = tnkeeh._remove_special_chars('3 + 3', execluded_chars = ['+'])
expected = '3 + 3'

if text == expected:
    print('success')
else:
    print('failed')

text = tnkeeh._remove_special_chars('9/8/1770', execluded_chars = ['/'])
expected = '9/8/1770'

if text == expected:
    print('success')
else:
    print('failed')