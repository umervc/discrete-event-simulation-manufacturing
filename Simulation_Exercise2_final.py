#!/usr/bin/env python
# coding: utf-8

# In[8]:


# Name: Muhammad Umer
# Student Number: 1686909

# Name: Lars Wouters
# Student Number: 1725076

import random
import simpy
import matplotlib.pyplot as plt
import numpy as np
import statistics as st


rng = np.random.default_rng(seed=2024)


def compute_resource_utilization(simulation, resource_type, simulation_duration):
    options = ['design','assembly', 'curing', 'quality', 'shipping']
    if str(resource_type) in options:
        cru = (getattr(simulation, f"total_{resource_type}_time") / simulation_duration)*100
        cru = round(int(cru), 2)
        return str(cru) + '%'
    else:
        return "RESOURCE TYPE DOES NOT EXIST!" 


def compute_average_cycle_time(simulation, tire_type):
    adj_cycle_start_time_A = simulation.cycle_start_time_A[:len(simulation.cycle_end_time_A)]
    adj_cycle_start_time_B = simulation.cycle_start_time_B[:len(simulation.cycle_end_time_B)]

    
    cycle_time_A = [a - b for a,b in zip(simulation.cycle_end_time_A, adj_cycle_start_time_A)]
    cycle_time_B = [a - b for a,b in zip(simulation.cycle_end_time_B, adj_cycle_start_time_B)]
    
    cycle_time_AB = []
    cycle_time_AB.extend(cycle_time_A) 
    cycle_time_AB.extend(cycle_time_B)
    
    if tire_type == 'A':
        return st.mean(cycle_time_A)
    elif tire_type == 'B':
        return st.mean(cycle_time_B)
    elif tire_type == 'Both':
        return st.mean(cycle_time_AB)
    else: 
        return "ORDER TYPE DOES NOT EXIST!"


