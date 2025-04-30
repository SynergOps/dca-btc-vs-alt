import pandas as pd
import os
import numpy as np
from datetime import datetime
from tabulate import tabulate

def calculate_max_drawdown(prices):
    cumulative_max = prices.cummax()
    drawdown = (prices - cumulative_max) / cumulative_max
    return round(drawdown.min() * 100, 2)

def calculate_cagr(final_value, net_invested, total_months):
    years = total_months / 12
    if net_invested <= 0 or years <= 0:
        return 0
    return round(((final_value / net_invested) ** (1 / years) - 1) * 100, 2)

def calculate_sharpe_ratio(returns, risk_free_rate=0):
    excess_returns = returns - risk_free_rate
    if excess_returns.std() == 0:
        return 0
    return round((excess_returns.mean() / excess_returns.std()) * np.sqrt(12), 2)

def calculate_sortino_ratio(returns, risk_free_rate=0):
    downside_returns = returns[returns < risk_free_rate]
    downside_std = downside_returns.std()
    if downside_std == 0:
        return 0
    return round((returns.mean() - risk_free_rate) / downside_std * np.sqrt(12), 2)

def calculate_calmar_ratio(cagr, max_drawdown):
    if max_drawdown == 0:
        return 0
    return round(cagr / abs(max_drawdown), 2)

# Ρυθμίσεις
symbols = ['BTC', 'ETH', 'LTC', 'XRP', 'ADA', 'Gold-PAXG']
csv_files = {sym: f'data/{sym}.csv' for sym in symbols}
monthly_investment = 100
fee_rate = 0.001

# Αποτελέσματα
results = []

for sym, path in csv_files.items():
    if not os.path.exists(path):
        continue

    df = pd.read_csv(path, parse_dates=['Date'])
    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)
    
    df = df.loc['2018-01-01':'2025-03-31']
    monthly_close = df['Close'].resample('ME').last().dropna()
    
    if len(monthly_close) < 2:
        continue

    net_monthly_investment = monthly_investment * (1 - fee_rate)
    coins_bought = net_monthly_investment / monthly_close
    coins_accumulated = coins_bought.cumsum()
    
    total_months = len(monthly_close)
    total_invested = total_months * monthly_investment

    final_price = monthly_close.iloc[-1]
    final_value = coins_accumulated.iloc[-1] * final_price
    roi = (final_value - total_invested) / total_invested * 100
    max_drawdown = calculate_max_drawdown(monthly_close)
    cagr = calculate_cagr(final_value, total_invested, total_months)

    # Μηνιαίες αποδόσεις για ratios
    returns = monthly_close.pct_change().dropna()
    sharpe = calculate_sharpe_ratio(returns)
    sortino = calculate_sortino_ratio(returns)
    calmar = calculate_calmar_ratio(cagr, max_drawdown)

    results.append({
        'Σύμβολο': sym,
        'Μήνες': total_months,
        'Τελική Τιμή (€)': round(final_price, 2),
        'Συγκεντρωμένη ποσότητα': round(coins_accumulated.iloc[-1], 4),
        'Τελική Αξία (€)': round(final_value, 2),
        'ROI (%)': round(roi, 2),
        'CAGR (%)': cagr,
        'Sharpe': sharpe,
        'Sortino': sortino,
        'Calmar': calmar,
        'Μέγιστη Πτώση (%)': max_drawdown
    })

# DataFrame & Εκτύπωση
results_df = pd.DataFrame(results)

print("\nΕπιδόσεις του DCA (Ιαν 2018 – Μαρ 2025)")
print(tabulate(
    results_df,
    headers='keys',
    tablefmt='grid',
    numalign='right',
    stralign='center'
))

# Εξαγωγή σε HTML
html_style = """
<style>
    body { font-family: Arial; background: #f8f9fa; padding: 20px; }
    h2 { color: #2c3e50; }
    table { border-collapse: collapse; width: 100%; background: white; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
    th { background: #2c3e50; color: white; padding: 10px; }
    td { padding: 8px; text-align: center; border-bottom: 1px solid #ddd; }
    tr:hover { background: #f1f1f1; }
</style>
"""

html_output = results_df.to_html(index=False, justify='center', border=0, float_format="%.2f")

with open("dca_results.html", "w", encoding="utf-8") as f:
    f.write("<html><head><meta charset='utf-8'><title>DCA Results</title>")
    f.write(html_style)
    f.write("</head><body>")
    f.write("<h2>Επιδόσεις του DCA (Ιαν 2018 – Μαρ 2025)</h2>")
    f.write(html_output)
    f.write("</body></html>")

print("\nΑποθηκεύτηκε αρχείο HTML: dca_results.html")
print("\nΑν σας άρεσε αυτό το εργαλείο, μπορείτε να κάνετε μια δωρεά:")
print("\n   PayPal: https://www.paypal.me/cerebrux\n")
