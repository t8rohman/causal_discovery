import pandas as pd
from itertools import chain, combinations
import pingouin as pg


class CausalDiscovery():
    '''
    Class for conducting causal discovery using conditional independence tests (only for continuous data).

    Attributes:
        data (pd.DataFrame): The dataset for causal discovery.
        vars_lst (list): List of variable names in the dataset.
        skeleton (list): List of variable combinations representing potential edges in the skeleton graph.
    '''

    def __init__(self, data, vars_lst, skeleton):
        self.data = data
        self.vars_lst = vars_lst
        self.skeleton = skeleton


    def skeleton_result(self):
        '''
        Conducts conditional independence tests to determine the final skeleton graph and creates a skeleton table.

        Parameters:
            - vars_lst (list): List of variable names.
            - skeleton (list): List of variable combinations representing potential edges in the skeleton graph.

        Returns:
            - skeleton_table (DataFrame): DataFrame containing information about the edges, conditioning sets, p-values, removal status, and unshielded triples.
            - result (list): List of tuples representing the final skeleton graph edges after conditional independence tests.
        '''
        data = self.data
        vars_lst = self.vars_lst
        skeleton = self.skeleton

        # we will remove edges one by one from this
        result = list(combinations(vars_lst, 2))

        # create the placeholder for the skeleton table
        skeleton_table = pd.DataFrame(columns=['node_1', 'node_2', 'edges', 's', 'p-val', 'removed'])
        i = 0

        for x, y in skeleton:
            
            # then define other vars for the covariates / variables to control for the independence tests
            other_vars = [var for var in vars_lst if var != x and var != y]
            all_combinations = list(chain.from_iterable(combinations(other_vars, r) for r in range(len(other_vars) + 1)))
            
            for comb in all_combinations:
                comb = list(comb)
                # remove edges X-Y if X is independent of Y given a conditioning set S
                # starting with S as the empty set S={} and increasing its size (cardinality) by 1 for every iteration.
                p_val = pg.partial_corr(data=data, x=x, y=y, covar=comb)['p-val'].values[0]

                skeleton_table.loc[i, 'node_1'] = x
                skeleton_table.loc[i, 'node_2'] = y
                skeleton_table.loc[i, 'edges'] = f'{x} - {y}'
                skeleton_table.loc[i, 's'] = comb
                skeleton_table.loc[i, 'p-val'] = p_val

                i += 1

                # eliminate as many edges as possible using conditional independence tests
                if p_val > 0.05: 
                    try:
                        result.remove((x, y))
                    except ValueError:
                        pass

        # now we fill in all the blank data in the skeleton_table
        # fill in the removed table with False, if it the edge hasn't been removed yet
        skeleton_table['removed'] = True

        for i in result:
            pairs = ' - '.join(i)
            skeleton_table.loc[skeleton_table['edges'] == pairs, 'removed'] = False

        # create ind_corr list for the next step of determining the causal direction
        ind_corr = skeleton_table[skeleton_table['p-val'] < 0.05].drop_duplicates('edges')['edges'].values

        print("final skeleton graph:", result)

        self.skeleton_table = skeleton_table

        return skeleton_table, ind_corr, result


    def causal_direct_collider(self, nodes, collider):
        '''
        Infers causal directions between nodes based on the skeleton_table with collider rule.

        Parameters:
            - skeleton_table (pd.DataFrame): DataFrame containing skeleton edges and other relevant data.
            - nodes (list): List of nodes to analyze.
            - collider (str): Collider variable to consider in causal inference.

        Returns:
            - pd.DataFrame: DataFrame containing inferred causal directions.
        '''
        skeleton_table = self.skeleton_table

        # initialize empty DataFrames to store intermediate and final results
        causal_table = pd.DataFrame(columns=['from', 'dir', 'to'])
        final_causal_table = pd.DataFrame(columns=['from', 'dir', 'to'])

        # iterate over each pair of nodes
        for node in nodes:

            # filter the skeleton table to get relevant edges for the current node pair
            result = skeleton_table[
                (skeleton_table['node_1'].isin([node[0], node[1]])) & 
                (skeleton_table['node_2'].isin([node[1], node[0]]))
            ]
            
            records = []

            # check if there are significant edges for the current node pair
            # if there are significant edges, add them to the records
            if len(result[(result['p-val'] > 0.05) & result['s'].apply(lambda x: collider not in x)]) > 0:
                
                for n in node:
                    records.append({'from': n, 'to': collider})

                causal_table = pd.concat([causal_table] + [pd.DataFrame(records)], ignore_index=True)

            # if there are no significant edges, add the reverse direction to the records
            else:
                result = result.loc[result['s'].values == 'z', 'p-val'] > 0.05
                for n in node:
                    new_record = {'from': collider, 'to': n}
                    records.append(new_record)

                    causal_table = pd.concat([causal_table] + [pd.DataFrame(records)], ignore_index=True)
            
            final_causal_table = pd.concat([final_causal_table] + [causal_table])
            final_causal_table = final_causal_table.drop_duplicates(ignore_index=True)


        # remove edges that violate the causal direction
        # meaning that, prioritize the first rule, then second
        # if there's a conflict, then prioritize the first rule

        for i in range(len(final_causal_table)):
            if final_causal_table.loc[i, 'from'] == collider:
                if final_causal_table.loc[i, 'to'] in final_causal_table['from'].values:
                    final_causal_table.drop(i, inplace=True)

        # last step, tidying up the dataframe
                    
        final_causal_table['dir'] = '->'
        final_causal_table.reset_index(drop=True, inplace=True)

        # put it into a list so we can pass it directly later for causal effect size
        
        final_causal_list = list(zip(final_causal_table['from'], final_causal_table['to']))
        print(final_causal_list)

        return final_causal_table