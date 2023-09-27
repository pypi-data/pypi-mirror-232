import numpy as np
# sqlalchemy < 2.0
from sqlalchemy import create_engine
from typing import Optional
import yaml
from datetime import datetime
import pandas as pd


def load_db_config(yaml_file_name, database):
    with open(yaml_file_name, 'r') as stream:
        config = yaml.safe_load(stream)
    return config[database]

def connect_to_db(cfg):
    return create_engine(str(r"mysql+mysqldb://%s:" + '%s' + "@%s:%s/%s") % 
                         (cfg['user'], cfg['password'], cfg['host'], cfg['port'], cfg['database']))

def clean_dataframe(df): 
    for col in df.select_dtypes(include=[np.number]).columns:  
        df[col].replace([np.inf, -np.inf], 0, inplace=True)

def execute_sql(engine, sql_statement):
    with engine.connect() as conn:
        conn.execute(sql_statement)

def update_data(raw_df, yaml_file_name, database, table, add_data=True, 
                df_date_col: Optional[str] = None, 
                db_date_col: Optional[str] = None):
    
    df = raw_df.copy()
    cfg = load_db_config(yaml_file_name, database)
    engine = connect_to_db(cfg)
    
    if df.shape[0] == 0:
        raise ValueError("Imported dataset is empty.")
    
    clean_dataframe(df)

    if add_data:
        df.to_sql(table, engine, if_exists='append', index=False)
        print_action_result(table, "added", df, df_date_col)
    elif df_date_col:
        start_date= min(df[df_date_col])
        end_date = max(df[df_date_col])
        df = df[(df[df_date_col]>=start_date)&(df[df_date_col]<=end_date)]
        try:
            df.to_sql(table, engine, if_exists='append', index=False)
        except Exception as e:
            raise ValueError(f"{e}")
        else:
            delete_sql = f"DELETE FROM {table} WHERE {db_date_col} BETWEEN '{start_date}' AND '{end_date}'"
            execute_sql(engine, delete_sql)
            df.to_sql(table, engine, if_exists='append', index=False)
            print_action_result(table, "updated", df, df_date_col)
    else:
        back_up_df = pd.read_sql(f"SELECT * FROM {table}", engine)
        back_up_df.to_sql("bk_up_" + table, engine, if_exists='append', index=False)
        try:
            df.to_sql(table, engine, if_exists='append', index=False)
        except Exception as e:
            raise ValueError(f"{e}")
        else:
            delete_sql = f"DELETE FROM {table}"
            execute_sql(engine, delete_sql)
            df.to_sql(table, engine, if_exists='append', index=False)
            print_action_result(table, "copied, cleared and updated", df, df_date_col)
    

def print_action_result(table, action, df, df_date_col):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    if df_date_col:
        date_range = f"{df[df_date_col].min()} to {df[df_date_col].max()}"
        print(f"{table} data has been {action}: {current_time}\nData date range: {date_range}")
    else:
        print(f"{table} data has been {action}: {current_time}")