import pandas as pd

KEY = '# killed'
GROUPS = ['Date of death', 'Status']
# GROUPS = ['Date of death', 'Sex']
# GROUPS = ['Date of death', 'Area']
# GROUPS = ['Date of death', 'Province']
# GROUPS = ['Date of death', 'Cause of Death']
def main(infile='data/deaths-in-syria.csv', outfile='data/counts.csv'):
    df = pd.read_csv(infile)
    df = df.rename(columns={'index': KEY})
    ix = df['Date of death'] > '1970-01-01'
    # ix = ix & (df['Status'] == 'Civilian')
    # 1/0
    df[ix].groupby(GROUPS).count()[KEY].unstack().to_csv(outfile, header=True)

if __name__ == '__main__':
    main()
