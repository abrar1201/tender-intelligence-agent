array = [2, 1, 6, 4, 5, 3,-1]

# def max(arr):
#     i = 0
#     while i < len(arr) - 1:  
#         if arr[i] < arr[i + 1]:
#             del arr[i]       # delete element at index i
#             i=0
#         else:
#             del arr[i + 1]   # delete element at index i+1
#             i = 0
            
#         # check if length becomes 1
#         if len(arr) == 1:
#             print("Final remaining element:", arr[0])
#             return  # exit from function

#     # If loop ends with more than one element
#     print("Array after processing:", arr)
    

# max(array)

def min(arr):
    i = 0
    while i < len(arr) - 1:  
        if arr[i] < arr[i + 1]:
            del arr[i+1]       # delete element at index i
            i=0
        else:
            del arr[i]   # delete element at index i+1
            i = 0
            
        # check if length becomes 1
        if len(arr) == 1:
            print("Final remaining element:", arr[0])
            return  # exit from function

    # If loop ends with more than one element
    print("Array after processing:", arr)
    

min(array)
