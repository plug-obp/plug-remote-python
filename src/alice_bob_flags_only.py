from soup_language import *
from language_server import server


def alice_bob_flags_only():
    alice, bob = 'alice', 'bob'
    init, wait, critical = 0, 1, 2

    def behavior(name, other):

        def i2wa(env):
            env['flag_'+name] = True
            env[name] = wait
        i2w = Behavior(lambda env: env[name] == init, i2wa, name+"_wantsIn")

        def w2ca(env):
            env[name] = critical
        w2c = Behavior(
            lambda env: env[name] == wait and (not env['flag_'+other]),
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
             bob: 2, 'flag_'+bob: 3},
            [init, False, init, False]),
        behavior(alice, bob) + behavior(bob, alice))

    # instantiate the TransitionRelation for the soup
    return LanguageModule(
        BehaviorSoupTransitionRelation(soup),
        BehaviorSoupRuntimeView(soup),
        BehaviorSoupAtomEvaluator(soup),
        BehaviorSoupMarshaller(soup)
    )

if __name__ == "__main__":
    server(alice_bob_flags_only)



