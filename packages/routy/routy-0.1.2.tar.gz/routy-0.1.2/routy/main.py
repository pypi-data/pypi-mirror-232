import torch
from torch.autograd import Variable

from torch.utils.data import  DataLoader

from routy import Comparison
from routy.distanceUtilities.distanceUtilities import DistanceType
from routy.modelsForComparison.tsp import CombinatorialRL, reward, TSPDataset
import matplotlib

from routy.plotUtilities.plotRoute import plot_multiple_routes_for_same_coordinates

matplotlib.use('Agg')



if __name__ == '__main__':

        num_nodes = 10
        seed = 12345
        valid_size = 100
        embedding_size = 128
        n_glimpses = 1
        hidden_size = 128
        tanh_exploration = 10
        use_tanh = False

        comparison = Comparison()
        model = CombinatorialRL(
            embedding_size,
            hidden_size,
            num_nodes,
            n_glimpses,
            tanh_exploration,
            use_tanh,
            reward,
            embedding="Conv",
            attention="Dot")

        path = "tsp_20_dot_attention.pt"
        model.load_state_dict(torch.load(path))

        train_size = 15
        val_size = 1000
        batch_size = 100
        num_nodes = 20
        epochs = 20

        train_20_dataset = TSPDataset(num_nodes, train_size)
        loader = DataLoader(train_20_dataset,
                            batch_size=batch_size,
                        shuffle=True, num_workers=1)
        tsp_dot_attention_model20_path = "tsp_20_dot_attention.pt"

        tsp_dot_attention_model20_trained = CombinatorialRL(
            embedding_size,
            hidden_size,
            20,
            n_glimpses,
            tanh_exploration,
            use_tanh,
            reward, embedding="Conv",
            attention="Dot")
        tsp_dot_attention_model20_trained.load_state_dict(torch.load(tsp_dot_attention_model20_path))
        tsp_dot_attention_model20_trained.eval()

        # We compare with an untrained model
        tsp_20_model_untrained = CombinatorialRL(
            embedding_size,
            hidden_size,
            20,
            n_glimpses,
            tanh_exploration,
            use_tanh,
            reward,
            embedding="Conv",
            attention="Dot")
        tsp_20_model_untrained.eval()
        test_size = 100
        test_20_dataset = TSPDataset(20, test_size)
        test_loader_20nodes = DataLoader(test_20_dataset, batch_size=100, shuffle=True, num_workers=1)

        test_5_dataset = TSPDataset(5, test_size)
        test_loader = DataLoader(test_5_dataset, batch_size=2, shuffle=True, num_workers=1)

        tsp_dot_attention_model20_path = "tsp_20_dot_attention.pt"

        tsp_dot_attention_model20_trained = CombinatorialRL(
            embedding_size,
            hidden_size,
            20,
            n_glimpses,
            tanh_exploration,
            use_tanh,
            reward, embedding="Conv",
            attention="Dot")
        tsp_dot_attention_model20_trained.load_state_dict(torch.load(tsp_dot_attention_model20_path))
        tsp_dot_attention_model20_trained.eval()

        # We compare with an untrained model
        tsp_20_model_untrained = CombinatorialRL(
            embedding_size,
            hidden_size,
            20,
            n_glimpses,
            tanh_exploration,
            use_tanh,
            reward, embedding="Conv",
            attention="Dot")
        tsp_20_model_untrained.eval()


        # for batch_id, sample_batch in enumerate(test_loader):
        #     inputs = Variable(sample_batch)
        #     R_1, probs_1, actions_1, actions_idxs_trained1 = tsp_dot_attention_model20_trained(inputs)
        #
        #     R, probs, actions, actions_idxs = tsp_20_model_untrained(inputs)
        #
        #     print(f'{actions_idxs}')
        #     tensors = actions_idxs
        #
        #     first_column_row = torch.cat([tensor[0].unsqueeze(0) for tensor in tensors])
        #     sec_column_row = torch.cat([tensor[1].unsqueeze(0) for tensor in tensors])
        #
        #
        #     print(f'{first_column_row}')
        #     print(f'{sec_column_row}')
        #     assert inputs.size(1) == 2
        #     assert actions_1[0][0].size(0) == 2
        #
        #     "inputs: [test_size, 2, seq_len]"
        #     "actions_1: [seq_len, test_size, 2]"
        #
        #     route = first_column_row.tolist()
        #     multiple_routes = [first_column_row.tolist(), sec_column_row.tolist()]
        #     coordinates = inputs[0].transpose(0,1).tolist()
        #
        #
        #     comparison.plot_route(coordinates,route)
        #     comparison.plot_routes(coordinates, multiple_routes)

        routes1 = []
        routes2 = []
        coordinates = []
        for batch_id, sample_batch in enumerate(test_loader):
            inputs = Variable(sample_batch)
            R_1, probs_1, actions_1, actions_idxs_trained1 = tsp_dot_attention_model20_trained(inputs)

            R, probs, actions, actions_idxs = tsp_20_model_untrained(inputs)

            print(f'{actions_idxs}')
            tensors = actions_idxs

            first_column_row = torch.cat([tensor[0].unsqueeze(0) for tensor in tensors])
            sec_column_row = torch.cat([tensor[1].unsqueeze(0) for tensor in tensors])


            print(f'{first_column_row}')
            print(f'{sec_column_row}')
            assert inputs.size(1) == 2
            assert actions_1[0][0].size(0) == 2

            "inputs: [test_size, 2, seq_len]"
            "actions_1: [seq_len, test_size, 2]"

            # route = first_column_row.tolist()
            # multiple_routes = [first_column_row.tolist(), sec_column_row.tolist()]
            # coordinates = inputs[0].transpose(0,1).tolist()

            coords = inputs[0].transpose(0, 1).tolist()
            coordinates.append(coords)
            routes1.append(first_column_row.tolist())
            routes2.append(sec_column_row.tolist())


        comparison.compare_model_distances(coordinates, routes1, routes2, DistanceType.EUCLIDEAN)
        comparison.compare_model_distances(coordinates, routes1, routes2, DistanceType.MANHATTAN)
        comparison.compare_model_distances(coordinates, routes1, routes2, DistanceType.CHEBYSHEV)