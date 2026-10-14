def read_number_in_range(prompt,end,start = 0):
    while True:
        number = input(prompt)
        if number.isdigit() and int(number) in range(start,end+1):
            return int(number)
        if not number.isdigit():
            print("Invalid data type, please enter a number")
        else:
            print("Invalid Input, your input out of range")