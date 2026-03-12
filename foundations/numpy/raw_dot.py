def dot_product(l1,l2):
    def check(l1,l2):
        # if it's 1-D
        if type(l1[0])==list and type(l2[0] == list):
                if len(l1[0])==len(l2):
                            return True
                else:
                            return "dimension not compatible!"
        else:
                return False
    def dot_prod(l1,l2):
        list_dot = 0
        for i in range(len(l1)):
                list_dot+=(l1[i]*l2[i])
        return list_dot
    
    # START of dot prod
    final = []
    if check(l1,l2)!=True and check(l1,l2)!=False:
        return check(l1,l2)
    elif check(l1,l2)==False: #means it's 1-D
        return dot_prod(l1,l2)
    else:
        for i in range(len(l1)):
                
                lst = []
                k =val = 0
                while k<3:
                    temp = []
                    for j in range(3):
                            temp.append(l2[j][k])
                    k+=1
                    lst.append(temp)
                temp=[]
                for l in lst:
                    temp.append(dot_prod(l1[i], l))
                
                final.append(temp)
        return final
    
l1 = [[1,2,1], 
      [0,1,1],
      [1,0,0]] 
l2 = [[1,0,1], 
      [1,0,0],
      [1,1,1]]

print(dot_product(l1,l2))
print(np.dot(l1,l2))