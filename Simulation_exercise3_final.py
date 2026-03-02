# -*- coding: utf-8 -*-
# Name: Muhammad Umer
# Student Number: 1686909

# Name: Lars Wouters
# Student Number: 1725076

import simpy
import random
import json


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

        with open('order_arrival_information.json') as data:
            self.arrival_information = json.load(data)

        

    def Shipping(self, env, seed, tiretype, ShippingResource, prio):
        
        sr = ShippingResource.request(priority=prio)
        yield sr
        
        if tiretype == 'A':
            yield env.timeout(12)
            self.nr_orders_completed_A += 1
        else:
            yield env.timeout(12)
            self.nr_orders_completed_B += 1
            
        ShippingResource.release(sr)
        
    def Quality_control(self, env, seed, tiretype, QualityResource, ShippingResource, prio):
        
        if len(ShippingResource.queue) == 0 and len(QualityResource.queue) != 0:
            qc = ShippingResource.request(priority=prio)
            yield qc
            
            random_value = random.uniform(0,1)
            
            if random_value < 0.01:
                yield env.timeout(36)
            else:
                yield env.timeout(12)
                
            ShippingResource.release(qc)
            env.process(self.Shipping(env, seed, tiretype, ShippingResource, prio))    
            
        else:
            qc = QualityResource.request(priority=prio)
            yield qc
            
            random_value = random.uniform(0,1)
            
            if random_value < 0.01:
                yield env.timeout(36)
            else:
                yield env.timeout(12)
            QualityResource.release(qc)
            env.process(self.Shipping(env, seed, tiretype, ShippingResource, prio))    
             
    def Tire_curing(self, env, seed, tiretype, CuringResource, QualityResource, ShippingResource, prio):
        tc = CuringResource.request(priority=prio)
        yield tc
        
        if tiretype == 'A':
            yield env.timeout(3*24)
            self.nr_orders_cured_A += 1
        else:
            yield env.timeout(3*24)
            self.nr_orders_cured_B += 1
         
        env.process(self.Quality_control(env, seed, tiretype, QualityResource, ShippingResource, prio))    
        CuringResource.release(tc)
    
    def Tire_assembly(self, env, seed, tiretype, has_crashed, AssemblyResource, CuringResource, QualityResource, ShippingResource, prio):
        
        if len(CuringResource.queue) == 0:
            ta = CuringResource.request(priority=prio)
            yield ta
            
            random_number = random.uniform(0, 1)
            
            if random_number < 0.05 and has_crashed == 0: 
                has_crashed = 1
                AssemblyResource.release(ta)
                env.process(self.Subcomponent_collection(env, seed, tiretype, has_crashed, AssemblyResource, CuringResource, QualityResource, ShippingResource, prio))
            else:
                if tiretype == 'A':
                    yield env.timeout(random.uniform(1*24, 3*24))
                    self.nr_orders_assembled_A += 1
                else:
                    yield env.timeout(random.uniform(1*24, 3*24))
                    self.nr_orders_assembled_B += 1
                
                env.process(self.Tire_curing(env, seed, tiretype, CuringResource, QualityResource, ShippingResource, prio))
            
            CuringResource.release(ta)
            
        else:
            ta = AssemblyResource.request(priority=prio)
            yield ta
            
            random_number = random.uniform(0, 1)
            
            if random_number < 0.05 and has_crashed == 0: 
                has_crashed = 1
                AssemblyResource.release(ta)
                env.process(self.Subcomponent_collection(env, seed, tiretype, has_crashed, AssemblyResource, CuringResource, QualityResource, ShippingResource, prio))
            else:
                
            
                if tiretype == 'A':
                    yield env.timeout(random.uniform(1*24, 3*24))
                    self.nr_orders_assembled_A += 1
                else:
                    yield env.timeout(random.uniform(1*24, 3*24))
                    self.nr_orders_assembled_B += 1
                
                env.process(self.Tire_curing(env, seed, tiretype, CuringResource, QualityResource, ShippingResource, prio))
            
            AssemblyResource.release(ta)
    
    def Subcomponent_collection(self, env, seed, tiretype, has_crashed, AssemblyResource, CuringResource, QualityResource, ShippingResource, prio):
        random_number = random.uniform(0, 1)
        
        if random_number <0.3 or has_crashed == 1: 
            yield env.timeout(random.uniform(2*24, 5*24))

        else:
            yield env.timeout(random.uniform(3, 6))

        env.process(self.Tire_assembly(env, seed, tiretype, has_crashed, AssemblyResource, CuringResource, QualityResource, ShippingResource, prio))        
    
    def Tire(self, env, seed, duration, tiretype, DesignResource, AssemblyResource, CuringResource, QualityResource, ShippingResource, prio):
        has_crashed = 0
        

        tr = DesignResource.request(priority=prio)
        yield tr
        #print("tire design for tire "of type", tiretype, "started at", round(env.now))
        if tiretype == 'A':
            yield env.timeout(random.uniform(2*24, 5*24))
            self.nr_orders_designed_A += 1
            env.process(self.Subcomponent_collection(env, seed, tiretype, has_crashed, AssemblyResource, CuringResource, QualityResource, ShippingResource, prio))
            
        else:
            yield env.timeout(random.uniform(5*24, 10*24))
            self.nr_orders_designed_B += 1
            env.process(self.Subcomponent_collection(env, seed, tiretype, has_crashed, AssemblyResource, CuringResource, QualityResource, ShippingResource, prio))
        DesignResource.release(tr)
        

    def new_Order_generator(self, env, seed, duration, DesignResource, AssemblyResource, CuringResource, QualityResource, ShippingResource):
        if TireFactory.arrival_information["order_types"][0] == 'B':
            prio = -1
            yield env.timeout(TireFactory.arrival_information["order_arrival_times"][0])
            self.nr_arrived_orders_B += 1
            env.process(self.Tire(env, seed, duration, TireFactory.arrival_information["order_types"][0] , DesignResource, AssemblyResource, CuringResource, QualityResource, ShippingResource, prio))
        else:
            prio = 0
            yield env.timeout(TireFactory.arrival_information["order_arrival_times"][0])
            self.nr_arrived_orders_A += 1
            env.process(self.Tire(env, seed, duration, TireFactory.arrival_information["order_types"][0] , DesignResource, AssemblyResource, CuringResource, QualityResource, ShippingResource, prio))
        
        for i in range(1,len(TireFactory.arrival_information["order_arrival_times"])):           
            if TireFactory.arrival_information["order_types"][i] == 'B':
                prio = -1
                yield env.timeout(TireFactory.arrival_information["order_arrival_times"][i] - TireFactory.arrival_information["order_arrival_times"][i-1])
                self.nr_arrived_orders_B += 1
                env.process(self.Tire(env, seed, duration, TireFactory.arrival_information["order_types"][i] , DesignResource, AssemblyResource, CuringResource, QualityResource, ShippingResource, prio))
            else:
                prio = 0
                yield env.timeout(TireFactory.arrival_information["order_arrival_times"][i] - TireFactory.arrival_information["order_arrival_times"][i-1])
                self.nr_arrived_orders_A += 1
                env.process(self.Tire(env, seed, duration, TireFactory.arrival_information["order_types"][i] , DesignResource, AssemblyResource, CuringResource, QualityResource, ShippingResource, prio))
            
    def simulate(self, seed, duration):
        random.seed(seed)

        # Define simulation environment
        env = simpy.Environment()

        DesignResource = simpy.PriorityResource(env, capacity=1)
        AssemblyResource = simpy.PriorityResource(env, capacity=1)
        CuringResource = simpy.PriorityResource(env, capacity=1)
        QualityResource = simpy.PriorityResource(env, capacity=1)
        ShippingResource = simpy.PriorityResource(env, capacity=1)
        
        env.process(self.new_Order_generator(env, seed, duration, DesignResource, AssemblyResource, CuringResource, QualityResource, ShippingResource))
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
simulation = TireFactory.simulate(2024, 8760)

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
#print(TireFactory.arrival_information)
#print(len(TireFactory.arrival_information["order_arrival_times"]))#185
print("\nDONE\n")