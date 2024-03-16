'''
Author: xinyan
Date: 2023-06-13 17:12:25
LastEditors: xinyan
LastEditTime: 2024-03-16 14:17:41
Description: Generate a picture which contans a table.
History:
   2024.03.05: 新增主要函数 complex_table_pic 实现更加复杂的表格绘制，以及个性化控制。
'''

import math
import sys
from PIL import Image, ImageFont, ImageDraw


def get_content_pos(rec_pos:list, content:str, font:ImageFont.FreeTypeFont, align:str='center'):
    content_list = content.split('\n')
    c_w, c_h = 0, 0
    for item in content_list:
        w, h = font.getbbox(item)[2:]
        c_w = max(c_w, w)
    c_h = h * len(content_list)
    rec_width = rec_pos[2] - rec_pos[0]
    rec_height = rec_pos[3] - rec_pos[1]
    if align == 'center':
        return (int(rec_pos[0]+rec_width/2-c_w/2), int(rec_pos[1]+rec_height/2-c_h/2))
    elif align == 'right':
        return (int(rec_pos[0]+rec_width-c_w-5), int(rec_pos[1]+rec_height/2-c_h/2))
    elif align == 'left':
        return (int(rec_pos[0]+5), int(rec_pos[1]+rec_height/2-c_h/2))

def get_font(font_path:str=None, font_size:int=20):
    """
    Returns a font object based on the given font path and font size.
    :param font_path: (str) The path to the font file. Default is None.
    :param font_size: (int) The size of the font to be returned. Default is 20.
    :return: (PIL.ImageFont.FreeTypeFont) The font object.
    """
    if font_path:
        return ImageFont.truetype(font_path, font_size)
    else:
        if sys.platform == 'win32':
            return ImageFont.truetype('simhei', font_size)
        elif sys.platform  in ("linux", "linux2"):
            return ImageFont.truetype('DejaVuSan', font_size)
        elif sys.platform == 'darwin':
            return ImageFont.truetype('PingFang', font_size)
        else:
            return ImageFont.load_default()


def generate_table_rec_coord(row_num:int, col_num:int, start_pos:list, margin:int=3, cell_width:int=150, cell_height:int=50,
                           col_width_dict:dict={}, row_height_dict:dict={}, cell_merge_dict:dict={}):
    """
    Generate the coordinates of each cell of the table.

    :param row_num: Number of rows in the table.
    :param col_num: Number of columns in the table.
    :param start_pos: Starting coordinate of the table in the image.
    :param margin: Space between cells of the table. Default is 3.
    :param cell_width: Width of each cell. Default is 150.
    :param cell_height: Height of each cell. Default is 50.
    :param col_width_dict: Specify the width of individual columns. For example,
        {0: 200} specifies the width of first column as 200. Columns without a specified width use the default width 150.
    :param row_height_dict: Specify the height of individual rows. For example,
        {1: 80} specifies the height of second row as 80. Rows without a specified height use the default height 50.
    :param cell_merge_dict: Information on merging cells. For example,
        {'0-0': [1,0], '0-1': [0, 2]} indicates that the cell at coordinate [0,0] needs to be merged,
        by merging 1 row downward and 0 columns to the right (i.e., not merging columns);
        The cell at coordinate [0,1] needs to be merged, by merging 0 rows downward and 1 column to the right.
    """
    def get_combined_size(index:int, combine_cnt:int, size:int, size_dict:dict, margin:int):
        combine_size = sum(size_dict.get(idx, size) for idx in range(index, index + combine_cnt + 1)) + margin * combine_cnt
        return combine_size if combine_cnt > 0 else size_dict.get(index, size)

    def get_start_size(index:int, size:int, margin:int, size_dict:dict):
        total_size = sum(size_dict.get(i, size) + margin for i in range(index))
        return total_size if index else 0

    rec_pos_list = []
    skip_pos_key = []
    max_x, max_y = 0, 0
    for i in range(row_num):
        for j in range(col_num):
            pos_key = '{}-{}'.format(i, j)
            if pos_key in skip_pos_key:
                continue
            x0 = start_pos[0] + get_start_size(j, cell_width, margin, col_width_dict)
            y0 = start_pos[1] + get_start_size(i, cell_height, margin, row_height_dict)
            row_combine, col_combine = cell_merge_dict.get(pos_key, [0,0])
            x1 = x0 + get_combined_size(j, col_combine, cell_width, col_width_dict, margin)
            y1 = y0 + get_combined_size(i, row_combine, cell_height, row_height_dict, margin)
            max_x = max(max_x, x1)
            max_y = max(max_y, y1)
            rec_pos_list.append([x0, y0, x1, y1])
            for t_i in range(row_combine):
                skip_pos_key.append('{}-{}'.format(i+t_i+1, j))
            for t_j in range(col_combine):
                skip_pos_key.append('{}-{}'.format(i, j+t_j+1))
            for t_i in range(row_combine):
                for t_j in range(col_combine):
                    skip_pos_key.append('{}-{}'.format(i+t_i+1, j+t_j+1))
    table_pos = [start_pos[0]-margin, start_pos[1]-margin, max_x+margin, max_y+margin]
    return rec_pos_list, table_pos

def __process_title_footnote(title_or_footnote:list, default_align:str, default_font_size:int, default_height:int, default_color:str) -> list:
    result_list = []
    for idx, content_dict in enumerate(title_or_footnote):
        content_dict['font_size'] = content_dict.get('font_size', default_font_size) if idx == 0 else content_dict.get('font_size', default_font_size-10)
        content_dict['color'] = content_dict.get('color', default_color)
        content_dict['align'] = content_dict.get('align', default_align)
        content_dict['height'] = content_dict.get('height', default_height) if idx == 0 else content_dict.get('height', default_height-20)
        result_list.append(content_dict)
    return result_list

def __get_max_width_title_footnote(title_list:list, footnote_list:list, font_path:str) -> int:
    max_width = 0
    for title in title_list:
        title_font = get_font(font_path, title['font_size'])
        max_width = max(max_width, title_font.getbbox(title['content'])[2])
    for footnote in footnote_list:
        footnote_font = get_font(font_path, footnote['font_size'])
        max_width = max(max_width, footnote_font.getbbox(footnote['content'])[2])
    return max_width

def __get_data_info(data_dict:dict, key:str, i, j, v_default, v_type):
    if type(data_dict.get(key, v_default)) == v_type:
            result = data_dict.get(key, v_default)
    elif data_dict[key].get(f'{i}-{j}', None):
        result = data_dict[key].get(f'{i}-{j}')
    elif data_dict[key].get(f'r{i}', None):
        result = data_dict[key].get(f'r{i}')
    elif data_dict[key].get(f'c{j}', None):
        result = data_dict[key].get(f'c{j}')
    else:
        result = v_default
    return result


