import matplotlib.pyplot as plt
import numpy as np

loss = []
triplet_acc = []
val_loss = []
val_triplet_acc = []
line_num = 1
with open('results224x1800v2.txt') as text_file:
    for line in text_file:
        line_num+=1
        if ("Beginning" in line) or ("None" in line) or ("Current" in line): continue
        line = line.rstrip('\n')
        line = line.split(' ')

        triplet_acc.append(line[10])
        val_triplet_acc.append(line[16])
        loss.append(line[7])
        val_loss.append(line[13])

def convert_strings_to_floats(input_array):
    output_array = []
    for element in input_array:
        if element == '':
            continue
        converted_float = float(element)
        output_array.append(converted_float)
    return output_array


loss = convert_strings_to_floats(loss)
print(loss)
triplet_acc = convert_strings_to_floats(triplet_acc)
print(triplet_acc)
val_loss = convert_strings_to_floats(val_loss)
print(val_loss)
val_triplet_acc = convert_strings_to_floats(val_triplet_acc)
print(val_triplet_acc)

print(len(val_loss))

indexes = []
for i in range(len(val_triplet_acc)):
    indexes.append(i)

print(indexes)
print(len(indexes))


d = 17

theta = np.polyfit(indexes, loss, deg=d)
theta2 = np.polyfit(indexes, val_loss, deg=d)
model = np.poly1d(theta)
model2 = np.poly1d(theta2)

plt.plot(indexes, loss, 'o', color='#4287f5', markersize=4)
plt.plot(indexes, val_loss, 'o', color='#2ec97c', markersize=4)
plt.plot(indexes, model(indexes), color='blue', label='loss', linewidth=2.0)
plt.plot(indexes, model2(indexes), color='green', label='val_loss', linewidth=2.0)
plt.title("Loss на 1861 фото, размер фото = 224x224px")
plt.xlabel("Количество эпох")
plt.ylabel("Loss")
plt.legend()
plt.show()

theta = np.polyfit(indexes, triplet_acc, deg=d)
theta2 = np.polyfit(indexes, val_triplet_acc, deg=d)
model = np.poly1d(theta)
model2 = np.poly1d(theta2)

plt.plot(indexes, triplet_acc, 'o', color='#f5427b', markersize=4)
plt.plot(indexes, val_triplet_acc, 'o', color='#f59c42', markersize=4)
plt.plot(indexes, model(indexes), color='red', label='triplet_acc', linewidth=2.0)
plt.plot(indexes, model2(indexes), color='orange', label='val_triplet_acc', linewidth=2.0)
plt.title("Accuracy на 1861 фото, размер фото = 224x224px")
plt.xlabel("Количество эпох")
plt.ylabel("Accuracy")
plt.legend()
plt.show()