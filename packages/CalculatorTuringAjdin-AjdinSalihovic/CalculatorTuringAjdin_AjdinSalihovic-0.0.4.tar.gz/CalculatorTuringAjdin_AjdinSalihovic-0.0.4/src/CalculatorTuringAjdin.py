'''
Student: Ajdin Salihovic
Class: Python Mastery
'''

class calculator:
    def __init__(self):
       self.memory = 0

# This function is for adding two numbers
    def add(self, x, y):
        return x + y

# This function is for subtracting two numbers
    def subtract(self, x, y):
        return x - y

# This function is for multiplying two numbers
    def multiply(self, x, y):
        return x * y

# This function is for dividing two numbers
    def divide(self, x, y):
        return x / y

# This takes (n) root of a number.
    def n_root(self, x, y):
        return x ** (1 / y)

# Function to reset memory to zero
    def reset_memory(self):
        self.memory = 0

    def run_calculator(self):
        print("Select operation.")
        print("1. Add +")
        print("2. Subtract -")
        print("3. Multiply *")
        print("4. Divide /")
        print("5. Takes (n) root of a number **")
        print("6. Reset Memory")

        while True:
            choice = input("Please choose (1/2/3/4/5/6): ")

            if choice in ('1', '2', '3', '4', '5'):
                try:
                    num1 = float(input("Enter the first number: "))
                    num2 = float(input("Enter the second number: "))
                except ValueError:
                    print("Invalid input. Please enter a number.")
                    continue

                if choice == '1':
                    print(num1, "+", num2, "=", self.add(num1, num2))
                    self.memory = self.add(num1, num2)

                elif choice == '2':
                    print(num1, "-", num2, "=", self.subtract(num1, num2))
                    self.memory = self.subtract(num1, num2)

                elif choice == '3':
                    print(num1, "*", num2, "=", self.multiply(num1, num2))
                    self.memory = self.multiply(num1, num2)

                elif choice == '4':
                    print(num1, "/", num2, "=", self.divide(num1, num2))
                    self.memory = self.divide(num1, num2)

                elif choice == '5':
                    print(num1, "**(1/", num2, ")", "=", self.n_root(num1, num2))
                    self.memory = self.n_root(num1, num2)

            elif choice == '6':
                self.reset_memory()
                print("Memory has been reset to 0.")

            else:
                print("Invalid choice. Please choose (1/2/3/4/5/6).")

            # check if user wants another calculation
            # break the while loop if answer is no
            next_calculation = input("Let's do the next calculation? (yes/no): ")
            if next_calculation == "no":
                break

if __name__ == "__main__":
    calculator = calculator()
    calculator.run_calculator()