def __calculate_data_cell_width_height(row_num:int, data_dict:dict, font_path:str, cell_width:int, cell_height:int):
    col_width_dict = {}
    row_height_dict = {}
    header_row = row_num - len(data_dict['content'])
    for i, data_line in enumerate(data_dict['content']):
        for j, data_content in enumerate(data_line):
            data_font = get_font(font_path, __get_data_info(data_dict, 'font_size', i, j, 20, int))
            c_w, c_h = 0, 0
            for item in data_content.split('\n'):
                w, h = data_font.getbbox(item)[2:]
                c_w = max(c_w, w) + 20
            c_h = h * len(data_content.split('\n')) + 20
            row_height_dict[i + header_row] = max(row_height_dict.get(i + header_row, cell_height), c_h)
            col_width_dict[j] = max(col_width_dict.get(j, cell_width), c_w)
    return col_width_dict, row_height_dict


def generate_table_pic(row_num:int, col_num:int, title_list:list, header_dict:dict, data_dict:dict, img_path:str=None, footnote_list:list=[],
                       cell_width:int=150, cell_height:int=50,  col_width_dict:dict={}, row_height_dict:dict={}, cell_merge_dict:dict={},
                       table_margin:int=20, pic_bk_color='#FFFFFF', table_line_color='#E8EAED', font_path:str=None):
    """
    Generate the table picture.
    :param row_num: int，Number of rows in the table.
    :param col_num: int，Number of columns in the table.
    :param title_list: list, set the title information. Multiple titles can be set, and the information for each title stores in a dict. Example:
        [{'content': 'I am the main title'}, {'content': 'I am the subtitle'}]
        In this example, there are two titles. You can also specify the font size, color, alignment, and height for each title. For example:
        [{'content': 'I am the main title', 'font_size': 40, 'color': '#000000', 'align': 'center', 'height': 100}, {'content': 'I am the subtitle', 'align':'right'}]
        In this example, the main title has a custom font size, color, alignment, and height. The subtitle has a custom alignment.
        'content' is a required key, other keys are optional. The default font size for the main title is 40, and 30 for the subtitle.
        The default height for the main title is 80, and 60 for the subtitle. The color is black, alignment is centered by default for all titles.
    :param header_dict: dict, set the information for the table header.
        Example 1: {'content': ['Header1', 'Header2', 'Header3']}
        In this example, there are 3 headers for the table. It doesn't mean you must have 3 columns, because you can combine the multiple columns as one header.
        The font size is 30, background color is '#CCD6EB', text color is white, and alignment is centered by default.

        Example 2: {'content': ['Header1', 'Header2', 'Header3'], 'font_size': 35, 'bk_color': '#000000', 'fore_color': '#FFFFFF', 'align': 'left'}
        In this example, it specifies the font size is 35, the background color is black, text color is white, and the alignment is left-aligned.

        If you like, you can specifies the particula header's font size, background color, text color, and alignment. For example:
        {'content': ['Header1', 'Header2', 'Header3'], 'bk_color': {0:'#FF0000',2:'#00FF00'}, 'fore_color': {1:'#0000FF'}, 'align': {1:'right'}}
        It specifies the first header's background color is red, and third header's background color is green. The other header's background color is '#CCD6EB' by default.
        The text color of the second header is blue, and other headers have a default text color of white. The alignment of the second header is right-aligned,
        other headers have a default alignment of centered.
    :param data_dict: dict, Set the information for the data content of the table.
        Example 1: {'content': [['A001', '123', '456'], ['A002', '234', '345']]}
        The data part is specified by a two-dimensional list. The first demension is the row, and the second dimension is the column. It should be noted that each element
        of the content must be a string type, even if it is a number.

        Like the header_dict, you can also specify the font size, background color, text color and the alignment for each row, column, even the cell.
        Example 2: {'content': [['A001', '123', '456'], ['A002', '234', '345']], 'bk_color': '#FFFFFF', 'fore_color': '#000000', 'align': 'right'}
        It specify the all data cell's background color is white, the text color is black, and the alignment is right-aligned.

        Example 3: {'content': ['A001', '123', '456'], ['A002', '234', '345']], 'bk_color': {'r0': '#FFFF00'}, 'fore_color': {'c1':'#00FF00'}, 'align': {'2-3':'left'}}
        It specify the first row's background color is yellow, the second column's text color is green, and the alignment of cell which in the third row and fourth column
        is left-aligned. 'r0' means 0-index row, 'c2' means 2-indexed column. '3-5' means the cell located in the fourth row and sixth column.
    :param img_path: Set the path for saving the image. If none then the image will not be saved.
    :param footnote_list: list, Optional parameter. Set the footnote information. The structure is the same as title_info. The default alignment
        is right-aligned, font size is 30, and height is 80 by default.
    :param cell_width: int, Optional parameter. Set the width of each cell. The default is 150.
    :param cell_height: int, Optional parameter. Set the height of each cell. The default is 50.
    :param col_width_dict: dict, Specify the width of individual columns. For example, {0: 200} specifies the width of the first column as 200.
        Other columns use the width specified by the parameter cell_width.

    :param row_height_dict: dict, Specify the height of individual rows. For example, {1: 80} specifies the height of the second row as 80.
        Other rows use the height specified by the parameter cell_height.

    :param cell_merge_dict: dict, contains the information of merging cells. For example, {'0-0': [1,0], '0-1': [0, 2]} indicates that the cell at coordinate [0,0] needs to be merged,
        by merging 1 row downward and 0 columns to the right (i.e., not merging columns); the cell at coordinate [0,1] needs to be merged, by merging
        0 rows downward and 1 column to the right.
    :param pic_bk_color: str, optional parameter. Set the background color of the picture, default value is '#FFFFFF'.
    :param table_line_color: str, optional parameter. Set the line color of the table, default value is '#E8EAED'.
    :param font_path: str, optional parameter. Given the font path to set a new font for the text (including title, header, data).
    """
    # Define default values
    __default_title_font_size = 40
    __default_footnote_font_size = 30
    __default_header_font_size = 30
    __default_data_font_size = 20
    __default_title_height = 80
    __default_footnote_height = 60
    __default_header_bk_color = '#CCD6EB'
    __default_title_color = '#000000'
    __default_footnote_color = '#000000'
    __default_title_align = 'center'
    __default_footnote_align = 'right'

    # Calculate the width for each column and the height for each row
    calc_col_width_dict, calc_row_height_dict = __calculate_data_cell_width_height(row_num, data_dict, font_path, cell_width, cell_height)
    calc_col_width_dict.update(col_width_dict)
    calc_row_height_dict.update(row_height_dict)

    color_white = '#FFFFFF'
    color_black = '#000000'

    title_list = __process_title_footnote(title_list, __default_title_align, __default_title_font_size, __default_title_height, __default_title_color)
    footnote_list = __process_title_footnote(footnote_list, __default_footnote_align, __default_footnote_font_size, __default_footnote_height, __default_footnote_color)
    total_title_height = sum([title['height'] for title in title_list])
    total_footnote_height = sum([footnote['height'] for footnote in footnote_list])
    max_title_footnote_width = __get_max_width_title_footnote(title_list, footnote_list, font_path)
    cell_pos_list, table_pos = generate_table_rec_coord(row_num, col_num, start_pos=[table_margin, total_title_height], cell_width=cell_width, cell_height=cell_height,
                                                     col_width_dict=calc_col_width_dict, row_height_dict=calc_row_height_dict, cell_merge_dict=cell_merge_dict,)

    # if the title is longer the table, need to adjust the table pos.
    if table_pos[2] < max_title_footnote_width:
        # print(table_pos, max_title_footnote_width)
        diff = (max_title_footnote_width - table_pos[2]) // 2 + 5
        # print(diff)
        new_cell_pos_list = []
        # update the cell rectangle coordinates(only for x axis).
        for rec_pos in cell_pos_list:
            new_cell_pos_list.append([x+diff if idx % 2 == 0 else x for idx, x in enumerate(rec_pos)])
        # update the total table pos
        new_table_pos = [x+diff if idx % 2 == 0 else x for idx, x in enumerate(table_pos)]
        # print(new_table_pos)
        cell_pos_list = new_cell_pos_list
        table_pos = new_table_pos


    pic_width = max(table_pos[2], max_title_footnote_width) + table_margin
    pic_height = table_pos[3] + table_margin + total_footnote_height

    image = Image.new('RGB', (pic_width, pic_height), pic_bk_color)
    draw = ImageDraw.Draw(image)
    draw.rectangle(table_pos, fill=table_line_color)

    # Draw Title
    tp_dict = {}
    for idx, title in enumerate(title_list):
        title_rec_coord = [0, tp_dict.get(idx-1, 0), pic_width, title['height'] + tp_dict.get(idx-1, 0)]
        tp_dict[idx] = title_rec_coord[3]
        title_font = get_font(font_path, title['font_size'])
        title_coord = get_content_pos(title_rec_coord, title['content'], title_font, title['align'])
        draw.text(title_coord, title['content'], font=title_font, fill=title['color'])

    # Draw Header
    for idx, header_content in enumerate(header_dict['content']):
        header_rec_pos = cell_pos_list[idx]
        header_font = get_font(font_path, header_dict.get('font_size', __default_header_font_size)) \
            if type(header_dict.get('font_size', __default_header_font_size)) == int \
            else get_font(font_path, header_dict['font_size'].get(idx, __default_header_font_size))
        header_coord = get_content_pos(header_rec_pos, header_content, header_font, header_dict.get('align', 'center')) \
            if type(header_dict.get('align', 'center')) == str \
            else get_content_pos(header_rec_pos, header_content, header_font, header_dict['align'].get(idx, 'center'))
        draw.rectangle(header_rec_pos, fill=header_dict.get('bk_color', __default_header_bk_color)) \
            if type(header_dict.get('bk_color', __default_header_bk_color)) == str \
            else draw.rectangle(header_rec_pos, fill=header_dict['bk_color'].get(idx, __default_header_bk_color))
        header_fore_color = header_dict.get('fore_color', color_black) \
            if type(header_dict.get('fore_color', color_black)) == str \
            else header_dict['fore_color'].get(idx, color_black)
        draw.text(header_coord, header_content, font=header_font, fill=header_fore_color)

    # Draw Data
    for i, data_line in enumerate(data_dict['content']):
        for j, data_content in enumerate(data_line):
            data_rec_coord = cell_pos_list[idx + 1 + (i * col_num) + j]
            data_rec_bk_color = __get_data_info(data_dict, 'bk_color', i, j, color_white, str)
            draw.rectangle(data_rec_coord, fill=data_rec_bk_color)
            data_font = get_font(font_path, __get_data_info(data_dict, 'font_size', i, j, __default_data_font_size, int))
            data_coord = get_content_pos(data_rec_coord, data_content, data_font, __get_data_info(data_dict, 'align', i, j, 'center', str))
            draw.text(data_coord, data_content, font=data_font, fill=__get_data_info(data_dict, 'fore_color', i, j, color_black, str))

    # Draw footnote
    tp_dict = {-1: table_pos[3] + table_margin}
    for idx, footnote in enumerate(footnote_list):
        footnote_rec_coord = [0, tp_dict[idx-1], pic_width, footnote['height'] + tp_dict[idx-1]]
        tp_dict[idx] = footnote_rec_coord[3]
        footnote_font = get_font(font_path, footnote['font_size'])
        footnote_coord = get_content_pos(footnote_rec_coord, footnote['content'], footnote_font, footnote['align'])
        draw.text(footnote_coord, footnote['content'], font=footnote_font, fill=footnote['color'])
    if img_path:
        image.save(img_path)
    else:
        return image


