class Stress:
    import pandas as pd
    from .files import File
    
    def __init__(self, file: File, cut_off: bool = True, fit_window: int = 500):
        
        self.file = file
        self.data = self.file.data
        self.max_stress_index = self.maxStressIndex()
        
        if cut_off:
            self.cutOffData()

        self.fit_window = fit_window
        self.fit_results = self.getBestFit()
        self.results = self.getResults()
        
        
    def maxStressIndex(self):
        max_stress_row = self.data[self.data['stress'] == self.data['stress'].max()]
        return max_stress_row.index[0]
        
    def getResults(self) -> pd.DataFrame:
        import pandas as pd
        
        maxValues = self.data.iloc[self.max_stress_index]
        yieldValues = self.getYield()
        return pd.DataFrame({
            'Max Stress [kPa]': [maxValues['stress']],
            'Max Strain': [maxValues['strain']], 
            'Young Modulus [kPa]': [self.fit_results.slope],
            'Intercept [kPa]': [self.fit_results.intercept],
            'Yield Stress [kPa]': [yieldValues['stress']],
            'Yield Strain': [yieldValues['strain']],})
    

    def cutOffData(self):
        self.data = self.data.iloc[0:self.max_stress_index + 1]
        return None
    
    def getBestFit(self):
        import pandas as pd
        import numpy as np
        
        step = 10
        left = 0
        right = self.fit_window
    
        fit_results = pd.DataFrame()
        sizeData = len(self.data)

        while True:
            if right > sizeData: 
                break

            data = self.data[left:right]

            slope, intercept = np.polyfit(data['strain'], data['stress'], 1)

            y_exp = slope * data['strain'] + intercept
            error = (data['stress'] - y_exp)**2

            fit_results = pd.concat([fit_results, pd.DataFrame({'strain':  data[['strain']].iloc[int(self.fit_window / 2)].values, 'slope': slope, 'intercept': intercept, 'error': error.sum()})],axis=0)

            left += step
            right += step
            
        bestFit = fit_results[fit_results['error'] == fit_results['error'].min()].iloc[0]
        return bestFit
    
    def getYield(self):
        df = self.data.copy()
        df['error'] = abs(df['stress'] - (df['strain']-0.02)*self.fit_results.slope - self.fit_results.intercept)
        yieldValues = df[df['error'] == df['error'].min()].iloc[0]
        return yieldValues

    
    def plotBestFit(self):
        import matplotlib.pyplot as plt
        max_stress = self.data['stress'].max()
        max_strain = (max_stress - self.fit_results.intercept) / self.fit_results.slope
        strain_range = self.data[self.data['strain'] < max_strain]['strain']

        line = self.fit_results.slope * strain_range + self.fit_results.intercept
        other = self.fit_results.slope * (strain_range) + self.fit_results.intercept

        plt.plot(strain_range, line, linestyle='--')
        plt.plot(strain_range + 0.02, other, linestyle='dotted')
    
    
    def plot(self):
        import matplotlib.pyplot as plt
        plt.plot(self.data['strain'], self.data['stress'])
        plt.xlabel('Strain')
        plt.ylabel('Stress [kPa]')
        plt.title(self.file.filename)
        
        self.plotBestFit()
        self.plotMaxStress()
        self.plotYield()
        
        plt.legend(['Data', 'Young Modulus', 'Shift', 'Max Stress', 'Yield'])
        
        plt.savefig('data/plots/'+self.file.filename + '.png')
        plt.show()
        
        
    def plotMaxStress(self):
        import matplotlib.pyplot as plt
        x = self.results.iloc[0, 1]
        y = self.results.iloc[0, 0]
        plt.scatter(x, y, marker='o', color='blue')
    
    def plotYield(self):
        import matplotlib.pyplot as plt
        x = self.results.iloc[0, 5]
        y = self.results.iloc[0, 4]
        plt.scatter(x, y, marker='o', color='green')
