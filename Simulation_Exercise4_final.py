# -*- coding: utf-8 -*-
#!/usr/bin/env python
# coding: utf-8

# In[88]:


# Name: Muhammad Umer
# Student Number: 1686909

# Name: Lars Wouters
# Student Number: 1725076

import simpy
import random
import numpy as np
import statistics as st
import itertools

rng = np.random.default_rng(seed=2024)


def valid_options(budget):
    resource_dict = {"design" : 40000 ,"assembly" : 10000,"curing" : 10000,"inspection" :10000 ,"shipping" : 10000}
    
    limit = int(budget/10000)
    combinations = list(itertools.product(range(limit+1), repeat=5))
    costs = find_cost(combinations,resource_dict)
    valid_options = [comb for comb, cost in zip(combinations, costs) if cost == budget]
    valid_options = [[x + 1 for x in comb] for comb in valid_options]
    #what will be fed in for the capacity
    return valid_options

def find_best_investment_option(budget):
    
    all_valid_options = []
    average_option_quality = []
    
    for x in range(len(valid_options(budget))):
        option_quality = []
        for i in range(5): 
            capacity_list = valid_options(budget)[x]
            TireFactory = TireFactorySimulator()
            simulation = TireFactory.simulate(2024+i, 8760, capacity_list)
            option_quality.append((((TireFactory.nr_orders_completed_A+TireFactory.nr_orders_completed_B)/(TireFactory.nr_arrived_orders_A + TireFactory.nr_arrived_orders_B))))
        
        all_valid_options.append(valid_options(budget)[x])
        average_option_quality.append(st.mean(option_quality))
    
    best_option_quality = max(average_option_quality)
    idx_of_max_quality = average_option_quality.index(best_option_quality)
    winner_option = all_valid_options[idx_of_max_quality]
    winner_option = [x - 1 for x in winner_option]
    string_bo = "Design resource: {}, Assembly resource: {}, Curing resource: {}, Inspection resource: {}, Shipping resource: {}".format(winner_option[0], winner_option[1], winner_option[2], winner_option[3], winner_option[4])
    
    best_option_quality = best_option_quality
    best_option = {string_bo}

    return best_option, best_option_quality

def find_cost(combination,resource_dict):
    costs = list(resource_dict.values())
    cost = [sum((tuple(c * m for c, m in zip(comb, costs)))) for comb in combination]
    return cost



