import pandas as pd
from regbot import signal

df = pd.read_csv('../reinforce/regbot_v60_training.csv')

y_pred = []
def getSignal(opening,high,a,b,vc,ema_26,ema_12,macd,macdsignal,macd_histogram,low,grad_histogram,close,vol_pct_change,rsi_05,rsi_15,sma_25,close_grad,close_grad_neg,grad_sma_25):
    
    args = [opening,high,a,b,vc,ema_26,ema_12,macd,macdsignal,macd_histogram,low,grad_histogram,close,vol_pct_change,rsi_05,rsi_15,sma_25,close_grad,close_grad_neg,grad_sma_25]
    try:
        return signal(*args)
    except Exception as e:
        print(e)

print(df.head())
print(df.columns)
df = df.sample(frac=1).reset_index(drop=True)
print(df.head())
df = df[df['targets'] == -1].tail(20)
print(df.head())

df['result'] = df.apply(lambda row: getSignal(row['open'], row['high'],row['a'],row['b'],
                                              row['vc'],row['ema-26'],row['ema-12'],row['macd'],
                                              row['macdsignal'],row['macd-histogram'],row['low'],
                                              row['grad-histogram'],row['close'],row['vol-pct-change'],row['rsi-05'],
                                              row['rsi-15'],row['sma-25'],row['close-gradient'],row['close-gradient-neg'],row['grad-sma-25']), axis=1)

print(df.head())

print(len(df[df['result'] == df['targets']]), len(df))
