import pandas as pd
from regbot import signal

df = pd.read_csv('../reinforce/regbot_v63_training.csv')

y_pred = []
def getSignal(opening,a,b,ema_26,ema_12,macd,macdsignal,macd_histogram,low,grad_histogram,vol_pct_change,ratio4,rsi_05,rsi_15,sma_25,close_grad,close_grad_neg,grad_sma_25):
    
    args = [opening,a,b,ema_26,ema_12,macd,macdsignal,macd_histogram,low,grad_histogram,vol_pct_change,ratio4,rsi_05,rsi_15,sma_25,close_grad,close_grad_neg,grad_sma_25]
    try:
        return signal(*args)
    except Exception as e:
        print(e)

#print(df.head())
#print(df.columns)
df = df.sample(frac=1).reset_index(drop=True)
#print(df.head())
df = df[df['targets'] == 0].head(20)
#print(df.head())

df['result'] = df.apply(lambda row: getSignal(row['open'],row['a'],row['b'],
                                              row['ema-26'],row['ema-12'],row['macd'],
                                              row['macdsignal'],row['macd-histogram'],row['low'],
                                              row['grad-histogram'],row['vol-pct-change'],row['ratio4'],row['rsi-05'],
                                              row['rsi-15'],row['sma-25'],row['close-gradient'],row['close-gradient-neg'],row['grad-sma-25']), axis=1)

print(df.head())

print(len(df[df['result'] == df['targets']]), len(df))
