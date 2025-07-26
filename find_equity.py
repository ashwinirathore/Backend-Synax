import os 
import psycopg2
from dotenv import load_dotenv
from fuzzywuzzy import fuzz

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
def find_equity_fuzzy(conn, user_input , threshold = 70):
    all_equities = fetch_all_equities(conn)
    matched_equity = []
    user_input_lower = user_input.lower()

    for equity in all_equities:
        name = equity['name'].lower()
        nse_symbol = equity['nse_symbol'].lower()

        score_name = fuzz.token_set_ratio(user_input_lower , name)
        score_nse_symbol = fuzz.token_set_ratio(user_input_lower , nse_symbol)
        score = max(score_name , score_nse_symbol)

        if score >= 70:
            equity['match_score'] = score
            matched_equity.append(equity)
    matched_equity.sort(key=lambda x:x['match_score'] , reverse= True)
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