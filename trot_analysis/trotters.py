import pandas as pd
from trot_analysis import awards

class trotters(object):

    def __init__(self,fname,**kwargs):
        '''
        fname : csv with trotter data
        **kwargs : mostly passed to pd.read_csv with following exceptions
        column_renamer :
        '''
        self.fname = fname
        self.expected_columns = [
            "name","elevation_ft","time_m_s","mi1_pace","mi2_pace",
            "mi3_pace","final_bit","extra_distance"
            ]
        self.time_columns = ['time_m_s','mi1_pace','mi2_pace','mi3_pace','final_bit']
        self.reference_distance_mi = 3.1
        self.reference_distance_km = 5

        self.awards_list = [
            awards.mountain_climber, awards.flatlander, awards.steady_pacer,
            awards.strong_finisher, awards.speediest_trukey
        ]


        self._load_turkeys(**kwargs)
        self._find_winners()

    def _load_turkeys(self,**kwargs):
        '''
        loads and does some initial cleaning
        '''

        columns_rn = kwargs.pop('column_renamer',None)
        df = pd.read_csv(self.fname,**kwargs)
        if columns_rn is not None:
            df = df.rename(columns = columns_rn)
        self.df = self._validate_columns(df,columns_rn)
        self._process()

    def _validate_columns(self,df,columns_rn):

        missing = []
        for col in list(self.expected_columns):
            if col not in df.columns:
                missing.append(col)

        msg = f"trotter csv is missing some columns: {missing}"
        if len(df.columns) != len(self.expected_columns):
            raise KeyError(msg + ". Not enough columns")
        elif missing:
            raise KeyError(msg + ", use the 'column_renamer' argument to rename columns.")

        return df

    def _process(self):
        # convert all the time-like values ot time_deltas
        for col in self.time_columns:
            self.df[col] = self.df.apply(lambda row : self._validate_dt(row[col]), axis = 1)

        self.df['trimmed_time'] = self.df.apply(lambda row: self._trim_time(row),axis = 1)

    @staticmethod
    def _validate_dt(raw_dt_like):

        if pd.isnull(raw_dt_like):
            return pd.to_timedelta('00:00:00')

        try:
            clean_dt = pd.to_timedelta(raw_dt_like)
        except ValueError:
            dt_like = '00:'+str(raw_dt_like)
            clean_dt = pd.to_timedelta(dt_like)

        return clean_dt

    @staticmethod
    def _trim_time(row):
        dist = row['extra_distance']
        if dist > 0.:
            if row['final_bit'] > pd.to_timedelta('00:00:00'):
                pace = row['final_bit'] # seconds per mile
            else:
                pace = row['time_m_s'] / row['reference_distance_mi']
            extra_time = pace * dist
            return row['time_m_s'] - extra_time
        else:
            return row['time_m_s']

    def _find_winners(self):

        self.award_winners = [award(self.df) for award in self.awards_list]
