import pandas as pd
from sklearn.linear_model import LinearRegression

def generate_forecast(df, days_ahead=90):
    """
    Fits a linear regression on daily expenditures to forecast future spend.
    Returns a dataframe of actuals + predicted future monthly points.
    """
    if len(df) < 5:
        return None, None
        
    df = df.copy()
    
    # We aggregate by month for smoother predictions
    df['month'] = df['date'].dt.to_period('M')
    monthly_spend = df.groupby('month')['amount'].sum().reset_index()
    monthly_spend['month_dt'] = monthly_spend['month'].dt.to_timestamp()
    monthly_spend['month_num'] = (monthly_spend['month_dt'].dt.year - 2000) * 12 + monthly_spend['month_dt'].dt.month
    
    if len(monthly_spend) < 3:
        # Fall back to daily if dataset is short
        df['day_num'] = (df['date'] - df['date'].min()).dt.days
        X = df[['day_num']]
        y = df['amount']
        
        model = LinearRegression()
        model.fit(X, y)
        
        # future 3 months roughly
        future_days = [[df['day_num'].max() + i] for i in range(1, days_ahead)]
        pred = model.predict(future_days)
        
        # Return generic metrics
        next_month_total = pred[:30].sum() if len(pred) >= 30 else sum(pred)
        return next_month_total, []
        
    # Fit monthly
    X = monthly_spend[['month_num']]
    y = monthly_spend['amount']
    
    model = LinearRegression()
    model.fit(X, y)
    
    last_month_num = monthly_spend['month_num'].max()
    future_X = pd.DataFrame({'month_num': [last_month_num + i for i in range(1, 4)]})
    future_Y = model.predict(future_X)
    
    predictions = []
    base_date = monthly_spend['month_dt'].max()
    for i, val in enumerate(future_Y):
        target_date = base_date + pd.DateOffset(months=i+1)
        predictions.append({
            'month': target_date.strftime('%b %Y'),
            'amount': max(0, val) # clamp to 0
        })
        
    # Returns (Total next month, List of next 3 months predictions)
    return predictions[0]['amount'] if predictions else 0, predictions
