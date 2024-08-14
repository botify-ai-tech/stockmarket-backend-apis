import numpy as np

class CrossOver:
    
    def __init__(self,primary_array:np.ndarray,secondary_array:np.ndarray,start_index:int=0) -> None:
        
        self.primary_array:np.ndarray = primary_array
        self.secondary_array:np.ndarray = secondary_array
        self.start_index = start_index
        self.array_length = len(self.primary_array)

    def calculate(self)->int:

        if self.primary_array.shape != self.secondary_array.shape:
            raise ValueError("Both arrays must have the same shape.")
        
        i = self.start_index + 1
        while self.primary_array[i-1] < self.secondary_array[i-1]:
            
            if i == self.array_length + 1:
                return -1
            
            i += 1    
    
        self.update_start_index(new_index=i)
        return i 

    def update_start_index(self,new_index:int)->None:
        self.start_index = new_index
        




if __name__ == '__main__':

    array1 = np.array([1, 2, 3, 4, 3, 2, 1, 2, 3, 4])
    array2 = np.array([2, 2, 2, 2, 2, 2, 2, 2, 2, 2])
    crossover_detector = CrossOver(
        primary_array=array1,
        secondary_array=array2
    )
    response = 0
    while response != -1:
        response = crossover_detector.calculate()
        print(response)
