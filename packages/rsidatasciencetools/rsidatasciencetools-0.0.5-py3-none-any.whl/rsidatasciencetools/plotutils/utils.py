'''utilities to improve plotting mechanisms'''

class DictToIntAutoIncr(dict):
    def __init__(self, *args, **kwargs):
        super(DictToIntAutoIncr,self).__init__(*args, **kwargs)
        self.counter = 0
    def __getitem__(self, k):
        if not(super(DictToIntAutoIncr,self).__contains__(k)):
            super(DictToIntAutoIncr,self).__setitem__(k, self.counter)
            self.counter += 1
        return super(DictToIntAutoIncr,self).__getitem__(k)


