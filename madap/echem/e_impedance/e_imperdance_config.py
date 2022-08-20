# Here there are some configurations for some suggested circuits
import json

suggested_circuits = dict()

suggested_circuits['R1-CPE1'] = [500, 1, 1]
suggested_circuits['R1-C1'] = [500, 0.000001]
suggested_circuits['R1-W1'] = [500, 100]
suggested_circuits['R1-L1'] = [500, 0.0001]
suggested_circuits['p(R1,C1)'] = [500, 0.000001]
suggested_circuits['p(R1,L1)'] = [500, 0.0001]
suggested_circuits['p(R1,CPE1)'] = [500, 1, 1]
suggested_circuits['p(C1,R1-CPE1)'] = [0.0001, 50, 1, 0.5]
suggested_circuits['p(C1,R1-W1)'] = [0.0001, 50, 5]
suggested_circuits['R0-p(R1,C1)'] = [50, 100, 0.001]  #simplified Randles
suggested_circuits['R0-p(CPE1,C1)'] = [50, 0.001, 0.05, 0.01]
suggested_circuits['R0-p(R1,CPE1)'] = [800, 1e+14, 1e-9, 0.8]
suggested_circuits['R0-p(R1-Wo1,CPE1)'] = [500, 500, 1, 0.1, 1, 1]   #'Randles w/ CPE'
suggested_circuits['R0-p(R1-Wo1,C1)'] = [500, 500, 1, 1, 0.000001]    #'Randles'
suggested_circuits['L1-R1-p(CPE1,R2)'] = [0.0002, 200, 2, 0.8, 50]
suggested_circuits['R0-p(R1-C1,C2)'] = [100, 300, 0.001, 1]
suggested_circuits['R0-p(R1-W1,C1)'] = [100, 200, 5, 0.00001]
suggested_circuits['R0-p(R1-W1,CPE1)'] = [100, 200, 5, 0.00001, 0.8]
suggested_circuits['R0-p(R1-CPE1,C1)'] = [100, 100, 2, 0.8, 0.01]
suggested_circuits['R1-p(CPE1,R2-CPE2)'] = [100, 2, 0.8, 200, 0.01, 0.8]
suggested_circuits['R1-p(CPE1,R2-p(CPE2,R3))'] = [100, 0.05, 0.8, 20, 0.001, 0.8, 20]
suggested_circuits['R1-p(CPE1,R2-p(CPE2,p(R3,L1-R4)))'] =  [100, 0.05, 0.8, 20, 0.001, 0.8, 20, 0.00001, 10]
suggested_circuits['R1-p(CPE1,R2)-p(CPE2,R3-CPE3)'] = [100, 0.05, 0.8, 20, 0.001, 0.8, 20, 0.001, 0.8]
suggested_circuits['R1-p(CPE1,R2)-p(CPE2,R3)'] = [10, 0.0001, 0.8, 20, 0.1, 0.8, 10]
suggested_circuits['R1-p(CPE1,R2)-p(CPE2,p(R3,L1-R4)'] = [100, 0.05, 0.8, 20, 0.001, 0.8, 20, 0.00001, 10]
suggested_circuits['R1-p(CPE1,p(R2,L1-R3)'] =  [100, 0.05, 0.8, 20, 0.001, 10]
suggested_circuits['R1-p(R2,CPE1-p(CPE2,R3))'] = [100, 50, 0.05, 0.8, 0.001, 0.8, 10]
suggested_circuits['R0-p(R1,CPE1)-p(R2,CPE2)-W1'] = [.34, .42, .08, 1, 1.23, 0.002, 0.62, 0.14]
suggested_circuits['R0-p(R1,C1)-p(R2-Wo1,C2)'] = [.01, .01, 100, .01, .05, 100, 1]
suggested_circuits['R0-p(R1,C1)-p(R2,C2)-Wo1'] = [.01, .005, .1, .005, .1, .001, 1]
suggested_circuits['p(C1,R1,R2-C2,R3-C3)'] = [0.000001, 200, 400, 0.0001, 800, 0.01]
suggested_circuits['p(C1,R1)-p(R2,C2)'] = [0.00001, 50, 100, 0.01]
suggested_circuits['p(C1,R1)-p(R2,C2)-p(R3,C3)'] = [0.00001, 150, 200, 0.001, 100, 0.1]
suggested_circuits['R1-p(R2,CPE1)-p(R3,CPE2)'] = [100, 50, 0.05, 0.8, 20, 0.001, 0.8]
suggested_circuits['p(R1,C1)-p(R2,C2)-C3'] = [200, 0.0001, 200, 0.01, 1]
suggested_circuits['p(CPE1,R1-p(R2,CPE2))'] = [2, 0.8, 50, 50, 1.5, 0.9]

with open("suggested_circuits.json", "w") as outfile:
    json.dump(suggested_circuits, outfile)

