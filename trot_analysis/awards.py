import pandas as pd
import numpy as np

class base_award(object):
    def __init__(self,name,df):
        self.name = name
        self.winner = None
        self.winner_stat = None
        self.winner_record = None
        self.process_award(df)

    def process_award(self,df):
        self.find_winner(df)
        self.display_winner()

    def find_winner(self, df):
        # implement in sub-awards!
        pass

    def display_winner(self):
        if self.winner is not None:
            msg = f"\n\nThe winner of the {self.name} award is {self.winner} with {self.winner_stat}"
            print(msg)

class simple_minmax(base_award):

    def __init__(self, name, df, column, min_or_max):
        self.column_to_use = column
        self.min_or_max = min_or_max
        super().__init__(name, df)


    def find_winner(self, df):
        col = self.column_to_use
        if self.min_or_max =='min':
            min_or_max = df[col].min()
        else:
            min_or_max = df[col].max()
        self.winner_record = df[df[col] == min_or_max]
        self.winner = self.winner_record.name.values[0]
        self.winner_stat = self.winner_record[col].values[0]

class mountain_climber(simple_minmax):
    def __init__(self, df):
        super().__init__('Mountain Climber',df,'elevation_ft','max')


class speediest_trukey(simple_minmax):
    def __init__(self, df):
        super().__init__('Speediest Turkey',df,'trimmed_time','min')

    def find_winner(self, df):
        super().find_winner(df)
        self.winner_stat = self.winner_record['trimmed_time']

class flatlander(simple_minmax):
    def __init__(self, df):
        super().__init__('Flatlander',df,'elevation_ft','min')


class steady_pacer(base_award):

    def __init__(self,df):
        super().__init__('Steady Pacer',df)

    def _get_paces(self,row, convert_to_s = True):
        cols = ['mi1_pace','mi2_pace','mi3_pace','final_bit']
        if convert_to_s:
            return [i.total_seconds() for i in row[cols]]
        else:
            return row[cols]

    def _pace_std(self,row):
        return np.std(self._get_paces(row))

    def find_winner(self, df):
        df0 = df[df.mi2_pace > pd.to_timedelta('00:00:00')].copy(deep=True)
        df0['std_vals'] = df0.apply(lambda row : self._pace_std(row),axis = 1)
        self.winner_record = df0[df0['std_vals'] == df0['std_vals'].min()]
        self.winner = self.winner_record.name.values[0]
        paces =  self._get_paces(self.winner_record,convert_to_s=False)
        self.winner_stat = [self.winner_record.std_vals.values[0],paces]

class strong_finisher(base_award):

    def __init__(self,df):
        super().__init__('Strong Finisher',df)

    def _get_paces(self,row, convert_to_s = True):
        cols = ['mi1_pace','mi2_pace','mi3_pace']
        if convert_to_s:
            return [i.total_seconds() for i in row[cols]]
        else:
            return row[cols]

    def _pace_std(self,row):
        mean_pace = np.mean(self._get_paces(row))
        final_pace = row['final_bit'].total_seconds()
        return (mean_pace - final_pace) / mean_pace * 100

    def find_winner(self, df):
        df0 = df[df.mi2_pace > pd.to_timedelta('00:00:00')].copy(deep=True)
        df0['pace_increase'] = df0.apply(lambda row : self._pace_std(row),axis = 1)
        self.winner_record = df0[df0['pace_increase'] == df0['pace_increase'].max()]
        self.winner = self.winner_record.name.values[0]
        paces =  self._get_paces(self.winner_record,convert_to_s=False)
        self.winner_stat = [
                            self.winner_record.pace_increase.values[0],
                            paces,
                            self.winner_record.final_bit.values[0]
                        ]
