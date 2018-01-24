from ga import VARIABLES, BEHAVIOURS, GUARD, ACTION, init_model, to_plug
import sys
import main
import functools


def inc_action(var,c):
    c[var] = c[var] + 1

def reset_action(var,c):
    c[var] = 0

def add_counter(var, maximum, ga_model):
    ga_model[VARIABLES][var] = 0
    ga_model[BEHAVIOURS]["inc_" + var] = {
        GUARD: lambda c: c[var] < maximum,
        ACTION: functools.partial(inc_action, var)
    }
    ga_model[BEHAVIOURS]["reset_" + var] = {
        GUARD: lambda c: c[var] >= maximum,
        ACTION: functools.partial(reset_action, var)
    }

if __name__ == "__main__":
    ga_model = init_model()
    add_counter("a", 5, ga_model)
    add_counter("b", 10, ga_model)
#    add_counter("c", 3, ga_model)
#    add_counter("d", 15, ga_model)
    main.main(sys.argv[1:], to_plug(ga_model))
