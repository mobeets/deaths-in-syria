import pandas as pd

KEY = '# killed'
def main(infile='data/deaths-in-syria.csv', outfile='data/counts.csv'):
    df = pd.read_csv(infile)
    df = df.rename(columns={'index': KEY})
    ix = df['Date of death'] > '1970-01-01'
    df[ix].groupby('Date of death').count()[KEY].to_csv(outfile, header=True)

if __name__ == '__main__':
    main()
