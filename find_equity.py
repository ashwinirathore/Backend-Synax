import difflib
def find_equity():
    user_input = input('enter a sentence: ')
    equities = [
        {'name': 'Reliance' , 'nse_symbol': 'JIO'} , 
        {'name': 'Tata' , 'nse_symbol': 'TATAMOTORS'},
        {'name': 'Infosys', 'nse_symbol': 'INFY'}
    ]
    user_input_lower = user_input.lower()
    empty_list = []
    for equity in equities:
        name_lower = equity['name'].lower()
        nse_symbol_lower = equity['nse_symbol'].lower()
        close_match = difflib.get_close_matches(user_input_lower , [name_lower , nse_symbol_lower] , n = 1 , cutoff= 0.6)
        if name_lower in close_match or nse_symbol_lower in close_match:
            empty_list.append(equity)
    return empty_list
result = find_equity()       
print(result) 