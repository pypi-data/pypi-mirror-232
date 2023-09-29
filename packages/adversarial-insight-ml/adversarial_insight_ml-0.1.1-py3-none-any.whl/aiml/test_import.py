import detectors
import timm
import torchvision as tv
import torchvision.transforms as T
from aiml.evaluation.evaluate import evaluate


cifar10_normalize_values = {
    "mean": [0.4914, 0.4822, 0.4465],
    "std": [0.2470, 0.2435, 0.2616],
}


def get_transforms(train=True, require_normalize=True):
    """Get data transformations for CIFAR-10 dataset."""
    state = "train" if train else "val"
    data_transforms = {
        "train": [
            T.AutoAugment(policy=T.AutoAugmentPolicy.CIFAR10),
            T.RandomHorizontalFlip(p=0.5),
            T.ToTensor(),
        ],
        "val": [
            T.ToTensor(),
        ],
    }
    transform_list = data_transforms[state]
    if require_normalize:
        transform_list = data_transforms[state] + [
            T.Normalize(
                mean=cifar10_normalize_values["mean"],
                std=cifar10_normalize_values["std"],
            )
        ]

    return T.Compose(transform_list)


def load_cifar10(train=True, require_normalize=True):
    """Return CIFAR10 dataset."""
    dataset = tv.datasets.CIFAR10(
        "./data",
        download=True,
        train=train,
        transform=get_transforms(train, require_normalize),
    )
    return dataset


def main():
    model = timm.create_model("resnet18_cifar10", pretrained=True)
    dataset = load_cifar10()
    evaluate(input_model=model, input_test_data=dataset)

if __name__ == "__main__":
    main()