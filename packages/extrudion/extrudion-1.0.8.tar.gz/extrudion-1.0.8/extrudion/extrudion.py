# Copyright 2023 Paride Azzari
#
# Licensed under the MIT License. See LICENSE

import pandas as pd

def analyzeDirectory(folder_path: str = '.', cut_off = True, sample_thickness = 10, save='') -> pd.DataFrame:
    '''
    Give a folder path as a relative or absolute path, the script will analyze all the .TAR files found in the directory and return a DataFrame containing the results.
    Leaving returns the Current Working Directory.
    '''
    from .files import Folder
    
    results = pd.DataFrame()
    
    try:
        files = Folder.getList(folder_path)
       
        for file in files:
            result = analyzeFile(file, folder_path, cut_off, sample_thickness)
            results = pd.concat([results, result])
            
        results.rename_axis(index='file')
        results.to_csv(folder_path+'/analysis.csv')
        return results
    except Exception as e:
        print(e)
    
        
    
def analyzeFile(filename:str, folder: str, cut_off: bool = True, sample_thickness = 10):
    '''
    Give a filename and a folder as a relative or absolute path, the script will analyze the .TAR files found and return a DataFrame containing the results.
    '''
    from .files import File
    from .stress import Stress
    file = File(filename, folder, sample_thickness)
    
    analysis = Stress(file, cut_off)
    
    analysis.plot()
    
    results = analysis.results
    results.index = [filename.replace('.TRA', '')]
    return results
