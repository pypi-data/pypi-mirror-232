class Calculator:
    """Calculator class with all the basic calculation options."""

    def __init__(self):
        """Initiating instance values"""
        self.memory = 0

    def add(self, value: float):
        """Addition function."""
        if self.validate_user_input(value):
            self.memory += value
            self.return_answer(self.memory)

    def sub(self, value: float):
        """Subtraction function."""
        if self.validate_user_input(value):
            self.memory -= value
            self.return_answer(self.memory)

    def multi(self, value: float):
        """Multiplication function."""
        if self.validate_user_input(value):
            self.memory *= value
            self.return_answer(self.memory)

    def div(self, value: float):
        """Division function."""
        if self.validate_user_input(value):
            try:
                # Check for division by zero
                if value == 0:
                    print("Error: Can't divide by zero.")
                else:
                    self.memory /= value
                    self.return_answer(self.memory)
            except TypeError:
                print("Error: Input need to be number.")

    def root(self, value: float):
        """Root n of number."""
        if self.validate_user_input(value):
            try:
                if self.memory < 0:
                    print("Error: Can't pull out the n root of negative number.")
                else:
                    self.memory = self.memory ** (1 / value)
                    self.return_answer(self.memory)
            except TypeError:
                print("Error: Input need to be number.")

    def reset_memory(self):
        """Cleaning memory."""
        self.memory = 0
        self.return_answer(self.memory)

    def return_answer(self, memory: float):
        """Show user the result of calculations."""
        # Format to 2 decimals.
        self.memory = round(self.memory, 3)
        print(f"Memory: {self.memory:.3f}")

    @staticmethod
    def validate_user_input(value: float):
        """
        Validating user input,
        checking if it's correct
        and giving user feedback."""

        # Check if it's number.
        if isinstance(value, (int, float)):
            return value
        else:
            print("Error: Please provide number.")
            return
