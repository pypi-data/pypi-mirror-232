# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['organage',
 'organage.data',
 'organage.data.ml_models',
 'organage.data.ml_models.KADRC',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95.Adipose',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95.Artery',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95.Brain',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95.Conventional',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95.Heart',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95.Immune',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95.Intestine',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95.Kidney',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95.Liver',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95.Lung',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95.Muscle',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95.Organismal',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95.Pancreas',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95_fiba',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95_fiba.CognitionAdipose',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95_fiba.CognitionArtery',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95_fiba.CognitionBrain',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95_fiba.CognitionHeart',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95_fiba.CognitionImmune',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95_fiba.CognitionIntestine',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95_fiba.CognitionKidney',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95_fiba.CognitionLiver',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95_fiba.CognitionLung',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95_fiba.CognitionMuscle',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95_fiba.CognitionOrganismal',
 'organage.data.ml_models.KADRC.Zprot_stableassayps_perf95_fiba.CognitionPancreas']

package_data = \
{'': ['*']}

install_requires = \
['dill>=0.3.6',
 'pandas>=1.5.3',
 'scikit-learn==1.0.2',
 'statsmodels>=0.14.0,<0.15.0']

setup_kwargs = {
    'name': 'organage',
    'version': '0.5.2',
    'description': 'A package to pestimate organ-specific biological age using SomaScan plasma proteomics data',
    'long_description': '# organage\n\nA package to estimate organ-specific biological age using aging models trained on SomaScan plasma proteomics data (Oh and Rutledge et al. _Nature_ 2023)  \n\n## System requirements\n\n### Hardware requirements\n\norganage package requires only a standard computer with enough RAM to support the in-memory operations.\n\n### Software requirements\n\n#### OS Requirements\n\nThis package is supported for macOS and Linux. The package has been tested on the following systems:\n- maxOS 11.7.1\n- Linux: CentOS 7.x\n\n#### Python dependencies\n\n- python>=3.9 and <=3.10\n- dill>=0.3.6\n- pandas>=1.5.3\n- scikit-learn==1.0.2. aging models were trained using this specific version of scikit-learn\n\n## Installation\n\n```bash\n$ pip install organage\n```\n\n## Usage\n\n- see docs/example.ipynb\n\n## License\n\n`organage` was created by Hamilton Oh. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`organage` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'Hamilton Oh',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9',
}


setup(**setup_kwargs)
