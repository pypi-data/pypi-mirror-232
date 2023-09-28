[![Tetra AI](https://tetra.ai/img/logo.svg)](https://tetra.ai/)

# [RegNet: Imagenet classifier and general purpose backbone optimized for mobile and edge](https://pr-119.dl2059zyljmsx.amplifyapp.com/model-zoo/regnet)

RegNet is a machine learning model that can classify images from the Imagenet dataset.
It can also be used as a backbone in building more complex models for specific use cases.
We present an optimized implementation of RegNet suitable to export and run it on-device.

This is based on [RegNet](https://github.com/pytorch/vision/blob/main/torchvision/models/regnet.py). You can optionally
fine-tune the pre-trained model before walking through the examples below.

## Example & Usage

1. Install the package via pip:
```
pip install tetra_model_zoo[regnet]
```

2. Load the model & app
```
from tetra_model_zoo.regnet import Model
from tetra_model_zoo.regnet import App

# check app.py for more details
app = App(Model.from_pretrained())
```

3. Run prediction
```
from tetra_model_zoo.utils.asset_loaders import load_image
from tetra_model_zoo.imagenet_classifier.test_utils import TEST_IMAGENET_IMAGE
from tetra_model_zoo.regnet import MODEL_NAME

image = load_image(TEST_IMAGENET_IMAGE, MODEL_NAME)
app.predict(image)
```

See [app.py](../imagenet_classifier/app.py#L49) for more information about e2e usage of the model.

Please refer to our [general instructions on using models](../../#tetra-model-zoo)

### Optimize, Profile, and Validate RegNet for a device with Tetra Hub
Using Tetra Hub, you can easily optimize, profile, and validate RegNet for a device.

Run the following python script to export and optimize for iOS and Android:
```
python -m tetra_model_zoo.regnet.export [ --help ]
```

# Model In-Application Deployment instructions
<a href="mailto:support@tetra.ai?subject=Request Access for Tetra Hub&body=Interest in using RegNet in model zoo for deploying on-device.">Get in touch with us</a> to learn more!

## License
- Code in this repository is covered by the LICENSE file at the repository root.
- RegNet's license can be found [here](https://github.com/pytorch/vision/blob/main/LICENSE).

## References
* [Designing Network Design Spaces](https://arxiv.org/abs/2003.13678)
* [RegNet Source Repository](https://github.com/pytorch/vision/blob/main/torchvision/models/regnet.py)
