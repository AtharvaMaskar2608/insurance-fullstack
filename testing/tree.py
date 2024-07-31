from typing import Dict
import json
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

class Tree:
    file_path: str = None
    data: Dict = None

    def __init__(self, file_path: str) -> None:
        """
        Description:
            - Constructor for Tree Data Class. 
            - Takes the filepath and loads json data. 

        Parameters:
            - file_path (str): Path of the json file you wanna read/interpret
        
        Returns:   
            - None
        """

        self.file_path = file_path

        # Load data from the path
        data = self._load_data()
        self.data = data
        self.temp_data = data
        self.client = OpenAI()


    def _load_data(self) -> Dict:
        """
        Description:
            - Internal method that loads json data from a file path.

        Parameters:
            - Self reference 
        
        Returns:
            - data (Dict): Data loaded from the json file path. 
        """

        file_path = self.file_path
        with open(file_path, 'r') as json_data:
            data = json.load(json_data)

        return data
    
    def _get_best_matching_key(self, data, input, gpt_key_values) -> Dict:
        """
        Description:
            - This function takes the data, query and returns which key matches the best to our query. 
        
        Parameters:
            - data (Dict): Dictionary of the data to be searched. 
            - input (str): Query that is to be searched
            - gpt_key_values (arr): Key values from which the answer is to be derived. 

        Returns:
            - result (str): The best key matching to the required inputs. 
        """
        # system_prompt = f"""
        # You will be given an array of objects having keys namely "node_name" and "children" in: {data}. You have to match the "children" of the nodes to the query {input} and return the the exact "node_name". Minimum confidence threshold is 92%.


        # Here are a couple of terms:
        # 1. Standalone TP or TP or Third Party or STP or 0+1  or ACT is  consider as  SATP or TP type policy
        # 2. Standalone OD or OD or Own Damage or SOD or 1+0 is consider as  SAOD or OD  type policy
        # 3. Comprehensive or Comp or Package or 1+1 or PACK is consider as Package/Comprehensive policy
        # 4. Power of the vehicle may or may not have cc in the end, it is your job to assume it. 
        # 5. Private car may be written as PC or pvt car and Two wheeler might be written as TW or 2W or 2 Wheeler.
        # 6. Some time at last node under the childe  part get more than one not null value and it relate to key od & Tp show consider this part as Comprehensive policy or Package policy


        # Interpret the following range expressions and apply them to find the best match:
        # - "up to" means less than or equal to the value.
        # - "more than" means greater than the value.
        # - "between" means the value is included in the range.
        # - "less than or equal to" means less than or equal to the value.
        # - "between X and Y" means the value is within the range [X, Y].
        # -  Ranges like "a-b" or "x-y" should be interpreted as the value being more than the lower limit and less than the upper limit if any value pass please check and use accordingly.
        # -  Ranges like example "100-500" or "30-100"  any other in similary pattern find it way should be interpreted as what ever value get this is between the lower and upper limit of that.


        # Note:
        # Just return the node_name and no extra text.
        # """

        system_prompt = f"""
        You will be given an array of objects having keys namely "node_name" and "children" in: {data}. You have to match the "children" of the nodes to the query {input} and return the the exact "node_name"

        Here are the types of policies and their definitions:

        1. **Standalone TP (Third Party)**: 
        - This includes terms like TP, Third Party, STP, 0+1, ACT. It is considered as SATP or TP type policy.

        2. **Standalone OD (Own Damage)**:
        - This includes terms like OD, Own Damage, SOD, 1+0, PC [SOD]. It is considered as SAOD or OD type policy.

        3. **Comprehensive/Package**:
        - This includes terms like Comprehensive, Comp, Package, 1+1, PACK, PC [PACK]. It is considered as Package policy.

        4. **Power of the Vehicle**:
        - Power may or may not include "cc" at the end. Assume it as needed.

        5. **Vehicle Type Abbreviations**:
        - Private Car may be written as PC or pvt car.
        - Two-Wheeler may be written as TW, 2W, or Two Wheeler.

        6. **Policy Determination**:
        - If the last node (i.e., the node containing values) has both 'OD Commission (including Rewards)' and 'TP Commission (including Rewards)' values that are not null, consider this part as a Comprehensive or Package policy.
        - If there is only one non-null value for either OD or TP, it is a Standalone policy.

        ### Special Cases:
        - If the input query is 'OD' and the policy type is SOD or SAOD, adjust the input query to match 'SOD' or 'SAOD'.
        - If the input query is 'TP' and the policy type is TP or SATP, adjust the input query to match 'STP' or 'SATP' accordingly.



        Interpret the following range expressions and apply them to find the best match:
        - "up to" means less than or equal to the value.
        - "more than" means greater than the value.
        - "between" means the value is included in the range.
        - "less than or equal to" means less than or equal to the value.
        - "between X and Y" means the value is within the range [X, Y].
        -  Ranges like "a-b" or "x-y" should be interpreted as the value being more than the lower limit and less than the upper limit if any value pass please check and use accordingly.
        -  Ranges like example "100-500" or "30-100"  any other in similary pattern find it way should be interpreted as what ever value get this is between the lower and upper limit of that.


        Note:
        Just return the node_name and no extra text.
        """

