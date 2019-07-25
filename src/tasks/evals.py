import torch
from tqdm import tqdm

from src.utils import set_and_print_random_seed
from src.uncertainty_measures import aggregate_data, get_predictions_from_multiple_tests, get_all_uncertainty_measures


def evaluate(model, evalloader, device, val=False):
    """

    Args:
        model (torch.nn.Module child): the model we evaluate
        evalloader (torch.utils.data.dataloader.DataLoader): test data
        device (torch.device || str): cpu or gpu
        val (Bool): if in validation mode, we do not print the progress bar

    Returns:
        float: accuracy
        torch.Tensor: size (number of test samples, number of classes) output of softmax of all the inputs

    """
    accuracy, all_outputs = eval_bayesian(model, evalloader, number_of_tests=1, device=device, val=val)
    return accuracy, all_outputs


def eval_bayesian(model, evalloader, number_of_tests, device, val=False):
    """

    Args:
        model (torch.nn.Module child): the model we evaluate
        evalloader (torch.utils.data.dataloader.DataLoader): test data
        number_of_tests (int): the number of times we do a forward for each input
        device (torch.device || str): cpu or gpu
        val (Bool): if in validation mode, we do not print the progress bar

    Returns:
        float: accuracy
        torch.Tensor: size (number of test samples, number of classes) output of softmax of all the inputs
    """
    model.eval()
    number_of_samples = len(evalloader.dataset)
    batch_size = evalloader.batch_size
    number_of_classes = model.number_of_classes
    all_correct_labels = torch.zeros(1, requires_grad=False)
    all_outputs = torch.Tensor().to(device).detach()

    if val:
        iterator = enumerate(evalloader)
    else:
        iterator = tqdm(enumerate(evalloader))
    for batch_idx, data in iterator:
        inputs, labels = [x.to(device).detach() for x in data]
        batch_outputs = torch.Tensor(number_of_tests, batch_size, number_of_classes).to(device).detach()
        for test_idx in range(number_of_tests):
            output = model(inputs)
            batch_outputs[test_idx] = output.detach()
        predicted_labels = get_predictions_from_multiple_tests(batch_outputs)

        all_correct_labels += torch.sum(predicted_labels.int() - labels.int() == 0)
        all_outputs = torch.cat((all_outputs, batch_outputs))

    accuracy = (all_correct_labels / number_of_samples).item()

    return accuracy, all_outputs


def eval_random(model, batch_size, img_channels, img_dim, number_of_tests, random_seed=None, device='cpu'):
    """

    Args:
        model (torch.nn.Module child): the model we evaluate
        batch_size (int): The size of the random sample
        img_channels (int): dimension of the random sample
        img_dim (int): dimension of the random sample
        number_of_tests (int): the number of times we do a forward for each input
        random_seed (int): the seed of the random generation, for reproducibility
        device (torch.device || str): cpu or gpu

    Returns:
        torch.Tensor: size (batch_size): the variation-ratio uncertainty
        torch.Tensor: size (batch_size): the predictive entropy uncertainty
        torch.Tensor: size (batch_size): the mutual information uncertainty
        int: the seed of the random generation, for reproducibility

    """
    number_of_classes = model.number_of_classes
    seed = set_and_print_random_seed(random_seed)
    random_noise = torch.randn(batch_size, img_channels, img_dim, img_dim).to(device)
    output_random = torch.Tensor(number_of_tests, batch_size, number_of_classes)
    for test_idx in range(number_of_tests):
        output_random[test_idx] = model(random_noise).detach()
    random_vr, random_prediction_entropy, random_mi = get_all_uncertainty_measures(output_random)
    return random_vr, random_prediction_entropy, random_mi, seed
