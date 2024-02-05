# -*- coding: utf-8 -*-
"""
IB API - Object Oriented Programming (OOPs) Basics - Class

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

class employee:
    def __init__(self,name="Tim",emp_id="E0001",exp=5,dept="R&D"):
        self.Name = name
        self.Emp_id = emp_id
        self.Exp = exp
        self.Dept = dept
        print("Employee {} is created".format(self.Emp_id))
        
    def calcSalary(self):
        if self.Exp > 5 and self.Dept == "R&D":
            self.Salary = 200000
        else:
            self.Salary = 80000
        print("Salary of {} calculated".format(self.Name))
            
    def empDesc(self):
        print("Employee {} from {} department working with us for {} years".format(self.Name,self.Dept,self.Exp))
    

emp1 = employee("Dan",emp_id="E0002",exp=0,dept="HR")
emp1.calcSalary()
emp1.Salary
emp1.empDesc()


