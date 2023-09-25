''' Container class for storing and access multiple related models'''
from sklearn.base import BaseEstimator, ClassifierMixin

class MultipleOutputModel(BaseEstimator,ClassifierMixin):
    def __init__(self,*model_list): # no *args or **kargs
        ''' 
            Args:
                *modellist: list of (name, pred_type, model) tuples

                "name" is full description, "pred_type" is 'isCalc' or 'isPII' (e.g.)
        '''

        self.names   = [nm[0] for nm in model_list]
        self.model_tag = [nm[1] for nm in model_list]
        self.models  = [nm[2] for nm in model_list]
        
    def __repr__(self):
        return self.__class__.__name__ + ': ' + str([(n,m) for n, m in zip(self.names,self.models)])
    
    def __getitem__(self, key):
        if isinstance(key,int):
            return self.models[key]
        elif key in self.model_tag:
            return self.models[self.model_tag.index(key)]
        else:
            raise KeyError(f'bad key: {key}')

    def __keys__(self):
        for tag in self.models:
            yield tag

    def keys(self):
        return [tag for tag in self.models]

    def __items__(self):
        for tag, model in zip(self.model_tag, self.models):
            yield tag, model

    def items(self):
        return [(tag, model) for tag, model in zip(self.model_tag, self.models)]

    @property
    def tags(self):
        return [pt for pt in self.model_tag]
    
    @property
    def _estimator_type(self):
        if all(getattr(estimator, "_estimator_type", None) == "classifier" 
                for estimator in self.models):
            return "classifier"
        elif all(getattr(estimator, "_estimator_type", None) == "regressor" 
                for estimator in self.models):
            return "regressor"
        else:
            return None

    def add_model(self,name_tag_model):
        self.names.append(name_tag_model[0])
        self.model_tag.append(name_tag_model[1])
        self.models.append(name_tag_model[2])
        
    def add_models(self,name_tag_model_list):
        self.names.extend([nm[0] for nm in name_tag_model_list])
        self.model_tag.extend([nm[1] for nm in name_tag_model_list])
        self.models.extend([nm[2] for nm in name_tag_model_list])
    
    def fit(self, X, ylist, **kwargs):
        if isinstance(X,dict):
            assert len(ylist) == len(X), 'input data set and labels mismatched sizes'
            if isinstance(ylist,list):
                ylist = {k: ylist[i] for i,k in enumerate(X.keys())}
            data_keys = set(X.keys())
            model_keys = set(self.model_tag)
            assert len(data_keys.symmetric_difference(model_keys)) == 0, (
                'data and models do not share the same tags')
            return {pt: model.fit(X[pt], ylist[pt],**kwargs) 
                    for pt, model in zip(self.model_tag,self.models)}
        else:
            assert len(ylist) == len(self.models), (
                'number of models mismatched to the number of label sets')
            return {pt: model.fit(X,y,**kwargs) 
                    for pt, model, y in zip(self.model_tag,self.models,ylist)}

    def predict_proba(self, X, with_tag=True, **kwargs):
        ''' predict_proba

            the 1 - prob(class=0) is used to identify the probability of the class of interest
        '''
        if with_tag:
            if isinstance(X,dict):
                data_keys = set(X.keys())
                model_keys = set(self.model_tag)
                assert len(data_keys.symmetric_difference(model_keys)) == 0, (
                    'data and models do not share the same tags')
                return {pt: 1.0-model.predict_proba(X[pt],**kwargs)[:,0] 
                        for pt, model in zip(self.model_tag,self.models)}
            else:
                return {pt: 1.0-model.predict_proba(X,**kwargs)[:,0] 
                        for pt, model in zip(self.model_tag,self.models)}
        else:
            if isinstance(X,list) and len(X) == len(self.models):
                return [1.0-model.predict_proba(Xsub,**kwargs)[:,0] for model, Xsub in zip(self.models, X)]
            else:
                return [1.0-model.predict_proba(X,**kwargs)[:,0] for model in self.models]

    def predict(self, X, with_tag=True, **kwargs):
        if with_tag:
            if isinstance(X,dict):
                data_keys = set(X.keys())
                model_keys = set(self.model_tag)
                assert len(data_keys.symmetric_difference(model_keys)) == 0, (
                    'data and models do not share the same tags')
                return {pt: model.predict(X[pt],**kwargs) 
                        for pt, model in zip(self.model_tag,self.models)}
            else:
                return {pt: model.predict(X,**kwargs) 
                        for pt, model in zip(self.model_tag,self.models)}
        else:
            if isinstance(X,list) and len(X) == len(self.models):
                return [model.predict(Xsub,**kwargs) for model, Xsub in zip(self.models, X)]
            else:
                return [model.predict(X,**kwargs) for model in self.models]
    