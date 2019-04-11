from soup_language import *
from language_server import server


def alice_bob_unfair():
    init, wait, critical = 0, 1, 2

    def alice():

        def i2wa(env):
            env['flag_alice'] = True
            env['alice'] = wait
        i2w = Behavior(lambda env: env['alice'] == init, i2wa, "alice_wantsIn")

        def w2ca(env):
            env['alice'] = critical
        w2c = Behavior(
            lambda env: env['alice'] == wait and (not env['flag_bob']),
            w2ca,
            "alice_goesIn")

        def c2ia(env):
            env['flag_alice'] = False
            env['alice'] = init
        c2i = Behavior(
            lambda env: env['alice'] == critical,
            c2ia,
            "alice_getsOut")
        return [i2w, w2c, c2i]

    def bob():

        def i2wa(env):
            env['flag_bob'] = True
            env['bob'] = wait
        i2w = Behavior(lambda env: env['bob'] == init, i2wa, "bob_wantsIn")

        def w2ca(env):
            env['bob'] = critical
        w2c = Behavior(
            lambda env: env['bob'] == wait and (not env['flag_alice']),
            w2ca,
            "bob_goesIn")

        def w2ia(env):
            env['flag_bob'] = False
            env['bob'] = init
        w2i = Behavior(
            lambda env: env['bob'] == wait and env['flag_alice'],
            w2ia,
            "bob_givesUp"
        )

        def c2ia(env):
            env['flag_bob'] = False
            env['bob'] = init
        c2i = Behavior(
            lambda env: env['bob'] == critical,
            c2ia,
            "bob_getsOut")
        return [i2w, w2c, w2i, c2i]

    # make the soup
    soup = BehaviorSoup(
        Environment(
            {'alice': 0, 'flag_alice': 1,
             'bob': 2, 'flag_bob': 3},
            [init, False, init, False]),
        alice() + bob())

    # instantiate the TransitionRelation for the soup
    return LanguageModule(
        BehaviorSoupTransitionRelation(soup),
        BehaviorSoupRuntimeView(soup),
        BehaviorSoupAtomEvaluator(soup),
        BehaviorSoupMarshaller(soup)
    )

if __name__ == "__main__":
    server(alice_bob_unfair)



