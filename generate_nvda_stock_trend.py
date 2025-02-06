import matplotlib.pyplot as plt
import pandas as pd

# Simulated NVDA historical data for February 2025
data = {
    'Date': ["2025-01-15", "2025-01-22", "2025-01-29", "2025-02-05"],
    'Close Price': [123.43, 120.07, 118.65, 116.66]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Convert Date to datetime for better plotting
df['Date'] = pd.to_datetime(df['Date'])

# Plotting the stock price trend
plt.figure(figsize=(10, 6))
plt.plot(df['Date'], df['Close Price'], marker='o', linestyle='-', color='b')
plt.title('NVDA Stock Price Trend (January - February 2025)', fontsize=14)
plt.xlabel('Date', fontsize=12)
plt.ylabel('Close Price (USD)', fontsize=12)
plt.grid(True)
plt.savefig('nvda_stock_trend.png')
plt.show()