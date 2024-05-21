from collections import Counter

def most_common_value(data):
    count = Counter(data)
    most_common = count.most_common(1)[0][0]
    return most_common

def closest_to_value(data, target):
    return min(data, key=lambda x: abs(x - target))

def closest_to_most_common(data):
    if not data:
        return None
    most_common = most_common_value(data)
    closest_value = closest_to_value(data, most_common)
    return closest_value

# مثال للاستخدام
data = [1, 2, 2, 3, 4, 4, 4, 5, 5, 6, 7]
closest_value = closest_to_most_common(data)
print(f"The closest value to the most common value is: {closest_value}")