def combine_multiple_pic(combine_path:str, path_list:list=None, img_list:list=None, pic_bk_color:str='#FFFFFF'):
    """
    Combine multiple pictures into one
    :param pic_path_list: list, the list of picture's path
    :param combine_pic_path: str, the path of combined picture
    """
    total_width = 0
    total_height = 0
    if path_list is None and img_list is None:
        raise Exception('Please specify the path_list or img_list!')
    elif path_list:
        img_list = []
        for path in path_list:
            img = Image.open(path)
            img_list.append(img)
            total_width = max(total_width, img.width)
            total_height += img.height
    elif img_list:
        total_width = max([img.width for img in img_list])
        total_height = sum([img.height for img in img_list])

    combine_img = Image.new('RGB', (total_width, total_height), pic_bk_color)
    start_height = 0
    for img in img_list:
        combine_img.paste(img, ((total_width-img.width)//2, start_height))
        start_height += img.height
    combine_img.save(combine_path)

# ---------------------------------------------------------------------------------------------------------
# 以下为 2024年3月 重新设计逻辑，新开发的代码。为了保证之前使用 generate_table_pic 函数的兼容，
# 暂时不对之前的代码逻辑做进一步的修改即优化。
# ---------------------------------------------------------------------------------------------------------

def __get_default_config():
    """
    获取必须参数的默认配置
    """
    return {
        'title_font_size': 40,      # 标题字体大小
        'footnote_font_size': 20,   # 脚注字体大小
        'cell_font_size': 20,       # 表格内容字体大小
        'title_align': 'center',    # 标题对齐方式
        'footnote_align': 'left',   # 脚注对齐方式
        'cell_align': 'center',     # 表格内容对齐方式
        'back_color': '#ffffff',    # 背景颜色(白色)
        'fore_color': '#000000',    # 字体颜色(黑色)
        'newline_margin_rate': 0.2, # 换行内容的间距比例（相对于内容高度）
        'title_padding_t': 50,      # 标题的上方间距（像素）
        'title_padding_b': 10,      # 标题的下方间距（像素）
        'title_padding_h': 80,      # 标题的水平间距（像素）
        'footnote_padding_t': 10,   # 脚注的上方间距（像素）
        'footnote_padding_b': 30,   # 脚注的下方间距（像素）
        'footnote_padding_h': 50,   # 脚注的水平间距（像素）
        'cell_padding_h': 20,       # 单元格内容与边框的水平间距（像素）
        'cell_padding_v': 10,       # 单元格内容与边框的垂直间距（像素）
        'table_padding': 30,        # 表格的外边框与图片之间的间距（像素）
    }

def __get_content_size(font:ImageFont.FreeTypeFont, content:str, new_line_flag:bool=True) -> list:
    """
    获取文本内容在指定字体下的宽度和高度
    :param font: 字体对象
    :param content: 文本内容
    :param new_line_flag: 是否考虑文本中的换行符
    :return: [width, height, y_adjust], 其中 y_adjust 为文本内容在指定字体下的垂直偏移量
    """
    if new_line_flag:
        size_list = []
        for item in content.split('\n'):
           bbox = font.getbbox(item)
           size_list.append([bbox[2], bbox[3]-bbox[1], -bbox[1]])
        return size_list
    else:
        bbox = font.getbbox(content)
        return [bbox[2], bbox[3]-bbox[1], -bbox[1]]

def __get_cell_content_width_height(content_size:list, newline_margin_rate:float, cell_padding_h:int, cell_padding_v:int) -> list:
    """
    计算单元格文本内容大小的宽度和高度，考虑内容在单元格内的水平、垂直间距；以及内容有换行的情况
    :param content_size: 内容的大小列表，单个元素格式为[width, height, y_adjust]
    :param newline_margin_rate: 换行内容的间距比例（相对于内容高度）
    :param cell_padding_h: 单元格的水平间距
    :param cell_padding_v: 单元格的垂直间距
    :return [width, height]: 该内容的最大的宽度和累计的高度
    """
    # 宽度取换行内容的最大宽度（考虑水平间距），高度为累计的高度（考虑垂直间距）
    width = max(size[0] + 2 * cell_padding_h for size in content_size)
    height = sum(size[1] for size in content_size) + cell_padding_v * 2
    __newline_margin = math.ceil(content_size[0][1] * newline_margin_rate) if content_size else 0
    if len(content_size) > 1:
        height += (len(content_size) - 1) * __newline_margin
    return [width, height]

def __get_content_coord(rec_coord:list, content_size:list, align_h:str='center', align_v:str='center', x_adjust:int=0, y_adjust:int=0):
    """
    计算文本内容在给定矩形框内不同对齐方式下的坐标，支持直接对x、y轴坐标进行调整。
    :param rec_size: 矩形框的大小，格式为[左上角x, 左上角y, 右下角x, 右下角y]
    :param content_size: 内容的大小，格式为[宽度, 高度, y轴调整量]
    :param align_h: 水平对齐方式，取值为['left', 'center', 'right']，默认为'center'
    :param align_v: 垂直对齐方式，取值为['top', 'center', 'bottom']，默认为'center'
    :param x_adjust: 额外的水平偏移量，默认为0
    :param y_adjust: 额外的垂直偏移量，默认为0
    :return: 内容在单元格内的坐标[x, y]
    """
    __rec_width = rec_coord[2] - rec_coord[0]
    __rec_height = rec_coord[3] - rec_coord[1]

    # 创建一个字典来映射对齐字符串到计算逻辑
    h_align_map = {
        'left': lambda w, m: rec_coord[0] + m + x_adjust,
        'center': lambda w, m: int(rec_coord[0] + (__rec_width - w) / 2) + x_adjust,
        'right': lambda w, m: rec_coord[2] - w - m + x_adjust,
    }
    v_align_map = {
        'top': lambda h, m: rec_coord[1] + m + y_adjust,
        'center': lambda h, m: int(rec_coord[1] + (__rec_height - h) / 2) + y_adjust,
        'bottom': lambda h, m: rec_coord[3] - h - m + y_adjust,
    }
    return [h_align_map[align_h](content_size[0], 5), v_align_map[align_v](content_size[1], 5) + content_size[2]]


def __get_multiline_content_coord(rec_coord:list, content_size:list, newline_margin_rate:float, align_h:str, align_v:str):
    """
    计算含换行符的文本内容在给定矩形框内不同对齐方式下的坐标，支持直接对x、y轴坐标进行调整。
    :param rec_size: 矩形框的大小，格式为[左上角x, 左上角y, 右下角x, 右下角y]
    :param content_size: 内容的大小，格式为[宽度, 高度, y轴调整量]
    :param align_h: 水平对齐方式，取值为['left', 'center', 'right']，默认为'center'
    :param align_v: 垂直对齐方式，取值为['top', 'center', 'bottom']，默认为'center'
    :param x_adjust: 额外的水平偏移量，默认为0
    :param y_adjust: 额外的垂直偏移量，默认为0
    :return: 内容在单元格内的坐标[x, y]
    """
    # 如果只有一行，则直接调用 __get_content_coord
    if len(content_size) == 1:
        return __get_content_coord(rec_coord, content_size[0], align_h, align_v)
    else:
        content_coord_list = []
        __max_width = max([__size[0] for __size in content_size])
        __newline_margin = math.ceil(content_size[0][1] * newline_margin_rate)
        __max_height = sum([__size[1] for __size in content_size]) + __newline_margin * (len(content_size) - 1)
        __global_coord = __get_content_coord(rec_coord, [__max_width, __max_height, 0], align_h, align_v)
        for __size in content_size:
            content_coord_list.append([
                __global_coord[0] + math.ceil((__max_width - __size[0]) / 2),
                __global_coord[1] + __size[2]
            ])
            __global_coord[1] += __size[1] + __newline_margin
        return content_coord_list

def __process_title_attribute(font_path:str, title_list:list, default_config:dict):
    """
    处理标题的属性，每个标题都包括以下属性，若标题中未指定属性，则取默认值：
        - 字体文件路径
        - 字体大小
        - 字体颜色
        - 水平对齐方式
        - 垂直方向顶部的间距大小
        - 垂直方向底部的间距大小
        - 水平方向的间距大小（设置单侧）
        - x轴的偏移量
    :param title_list: 标题列表
    :param default_config: 默认配置
    :return: title_attribute_dict, key为标题的索引，value为标题的属性字典
    """
    title_attribute_dict = {}
    __attribute_list = [
        ['font_path', font_path],
        ['font_size', default_config['title_font_size']],
        ['color', default_config['fore_color']],
        ['align', default_config['title_align']],
        ['padding_t', default_config['title_padding_t']],
        ['padding_b', default_config['title_padding_b']],
        ['padding_h', default_config['title_padding_h']],
        ['x_offset', 0]
    ]
    for idx, title in enumerate(title_list):
        title_attribute_dict[idx] = dict([[__attr[0], title.get(__attr[0], __attr[1])] for __attr in __attribute_list])
    return title_attribute_dict

def __process_footnote_attribute(font_path:str, footnote_list:list, default_config:dict):
    """
    处理标题的属性，每个脚注都包括以下属性，若标题中未指定属性，则取默认值：
        - 字体文件路径
        - 字体大小
        - 字体颜色
        - 水平对齐方式
        - 垂直方向顶部的间距大小
        - 垂直方向底部的间距大小
        - 水平方向的间距大小（设置单侧）
        - x轴的偏移量
    :param title_list: 标题列表
    :param default_config: 默认配置
    :return: footnote_attribute_dict, key为标题的索引，value为标题的属性字典
    """
    footnote_attribute_dict = {}
    __attribute_list = [
        ['font_path', font_path],
        ['font_size', default_config['footnote_font_size']],
        ['color', default_config['fore_color']],
        ['align', default_config['footnote_align']],
        ['padding_t', default_config['footnote_padding_t']],
        ['padding_b', default_config['footnote_padding_b']],
        ['padding_h', default_config['footnote_padding_h']],
        ['x_offset', 30]
    ]
    for idx, footnote in enumerate(footnote_list):
        footnote_attribute_dict[idx] = dict([[__attr[0], footnote.get(__attr[0], __attr[1])] for __attr in __attribute_list])
    return footnote_attribute_dict



def __get_title_footnote_size(title_list:list, title_attribute_dict:dict) -> list:
    """
    计算标题和脚注的大小
    :param font_path: 字体路径
    :param title_list: 标题列表
    :param title_attribute_dict: 标题属性字典
    :return: list: title_content_size, title_rectangle_size。标题的内容大小列表，标题的矩形框大小列表
    """
    title_content_size, title_rectangle_size = [], []
    for idx, title in enumerate(title_list):
        __font = ImageFont.truetype(title_attribute_dict[idx]['font_path'], title_attribute_dict[idx]['font_size'])
        __size = __get_content_size(__font, title['content'], new_line_flag=False)
        title_content_size.append(__size)
        title_rectangle_size.append([
            __size[0] + 2 * title_attribute_dict[idx]['padding_h'],
            __size[1] + title_attribute_dict[idx]['padding_t'] + title_attribute_dict[idx]['padding_b']
        ])
    return title_content_size, title_rectangle_size


def __get_title_footnote_coord(pic_width:int, y_start:int, content_size:list, rectangle_size:list, attribute_dict:dict) -> list:
    """
    计算标题和脚注内容的坐标位置
    :param pic_width: 图片宽度
    :param y_start: y坐标起始位置
    :param content_size: 内容大小列表
    :param rectangle_size: 矩形框大小列表
    :param attribute_dict: 属性字典
    :return: content_coord_list, y_start：内容坐标列表，y_start：y轴的结束位置
    """
    content_coord_list = []
    for __idx, __rectangle_size in enumerate(rectangle_size):
        __content_size = content_size[__idx]
        __retange_coord = [0, y_start, max(__rectangle_size[0], pic_width), __rectangle_size[1] + y_start]
        __content_coord = __get_content_coord(__retange_coord, __content_size, align_h=attribute_dict[__idx]['align'],
            x_adjust = attribute_dict[__idx]['x_offset'],
            # 因为上下间距不同导致的y轴位置的调整
            y_adjust=(attribute_dict[__idx]['padding_t']-attribute_dict[__idx]['padding_b'])/2)
        content_coord_list.append(__content_coord)
        y_start = __retange_coord[3]
    return content_coord_list, y_start

def __draw_title_footnote(draw:ImageDraw, content_coord_list:list, title_footnote_list:list, attribute_dict:dict):
    """
    绘制标题和脚注
    :param draw: ImageDraw对象
    :param content_coord_list: 内容坐标列表
    :param title_footnote_list: 标题和脚注列表
    :param attribute_dict: 属性字典
    """
    for idx, title in enumerate(title_footnote_list):
        draw.text(content_coord_list[idx], title['content'], fill=attribute_dict[idx]['color'],
            font=ImageFont.truetype(attribute_dict[idx]['font_path'], attribute_dict[idx]['font_size']))


def __process_table_attribute(font_path:str, row_num:int, col_num:int, cell_dict:dict, cell_merge_dict:dict, default_config:dict) -> dict:
    """
    处理表格单元格的属性。包括两部分：针对表格整体的属性，以及可以按单元格、列、行单独设置的属性的个性化设置属性。
    整体属性包括：
        - newline_margin_rate: 换行内容的行间距比例
        - pading_h: 单元格内容与左右边框的间距（设置单侧间距为多少）
        - pading_v: 单元格内容与上下边框的间距（设置单侧间距为多少）
    按照【单元格、列、行、全局默认】的顺序依次获取每个单元格的以下属性：
        - font_path: 文字内容的字体路径
        - font_size: 文字内容的字体大小
        - back_color: 单元格背景色
        - fore_color: 文字内容颜色
        - align_h: 文字内容的水平对齐方式
        - align_v: 文字内容的垂直对齐方式
    :param row_num: 表格行数
    :param col_num: 表格列数
    :param cell_dict: 单元格内容格式字典
    :param default_config: 默认配置字典
    :return: table_attribute_dict, 表格属性以属性名为key返回属性值，个性化属性，以单元格坐标为key返回属性字典。
    """
    # 表格整体的属性
    table_attribute_dict = {
        'newline_margin_rate': cell_dict.get('newline_margin_rate', default_config['newline_margin_rate']),
        'padding_h': cell_dict.get('padding_h', default_config['cell_padding_h']),
        'padding_v': cell_dict.get('padding_v', default_config['cell_padding_v']),
    }
    # 以下获取可以单独设置的属性
    lam_dict_attribute = lambda x, i, j: x.get(i) or x.get(j) if isinstance(x, dict) else None
    lam_final_attribute = lambda cell, col, row, table, obj_type, default: cell or col or row or (table if isinstance(table, obj_type) else default)
    __cell_idx = 0
    __skip_coord_list = []
    # 属性列表，构成：属性名、类型、默认值、从参数获取到的属性值
    __attribute_list = [
        ['font_path', str, font_path, cell_dict.get('font_path')],
        ['font_size', int, default_config['cell_font_size'], cell_dict.get('font_size')],
        ['back_color', str, default_config['back_color'], cell_dict.get('back_color')],
        ['fore_color', str, default_config['fore_color'], cell_dict.get('fore_color')],
        ['align_h', str, default_config['cell_align'], cell_dict.get('align_h')],
        ['align_v', str, default_config['cell_align'], cell_dict.get('align_v')],
    ]
    for i in range(row_num):
        # 从参数值按行获取属性
        __row_attribute_list = [lam_dict_attribute(attribute[3], f'r{i}', '__NONE__') for attribute in __attribute_list]
        for j in range(col_num):
            __curr_coord = f'{i}-{j}'
            # 如果当前单元格是被合并的，则跳过
            if __curr_coord in __skip_coord_list:
                continue
            # 从参数值按列获取属性
            __col_attribute_list = [lam_dict_attribute(attribute[3], f'c{j}', '__NONE__') for attribute in __attribute_list]
            # 从参数值按索引顺序获取字体属性(可以按照content的顺序索引，也可以按照单元格的坐标索引)
            __cell_attribute_list = [lam_dict_attribute(attribute[3], __cell_idx, __curr_coord) for attribute in __attribute_list]
            # 计算单元格最终的属性，按照：单元格、列、行、表格、默认的顺序依次获取
            table_attribute_dict[__curr_coord] = dict([[__attr_name, lam_final_attribute(__cell_v, __col_v, __row_v, __attr_obj, __attr_type, __attr_default)]
                for (__attr_name, __attr_type, __attr_default, __attr_obj), __cell_v, __col_v, __row_v in zip(__attribute_list, __cell_attribute_list, __col_attribute_list, __row_attribute_list)
            ])

            # 处理合并单元格
            __row_combine, __col_combine = cell_merge_dict.get(__curr_coord, [0,0])
            # 向下合并行，下方单元格跳过
            __skip_coord_list.extend(f'{i+t}-{j}' for t in range(1, __row_combine+1))
            # 向右合并列，右侧单元格跳过
            __skip_coord_list.extend(f'{i}-{j+t}' for t in range(1, __col_combine+1))
            # 纵向、横向都有合并，跳过导致被合并的单元格
            __skip_coord_list.extend(f'{i+t_i}-{j+t_j}' for t_i in range(1, __row_combine+1) for t_j in range(1, __col_combine+1))
            # 单元格内容自增
            __cell_idx += 1
    return table_attribute_dict



def __get_table_size(row_num:int, col_num:int, cell_dict:dict, cell_merge_dict:dict, col_width_dict:dict, row_height_dict:dict, table_attribute_dict:dict, default_config:dict) -> list:
    """
    计算表格的大小
    :param row_num: 表格行数
    :param col_num: 表格列数
    :param cell_dict: 单元格内容格式字典
    :param cell_merge_dict: 单元格合并字典
    :param default_config: 默认配置字典
    :param col_width_dict: 用户自定义列宽字典
    :param row_height_dict: 用户自定义行高字典
    :param table_attribute_dict: 单元格属性字典
    :param default_config: 默认配置
    :return: final_content_size_dict, final_row_height_dict, final_col_width_dict, 前者为每个单元格的大小，后者为每一行的高度、每一列的宽度
    """
    __skip_coord_list = []
    __cell_idx = 0
    final_content_size_dict, final_row_height_dict, final_col_width_dict = {}, dict([i, 0] for i in range(row_num)), dict([i, 0] for i in range(col_num))
    for i in range(row_num):
        for j in range(col_num):
            __curr_coord = f'{i}-{j}'
            # 如果当前单元格是被合并的，则跳过
            if __curr_coord in __skip_coord_list:
                continue

            # 计算内容的大小
            __curr_size = __get_content_size(
                ImageFont.truetype(table_attribute_dict[__curr_coord]['font_path'], table_attribute_dict[__curr_coord]['font_size']),
                cell_dict['content'][__cell_idx]
            )
            __curr_width_height = __get_cell_content_width_height(__curr_size, table_attribute_dict['newline_margin_rate'], table_attribute_dict['padding_h'], table_attribute_dict['padding_v'])
            final_content_size_dict[__curr_coord] = __curr_size

            # 处理合并单元格
            __row_combine, __col_combine = cell_merge_dict.get(__curr_coord, [0,0])
            # 计算每一行的最大高度、列的最大宽度，按照以下规则
            # 1. 没有合并的单元格参与行、列的最大高度、宽度计算
            # 2. 仅有按行合并的单元格，参与列最大宽度计算
            # 3. 仅有按列合并的单元格，参与行最大高度计算
            # 4. 既有行又有列合并的单元格，不参与计算
            if __row_combine + __col_combine == 0:
                final_row_height_dict[i] = max(final_row_height_dict[i], __curr_width_height[1]) # 行的高度
                final_col_width_dict[j] = max(final_col_width_dict[j], __curr_width_height[0]) # 列的宽度
            elif __row_combine > 0 and __col_combine == 0:
                final_col_width_dict[j] = max(final_col_width_dict[j], __curr_width_height[0]) # 列的宽度
            elif __row_combine == 0 and __col_combine > 0:
                final_row_height_dict[i] = max(final_row_height_dict[i], __curr_width_height[1]) # 行的高度

            # 向下合并行，下方单元格跳过
            __skip_coord_list.extend(f'{i+t}-{j}' for t in range(1, __row_combine+1))
            # 向右合并列，右侧单元格跳过
            __skip_coord_list.extend(f'{i}-{j+t}' for t in range(1, __col_combine+1))
            # 纵向、横向都有合并，跳过导致被合并的单元格
            __skip_coord_list.extend(f'{i+t_i}-{j+t_j}' for t_i in range(1, __row_combine+1) for t_j in range(1, __col_combine+1))
            # 单元格内容自增
            __cell_idx += 1

    # 考虑合并单元格的内容对行、列的大小影响。
    # 例如：0,1列有合并，则判断合并后的内容宽度是否小于0,1列的总宽度；若0,1列总宽度不满足，则0,1列都增加宽度。
    for __curr_coord, (__row_combine, __col_combine) in cell_merge_dict.items():
        # 合并单元格内容的宽度和高度
        __w, __h = __get_cell_content_width_height(final_content_size_dict[__curr_coord],
                                                   table_attribute_dict['newline_margin_rate'],
                                                   table_attribute_dict['padding_h'],
                                                   table_attribute_dict['padding_v'])
        i, j = map(int, __curr_coord.split('-'))
        # 合并行处理
        if __row_combine > 0:
            __combine_cell_height = sum(final_row_height_dict[i+t] for t in range(__row_combine +1 ))
            # 如果内容的高度大于合并后的高度，则每一行要分别增加高度
            if __h > __combine_cell_height:
                __diff_h = math.ceil((__h - __combine_cell_height) / (__row_combine + 1))
                for t in range(__row_combine + 1):
                    final_row_height_dict[i+t] += + __diff_h
        # 合并列处理
        if __col_combine > 0:
            __combine_cell_width = sum(final_col_width_dict[j+t] for t in range(__col_combine + 1))
            # 如果内容的宽度大于合并后的宽度，则每一列要分别增加宽度
            if __w > __combine_cell_width:
                __diff_w = math.ceil((__w - __combine_cell_width) / (__col_combine + 1))
                for t in range(__col_combine + 1):
                    final_col_width_dict[j+t] += __diff_w

    # 检查用户自定义列宽和行高是否满足内容的大小，若满足则使用用户自定义的列宽和行高，若不满足则使用计算的列宽和行高
    for __row, __height in row_height_dict.items():
        if __height > final_row_height_dict[__row]:
            final_row_height_dict[__row] = __height
        else:
            print(f'警告：用户自定义的行高【{__row} = {__height}】不满足内容的大小，忽略设置。')
    for __col, __width in col_width_dict.items():
        if __width > final_col_width_dict[__col]:
            final_col_width_dict[__col] = __width
        else:
            print(f'警告：用户自定义的列宽【{__col} = {__width}】不满足内容的大小，忽略设置。')

    return final_content_size_dict, final_row_height_dict, final_col_width_dict

def __get_table_cell_coord(start_x_pos:int, start_y_pos:int, row_num:int, col_num:int, content_size_dict:dict, row_height_dict:dict, col_width_dict:dict, cell_merge_dict:dict, table_attribute_dict:dict,  line_width:int):
    content_coord_list = []
    cell_retangle_list = []

    __y_pos = start_y_pos
    for i in range(row_num):
        __x_pos = start_x_pos
        __y_pos += row_height_dict[i-1] + line_width if i > 0 else 0
        for j in range(col_num):
            __idx = f'{i}-{j}'
            # 单元格x轴坐标更新
            __x_pos += col_width_dict[j-1] + line_width if j > 0 else 0
            # 被合并的单元格跳过
            if content_size_dict.get(__idx) is None:
                continue
            # 单元格矩形框的坐标
            __cell_rectange = [__x_pos, __y_pos, __x_pos + col_width_dict[j], __y_pos + row_height_dict[i]]
            # 获取合并单元格信息，若有合并单元格，调整宽度和高度
            __combine_row, __combine_col = cell_merge_dict.get(__idx, (0, 0))
            for idx in range(1, __combine_row+1):
                __cell_rectange[3] += row_height_dict[i+idx] + line_width
            for idx in range(1, __combine_col+1):
                __cell_rectange[2] += col_width_dict[j+idx] + line_width
            # 获取内容的坐标
            __content_coord = __get_multiline_content_coord(__cell_rectange, content_size_dict[__idx], table_attribute_dict['newline_margin_rate'], table_attribute_dict[__idx]['align_h'], table_attribute_dict[__idx]['align_v'])
            content_coord_list.append(__content_coord)
            cell_retangle_list.append(__cell_rectange)
    return cell_retangle_list, content_coord_list

def __draw_table(draw:ImageDraw.Draw, row_num:int, col_num:int, cell_dict:dict, rectangle_coord_list, content_coord_list, cell_attribute_dict:dict):
    __idx = 0
    for i in range(row_num):
        for j in range(col_num):
            __curr_coord = f'{i}-{j}'
            if cell_attribute_dict.get(__curr_coord) is None:
                continue
            __cell_rectange = rectangle_coord_list[__idx]
            __content_coord = content_coord_list[__idx]
            draw.rectangle(__cell_rectange, fill=cell_attribute_dict[__curr_coord]['back_color'])
            if len(cell_dict['content'][__idx].split('\n')) == 1:
                draw.text(__content_coord, cell_dict['content'][__idx],
                        font=ImageFont.truetype(cell_attribute_dict[__curr_coord]['font_path'], cell_attribute_dict[__curr_coord]['font_size']),
                        fill=cell_attribute_dict[__curr_coord]['fore_color'])
            else:
                # 需要考虑换行符的处理
                for __content, __coord in zip(cell_dict['content'][__idx].split('\n'), __content_coord):
                    draw.text(__coord, __content,
                        font=ImageFont.truetype(cell_attribute_dict[__curr_coord]['font_path'], cell_attribute_dict[__curr_coord]['font_size']),
                        fill=cell_attribute_dict[__curr_coord]['fore_color'])
            __idx += 1



def complex_table_pic(row_num:int, col_num:int, title_list:list, cell_dict:dict, font_path:str, img_path:str=None, footnote_list:list=[], col_width_dict:dict={},
        row_height_dict:dict={}, cell_merge_dict:dict={}, table_padding=30, table_line_width:int=3, table_line_color:str='#000000', pic_bk_color:str='#f1f2f6'):
    """
    生成复杂的二维表格图像，与 generate_table_pic() 函数不同，此函数不再区分表头部分和数据部分，统一视为单元格。
    :param row_num: int，表格的行数
    :param col_num: int，表格的列数
    :param title_list: list, 标题内容及属性列表。示例:
        - `[{'content': 'I am the main title'}, {'content': 'I am the subtitle'}]`
        - `[{'content': 'I am the main title', 'font_size': 40, 'color': '#000000', 'align': 'center'}, {'content': 'I am the subtitle', 'align':'right'}]`
    :param cell_dict: dict, 表格单元格内容及属性字典。示例：
            `{'content': ['Header1','Header2','Data1','Data2']}`
        `content`键包含表格所有单元格的内容，并且都是字符串类型。还包括以下可选的键：
            `font_path`, `font_size`, `back_color`, `fore_color`, `align_h`, `align_v`, `height`, `width`, `padding_h`, `padding_v`。
        取值示例：
            - `{'content': ['Header1','Header2','Data1','Data2'], 'back_color': {'r0': '#FFFF00'}, 'fore_color': {'c1':'#00FF00'}, 'align_h': {6: 'left'}}`
    :param font_path: str, 设置表格默认的字体文件路径
    :param img_path: str, 可选参数：设置保存图像的路径；如果设置为 None，则返回图像对象
    :param footnote_list: list, 可选参数，设置表格的脚注，取值方法同标题
    :param col_width_dict: dict, 可选参数，自定义列宽，示例：{0: 200} 表示第一列宽度为200像素。默认会根据文本内容自动计算合适的宽度。
    :param row_height_dict: dict, 可选参数，自定义行高，示例：{1: 80} 表示第二行高度为80像素。默认会根据文本内容自动计算合适的高度。
    :param cell_merge_dict: dict, 可选参数，设置合并单元格的信息。例如，{'0-0': [1,0], '0-5': [1, 2]} 表示坐标为 [0,0] 的单元格需向下合并1行；
        坐标为 [0,5] 的单元格向下合并1行，并向右合并2列；即共有6个单元格被合并。
    :param table_padding: int or dict, 可选参数，设置表格与图片的间距，默认为30
    :param table_line_width: int, 可选参数，设置表格线条的宽度，默认为3
    :param pic_bk_color: str, 可选参数，设置图片整个的背景色，默认为浅灰色：'#F1F2F6'
    :param table_line_color: str, 可选参数，设置表格线条的颜色，默认为黑色：'#000000'
    """
    # Deafault configuration value
    __default_config = __get_default_config()
    # 处理标题的属性
    __title_attribute_dict = __process_title_attribute(font_path, title_list, __default_config)
    # 计算标题的大小
    __title_content_size, __title_rectangle_size = __get_title_footnote_size(title_list, __title_attribute_dict)
    # 处理脚注的属性
    __footnote_attribute_dict = __process_footnote_attribute(font_path, footnote_list, __default_config)
    # 计算脚注的大小
    __footnote_content_size, __footnote_rectangle_size = __get_title_footnote_size(footnote_list, __footnote_attribute_dict)
    # 计算标题和脚注的宽度和高度
    # __title_footnote_size_dict = __get_title_footnote_size(font_path, title_list, footnote_list, __default_config)
    # 处理表格/单元格的属性
    __table_attribute_dict = __process_table_attribute(font_path, row_num, col_num, cell_dict, cell_merge_dict, __default_config)
    # 计算表格单元格以及行、列的宽度和高度
    __cell_content_size_dict, __row_height_dict, __col_width_dict = __get_table_size(row_num, col_num, cell_dict, cell_merge_dict, col_width_dict, row_height_dict, __table_attribute_dict, __default_config)
    # 开始计算图片的总大小
    # 1. 宽度=max(标题宽度, 表格宽度, 脚注宽度)；其中表格宽度需要额外加上：表格线的宽度，表格左侧左右的padding宽度
    # 2. 高度=sum(标题高度, 表格高度, 脚注高度)
    __table_padding_t = table_padding.get('padding_t', __default_config['table_padding']) if isinstance(table_padding, dict) else table_padding
    __table_padding_b = table_padding.get('padding_b', __default_config['table_padding']) if isinstance(table_padding, dict) else table_padding
    __table_padding_h = table_padding.get('padding_h', __default_config['table_padding']) if isinstance(table_padding, dict) else table_padding

    # 计算表格整体的大小(不考虑表格的上、下、左、右间距，考虑线的宽度)
    __table_size = [sum(__col_width_dict.values())+(col_num+1)*table_line_width, sum(__row_height_dict.values())+(row_num+1)*table_line_width]

    # 图片宽度=max(标题宽度, 表格宽度, 脚注宽度)；其中表格宽度需要额外加上表格左右两侧与图片边缘的间距
    __pic_width = max([rec[0] for rec in __title_rectangle_size] + [rec[0] for rec in __footnote_rectangle_size] + [__table_size[0] + __table_padding_h*2])
    __pic_height = sum([rec[1] for rec in __title_rectangle_size] + [rec[1] for rec in __footnote_rectangle_size] + [__table_size[1] + __table_padding_t + __table_padding_b])

    # 创建图片对象
    image = Image.new('RGB', (__pic_width, __pic_height), pic_bk_color)
    draw = ImageDraw.Draw(image)
    # 计算每个标题输出的坐标
    __title_coord_list, __y_pos = __get_title_footnote_coord(__pic_width, 0, __title_content_size, __title_rectangle_size, __title_attribute_dict)
    # 输出标题内容
    __draw_title_footnote(draw, __title_coord_list, title_list, __title_attribute_dict)
    # 计算表格的y轴开始位置（考虑标题的padding）
    __y_pos += __table_padding_t
    # ----------------------------------------------------------------------------------------
    # 表格的线和单元格的实现方式说明，以白色单元格和黑色边框的表格为例：
    # 1、计算表格的整体大小，绘制一个黑色背景的矩形
    # 2、然后再独立绘制白色背景的单元格矩形，就可实现绘制黑色边框的表格
    # 用此方法，可以省去计算每个边框线的坐标，也可以实现为不同的单元格填充不同的背景颜色
    # ----------------------------------------------------------------------------------------
    # 在整个图片的宽度下，计算整个表格输出位置坐标
    __table_x_pos = int((__pic_width - __table_size[0] - __table_padding_h*2)/2) + __table_padding_h
    draw.rectangle((__table_x_pos, __y_pos, __table_x_pos+__table_size[0], __y_pos+__table_size[1]), fill=table_line_color)
    # 单元格的开始坐标
    __x_pos = __table_x_pos + table_line_width
    __y_pos += table_line_width
    # 计算每个单元格矩形框的坐标，以及文本内容的坐标
    __cell_rectangle_coord_list, __cell_content_coord_list = __get_table_cell_coord(__x_pos, __y_pos, row_num, col_num, __cell_content_size_dict, __row_height_dict, __col_width_dict , cell_merge_dict, __table_attribute_dict, table_line_width)
    # 绘制单元格以及文本内容
    __draw_table(draw, row_num, col_num, cell_dict, __cell_rectangle_coord_list, __cell_content_coord_list, __table_attribute_dict)
    # 开始绘制脚注
    __y_pos += __table_size[1] + __table_padding_b
    __footnote_coord_list, __y_pos = __get_title_footnote_coord(__pic_width, __y_pos, __footnote_content_size, __footnote_rectangle_size, __footnote_attribute_dict)
    __draw_title_footnote(draw, __footnote_coord_list, footnote_list, __footnote_attribute_dict)
    # 如果有图片路径则保存，否则返回图片对象
    if img_path:
        image.save(img_path)
    else:
        return image
