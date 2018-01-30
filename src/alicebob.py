from ga import VARIABLES, BEHAVIOURS, GUARD, ACTION, init_model, to_plug
import sys
import main
import functools

UP = 1
DOWN = 0

I = 0
W = 1
CS = 2

def to_w_action(prefix,c):
    c[prefix + "_s"] = W
    c[prefix + "_f"] = UP

def to_cs_action(prefix, c):
    c[prefix + "_s"] = CS

def to_i_action(prefix,c):
    c[prefix + "_s"] = I
    c[prefix + "_f"] = DOWN

def add_neighboor(me, other, ga_model):
    state = me + "_s"
    flag = me + "_f"
    ga_model[VARIABLES][state] = I
    ga_model[VARIABLES][flag] = DOWN

    ga_model[BEHAVIOURS][me + "_to_W"] = {
        GUARD: lambda c: c[state] == I,
        ACTION: functools.partial(to_w_action, me)
    }

    ga_model[BEHAVIOURS][me + "_to_CS"] = {
        GUARD: lambda c: c[state] == W and c[other+"_f"] != UP,
        ACTION: functools.partial(to_cs_action, me)
    }

    ga_model[BEHAVIOURS][me + "_to_I"] = {
        GUARD: lambda c: c[state] == CS,
        ACTION: functools.partial(to_i_action, me)
    }

if __name__ == "__main__":
    ga_model = init_model(globals())
    add_neighboor("alice", "bob", ga_model)
    add_neighboor("bob", "alice", ga_model)
    main.main(sys.argv[1:], to_plug(ga_model))
