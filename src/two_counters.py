import functools
from soup_language import *
from language_server import server


def two_counters(max=1):
    # create the two actions
    def inc(key, env):
        env[key] = env[key] + 1

    def reset(key, env):
        env[key] = 0

    # define the guard/action behaviors
    i0 = Behavior(lambda env: env['a'] < max, functools.partial(inc, 'a'), "a_inc")
    r0 = Behavior(lambda env: env['a'] >= max, functools.partial(reset, 'a'), "a_reset")

    i1 = Behavior(lambda env: env['b'] < max, functools.partial(inc, 'b'), "b_inc")
    r1 = Behavior(lambda env: env['b'] >= max, functools.partial(reset, 'b'), "b_reset")

    # make the soup
    soup = BehaviorSoup(Environment({'a': 0, 'b': 1}, [0, 0]), [i0, r0, i1, r1])

    # instantiate the TransitionRelation for the soup

    return LanguageModule(
        BehaviorSoupTransitionRelation(soup),
        BehaviorSoupRuntimeView(soup),
        BehaviorSoupAtomEvaluator(soup),
        BehaviorSoupMarshaller
    )

if __name__ == "__main__":
    server(lambda : two_counters(10))