# Περιγραφή: Αυτό το script υπολογίζει την απόδοση μιας στρατηγικής Dollar-Cost Averaging (DCA)
# για διάφορα κρυπτονομίσματα σε μια καθορισμένη χρονική περίοδο.
# Διαβάζει ιστορικά δεδομένα τιμών από αρχεία CSV, υπολογίζει τη συνολική επένδυση,
# την τελική αξία της επένδυσης και την απόδοση της επένδυσης (ROI).
# Τα αποτελέσματα εμφανίζονται σε μορφή πίνακα στην κονσόλα.
# LICENSE: GPL-3.0
# Copyright: Salih Emin
# Date: 2025-04-01
# Website: https://cerebrux.net
import pandas as pd
import os
from datetime import datetime
from tabulate import tabulate

# Λίστα συμβόλων και αντίστοιχων ονομάτων αρχείων CSV
symbols = ['BTC', 'ETH', 'LTC', 'XRP', 'ADA']
csv_files = {sym: f'data/{sym}.csv' for sym in symbols}

# Το μηνιαίο ποσό επένδυσης σε ευρώ
monthly_investment = 100

# Αποτελέσματα
results = []

for sym, path in csv_files.items():
    # Παράλειψη συμβόλων χωρίς αρχεία CSV
    if not os.path.exists(path):
        continue
    
    # Διάβασε το CSV και κάνε ανάλυση ημερομηνιών
    df = pd.read_csv(path, parse_dates=['Date'])
    
    # Ορισμός του index ως ημερομηνία
    df.set_index('Date', inplace=True)
    
    # Ταξινόμηση του index για να διασφαλιστεί ότι είναι μονοτονικός
    df.sort_index(inplace=True)
    
    # Φιλτράρισμα περιόδου Ιαν 2018 - Μαρ 2025
    start, end = '2018-01-01', '2025-03-31'
    df = df.loc[start:end]
    
    # Λήψη τιμών κλεισίματος στο τέλος κάθε μήνα
    monthly_close = df['Close'].resample('ME').last()
    
    # Υπολογισμός DCA: επένδυση κάθε μήνα
    coins_accumulated = (monthly_investment / monthly_close).cumsum()
    
    # Υπολογισμός συνολικών μηνών και τελικής τιμής
    total_months = len(monthly_close)
    total_invested = total_months * monthly_investment
    final_price = monthly_close.iloc[-1]
    
    # Υπολογισμός τελικής αξίας και ROI
    final_value = coins_accumulated.iloc[-1] * final_price
    roi = (final_value - total_invested) / total_invested * 100

    results.append({
        'Σύμβολο': sym,
        'Μήνες': total_months,
        'Τελική Τιμή (€)': round(final_price, 2),
        'Συγκεντρωμένα crypto': round(coins_accumulated.iloc[-1], 4),
        'Τελική Αξία Επένδυσης (€)': round(final_value, 2),
        'ROI (%)': round(roi, 2)
    })

# Δημιουργία DataFrame και εμφάνιση
results_df = pd.DataFrame(results)

print("\nΕπιδόσεις του DCA (Ιαν 2018 – Μαρ 2025)")
print(tabulate(
    results_df, 
    headers='keys', 
    tablefmt='grid', 
    numalign='right',
    stralign='center'
))

print("\nΑν σας άρεσε αυτό το εργαλείο, μπορείτε να κάνετε μια δωρεά:")
print("PayPal: https://www.paypal.me/cerebrux")
