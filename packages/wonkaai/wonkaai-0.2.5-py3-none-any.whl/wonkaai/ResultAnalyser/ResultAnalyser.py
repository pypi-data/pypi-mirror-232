from copy import deepcopy

class ResultAnalyser() :

    def __init__ (self) :
        self.raw = {}
        self.n = 0

    def append_item(self, key, value, raw=None) :
        if raw is None :
            raw = self.raw

        if key not in raw :
            raw[key] = {}

        if isinstance(value, dict) : 
            for k, v in value.items() :
                raw[key] = self.append_item(k, v, raw[key])
            return raw
        else :
            if value in raw[key] :
                raw[key][value] += 1
            else :
                raw[key][value] = 1
            return raw
        
    
    def add_result(self, res) :
        #iterate over dict res
        for key, value in res.items() :
            self.raw = self.append_item(key, value)
        self.n += 1

    def divide_by_n(self, d=None):
        if d is None:
            d = deepcopy(self.raw)

        for key, value in d.items():
            if isinstance(value, dict):
                self.divide_by_n(value)
            else:
                # Check if the leaf value is an integer and non-zero
                if isinstance(value, int) and value != 0:
                    d[key] = value / self.n

        self.results = d


    def get_dict_depth(self, d, depth=0):
        if not isinstance(d, dict) or not d:
            return depth
        else:
            return max(self.get_dict_depth(v, depth + 1) for v in d.values())

    def get_max(self, d = None):
        if d is None:
            d = deepcopy(self.results)

        for key, value in d.items():
            if not isinstance(value, dict):
                continue
            depth = self.get_dict_depth(value)
            if depth == 1:
                d[key] = max(value, key=value.get)
            else:
                self.get_max(value)
        self.results_max = d

    def analyse(self) :
        self.divide_by_n()
        print(self.results)
        self.get_max()

    def to_dict(self) :
        return {
            "results" : self.results,
            "results_max" : self.results_max
        }