#      - Ranges like example "30-100" or any value like came as a-b or x-y should be interpreted as what ever value get is more than lower limit and less than upper limit follow under this.
        user_prompt = f""" You will be given an array of objects having keys namely "node_name" and "children": {data}. , find which node has children that best match {input} and return the the exact "node_name" from {gpt_key_values} only Without any extra text and without quotes: '' ."""
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ], 
            temperature= 0 ## added on 29-7-2024 by gopal
        ) 

        result = completion.choices[0].message.content.strip()

        return result
    

    def _tree_traversal(self, input, path):
        """
        Description:
            - This function traverses the tree and returns the best key
        
        Parameters:
            - data (Dict): data which is to be traversed
            - input (str): Query which is to be matched in the tree

        returns:
            - result (Dict): Dictionary of the best key
        """

        nodes = []
        # print("Working: ", data) #UNCOMMENT WHILE DEBUGGING
        for key, value in self.temp_data.items():
            children = []
            if isinstance(value, dict):
                # print(key, value.keys())
                for k in value.keys():
                    children.append(k)
        
            nodes.append({
                "node_name": key, 
                "children": children
            })
        
        # Generate Best key from nodes array
        # print(nodes) #UNCOMMENT WHLIE DEBUGGING
        try:        
            # Key values for Open AI
            gpt_key_values = [node['node_name'] for node in nodes]
            best_key = self._get_best_matching_key(nodes, input, gpt_key_values)
            path.append(best_key)
            print("Best Key", best_key) #UNCOMMENT WHILE DEBUGGIN
            next_level = self.temp_data[best_key]
            
            # Traverse the tree for the best key and check if the best key node is second last (has values), if yes return that
            children_values = next_level.values()
            # print(f"Children Values: {children_values}")
            grandchildren_values = []

            # for value in children_values:
            #     grandchildren_values.append(next_level[value])

            if isinstance(next_level, dict) and "values" not in children_values:
                if any(isinstance(val, dict) for val in next_level.values()):
                    self.temp_data = next_level
                    return self._tree_traversal(input, path)
                else:
                    return self.temp_data, next_level, path
            else:
                return self.temp_data, next_level, path
        except Exception as e:
            print(e)
            return self.temp_data, self.temp_data, path
        # None, self.temp_data, path

    def get_commision_rate(self, input):
        """
        Description:
            - This function takes the answer generated by the tree_traversal function and returns a final answer based on our input query. 

        Parameters:
            - input (str): Input Query String 
        
        Returns:
            - commision_rate (float): Commision rate
        """
        path = []
        best_results, commision, path = self._tree_traversal(input, path)
        # system_prompt = f"You will be given an output, based on the input query: {input}, return the commision rate applicable from: {commision}. If you receive more than 1 value return both of them separated by a comma with their assigned keys."

        system_prompt = f"You will be given an output, based on the input query: {input}, return the commision rate applicable from: {commision}. Just return the commision rate and no extra text."


        # user_prompt = f"For the given commision rate: {commision}. Find the commision rate for the given input query: {input}. If you receive more than 1 value return both of them separated by a comma with their assigned keys."

        user_prompt = f"For the given commision rate: {commision}. Find the commision rate for the given input query: {input}. Just return the commision rate and no extra text. If the value is none return 0."

        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
           temperature= 0 # added on 29-7-2024 by Gopal
        )

        result = completion.choices[0].message.content
        result_type = type(result)

        return path, best_results, float(result)
    
    def calculate_commission(self, amount: float, commission_rate: float) -> float:
        """
        Description:
            - This function calculates the commission for a given amount based on the commission rate.

        Parameters:
            - amount (float): The amount for which the commission is to be calculated.
            - commission_rate (float): The commission rate.

        Returns:
            - commission (float): The calculated commission.
        """
        commission = (commission_rate / 100) * amount
        return commission