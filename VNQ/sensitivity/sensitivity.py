from model import inequality


utility = [1,1]

result = inequality.GiniAlgorithm.instance().base_gini(utility, 3)

print(result)


