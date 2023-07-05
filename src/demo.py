'''
Author: xinyan
Date: 2023-06-14 23:43:57
LastEditors: xinyan
LastEditTime: 2023-07-05 11:36:19
Description: file content
'''
import tablepic as tp


# ---------------------------------
# Generate a regular table.
# ---------------------------------


# the title you want to put on the table
title_list = [{'content': 'This is a title.'}]
header_dict = {'content': [f'Header{i+1}' for i in range(8)]}
data_dict = {'content':[[f'Data{i+j}' for j in range(8)] for i in range(9)]}

# tp.generate_table_pic(10, 8, title_list=title_list, header_dict=header_dict, data_dict=data_dict, img_path='./pic/basic_table1.jpg')


# Multiple title.
title_list = [{'content': 'This is a title.'}, {'content': 'This is a second title.'}, {'content': 'This is a third title.'}]
header_dict = {'content': [f'Header{i+1}' for i in range(8)]}
data_dict = {'content':[[f'Data{i+j}' for j in range(8)] for i in range(9)]}

# tp.generate_table_pic(10, 8, title_list=title_list, header_dict=header_dict, data_dict=data_dict, img_path='./pic/basic_table2.jpg')


# Add a footnote
title_list = [{'content': 'This is a title.'}, {'content': 'This is a second title.'}, {'content': 'This is a third title.'}]
header_dict = {'content': [f'Header{i+1}' for i in range(8)]}
data_dict = {'content':[[f'Data{i+j}' for j in range(8)] for i in range(9)]}
footnote_list = [{'content': 'This is a footnote.'}]
# tp.generate_table_pic(10, 8, title_list=title_list, header_dict=header_dict, data_dict=data_dict, img_path='./pic/basic_table3.jpg', footnote_list=footnote_list)


# ---------------------------------
# Generate a cell merged table.
# ---------------------------------

title_list = [{'content': 'This is a cell merged table'}]
# 11 header text
header_dict = {'content': ['MergedHead1', 'MergedHead2','MergedHead3'] + [f'Header{i+1}' for i in range(8)]}
# 8 * 8 data content
data_dict = {'content':[[f'Data{i+j}' for j in range(8)] for i in range(8)]}
# cell merged info
cell_merge_dict = {'0-0':[0,1], '0-2':[0,3], '0-6':[0,1]}
# tp.generate_table_pic(10, 8, title_list=title_list, header_dict=header_dict, data_dict=data_dict, img_path='./pic/merged_table1.jpg', cell_merge_dict=cell_merge_dict)


title_list = [{'content': 'This is a cell merged table for row and column'}]
# 8 header text
header_dict = {'content': ['Merge row and column', 'MergedHead2','row\nmerged'] + [f'Header{i+1}' for i in range(5)]}
# 8 * 8 data content
data_dict = {'content':[[f'Data{i+j}' for j in range(8)] for i in range(8)]}
# cell merged info
cell_merge_dict = {'0-0':[1,2], '0-3':[0,2], '0-6':[1,0]}
# tp.generate_table_pic(10, 8, title_list=title_list, header_dict=header_dict, data_dict=data_dict, img_path='./pic/merged_table2.jpg', cell_merge_dict=cell_merge_dict)




# ---------------------------------
# Change width and height
# ---------------------------------

# merge row and column
title_list = [{'content': 'This is a cell merged table and changed the size,'}]
# 8 header text
header_dict = {'content': ['Merge row and column', 'MergedHead2','row\nmerged'] + [f'Header{i+1}' for i in range(5)]}
# 8 * 8 data content
data_dict = {'content':[[f'Data{i+j}' for j in range(8)] for i in range(8)]}
# cell merged info
cell_merge_dict = {'0-0':[1,2], '0-3':[0,2], '0-6':[1,0]}
# tp.generate_table_pic(10, 8, title_list=title_list, header_dict=header_dict,
#                       data_dict=data_dict, img_path='./pic/change_size_table1.jpg',
#                       cell_merge_dict=cell_merge_dict,
#                       cell_width=200, cell_height=80)



# ---------------------------------
# Change font-size
# ---------------------------------

# merge row and column
title_list = [{'content': 'This is a cell merged table and changed the size,'}]
# 8 header text
header_dict = {'content': ['Merge row and column', 'MergedHead2','row merged'] + [f'Header{i+1}' for i in range(5)]}
# 8 * 8 data content
data_dict = {'content':[[f'Data{i+j}' for j in range(8)] for i in range(8)]}
# cell merged info
cell_merge_dict = {'0-0':[1,2], '0-3':[0,2], '0-6':[1,0]}
# tp.generate_table_pic(10, 8, title_list=title_list, header_dict=header_dict,
#                       data_dict=data_dict, img_path='./pic/change_size_table2.jpg',
#                       cell_merge_dict=cell_merge_dict,
#                       col_width_dict={6:300}, row_height_dict={5:80})


# Modify the style of the title.
title_list = [{'content': 'This is a cell merged table', 'font_size': 80, 'color':'#EE00DD', 'height': 100},
    {'content': 'This is a subtitle', 'color':'#0000FF', 'align':'right'}]
