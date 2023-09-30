from routy.plotUtilities.plotRoute import plot_route, plot_multiple_routes_for_same_coordinates


class Comparison:
    """
    Instantiate a comparison operation.
    Numbers will be multiplied by the given multiplier.

    :param multiplier: The multiplier.
    :type multiplier: int
    """

    def __init__(self):
        pass

    def plot_route(self, coordinates, routes, filename="route"):
        '''
        coordinates: list size seq_len, (x,y), size: [seq_len, 2]
        routes: list with size [seq_len]
        '''

        seq_len = len(routes)
        assert seq_len == len(coordinates)
        assert type(coordinates[0]) is tuple

        plot_route(coordinates, routes, f'{filename}.png')

    def plot_routes(self,coordinates, routes, filename="routes"):
        '''

        '''
        seq_len = len(routes[0])
        assert seq_len == len(coordinates)

        assert type(coordinates[0]) is tuple
        assert type(routes) is list
        plot_multiple_routes_for_same_coordinates(coordinates,
                                                  routes,
                                                  filename)


