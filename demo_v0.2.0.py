'''
Author: xinyan
Date: 2024-03-08 21:20:04
LastEditors: xinyan
LastEditTime: 2024-03-22 21:16:23
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
    'font_path': {'r4': font_bold_path, '3-2': font_bold_path},
    'font_size': {12: 30}
}
cell_merge_dict = {'0-0':[0,1], '1-1':[1,0], '3-2':[0,1]}
img_path = './pic/demo_complex_table.jpg'
# tp.complex_table_pic(5, 4, title_list, cell_dict, font_path, img_path, footnote_list, cell_merge_dict=cell_merge_dict)


# -- Generate a tablepic with icon.

import pandas as pd
import tablepic as tp

data_list = [
    ['华北', '北京', 800, 1200, 950, 1400],
    ['华北', '天津', 950, 1210, 860, 1410],
    ['东北', '辽宁', 1100, 1220, 1370, 1420],
    ['东北', '吉林', 1120, 1230, 1380, 1430],
    ['华东', '上海', 1200, 1240, 1090, 1440],
    ['华东', '江苏', 1210, 1250, 950, 1450],
    ['华中', '湖北', 1220, 1260, 560, 1460],
    ['华中', '湖南', 1230, 1270, 1270, 1470],
    ['华南', '广东', 1240, 1280, 1370, 1480],
    ['华南', '广西', 1250, 1290, 1480, 1490],
]

df = pd.DataFrame(data_list, columns=['区域', '省份', '指标1', '指标2', '指标3', '指标4'])
df_sum = df.groupby('区域').sum(numeric_only=True).reset_index()
df_sum['区域'] = df_sum['区域'].apply(lambda x: x+'合计')
df_sum['省份'] = ''

df_final = pd.concat([df, df_sum], axis=0).sort_values(by='区域').reset_index(drop=True)
df_final['指标5'] = df_final['指标1'] / df_final['指标2']
df_final['指标6'] = df_final['指标3'] / df_final['指标4']

# 类型处理
for col in ['指标1', '指标2', '指标3', '指标4']:
    df_final[col] = df_final[col].apply(lambda x: f'{x:,}')
for col in ['指标5', '指标6']:
    df_final[col] = df_final[col].apply(lambda x: f'{x:.2%}')



font_path = '/Users/xinyan/Library/Fonts/sarasa-mono-sc-regular.ttf'
font_bold_path = '/Users/xinyan/Library/Fonts/sarasa-mono-sc-bold.ttf'
title_list = [
    {'content': 'XXX区域数据统计', 'padding_b': 0, 'font_path': font_bold_path},
    {'content': '统计日期：2024.03.18', 'font_size': 20, 'align': 'right', 'padding_t':10, 'padding_b':0, 'x_offset': -30},
]

footnote_list = [
    {'content': '注：以上数据与实际图标只为演示，无实际意义！', 'padding_t': 0},
]

# 单元格内容
content_list = [df_final.columns.tolist()] + df_final.values.tolist()
# 合并单元格计算：合计行的【区域】字段合并
merge_dict = {}
row_font_path = {}
for idx, val in enumerate(df_final['区域']):
    if val.endswith('合计'):
        merge_dict[f'{idx+1}-0'] = [0, 1]
        row_font_path[f'r{idx+1}'] = font_bold_path
# 颜色定义
clr_good = '#2a6e3f'
clr_warn = '#f39c12'
clr_bad = '#c12c1f'
# 图标配置
icon_config = {}
for r_idx, row in df_final.iterrows():
    c_idx = 0
    for col, val in row.items():
        # 指标1：箭头
        if col == '指标1':
            if float(val.replace(',', '')) > 1200:
                icon_config[f'{r_idx+1}-{c_idx}'] = f'arrow_up@{clr_good}'
            elif float(val.replace(',', '')) > 1100:
                icon_config[f'{r_idx+1}-{c_idx}'] = f'neutral@{clr_warn}'
            else:
                icon_config[f'{r_idx+1}-{c_idx}'] = f'arrow_down@{clr_bad}'
        # 指标2：圆圈箭头
        elif col == '指标2':
            if float(val.replace(',', '')) > 1280:
                icon_config[f'{r_idx+1}-{c_idx}'] = f'circle_up@{clr_good}'
            elif float(val.replace(',', '')) > 1250:
                icon_config[f'{r_idx+1}-{c_idx}'] = f'neutral@{clr_warn}'
            else:
                icon_config[f'{r_idx+1}-{c_idx}'] = f'circle_down@{clr_bad}'
        # 指标3：方块箭头
        elif col == '指标3':
            if float(val.replace(',', '')) > 1400:
                icon_config[f'{r_idx+1}-{c_idx}'] = f'square_up@{clr_good}'
            elif float(val.replace(',', '')) > 1380:
                icon_config[f'{r_idx+1}-{c_idx}'] = f'neutral@{clr_warn}'
            else:
                icon_config[f'{r_idx+1}-{c_idx}'] = f'square_down@{clr_bad}'
        # 指标4：三角箭头
        elif col == '指标4':
            if float(val.replace(',', '')) > 1450:
                icon_config[f'{r_idx+1}-{c_idx}'] = f'triangle_up@{clr_good}'
            elif float(val.replace(',', '')) > 1430:
                icon_config[f'{r_idx+1}-{c_idx}'] = f'neutral@{clr_warn}'
            else:
                icon_config[f'{r_idx+1}-{c_idx}'] = f'triangle_down@{clr_bad}'
        # 指标5：表情
        elif col == '指标5':
            if float(val.replace('%', '')) > 90:
                icon_config[f'{r_idx+1}-{c_idx}'] = f'happy_face@{clr_good}'
            elif float(val.replace('%', '')) > 70:
                icon_config[f'{r_idx+1}-{c_idx}'] = f'neutral_face@{clr_warn}'
            else:
                icon_config[f'{r_idx+1}-{c_idx}'] = f'sad_face@{clr_bad}'
        # 指标6：百分比
        elif col == '指标6':
            if float(val.replace('%', '')) > 90:
                icon_config[f'{r_idx+1}-{c_idx}'] = f"percent_{float(val.replace('%', ''))}@{clr_good}"
            elif float(val.replace('%', '')) > 70:
                icon_config[f'{r_idx+1}-{c_idx}'] = f"percent_{float(val.replace('%', ''))}@{clr_warn}"
            else:
                icon_config[f'{r_idx+1}-{c_idx}'] = f"percent_{float(val.replace('%', ''))}@{clr_bad}"
        c_idx += 1

cell_dict = {
    'content': content_list,
    'back_color': {'r0': '#2e59a7'},
    'fore_color': {'r0': '#FFFFFF'},
    'font_path': row_font_path,
    'icon_config': icon_config,
}
img_path = './pic/demo_complex_table_with_icon.png'
tp.complex_table_pic(df_final.shape[0]+1, df_final.shape[1], title_list, cell_dict, font_path, img_path,
    footnote_list=footnote_list, cell_merge_dict=merge_dict)
