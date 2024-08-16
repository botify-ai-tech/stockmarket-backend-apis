from BacktestMain.Models import Backtest
from TechnicalIndicator.SMA.main import Sma
from TechnicalAnalysis.CrossOver.main import CrossOver


class BacktestExecution:
    
    def __init__(self,backtest:Backtest) -> None:
        self.backtest = backtest
        
    def run(self):
        # array_length = (self.backtest.data.close)
        self.indicator_fast = Sma(data=self.backtest.data.close,period=12)
        self.indicator_slow = Sma(data=self.backtest.data.close,period=26)
        
        self.analysis = CrossOver(
            primary_array = self.indicator_fast,
            secondary_array = self.indicator_slow
        )
        
        row = 0
        while row != self.analysis.array_length:
            
            result = self.analysis.calculate()
            # result will be the index where crossover took Place.
            if result == -1:
                break
            else:
                # cross over
                strat_index = result 
                current_close = self.backtest.data.close[result] 
                taregt = self.calculate_taregt(current_close=current_close)
                stoploss = self.calculate_stoploss(current_close=current_close)
                row = self.check_target_stoploss(target=taregt,stoploss=stoploss,start_index=strat_index)
                
                if row == -1:
                    "No Exit"
                    "Add Square off Logic"
                    
                    break
                
                
        
        
    def calculate_taregt(self,current_close:float)->float:
        return current_close + ((self.backtest.parameters.target_percentage / current_close) * 100)
            
    def calculate_stoploss(self,current_close:float)->float:
        current_close - ((self.backtest.parameters.stoploss_percentage / current_close) * 100)
            
            
    def check_target_stoploss(self,target:float,stoploss:float,start_index:int=0)->int:
        
        while start_index != self.analysis.array_length:
            
            current_close = self.backtest.data.close[start_index] 
            if target >= current_close:
                """
                Create a way to determine target hit
                """
                return start_index

            elif stoploss >= current_close:
                """
                Create a way to determiine stoploss hit
                """
                return start_index
        else:
            return -1
                
            
        
            
        
        
        
        