'''
Author: xinyan
Date: 2023-06-13 17:12:25
LastEditors: xinyan
LastEditTime: 2023-12-11 13:17:40
Description: file content
'''


import sys
from PIL import Image, ImageFont, ImageDraw


def __get_content_pos(rec_pos:list, content:str, font:ImageFont.FreeTypeFont, align:str='center'):
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

def __get_font(font_path:str=None, font_size:int=20):
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


def __generate_table_rec_coord(row_num:int, col_num:int, start_pos:list, margin:int=3, cell_width:int=150, cell_height:int=50,
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
        title_font = __get_font(font_path, title['font_size'])
        max_width = max(max_width, title_font.getbbox(title['content'])[2])
    for footnote in footnote_list:
        footnote_font = __get_font(font_path, footnote['font_size'])
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
            data_font = __get_font(font_path, __get_data_info(data_dict, 'font_size', i, j, 20, int))
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
    cell_pos_list, table_pos = __generate_table_rec_coord(row_num, col_num, start_pos=[table_margin, total_title_height], cell_width=cell_width, cell_height=cell_height,
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
        title_font = __get_font(font_path, title['font_size'])
        title_coord = __get_content_pos(title_rec_coord, title['content'], title_font, title['align'])
        draw.text(title_coord, title['content'], font=title_font, fill=title['color'])

    # Draw Header
    for idx, header_content in enumerate(header_dict['content']):
        header_rec_pos = cell_pos_list[idx]
        header_font = __get_font(font_path, header_dict.get('font_size', __default_header_font_size)) \
            if type(header_dict.get('font_size', __default_header_font_size)) == int \
            else __get_font(font_path, header_dict['font_size'].get(idx, __default_header_font_size))
        header_coord = __get_content_pos(header_rec_pos, header_content, header_font, header_dict.get('align', 'center')) \
            if type(header_dict.get('align', 'center')) == str \
            else __get_content_pos(header_rec_pos, header_content, header_font, header_dict['align'].get(idx, 'center'))
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
            data_font = __get_font(font_path, __get_data_info(data_dict, 'font_size', i, j, __default_data_font_size, int))
            data_coord = __get_content_pos(data_rec_coord, data_content, data_font, __get_data_info(data_dict, 'align', i, j, 'center', str))
            draw.text(data_coord, data_content, font=data_font, fill=__get_data_info(data_dict, 'fore_color', i, j, color_black, str))

    # Draw footnote
    tp_dict = {-1: table_pos[3] + table_margin}
    for idx, footnote in enumerate(footnote_list):
        footnote_rec_coord = [0, tp_dict[idx-1], pic_width, footnote['height'] + tp_dict[idx-1]]
        tp_dict[idx] = footnote_rec_coord[3]
        footnote_font = __get_font(font_path, footnote['font_size'])
        footnote_coord = __get_content_pos(footnote_rec_coord, footnote['content'], footnote_font, footnote['align'])
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




