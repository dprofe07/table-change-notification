import gspread
from gspread.utils import rowcol_to_a1


def get_cell_color(sheet, row, col):
    """Возвращает значение ячейки"""
    cell_ref = rowcol_to_a1(row, col)

    # Запрашиваем только нужную ячейку
    data = sheet.spreadsheet.fetch_sheet_metadata({
        'includeGridData': True,
        'ranges': [f"{sheet.title}!{cell_ref}"]
    })

    try:
        rgb = data['sheets'][0]['data'][0]['rowData'][0]['values'][0]
        rgb = rgb['effectiveFormat']['backgroundColor']
    except (KeyError, IndexError):
        return '#FFFFFF'
    if not rgb:
        return '#FFFFFF'

    # Конвертируем float (0-1) в HEX
    return '#{:02X}{:02X}{:02X}'.format(
        int(rgb.get('red', 0) * 255),
        int(rgb.get('green', 0) * 255),
        int(rgb.get('blue', 0) * 255)
    )

def get_cell_data(sheet, row, col):
    cell_ref = rowcol_to_a1(row, col)

    # Запрашиваем только нужную ячейку
    data = sheet.spreadsheet.fetch_sheet_metadata({
        'includeGridData': True,
        'ranges': [f"{sheet.title}!{cell_ref}"]
    })

    try:
        res = data['sheets'][0]['data'][0]['rowData'][0]['values'][0]
        res = res['effectiveValue']
    except (KeyError, IndexError):
        return None
    if len(res.items()) == 1:
        return res[list(res.keys())[0]]
    return res

