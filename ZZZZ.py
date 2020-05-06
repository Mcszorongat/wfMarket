mat = [[1 ,2 ,3], [4, 5, 6], [7, 8, 9]]

print("\n_____________FIRST_____________\n")
for row in mat:
    for element in row:
        print(element)

print("\n_____________SECOND_____________\n")
for element in row:
    for row in mat:
        print(element)

print("\n_____________THIRD_____________\n")
[print(element) for row in mat for element in row]
