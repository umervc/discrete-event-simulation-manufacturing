# -*- coding: utf-8 -*-
# Name: Muhammad Umer
# Student Number: 1686909

# Name: Lars Wouters
# Student Number: 1725076

import simpy
import random


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
            yield env.timeout(12)
            self.nr_orders_completed_A += 1
        else:
            yield env.timeout(12)
            self.nr_orders_completed_B += 1
            
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
            yield env.timeout(3*24)
            self.nr_orders_cured_A += 1
        else:
            yield env.timeout(3*24)
            self.nr_orders_cured_B += 1
         
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
                yield env.timeout(random.uniform(1*24, 3*24))
                self.nr_orders_assembled_A += 1
            else:
                yield env.timeout(random.uniform(1*24, 3*24))
                self.nr_orders_assembled_B += 1
            
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
            yield env.timeout(random.uniform(2*24, 5*24))
            self.nr_orders_designed_A += 1
            env.process(self.Subcomponent_collection(env, seed, tiretype, has_crashed, AssemblyResource, CuringResource, QualityResource, ShippingResource))
            
        else:
            yield env.timeout(random.uniform(5*24, 10*24))
            self.nr_orders_designed_B += 1
            env.process(self.Subcomponent_collection(env, seed, tiretype, has_crashed, AssemblyResource, CuringResource, QualityResource, ShippingResource))
            
        DesignResource.release(tr)
        
        #print("tire of type", tiretype, "finished designing at", round(env.now))
        
    def Order_generator(self, env, seed, duration, DesignResource, AssemblyResource, CuringResource, QualityResource, ShippingResource):
        while env.now < duration:
            new_arrival_time = random.expovariate(0.5/24) #creates a time in hours until new order arrives
            
            
            
            
            R = random.random()
            
            if R < 0.1:
                yield env.timeout(new_arrival_time)
                self.nr_arrived_orders_B += 1
                #print("Order of type B has arrived at", round(env.now))
            else:
                yield env.timeout(new_arrival_time)
                self.nr_arrived_orders_A += 1
                #print("Order of type A has arrived at", round(env.now))
            
            env.process(self.Tire(env, seed, duration, R, DesignResource, AssemblyResource, CuringResource, QualityResource, ShippingResource))
            
    def simulate(self, seed, duration):
        random.seed(seed)  # use this line to set the seed

        # Define simulation environment
        env = simpy.Environment()
        DesignResource = simpy.Resource(env, capacity=1)
        AssemblyResource = simpy.Resource(env, capacity=1)
        CuringResource = simpy.Resource(env, capacity=1)
        QualityResource = simpy.Resource(env, capacity=1)
        ShippingResource = simpy.Resource(env, capacity=1)
        env.process(self.Order_generator(env, seed, duration, DesignResource, AssemblyResource, CuringResource, QualityResource, ShippingResource))
        env.run(until=duration)
        
        return env
    
##########################
##### SOLUTION CHECK #####
##########################

print("\n\nDISCLAIMER\nIf you do not see DONE, this means that the program got stuck somewhere and consequently does not work properly. " +
      "Finally, note that you must use all attributes and functions that are defined in the template and give them correct values according to the assignment description. " +
      "You must not change names or signatures of predefined classes, attributes or functions. Doing so may lead to severe deduction of points. " +
      "\n\nRESULTS")

TireFactory = TireFactorySimulator()
simulation = TireFactory.simulate(2024, 8760) # need 2024, 8760

# Check if the simulation is correct
print('Simulation Duration:', simulation.peek())
print('Total Arrived Orders A:', TireFactory.nr_arrived_orders_A)
print('Total Arrived Orders B:', TireFactory.nr_arrived_orders_B)
print('Designed Orders A:', TireFactory.nr_orders_designed_A)
print('Designed Orders B:', TireFactory.nr_orders_designed_B)
print('Assembled Orders A:', TireFactory.nr_orders_assembled_A)
print('Assembled Orders B:', TireFactory.nr_orders_assembled_B)
print('Cured Orders A:', TireFactory.nr_orders_cured_A)
print('Cured Orders B:', TireFactory.nr_orders_cured_B)
print('Completed Orders A:', TireFactory.nr_orders_completed_A)
print('Completed Orders B:', TireFactory.nr_orders_completed_B)

print("\nDONE\n")