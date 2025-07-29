import unittest
from find_equity import best_Similarity_score , find_equity_fuzzy


class Test_best_similarity_score(unittest.TestCase):


    def test_exact_match(self):
        result = best_Similarity_score("Reliance" , "Reliance" ,"RELIANCE")
        self.assertEqual(result['best_score'] , 100)
        self.assertIn("fuzz" , result['best_method'])
        print('\n Exact Method:' , result)

    def test_partial_match(self):
        result = best_Similarity_score("Rel", "Reliance"  , "RELIANCE")
        self.assertGreater(result['best_score'] , 50)
        print('\n Partial Match: ', result)
    def test_no_match(self):
        result = best_Similarity_score('Abcd' , "Reliance" , "RELIANCE")
        self.assertLess(result['best_score'] , 50)
        print('\n No match: ' , result)




class Test_find_equity_fuzzy(unittest.TestCase):
    def test_find_equity_with_fake_data(self):
        class FakeConn:
            pass

        def fake_fetch_all_equities(conn):
            return [
                {'id': 1, 'name': 'Reliance Industries Limited', 'nse_symbol': 'RELIANCE', 'bse_code': '500325', 'isin': 'INE002A01018'},
                {'id': 2, 'name': 'Tata Motors', 'nse_symbol': 'TATAMOTORS', 'bse_code': '500570', 'isin': 'INE155A01022'},
            ]
        
        import find_equity

        find_equity.fetch_all_equities = fake_fetch_all_equities
        result = find_equity_fuzzy(FakeConn() , "Reliance")
        self.assertEqual(result[0]['name'] , "Reliance Industries Limited")
        self.assertGreater(result[0] ['match_score'] , 70)
        print("/n Results: " , result)

        