def plot_processing_times(simulation):
    adj_cycle_start_time_A = simulation.cycle_start_time_A[:len(simulation.cycle_end_time_A)]
    adj_cycle_start_time_B = simulation.cycle_start_time_B[:len(simulation.cycle_end_time_B)]

    
    cycle_time_A = [a - b for a,b in zip(simulation.cycle_end_time_A, adj_cycle_start_time_A)]
    cycle_time_B = [a - b for a,b in zip(simulation.cycle_end_time_B, adj_cycle_start_time_B)]
    
    adj_cycle_start_time = simulation.cycle_start_time[:len(simulation.cycle_end_time)]
    cycle_times_AB = [a - b for a,b in zip(simulation.cycle_end_time, adj_cycle_start_time)]

    x3 = simulation.cycle_start_time[:len(simulation.cycle_end_time)]
    
    
    y1 = cycle_time_A
    y2= cycle_time_B
    y3 = cycle_times_AB
    
    plt.plot(adj_cycle_start_time_A, y1, '-', label='Type A')  # Line 1 with circle markers
    plt.plot(adj_cycle_start_time_B, y2, '-', label='Type B')  # Line 2 with cross markers
    plt.plot(x3, y3, '-', label='Both types')  # Line 3 with square markers

    plt.xlabel("Time of arrival of order throughout simulation (hours)");
    plt.ylabel("Cycle Time (hours)");
    plt.title("Development of order cycle times throughout the simulation");
    plt.grid(True)
    plt.legend()
    return plt.figure()


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
        
        self.total_design_time = 0
        self.total_assembly_time = 0
        self.total_curing_time = 0
        self.total_quality_time = 0
        self.total_shipping_time = 0
        
        self.cycle_start_time_A = []
        self.cycle_start_time_B = []
        self.cycle_end_time_A = []
        self.cycle_end_time_B = []
        self.cycle_start_time = []
        self.cycle_end_time = []

    def generate_orders(self, env, duration, designResource, assemblyResource, curingResource, qualityInspectionResource, shippingResource):
        """Generate orders at an exponential rate."""
        while env.now < duration:
            # Time between orders follows an exponential distribution with mean 1/λ
            yield env.timeout(random.expovariate(0.5/24))  # Wait for the next order

            # 90% chance of Type A, 10% chance of Type B
            order_type = 'A' if random.random() < 0.9 else 'B'
           
            if order_type == 'A':
                self.nr_arrived_orders_A += 1
                self.cycle_start_time_A.append(env.now)
            else:
                self.nr_arrived_orders_B += 1
                self.cycle_start_time_B.append(env.now)
            
            self.cycle_start_time.append(env.now)
            env.process(self.design_order(env, duration, order_type, designResource, assemblyResource, curingResource, qualityInspectionResource, shippingResource))
        else:
            self.design_order.interrupt()
            self.subCompCollect_for_order.interrupt()
            self.subCompCollect_for_order.interrupt()
            self.assemble_order.interrupt()
            self.cure_order.interrupt()
            self.q_inspect_order()
            self.complete_order()
            
            
    def design_order(self, env, duration, order_type, designResource, assemblyResource, curingResource, qualityInspectionResource, shippingResource):            
            req1 = designResource.request()
            yield req1
            design_start_time = env.now
            
            if order_type == 'A':
                yield env.timeout(random.uniform(48,120))
                self.nr_orders_designed_A += 1
                
            else:
                yield env.timeout(random.uniform(120,240))
                self.nr_orders_designed_B += 1
            
            designResource.release(req1)
            design_end_time = env.now 
        
            self.total_design_time += design_end_time - design_start_time 
            
            env.process(self.subCompCollect_for_order(env, duration, order_type, designResource, assemblyResource, curingResource, qualityInspectionResource, shippingResource))

                    
           

    def subCompCollect_for_order(self, env, duration, order_type, designResource, assemblyResource, curingResource, qualityInspectionResource, shippingResource):            
            if random.random() < 0.7:
                yield env.timeout(random.uniform(3,6))
            else:
                yield env.timeout(random.uniform(2*24,5*24))
                            
            env.process(self.assemble_order(env, duration, order_type, designResource, assemblyResource, curingResource, qualityInspectionResource, shippingResource))
    
    
    def assemble_order(self, env, duration, order_type, designResource, assemblyResource, curingResource, qualityInspectionResource, shippingResource):            
            req2 = assemblyResource.request()
            
            if random.random() < 0.95:
                yield req2
                assembly_start_time = env.now
                yield env.timeout(random.uniform(1*24,3*24))
                if order_type == 'A':
                    self.nr_orders_assembled_A += 1
                else :
                    self.nr_orders_assembled_B += 1 
                assemblyResource.release(req2)
                assembly_end_time = env.now

            else:
                yield req2
                assembly_start_time = env.now
                yield env.timeout(random.uniform(3,6))
                yield env.timeout(random.uniform(1*24,3*24))
                if order_type == 'A':
                    self.nr_orders_assembled_A += 1
                else :
                    self.nr_orders_assembled_B += 1 
                assemblyResource.release(req2)
                assembly_end_time = env.now
            
            self.total_assembly_time += assembly_end_time - assembly_start_time 
            
            env.process(self.cure_order(env, duration, order_type, designResource, assemblyResource, curingResource, qualityInspectionResource, shippingResource))
                
    def cure_order(self, env, duration, order_type, designResource, assemblyResource, curingResource, qualityInspectionResource, shippingResource):            
            req3 = curingResource.request()
            
            yield req3
            curing_start_time = env.now
            yield env.timeout(24*3)
            
            if order_type == 'A':
                self.nr_orders_cured_A += 1
            else:
                self.nr_orders_cured_B += 1
            
            curingResource.release(req3)
            curing_end_time = env.now
            
            self.total_curing_time += curing_end_time - curing_start_time
            
            env.process(self.q_inspect_order(env, duration, order_type, designResource, assemblyResource, curingResource, qualityInspectionResource, shippingResource))

    def q_inspect_order(self, env, duration, order_type, designResource, assemblyResource, curingResource, qualityInspectionResource, shippingResource):            
            req4 = qualityInspectionResource.request()
            
            yield req4
            quality_start_time = env.now
            
            yield env.timeout(12)            
            if rng.random() > 0.99:
                yield env.timeout(24)
            
            qualityInspectionResource.release(req4)
            quality_end_time = env.now
            
            self.total_quality_time += quality_end_time - quality_start_time
            
            env.process(self.complete_order(env, duration, order_type, designResource, assemblyResource, curingResource, qualityInspectionResource, shippingResource))
            
    def complete_order(self, env, duration, order_type, designResource, assemblyResource, curingResource, qualityInspectionResource, shippingResource):            
            req5 = shippingResource.request()
            
            yield req5
            shipping_start_time = env.now
            yield env.timeout(12)
            
            if order_type == 'A':
                self.nr_orders_completed_A += 1
                self.cycle_end_time_A.append(env.now)
            else:
                self.nr_orders_completed_B += 1
                self.cycle_end_time_B.append(env.now)
            
            self.cycle_end_time.append(env.now)
            
            shippingResource.release(req5)
            shipping_end_time = env.now
            
            self.total_shipping_time += shipping_end_time - shipping_start_time

    def simulate(self, seed, duration):
        random.seed(seed)  # use this line to set the seed
        
        # Define simulation environment
        env = simpy.Environment()
        
        designResource = simpy.Resource(env, capacity=1)
        assemblyResource = simpy.Resource(env, capacity=1)
        curingResource = simpy.Resource(env, capacity=1)
        qualityInspectionResource = simpy.Resource(env, capacity=1)
        shippingResource = simpy.Resource(env, capacity=1)

        
        env.process(self.generate_orders(env, duration, designResource, assemblyResource, curingResource, qualityInspectionResource, shippingResource))
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
print('\n')

# Example usage of the new functions
print('Utilization rate of design resources:', compute_resource_utilization(TireFactory, 'design', 8760))
print('Utilization rate of assembly resources:', compute_resource_utilization(TireFactory, 'assembly', 8760))
print('Utilization rate of curing resources:', compute_resource_utilization(TireFactory, 'curing', 8760))
print('Utilization rate of quality resources:', compute_resource_utilization(TireFactory, 'quality', 8760))
print('Utilization rate of shipping resources:', compute_resource_utilization(TireFactory, 'shipping', 8760))
print('\n')

print('Average cycle time of type A orders:', compute_average_cycle_time(TireFactory, 'A'))
print('Average cycle time of type B orders:', compute_average_cycle_time(TireFactory, 'B'))
print('Average cycle time of both types of orders:', compute_average_cycle_time(TireFactory, 'Both'))
print('\n')

# Dummy Plot
plt = plot_processing_times(TireFactory)
plt.show()


print("\nDONE\n")


# In[ ]:






