from xlrd import open_workbook
import sqlite3
import os

db_filename = 'keywords.db'
schema_filename = 'keywords_schema.sql'
db_is_new = not os.path.exists(db_filename)

def remove_text_from_string(orig_str, to_be_removed_str):
    return orig_str[len(to_be_removed_str):]

def remove_empty_rows(column):
    final_ls = []
    for col in column:
        if (str(col).find('empty') == -1):
            final_ls.append(str(col))
            
    return final_ls

def reparse_keywords(keywords_column):
    ''' Keyword lists can be separated by a separator '|'. For this 
        reason we need to split them and create separate rows for them '''
    new_column = []
    for keyword_row in keywords_column:
        # Take the row and replace the '|' character with ','
        keyword_row_text = remove_text_from_string(str(keyword_row), "text:u'")
        kwrd_row_list = [s.strip() for s in keyword_row_text.replace('|', ',').split(',')]
        new_column.append(kwrd_row_list)
    
    return new_column

def init_connection():
    global db_filename
    with sqlite3.connect(db_filename) as conn:
        if db_is_new:
            print 'Creating schema'
            with open(schema_filename, 'rt') as f:
                schema = f.read()
                conn.executescript(schema)
        else:
            print 'Database exists, assume schema does, too.'


def write_table(table_name, column_name, data_list):
    global db_filename
    conn = sqlite3.connect(db_filename)
    
    sql_query = """insert into %s (%s) values('%s')""" % (table_name, column_name, data)

def read_excel(filename):
    ''' sl are service lines '''
    wb = open_workbook(filename)
    sheet0 = wb.sheet_by_index(0)
    
    sl1 = sheet0.col_slice(3,2)
    sl2 = sheet0.col_slice(4,2)
    sl3 = sheet0.col_slice(5,2)
    keywords = sheet0.col_slice(10, 2)

    sl1 = set(remove_empty_rows(sl1))
    sl2 = set(remove_empty_rows(sl2))
    sl3 = set(remove_empty_rows(sl3))
    keywords_column = remove_empty_rows(keywords)
    
    keywords_column = reparse_keywords(keywords_column)
            
    for keyword in keywords_column:
        print keyword
        
if __name__ == "__main__":
    read_excel('automapping.xls')
