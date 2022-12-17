dprefix = '/home/examsection/Downloads/'

def verify_rollLists():
    import pandas as pd
    error_df = pd.read_excel(dprefix+'SampleRes.xlsx')
    gen_df = pd.read_excel(dprefix+'RollList(PHYSICS_I_I_2019_1_3.0_B).xlsx')
    error_df = error_df[gen_df['_merge']=='left_only']
    gen_df.drop(gen_df.loc[gen_df['RegNo'] in error_df['RegNo']], inplace=True)
    print("done")

verify_rollLists() 