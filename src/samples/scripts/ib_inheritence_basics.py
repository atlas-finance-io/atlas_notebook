# -*- coding: utf-8 -*-
"""
IB API - Object Oriented Programming (OOPs) Basics - Inheritance

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
    

class subEmployee(employee):
    def __init__(self,name="Tim",emp_id="E0001",exp=5,dept="R&D",sub_id="S001"):
        super(subEmployee,self).__init__(name,emp_id,exp,dept)
        self.Sub_ID = sub_id
        print("Employee {} is created for subsidiary {}".format(self.Emp_id,self.Sub_ID))
     
    def calcSalary(self):
        self.Salary = min(max(1,self.Exp)*30000,200000)
    

emp1_sub = subEmployee("Tina","E0004",6,"Marketing","S009")
emp1_sub.calcSalary()
emp1_sub.Salary