class TireFactorySimulator:

    def __init__(self):
        # Initialize variables
        self.nr_arrived_orders_A = 0  # The total number of type A orders the factory receives
        self.nr_arrived_orders_B = 0  # The total number of type B orders the factory receives

        self.nr_orders_designed_A = 0  # The total number of type A orders designed
        self.nr_orders_designed_B = 0  # The total number of type B orders designed

        self.nr_orders_assembled_A = 0  # The total number of type A orders assembled
        self.nr_orders_assembled_B = 0  # The total number of type B orders assembled

        self.nr_orders_cured_A = 0  # The total number of type A orders cured
        self.nr_orders_cured_B = 0  # The total number of type B orders cured

        self.nr_orders_completed_A = 0  # Total number of type A orders the factory finishes
        self.nr_orders_completed_B = 0  # Total number of type B orders the factory finishes
    
    def Shipping(self, env, seed, tiretype, ShippingResource):
        sr = ShippingResource.request()
        yield sr
        
        if tiretype == 'A':
            self.nr_orders_completed_A += 1
            yield env.timeout(12)
        else:
            self.nr_orders_completed_B += 1
            yield env.timeout(12)
            
        ShippingResource.release(sr)
        
    def Quality_control(self, env, seed, tiretype, QualityResource, ShippingResource):
        qc = QualityResource.request()
        yield qc
        
        random_value = random.uniform(0,1)
        
        if random_value < 0.01:
            yield env.timeout(36)
        else:
            yield env.timeout(12)
        
        env.process(self.Shipping(env, seed, tiretype, ShippingResource))    
        QualityResource.release(qc)
    
    def Tire_curing(self, env, seed, tiretype, CuringResource, QualityResource, ShippingResource):
        tc = CuringResource.request()
        yield tc
        
        if tiretype == 'A':
            self.nr_orders_cured_A += 1
            yield env.timeout(3*24)
        else:
            self.nr_orders_cured_B += 1
            yield env.timeout(3*24)
         
        env.process(self.Quality_control(env, seed, tiretype, QualityResource, ShippingResource))    
        CuringResource.release(tc)
    
    def Tire_assembly(self, env, seed, tiretype, has_crashed, AssemblyResource, CuringResource, QualityResource, ShippingResource):
        ta = AssemblyResource.request()
        yield ta
        
        random_number = random.uniform(0, 1)
        
        if random_number < 0.05 and has_crashed == 0: 
            has_crashed = 1
            AssemblyResource.release(ta)
            env.process(self.Subcomponent_collection(env, seed, tiretype, has_crashed, AssemblyResource, CuringResource, QualityResource, ShippingResource))
        else:
            
        
            if tiretype == 'A':
                self.nr_orders_assembled_A += 1
                yield env.timeout(random.uniform(1*24, 3*24))
            else:
                self.nr_orders_assembled_B += 1
                yield env.timeout(random.uniform(1*24, 3*24))
            
            env.process(self.Tire_curing(env, seed, tiretype, CuringResource, QualityResource, ShippingResource))
        
        AssemblyResource.release(ta)
    
    def Subcomponent_collection(self, env, seed, tiretype, has_crashed, AssemblyResource, CuringResource, QualityResource, ShippingResource):
        random_number = random.uniform(0, 1)
        
        if random_number <0.3 or has_crashed == 1: 
            yield env.timeout(random.uniform(2*24, 5*24))

        else:
            yield env.timeout(random.uniform(3, 6))

        env.process(self.Tire_assembly(env, seed, tiretype, has_crashed, AssemblyResource, CuringResource, QualityResource, ShippingResource))        
    
    def Tire(self, env, seed, duration, tiretype, DesignResource, AssemblyResource, CuringResource, QualityResource, ShippingResource):
        if tiretype < 0.1:
            tiretype = 'B' 
        else:
            tiretype = 'A'
        
        has_crashed = 0
        
        tr = DesignResource.request()
        yield tr
        #print("tire design for tire "of type", tiretype, "started at", round(env.now))
        if tiretype == 'A':
            self.nr_orders_designed_A += 1
            yield env.timeout(random.uniform(2*24, 5*24))
            env.process(self.Subcomponent_collection(env, seed, tiretype, has_crashed, AssemblyResource, CuringResource, QualityResource, ShippingResource))
            
        else:
            self.nr_orders_designed_B += 1
            yield env.timeout(random.uniform(5*24, 10*24))
            env.process(self.Subcomponent_collection(env, seed, tiretype, has_crashed, AssemblyResource, CuringResource, QualityResource, ShippingResource))
            
        DesignResource.release(tr)
        
        #print("tire of type", tiretype, "finished designing at", round(env.now))
        
    def Order_generator(self, env, seed, duration, DesignResource, AssemblyResource, CuringResource, QualityResource, ShippingResource):
        while env.now < duration:
            new_arrival_time = random.expovariate(0.5/24) #creates a time in hours until new order arrives
            
            
            
            
            R = random.random()
            
            if R < 0.1:
                self.nr_arrived_orders_B += 1
                yield env.timeout(new_arrival_time)
                #print("Order of type B has arrived at", round(env.now))
            else:
                self.nr_arrived_orders_A += 1
                yield env.timeout(new_arrival_time)
                #print("Order of type A has arrived at", round(env.now))
            
            env.process(self.Tire(env, seed, duration, R, DesignResource, AssemblyResource, CuringResource, QualityResource, ShippingResource))
            
    def simulate(self, seed, duration, capacity_list):
        random.seed(seed)  # use this line to set the seed

        # Define simulation environment
        env = simpy.Environment()
        DesignResource = simpy.Resource(env, capacity=capacity_list[0])
        AssemblyResource = simpy.Resource(env, capacity=capacity_list[1])
        CuringResource = simpy.Resource(env, capacity=capacity_list[2])
        QualityResource = simpy.Resource(env, capacity=capacity_list[3])
        ShippingResource = simpy.Resource(env, capacity=capacity_list[4])
        env.process(self.Order_generator(env, seed, duration, DesignResource, AssemblyResource, CuringResource, QualityResource, ShippingResource))
        env.run(until=duration)
        #print(random.expovariate(0.5/24)) #prints a random number in hours with a mean of 48
        
        
        return env

##########################
##### SOLUTION CHECK #####
##########################

print("\n\nDISCLAIMER\nIf you do not see DONE, this means that the program got stuck somewhere and consequently does not work properly. " +
      "Finally, note that you must use all attributes and functions that are defined in the template and give them correct values according to the assignment description. " +
      "You must not change names or signatures of predefined classes, attributes or functions. Doing so may lead to severe deduction of points. " +
      "\n\nRESULTS")

budget = 50000  # Example budget
best_investment, best_quality = find_best_investment_option(budget)

print(f'Best Investment Option: {best_investment}')
print(f'Best Completion Rate: {best_quality * 100:.2f}%')

print("\nDONE\n")

