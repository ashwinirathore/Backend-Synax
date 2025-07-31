CREATE TABLE equities_ (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    nse_symbol VARCHAR(50) NOT NULL UNIQUE,
    bse_code VARCHAR(10) NOT NULL UNIQUE, 
    isin VARCHAR(12) NOT NULL UNIQUE
);


INSERT INTO equities_ (name, nse_symbol, bse_code, isin)
VALUES
    ('Reliance Industries Limited', 'RELIANCE', '500325', 'INE002A01018'),
    ('Tata Consultancy Services Ltd', 'TCS', '532540', 'INE467A01029'),
    ('HDFC Bank Limited', 'HDFCBANK', '500180', 'INE040A01034'),
    ('Infosys Limited', 'INFY', '500209', 'INE009A01021');
