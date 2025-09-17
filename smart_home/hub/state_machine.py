from transitions import Machine

class StateMachine:

    def __init__(self, model, states, initial_state, transitions):

        self.model = model
        self.machine = Machine(model=model, states=states, initial_state=initial_state, transitions=transitions)

    def add_transition(self, trigger, source, dest, **kwargs):
        self.machine.add_transition(trigger, source, dest, **kwargs)
