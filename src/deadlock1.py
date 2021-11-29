from obp2_soup_language import *
from obp2_language_server import server


def deadlock1():
    def behavior():
        def inc_action(env):
            env['pc'] = env['pc'] + 1

        inc = Behavior(lambda env: env['pc'] < 2, inc_action, "inc")

        return [inc]

    # make the soup
    soup = BehaviorSoup(
        Environment(
            {'pc': 0},
            [0]),
        behavior()
    )

    # instantiate the TransitionRelation for the soup
    return soup_language_module(soup)


if __name__ == "__main__":
    server(deadlock1)
