'''
Author: xinyan
Date: 2024-03-08 21:20:04
LastEditors: xinyan
LastEditTime: 2024-03-08 21:22:00
Description: file content
'''
import tablepic as tp

# -- Test complex_table_pic
font_path = '/Users/xinyan/Library/Fonts/sarasa-mono-sc-regular.ttf'
font_bold_path = '/Users/xinyan/Library/Fonts/UbuntuMono-BI.ttf'
title_list = [
    {'content': 'This is a main title', 'padding_b': 0, 'font_path': font_bold_path},
    {'content': 'Second title - Date: 2024.03.05', 'font_size': 20, 'align': 'right', 'padding_t':30, 'padding_b':0, 'x_offset': -30},
]

footnote_list = [
    {'content': 'This is first footnote.', 'padding_t': 0, 'padding_b': 10},
    {'content': 'This is second footnote.', 'font_size': 15, 'font_path': font_bold_path},
]
cell_dict = {
    'content': [f'Main Content{i}\nnew line' if i==12 else f'Main Content{i}' for i in range(20) ],
    'back_color': {'r0': '#AC3456'},
    'fore_color': {'r0': '#FFFFFF', 12: '#FF0000'},
    'font_path': {'r4': font_bold_path, 12: font_bold_path},
    'font_size': {12: 30}
}
cell_merge_dict = {'0-0':[0,1], '1-1':[1,0], '3-2':[0,1]}
img_path = './pic/demo_complex_table.jpg'
tp.complex_table_pic(5, 4, title_list, cell_dict, font_path, img_path, footnote_list, cell_merge_dict=cell_merge_dict)