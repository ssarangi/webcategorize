import string

class StringUtils:
    @staticmethod
    def remove_text_from_string(orig_str, to_be_removed_str):
        new_str = orig_str[len(to_be_removed_str):]
        new_str = new_str.replace("'", " ").strip()
        return new_str
    
    @staticmethod
    def remove_empty_rows(column):
        final_ls = []
        for col in column:
            if (str(col).find('empty') == -1):
                final_ls.append(str(col))
                
        return final_ls
    
    @staticmethod
    def reparse_keywords(keywords_column):
        ''' Keyword lists can be separated by a separator '|'. For this 
            reason we need to split them and create separate rows for them '''
        new_column = []
        for keyword_row in keywords_column:
            # Take the row and replace the '|' character with ','
            keyword_row_text = StringUtils.remove_text_from_string(str(keyword_row), "text:u'")
            kwrd_row_list = [s.strip() for s in keyword_row_text.replace('|', ',').split(',')]
            new_column.append(kwrd_row_list)
        
        return new_column
    
    @staticmethod
    def add_quotes(string_list):
        new_str = []
        for string in string_list:
            string = "'" + string + "'"
            new_str.append(string)
        
        return new_str
    
    @staticmethod
    def get_word_frequency(orig_string, split_separator):
        ''' Calculate the Keyword Statistics '''
        # orig_string: Original String
        # split_separator: Word used to split the string
        #try:
        return len(orig_string.split(split_separator)) - 1    
        