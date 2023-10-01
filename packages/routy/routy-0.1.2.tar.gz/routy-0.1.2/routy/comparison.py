from routy.Logger import Logger
from routy.distanceUtilities.distanceUtilities import calculate_distance, DistanceType
from routy.plotUtilities.plotRoute import plot_multiple_routes_for_same_coordinates, plot_route


class Comparison:
    """
    Instantiate a comparison operation. This class is the starting point for comparing your
    routing models.
    :param None
    """

    def __init__(self):

        self.logger = Logger()

    def plot_route(self, coordinates, routes, filename="route"):
        '''
        Plot a single route based on coordinates and routes.

        :param coordinates: List of coordinates [(x, y)] for each point on the route.
        :type coordinates: list of tuples
        :param routes: List of indices representing the route.
        :type routes: list
        :param filename: Name of the output plot file (default: "route.png").
        :type filename: str
         :Examples:
        plot_route([(0, 0), (1, 1), (2, 2)], [0, 1, 2], "example_route.png")
        '''

        seq_len = len(routes)
        assert seq_len == len(coordinates)
        assert type(coordinates[0]) is tuple or len(coordinates[1]) ==2

        plot_route(coordinates, routes, f'{filename}.png')

    def plot_routes(self,coordinates, routes, filename="routes"):
        '''
        Plot multiple routes for the same set of coordinates.

        :param coordinates: List of coordinates [(x, y)] for each point on the routes.
        :type coordinates: list of tuples
        :param routes: List of lists, each representing a route with indices.
        :type routes: list of lists
        :param filename: Name of the output plot file (default: "routes.png").
        :type filename: str

         :Examples:
        plot_routes([(0, 0), (1, 1), (2, 2)], [[0, 1, 2], [2, 1, 0]], "example_routes.png")
        '''
        seq_len = len(routes[0])
        assert seq_len == len(coordinates)

        assert type(coordinates[0]) is tuple or  len(coordinates[0]) == 2
        assert type(routes) is list
        plot_multiple_routes_for_same_coordinates(coordinates,
                                                  routes,
                                                  filename)
    def compare_model_distances(self, coordinates, model1Routes, model2Routes, distance_type=DistanceType.EUCLIDEAN):
        """
        Calculate the percentage of routes where model1 suggests a shorter route compared to model2.

        Parameters:
        model1_routes (list): List of routes suggested by model1.
        model2_routes (list): List of routes suggested by model2.
        Returns:
        float: Percentage of routes where model1 suggests a shorter route compared to model2.
        """
        # assert they are a list of lists
        assert isinstance(coordinates, list)  and all(isinstance(coordinates, list) for item in coordinates)
        assert isinstance(model1Routes, list) and all(isinstance(model1Routes, list) for item in model1Routes)
        assert isinstance(model2Routes, list) and all(isinstance(model2Routes, list) for item in model2Routes)

        total_routes = len(coordinates)
        assert total_routes == len(model1Routes)
        assert total_routes == len(model2Routes)


        shorter_routes_count = 0

        for i in range(total_routes):
            coords = coordinates[i]
            route1 = model1Routes[i]
            route2 = model2Routes[i]
            dist1 = calculate_distance(coords, route1, distance_type)
            dist2 = calculate_distance(coords, route2, distance_type)

            if dist1 < dist2:
                shorter_routes_count += 1


        percentage_shorter_routes = (shorter_routes_count / total_routes) * 100

        self.logger.log(f'Using {distance_type} distance')
        self.logger.log(f'Model 1 has {percentage_shorter_routes:.2f}% shorter routes from model 2, for {total_routes} total routes')
        return percentage_shorter_routes
