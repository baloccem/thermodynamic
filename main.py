#!/usr/bin/env python

'''Thermodynamic module to calculate the enthalpy and entropy
of a fluid at given temperature and pressure.

TBD:    
        - add saturated and superheated states
        - calculation of exergy
 

Author: Emilio Balocchi
'''

import pandas as pd
import unittest


#ch_exergy = pd.read_excel('ch_exergy.xls',index_col=0, header = 0, skiprows = 0 )
tblwater = pd.read_csv('water_l.dat',' ', header = 0, skiprows = 0 )
tblwater = tblwater.set_index(['T K','p [Bar]'])
#tblR134a = pd.read_csv('R134a.dat',' ', header = 0, skiprows = 0 )
#tblR134a = tblR134a.set_index(['T K','p [Bar]'])
#tblch4 = pd.read_csv('ch4.dat',' ', header = 0, skiprows = 0 )
#tblch4 = tblch4.set_index(['T K','p [Bar]'])
#tblmolmass = pd.read_excel('molecularmass.xls',index_col=0, header = 0, skiprows = 0 ) 
#tblmolmass = pd.read_excel('molecularmass.xls',index_col=0, header = 0, skiprows = 0 ) 
#constPropTerm = pd.read_csv('constPropTerm.txt',' ',header = 0, skiprows = 0 )



class State():
    def __init__(self,df,T,P,x,param):
        self.T = T
        self.P = P
        self.x = x
        self.df = df
        self.param = param

    def get_closest_rows(self):

        '''
        input: df, thermodynamic table; 
        output: df, 4 closest rows from target T and P
        '''

        dT_sup = 1
        dT_inf = 1
        dP_sup = 1
        dP_inf = 1
        rows = self.df.loc[(self.df.index.get_level_values(level=0) > self.T-dT_inf) &
                            (self.df.index.get_level_values(level=0) <= self.T+dT_sup)&
                            (self.df.index.get_level_values(level=1) > self.P-dP_inf) &
                            (self.df.index.get_level_values(level=1) <= self.P+dP_sup)]
        return rows

        
    def get_data_T_P(self):

        '''
        input: df, thermodynamic table; 
        output: df, properties at defined T and P
        '''

        rows = self.get_closest_rows()

        # interpolate by temperature
        slope_T = self.slope_T(rows)
        min_value_T = self.min_value(rows,level=0)
        max_value_T = self.max_value(rows,level=0)
        output = self.interpolation(min_value_T,max_value_T,slope_T)
        output = output.set_index(['T K','p [Bar]'])

        # interpolation by pressure over the interpolation by temperature
        slope_P = self.slope_P(output)
        min_value_P = self.min_value(output,level=1)
        max_value_P = self.max_value(output,level=1)
        output = self.interpolation(min_value_P,max_value_P,slope_P)
        output = output.set_index(['T K','p [Bar]'])
        return output

    def select_property(self):
        return self.get_data_T_P()[self.param][0]

    def check_state():

        '''
        check state against fluid saturated line
        '''

        pass


    def slope_T(self,rows):

        '''
        get slope to intrerpolate by temperature
        '''
        
        T_pr = (self.T - rows.index.get_level_values(level=0).unique()[0]) /  (rows.index.get_level_values(level=0).unique()[1] - \
                rows.index.get_level_values(level=0).unique()[0])
        return T_pr

    def min_value(self,rows,level):
        min_value = rows[rows.index.get_level_values(level=level)==rows.index.get_level_values(level=level).min()]
        min_value = min_value.reset_index()
        return min_value

    def max_value(self,rows,level):        
        max_value = rows[rows.index.get_level_values(level=level)==rows.index.get_level_values(level=level).max()]
        max_value = max_value.reset_index()
        return max_value

    def interpolation(self,value_min,value_max,slope):
        output = value_min +(value_max-value_min)*slope
        return output

    def slope_P(self,rows):
        # get slope to intrerpolate by pressure
        P_pr = (self.P-rows.index.get_level_values(level=1)[0])/(rows.index.get_level_values(level=1)[1]- \
        rows.index.get_level_values(level=1)[0])
        return P_pr


    def __str__(self):
        return 'The thermodinamic property {} has a value of {}'.format(self.param, self.select_property())

# trying some values

h1 = State(tblwater,297,1.51,0,'H saturated liquid [kJ/kg]')
h1.get_data_T_P()
h1.select_property()
print(h1,'\n')


s1 = State(tblwater,297,1.51,0,'S saturated liquid [kJ/(kg K)]')
s1.get_data_T_P()
s1.select_property()
print(s1,'\n')


# ---------------------------
#           tests
# ---------------------------

class ThermoTest(unittest.TestCase):
    # enthalpy sub-cooled  water
    def test_Item_1(self):
        #self.s = State(df,T,P,x,param)
        x = 104.8
        self.s = State(tblwater,273.15+25,1,0,'H saturated liquid [kJ/kg]')
        self.s.get_data_T_P()
        self.assertAlmostEqual(self.s.select_property(), x, delta=x*0.01)

    # entropy sasturated water
    def test_Item_2(self):
        #self.s = State(df,T,P,x,param)
        x = 0.3673
        self.s = State(tblwater,273.15+25,1,0,'S saturated liquid [kJ/(kg K)]')
        self.s.get_data_T_P()
        self.assertAlmostEqual(self.s.select_property(), x, delta=x*0.01)
        #print('error = ', ((104.8-self.s.get_data_T_P()[0])) / \
        #    self.s.get_data_T_P()[0] )

if __name__ == "__main__":
    unittest.main()


