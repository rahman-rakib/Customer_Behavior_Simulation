import numpy as np
import pandas as pd
import random
import cv2

class Supermarket:
    """Gives supermarket floor layout with customer location"""

    def __init__(self, floor_image, customers):
        self.floor_image = floor_image
        self.customers = customers

    def draw(self, customers):
        """ Draws customer locations on the supermarket image"""
        
        self.frame = self.floor_image.copy()
        for customer in customers:
            y, x = customer.current_location
            self.frame[y:y+15, x:x+15, :] = customer.image

class Customer:
    """Helps moving customers across the supermarket"""

    def __init__(self):
        
        # transition probability matrix
        self.prob_matrix = pd.read_csv('data/transition_matrix.csv')
        self.prob_matrix = self.prob_matrix.set_index(self.prob_matrix.columns)
        
        # customer image
        self.image = np.zeros((15, 15, 3), dtype=np.uint8)
        for i in range(3):
            self.image[:,:,i] = random.randint(0, 255)
        
        # initial location at entrance
        self.current_location = [650, random.randint(680, 880)]
        # initial target section
        self.target_section = np.random.choice(
            self.prob_matrix.columns, 
            p=self.prob_matrix.loc['entry'].values
            )
        # initial target position coordinates
        self.ty, self.tx = self.get_coordinates(self.target_section)
        
        # counters for time and customer number
        self.time_counter, self.customer_counter = (0,0)


    def get_coordinates(self, target):
        """find position coordinates in a target section"""
        
        if target == 'checkout':
            ty, tx = [555, random.choice([100, 250, 400, 535])]
        else:
            ty = random.randint(135, 435)
            if target == 'drinks': tx = random.randint(65, 175)
            if target == 'dairy': tx = random.randint(295, 405)
            if target == 'spices': tx = random.randint(535, 640)
            if target == 'fruit': tx = random.randint(755, 865)
        
        return ty, tx


    def next_target(self, section):
        """finding the next section with the probability matrix, 
        setting target coordinates to new values"""

        section_probs = self.prob_matrix.loc[section]
        self.target_section = np.random.choice(
            section_probs.index, 
            p=section_probs.values
            )
        self.ty, self.tx = self.get_coordinates(self.target_section)

    
    def remove_add_customer(self):
        """removes and add customers"""
        self.image = np.zeros((15, 15, 3),dtype=np.uint8)
        if self.time_counter < 150:
            self.image[:,:,2] = 255  # red image
            self.time_counter += 1   # waiting
        else:
            self.image[:,:,0:3] = 255 # white image (disappearing)
            if self.customer_counter == 0:
                customers.append(Customer())
                self.customer_counter +=1


    def move_customer(self):
        """ Moving a customer through the supermarket"""
        
        y, x = self.current_location

        # case: target is checkout
        if self.ty == 555:
            # reached checkout 
            if y == self.ty and x == self.tx:
                self.remove_add_customer()
            # go down towards checkout
            elif y < 470: 
                self.current_location[0] += 1       # go down
            # reach checkout x and pass through
            elif y >= 470:
                if x == self.tx: self.current_location[0] += 1  # go down
                if x > self.tx: self.current_location[1] -= 1   # go left
                else: self.current_location[1] += 1             # go right
        
        # case target x and y is reached:
        elif x == self.tx and y == self.ty:
            self.next_target(self.target_section)

        # case: target x is not yet reached
        elif x != self.tx:
            if y == 100 or y == 450:
                if self.tx > x: self.current_location[1] += 1   # go right
                else: self.current_location[1] -= 1             # go left
            elif y < 275 or y > 450: 
                self.current_location[0] -= 1   # go up
            else:
                self.current_location[0] += 1   # go down

        # case: target x is reached, but not target y
        else:
            if self.ty < y: self.current_location[0] -= 1   # go up
            else: self.current_location[0] += 1             # go down


if __name__ == '__main__':
    
    # get customer number
    print("enter number of customers allowed")
    customer_number = int(input())

    # get supermarket layout
    layout_image = cv2.imread('floor_plan.png')

    # customer instances:
    customers = []
    for _ in range(customer_number):
        customers.append(Customer())

    # supermarket instance:
    simulation = Supermarket(layout_image, customers)

    # drawing of the supermarket and moving of customers
    while True:
        simulation.draw(customers)
        for customer in customers:
            customer.move_customer()
        cv2.imshow('frame', simulation.frame)
        
        # stop if q is pressed 
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()
