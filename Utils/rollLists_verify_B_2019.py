dprefix = '/home/examsection/Downloads/'

def verify_rollLists():
    import pandas as pd
    f_name = 'RollList(PHYSICS_I_I_2019_1_3.0_B).xlsx'
    error_df = pd.read_excel(dprefix+'SampleRes.xlsx')
    gen_df = pd.read_excel(dprefix+f_name)
    error_df = error_df[error_df['_merge']=='left_only']
    for _,row in error_df.iterrows():
        gen_df = gen_df[gen_df['RegNo']!=row['RegNo']]
        
    gen_df.to_excel(dprefix+f_name, index=False)
    print("done")

verify_rollLists() 