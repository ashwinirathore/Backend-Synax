import os 
import psycopg2
from dotenv import load_dotenv
from fuzzywuzzy import fuzz
from polyfuzz import PolyFuzz
from rapidfuzz import fuzz as rf
from difflib import SequenceMatcher
import textdistance

load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

def fetch_all_equities(conn):
    cur = conn.cursor()
    equities = []
    try:
        select_query = '''
        SELECT id , name , nse_symbol , bse_code , isin
        FROM equities_;
    '''
        cur.execute(select_query)
        rows = cur.fetchall()
        col_names = [descr[0] for descr in cur.description]
        for row in rows:
            equities.append(dict(zip(col_names , row)))
    except psycopg2.Error as e:
        print(f"Error fetching all equities: {e}")
    finally:
        cur.close()
    return equities


def best_Similarity_score(user_input,name,nse_symbol):
    user_input_lower = user_input.lower()
    name = name.lower()
    nse_symbol = nse_symbol.lower()


    best_score = 0
    best_method = ''

    def check(score,method):
        nonlocal best_score , best_method
        if score > best_score:
            best_score = score
            best_method = method



    #The Fuzzwuzzy
    check(fuzz.token_set_ratio(user_input_lower, name), "name_set_ratio_fuzz")
    check(fuzz.token_set_ratio(user_input_lower, nse_symbol), "nse_set_ratio_fuzz")
    check(fuzz.ratio(user_input_lower, name), "name_ratio_fuzz")
    check(fuzz.ratio(user_input_lower, nse_symbol), "nse_ratio_fuzz")
    check(fuzz.partial_ratio(user_input_lower, name), "name_partial_fuzz")
    check(fuzz.partial_ratio(user_input_lower, nse_symbol), "nse_partial_fuzz")
    check(fuzz.token_sort_ratio(user_input_lower, name), "name_token_sort_fuzz")
    check(fuzz.token_sort_ratio(user_input_lower, nse_symbol), "nse_token_sort_fuzz")

    # RapidFuzz
    check(rf.token_set_ratio(user_input_lower, name), "name_set_ratio_rapid")
    check(rf.token_set_ratio(user_input_lower, nse_symbol), "nse_set_ratio_rapid")
    check(rf.ratio(user_input_lower, name), "name_ratio_rapid")
    check(rf.ratio(user_input_lower, nse_symbol), "nse_ratio_rapid")

    # Difflib
    check(SequenceMatcher(None, user_input_lower, name).ratio() * 100, "name_difflib")
    check(SequenceMatcher(None, user_input_lower, nse_symbol).ratio() * 100, "nse_difflib")


    # TextDistance
    check(textdistance.levenshtein.normalized_similarity(user_input_lower, name) * 100, "name_textdistance")
    check(textdistance.levenshtein.normalized_similarity(user_input_lower, nse_symbol) * 100, "nse_textdistance")

    # PolyFuzz
    model = PolyFuzz("TF-IDF")
    model.match([user_input_lower], [name])
    check(model.get_matches()["Similarity"][0] * 100, "name_polyfuzz")
    model.match([user_input_lower], [nse_symbol])
    check(model.get_matches()["Similarity"][0] * 100, "nse_polyfuzz")

    return {"best_score": best_score, "best_method": best_method}





def find_equity_fuzzy(conn,user_input , threshold = 70):
    all_equities = fetch_all_equities(conn)
    matched_equity = []

    for equity in all_equities:
        name = equity['name'].lower()
        nse_symbol = equity['nse_symbol'].lower()
        result = best_Similarity_score(user_input , equity['name'], equity['nse_symbol'])
        if result['best_score'] >= threshold:
            equity['match_score'] = result['best_score'] 
            equity['match_method'] = result['best_method']
            matched_equity.append(equity)
    matched_equity.sort(key=lambda x: x['match_score'], reverse=True)
    return matched_equity        




def test_db_connection():
    conn = None
    try:
        conn = psycopg2.connect(database = DB_NAME,
                                user = DB_USER,
                                password = DB_PASSWORD,
                                host = DB_HOST,
                                port = DB_PORT)
        print('Database is succesfully connected.')
    except psycopg2.Error as e:
        print(f"Database not connected successfully. Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print('Database connection is closed')    
if __name__ == '__main__':
    test_db_connection()
    conn = psycopg2.connect(database = DB_NAME,
                            user = DB_USER, 
                            password = DB_PASSWORD, 
                            host = DB_HOST, 
                            port = DB_PORT)
    user_input = input('Enter a sentence with your equity name or NSE symbol:')
    result = find_equity_fuzzy(conn , user_input)
    print('Result:' , result)
    conn.close()