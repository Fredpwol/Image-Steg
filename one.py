
count = 0

def findMissingSamples(numbers, missing, mean, values):
    global count
    if missing == 0:
        if (sum(numbers) / len(numbers)) == mean:
            return values
        return [0]
        
    for i in range(1, 6+1):
        temp_number = numbers + [i]
        res = findMissingSamples(temp_number, missing-1, mean, values + [i])
        count += 1
        if len(res) > 1  and res[0] != 0:
            return res
    return [0]


#3+6+1+2+4+5+1+2

missing = findMissingSamples([4, 4], 2, 5, [])

print(missing, count)
