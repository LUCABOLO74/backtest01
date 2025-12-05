import pandas as pd
import yfinance as yf
from datetime import datetime

def calcola_guadagno_perdita(file_csv, data_trading):
    """
    Calcola il guadagno o la perdita per ogni titolo acquistato all'apertura
    e venduto alla chiusura in una data specifica.
    
    Args:
        file_csv (str): Path al file CSV con i ticker nella prima colonna
        data_trading (str): Data nel formato 'YYYY-MM-DD'
    
    Returns:
        pandas.DataFrame: DataFrame con i risultati
    """
    
    # Leggi il file CSV
    df = pd.read_csv(file_csv)
    
    # Estrai i ticker dalla prima colonna
    ticker_column = df.columns[0]
    tickers = df[ticker_column].dropna().unique()
    
    print(f"Analisi per la data: {data_trading}")
    print(f"Numero di titoli da analizzare: {len(tickers)}\n")
    
    risultati = []
    
    for ticker in tickers:
        try:
            # Scarica i dati per il ticker
            stock = yf.Ticker(ticker)
            
            # Ottieni i dati storici per la data specifica
            # Aggiungiamo un giorno extra per sicurezza
            data_obj = datetime.strptime(data_trading, '%Y-%m-%d')
            hist = stock.history(start=data_trading, end=pd.Timestamp(data_obj) + pd.Timedelta(days=2))
            
            if hist.empty:
                print(f"⚠️  {ticker}: Nessun dato disponibile per questa data")
                risultati.append({
                    'Ticker': ticker,
                    'Prezzo Apertura': None,
                    'Prezzo Chiusura': None,
                    'Guadagno/Perdita (%)': None,
                    'Guadagno/Perdita ($)': None,
                    'Status': 'Dati non disponibili'
                })
                continue
            
            # Prendi il primo giorno disponibile
            prezzo_apertura = hist['Open'].iloc[0]
            prezzo_chiusura = hist['Close'].iloc[0]
            
            # Calcola guadagno/perdita
            differenza_dollari = prezzo_chiusura - prezzo_apertura
            percentuale = (differenza_dollari / prezzo_apertura) * 100
            
            status = "Guadagno" if differenza_dollari > 0 else "Perdita" if differenza_dollari < 0 else "Pareggio"
            
            risultati.append({
                'Ticker': ticker,
                'Prezzo Apertura': round(prezzo_apertura, 2),
                'Prezzo Chiusura': round(prezzo_chiusura, 2),
                'Guadagno/Perdita (%)': round(percentuale, 2),
                'Guadagno/Perdita ($)': round(differenza_dollari, 2),
                'Status': status
            })
            
            print(f"✓ {ticker}: {status} di ${differenza_dollari:.2f} ({percentuale:.2f}%)")
            
        except Exception as e:
            print(f"❌ {ticker}: Errore - {str(e)}")
            risultati.append({
                'Ticker': ticker,
                'Prezzo Apertura': None,
                'Prezzo Chiusura': None,
                'Guadagno/Perdita (%)': None,
                'Guadagno/Perdita ($)': None,
                'Status': f'Errore: {str(e)}'
            })
    
    # Crea DataFrame con i risultati
    df_risultati = pd.DataFrame(risultati)
    
    # Salva i risultati in un nuovo CSV
    output_file = f'risultati_trading_{data_trading}.csv'
    df_risultati.to_csv(output_file, index=False)
    print(f"\n✓ Risultati salvati in: {output_file}")
    
    # Stampa statistiche generali
    print("\n" + "="*60)
    print("STATISTICHE GENERALI")
    print("="*60)
    df_validi = df_risultati[df_risultati['Guadagno/Perdita ($)'].notna()]
    
    if not df_validi.empty:
        guadagni = df_validi[df_validi['Guadagno/Perdita ($)'] > 0]
        perdite = df_validi[df_validi['Guadagno/Perdita ($)'] < 0]
        
        print(f"Titoli con guadagno: {len(guadagni)}")
        print(f"Titoli con perdita: {len(perdite)}")
        print(f"Guadagno/Perdita media: ${df_validi['Guadagno/Perdita ($)'].mean():.2f}")
        print(f"Percentuale media: {df_validi['Guadagno/Perdita (%)'].mean():.2f}%")
    
    return df_risultati


# Esempio di utilizzo
if __name__ == "__main__":
    # Esempio: specifica il path al tuo file CSV e la data
    file_csv = "raccomandazioni_analisti_bullish.csv"  # Modifica con il tuo file
    data = "2024-12-04"  # Modifica con la tua data (formato YYYY-MM-DD)
    
    # Esegui l'analisi
    risultati = calcola_guadagno_perdita(file_csv, data)
    
    # Mostra i primi risultati
    print("\nPrimi 10 risultati:")
    print(risultati.head(10).to_string(index=False))
