from .glm import GLMRegressor, GLMClassifier
from .gam import GAMRegressor, GAMClassifier
from .tree import TreeClassifier, TreeRegressor
from .figs import FIGSClassifier, FIGSRegressor
from .xgb1 import XGB1Classifier, XGB1Regressor
from .xgb2 import XGB2Classifier, XGB2Regressor
from .ebm import ExplainableBoostingRegressor, ExplainableBoostingClassifier
from .gaminet import GAMINetClassifier, GAMINetRegressor
from .reludnn import ReluDNNClassifier, ReluDNNRegressor

__all__ = ['GLMRegressor', 'GLMClassifier',
           'GAMRegressor', 'GAMClassifier',
           'TreeClassifier', 'TreeRegressor',
           'FIGSClassifier', 'FIGSRegressor',
           'XGB1Classifier', 'XGB1Regressor',
           'XGB2Classifier', 'XGB2Regressor',
           'ExplainableBoostingRegressor', 'ExplainableBoostingClassifier',
           'GAMINetClassifier', 'GAMINetRegressor',
           'ReluDNNClassifier', 'ReluDNNRegressor']


def get_all_supported_models():
    return sorted(__all__)
