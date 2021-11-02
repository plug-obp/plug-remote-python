from obp2_soup_language import *
from obp2_language_server import server


def alice_bob_peterson():
    alice, bob = 'alice', 'bob'
    idmap = {alice: 0, bob: 1}
    init, wait, critical = 0, 1, 2

    def behavior(name, other):

        def i2wa(env):
            env['flag_'+name] = True
            env['turn'] = 1 - idmap.get(name)
            env[name] = wait
        i2w = Behavior(lambda env: env[name] == init, i2wa, name+"_wantsIn")

        def w2ca(env):
            env[name] = critical
        w2c = Behavior(
            lambda env: env[name] == wait and ((env['turn'] == idmap.get(name)) or (not env['flag_'+other])),
            w2ca,
            name + "_goesIn")

        def c2ia(env):
            env['flag_'+name] = False
            env[name] = init
        c2i = Behavior(
            lambda env: env[name] == critical,
            c2ia,
            name + "_getsOut")
        return [i2w, w2c, c2i]

    # make the soup
    soup = BehaviorSoup(
        Environment(
            {alice: 0, 'flag_'+alice: 1,
             bob: 2, 'flag_'+bob: 3,
             'turn': 4},
            [init, False, init, False, 0]),
        behavior(alice, bob) + behavior(bob, alice))

    # instantiate the TransitionRelation for the soup
    return soup_language_module(soup)


def example_extended_eval():
    # instantiate the model
    m = alice_bob_peterson()
    tr = m.transition_relation
    # get initial configurations
    i = list(tr.initial())[0]
    # get the first fireable transition from the initial configuration
    f = list(tr.actions(i))[0]
    # fire the transition
    result = tr.execute(i, f)
    targets = list(map(lambda f: f[0], result))
    payload = list(result)[0][1]

    print(f"symbol_table: {tr.soup.environment.symbols}\n"
          f"step = [\n"
          f"\tsource:{i},\n"
          f"\tfireableID:{f},\n"
          f"\tpayload:{payload},\n"
          f"\ttarget:{targets}\n]\n")

    # build the source and target evaluation environments
    s_e = Environment(tr.soup.environment.symbols, i)
    t_e = Environment(tr.soup.environment.symbols, list(targets)[0])

    # create the extended eval function
    evalf = lambda code: eval(code, globals(), {'s': s_e, 'a': tr.soup.behaviors[f], 'p': payload, 't': t_e})

    # the state of alice in the source
    code = 's.alice'
    print(f"eval('{code}') = {evalf(code)}")

    # the state of alice in the target
    code = 't.alice'
    print(f"eval('{code}') = {evalf(code)}")

    # the name of the fireable transition
    code = 'a.name'
    print(f"eval('{code}') = {evalf(code)}")

    # is the payload the one we expect?
    code = 'p == \'payload[alice_2wait]\''
    print(f"eval('{code}') = {evalf(code)}")

    code = 'p == \'payload[alice_wantsIn]\''
    print(f"eval('{code}') = {evalf(code)}")

    # does alice goes from state 0 to state 1 in this step?
    code = 's.alice == 0 and t.alice == 1'
    print(f"eval('{code}') = {evalf(code)}")

    # alice' = alice + 1
    code = 't.alice == s.alice + 1'
    print(f"eval('{code}') = {evalf(code)}")

    # rising edge on the alice flag
    code = 't.flag_alice and not s.flag_alice'
    print(f"eval('{code}') = {evalf(code)}")


if __name__ == "__main__":
    server(alice_bob_peterson)
    # example_extended_eval()


