# Περιγραφή: Αυτό το script υπολογίζει την απόδοση μιας στρατηγικής Dollar-Cost Averaging (DCA)
# για διάφορα κρυπτονομίσματα σε μια καθορισμένη χρονική περίοδο.
# Διαβάζει ιστορικά δεδομένα τιμών από αρχεία CSV, υπολογίζει τη συνολική επένδυση,
# την τελική αξία της επένδυσης, την απόδοση της επένδυσης (ROI), CAGR και Sharpe Ratio.
# Τα αποτελέσματα εμφανίζονται σε μορφή πίνακα στην κονσόλα.
# LICENSE: GPL-3.0
# Copyright: Salih Emin
# Date: 2025-04-01
# Website: https://cerebrux.net

import pandas as pd
import os
from datetime import datetime
from tabulate import tabulate

def calculate_max_drawdown(prices):
    """
    Υπολογισμός μέγιστης πτώσης (Max Drawdown) από τις τιμές κλεισίματος.
    """
    cumulative_max = prices.cummax()
    drawdown = (prices - cumulative_max) / cumulative_max
    max_drawdown = drawdown.min() * 100
    return round(max_drawdown, 2)

def calculate_cagr(initial_value, final_value, periods_years):
    """
    Υπολογισμός CAGR (Σύνθετος Ετήσιος Ρυθμός Ανάπτυξης)
    """
    if initial_value == 0 or periods_years == 0:
        return 0.0
    return ((final_value / initial_value) ** (1 / periods_years) - 1) * 100

def calculate_sharpe_ratio(returns, risk_free_rate=0.005):
    """
    Υπολογισμός Sharpe Ratio, με ετήσιο risk-free rate (π.χ. 0.5%)
    """
    excess_returns = returns - (risk_free_rate / 12)
    if excess_returns.std() == 0:
        return 0.0
    return (excess_returns.mean() / excess_returns.std()) * (12 ** 0.5)

# Λίστα συμβόλων και αντίστοιχων ονομάτων αρχείων CSV
symbols = ['BTC', 'ETH', 'LTC', 'XRP', 'ADA', 'Gold-PAXG']
csv_files = {sym: f'data/{sym}.csv' for sym in symbols}

# Το μηνιαίο ποσό επένδυσης σε ευρώ
monthly_investment = 100

# Αποτελέσματα
results = []

for sym, path in csv_files.items():
    if not os.path.exists(path):
        continue

    df = pd.read_csv(path, parse_dates=['Date'])
    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)

    # Φιλτράρισμα περιόδου Ιαν 2018 - Μαρ 2025
    start, end = '2018-01-01', '2025-03-31'
    df = df.loc[start:end]

    # Λήψη τιμών κλεισίματος στο τέλος κάθε μήνα
    monthly_close = df['Close'].resample('ME').last()

    # Υπολογισμός DCA: επένδυση κάθε μήνα
    coins_accumulated = (monthly_investment / monthly_close).cumsum()
    total_months = len(monthly_close)
    total_invested = total_months * monthly_investment
    final_price = monthly_close.iloc[-1]
    final_value = coins_accumulated.iloc[-1] * final_price
    roi = (final_value - total_invested) / total_invested * 100

    # Μέγιστη πτώση
    max_drawdown = calculate_max_drawdown(monthly_close)

    # CAGR
    years = total_months / 12
    cagr = calculate_cagr(total_invested, final_value, years)

    # Sharpe Ratio
    monthly_returns = monthly_close.pct_change().dropna()
    sharpe = calculate_sharpe_ratio(monthly_returns)

    results.append({
        'Σύμβολο': sym,
        'Μήνες': total_months,
        'Τελική Τιμή (€)': round(final_price, 2),
        'Συγκεντρωμένη ποσότητα': round(coins_accumulated.iloc[-1], 4),
        'Τελική Αξία Επένδυσης (€)': round(final_value, 2),
        'ROI (%)': round(roi, 2),
        'CAGR (%)': round(cagr, 2),
        'Sharpe Ratio': round(sharpe, 2),
        'Μέγιστη Πτώση (%)': max_drawdown
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
print("\n   PayPal: https://www.paypal.me/cerebrux\n")
# Εξαγωγή αποτελεσμάτων σε HTML με ενσωματωμένο CSS styling
html_style = """
<style>
    body {
        font-family: Arial, sans-serif;
        background-color: #f4f6f9;
        padding: 20px;
        color: #333;
    }
    h2 {
        color: #2c3e50;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        background-color: white;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    th {
        background-color: #34495e;
        color: white;
        padding: 10px;
        text-align: center;
    }
    td {
        padding: 8px;
        text-align: center;
        border-bottom: 1px solid #ddd;
    }
    tr:hover {
        background-color: #f1f1f1;
    }
</style>
"""

html_output = results_df.to_html(
    index=False,
    justify='center',
    border=0,
    float_format="%.2f"
)

with open("dca_results.html", "w", encoding="utf-8") as f:
    f.write("<html><head><meta charset='utf-8'><title>DCA Results</title>")
    f.write(html_style)
    f.write("</head><body>")
    f.write("<h2>Επιδόσεις του DCA (Ιαν 2018 – Μαρ 2025)</h2>")
    f.write(html_output)
    f.write("</body></html>")

print("Αποθηκεύτηκε αρχείο HTML με styling: dca_results.html")