# 11 header text
header_dict = {'content': ['MergedHead1', 'MergedHead2','MergedHead3'] + [f'Header{i+1}' for i in range(8)]}
# 8 * 8 data content
data_dict = {'content':[[f'Data{i+j}' for j in range(8)] for i in range(8)]}
# cell merged info
cell_merge_dict = {'0-0':[0,1], '0-2':[0,3], '0-6':[0,1]}
# tp.generate_table_pic(10, 8, title_list=title_list, header_dict=header_dict,
#                       data_dict=data_dict, img_path='./pic/title_style_table.jpg',
#                       cell_merge_dict=cell_merge_dict)




title_list = [{'content': 'This is a cell merged table'}]
# Modify the header style.
header_dict = {'content': ['MergedHead1', 'MergedHead2','MergedHead3'] + [f'Header{i+1}' for i in range(8)],
    'font_size': {1: 45},
    'bk_color': '#BADC58',
    'align': {0:'left', 2:'right'},
    'fore_color': {0:'#B71540', 1: '#6F1E51', 2:'#546DE5'}}
# 8 * 8 data content
data_dict = {'content':[[f'Data{i+j}' for j in range(8)] for i in range(8)]}
# cell merged info
cell_merge_dict = {'0-0':[0,1], '0-2':[0,3], '0-6':[0,1]}
# tp.generate_table_pic(10, 8, title_list=title_list, header_dict=header_dict,
#                       data_dict=data_dict, img_path='./pic/header_style_table.jpg',
#                       cell_merge_dict=cell_merge_dict)



title_list = [{'content': 'This is a cell merged table'}]
# Modify the header style.
header_dict = {'content': ['MergedHead1', 'MergedHead2','MergedHead3'] + [f'Header{i+1}' for i in range(8)]}
# 8 * 8 data content
data_dict = {'content':[[f'Data{i+j}' for j in range(8)] for i in range(8)],
    'font_size': 20,
    'bk_color': {'r0': '#78E08F', '3-5': '#686DE0'},
    'fore_color': {'c3': '#EB3B5A'},
    'align': {'3-5': 'right'}
    }
# cell merged info
cell_merge_dict = {'0-0':[0,1], '0-2':[0,3], '0-6':[0,1]}
# tp.generate_table_pic(10, 8, title_list=title_list, header_dict=header_dict,
#                       data_dict=data_dict, img_path='./pic/data_style_table.jpg',
#                       cell_merge_dict=cell_merge_dict)



# Change Font
font_path = '/System/Library/Fonts/Supplemental/Comic Sans MS.ttf'

title_list = [{'content': 'This is a cell merged table'}]
# Modify the header style.
header_dict = {'content': ['MergedHead1', 'MergedHead2','MergedHead3'] + [f'Header{i+1}' for i in range(8)]}
# 8 * 8 data content
data_dict = {'content':[[f'Data{i+j}' for j in range(8)] for i in range(8)],
    'font_size': 20,
    'bk_color': {'r0': '#78E08F', '3-5': '#686DE0'},
    'fore_color': {'c3': '#EB3B5A'},
    'align': {'3-5': 'right'}
    }
# cell merged info
cell_merge_dict = {'0-0':[0,1], '0-2':[0,3], '0-6':[0,1]}
# tp.generate_table_pic(10, 8, title_list=title_list, header_dict=header_dict,
#                       data_dict=data_dict, img_path='./pic/font_style_table.jpg',
#                       font_path=font_path,
#                       cell_merge_dict=cell_merge_dict)



title_list = [{'content': 'This is a cell merged table'}]
# Modify the header style.
header_dict = {'content': ['MergedHead1', 'MergedHead2','MergedHead3'] + [f'Header{i+1}' for i in range(8)]}
# 8 * 8 data content
data_dict = {'content':[[f'Data{i+j}' for j in range(8)] for i in range(8)],
    'font_size': 20,
    'bk_color': {'r0': '#78E08F', '3-5': '#686DE0'},
    'fore_color': {'c3': '#EB3B5A'},
    'align': {'3-5': 'right'}
    }
# cell merged info
cell_merge_dict = {'0-0':[0,1], '0-2':[0,3], '0-6':[0,1]}
# tp.generate_table_pic(10, 8, title_list=title_list, header_dict=header_dict,
#                       data_dict=data_dict, img_path='./pic/bk_style_table.jpg',
#                       font_path=font_path,
#                       cell_merge_dict=cell_merge_dict,
#                       pic_bk_color='#DFE4EA',
#                       table_line_color='#2F3542')


# fixed-width table
title_list = [{'content': 'This is a fixed-width table'}]
header_dict = {'content': [f'Header{i+1}' for i in range(4)]}
# 8 * 4 data content
data_dict = {'content':[[f'Data{i}-0', f'Data{i}-1 this is a long content.', f'Data{i}-2', f'Data{i}-3'] for i in range(9)]}
# tp.generate_table_pic(10, 4, title_list=title_list, header_dict=header_dict,
#                       data_dict=data_dict, img_path='./pic/fixed_width_table.jpg')


# ------------------- version: v0.0.4 -------------------
# adaptive-width table
title_list = [{'content': 'This is a adaptive-width table'}]
header_dict = {'content': [f'Header{i+1}' for i in range(4)]}
# 8 * 4 data content
data_dict = {'content':[[f'Data{i}-0', f'Data{i}-1 this is a long content.', f'Data{i}-2', f'Data{i}-3'] for i in range(9)]}
tp.generate_table_pic(10, 4, title_list=title_list, header_dict=header_dict,
                      data_dict=data_dict, img_path='./pic/adaptive_width_table.jpg')

