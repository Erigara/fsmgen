class FiniteStateMachine:
    """
    Example of concrete Finite State Machine implementation.
    """

    def __init__(self):
        self.state = "A"

    def tick(self, input):
        if self.state == "A":
            if input == 0:
                self.state = "D"
                return 2
            elif input == 1:
                self.state = "C"
                return 0
            elif input == 3:
                self.state = "B"
                return 1
            else:
                return None
        if self.state == "B":
            if input == 0:
                # Invade bug inside implementation
                # self.state = "A"
                return 1
            else:
                return None
        elif self.state == "C":
            if input == 1:
                return 1
            else:
                return None
        elif self.state == "D":
            if input == 1:
                self.state = "B"
                return 0
            elif input == 2:
                self.state = "A"
                return 1
            else:
                return None
        else:
            return None
