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
H2O_complete = pd.read_csv('water_l.dat',' ', header = 0, skiprows = 0 )
H2O_complete = H2O_complete.set_index(['T K','p [Bar]'])
H2O_sat = pd.read_csv('H2O_sat.dat',' ', header = 0, skiprows = 0 )
H2O_sat = H2O_sat.set_index(['T K','p [Bar]'])
#tblR134a = pd.read_csv('R134a.dat',' ', header = 0, skiprows = 0 )
#tblR134a = tblR134a.set_index(['T K','p [Bar]'])
#tblch4 = pd.read_csv('ch4.dat',' ', header = 0, skiprows = 0 )
#tblch4 = tblch4.set_index(['T K','p [Bar]'])
#tblmolmass = pd.read_excel('molecularmass.xls',index_col=0, header = 0, skiprows = 0 ) 
#tblmolmass = pd.read_excel('molecularmass.xls',index_col=0, header = 0, skiprows = 0 ) 
#constPropTerm = pd.read_csv('constPropTerm.txt',' ',header = 0, skiprows = 0 )


class State():
    def __init__(self,df,df_sat,T,P,x,param):
        self.T = T
        self.P = P
        self.x = x
        self.df = df
        self.df_sat = df_sat
        self.param = param

   
    def saturation_check_state(self):
        '''
        1.-
        check state against saturated line
        '''
        self.P_sat = self.saturation_data().reset_index()['p [Bar]'][0]

        print("The saturation pressure for the given temperature is: ", self.P_sat, ' bar')
        if float(self.P) > float(self.P_sat):
            print("At current P of:", self.P, " bar the state condition is subcooled liquid")
            self.state = 0
        elif float(self.P) < float(self.P_sat):
            print("At current P of:", self.P, " bar the state condition is superheated")
            self.state = 1
        else:
            print("At current P of:", self.P, " bar the state condition is saturated")
            self.state = 2
        return self.state


    def saturation_data(self):
        '''
        1.1.-
        input: df, thermodynamic table; 
        output: df, properties at defined T and P
        '''

        rows = self.saturation_closest_data()

        # interpolate by temperature
        slope = self.slope(rows,self.T,level=0)
        min_value_T = self.min_value(rows,level=0)
        max_value_T = self.max_value(rows,level=0)
        output = self.interpolation(min_value_T,max_value_T,slope)
        output = output.set_index(['T K','p [Bar]'])
        return output

    def saturation_closest_data(self):

        '''
        1.1.1.-
        input: df, thermodynamic table; 
        output: df, 2 closest rows from target T 
        '''

        df1 =self.df_sat.loc[self.df_sat.index.get_level_values(level=0) < self.T]
        df1 = df1[df1.index.get_level_values(level=0).max()==df1.index.get_level_values(level=0)]

        df2 =self.df_sat.loc[self.df_sat.index.get_level_values(level=0) > self.T]
        df2 = df2[df2.index.get_level_values(level=0).min()==df2.index.get_level_values(level=0)]

        return df1.append(df2)

       
    def get_property_data(self,rows,level):

        '''
        3.-
        input: df, thermodynamic table; 
        output: df, properties at defined T and P
        '''

        #rows = self.get_closest_rows()

        # interpolate by temperature
        if level == 0:
            slope = self.slope(rows,self.T,level)
        else:
            slope = self.slope(rows,self.P,level)
        min_value = self.min_value(rows,level)
        max_value = self.max_value(rows,level)
        output = self.interpolation(min_value,max_value,slope)
        output = output.set_index(['T K','p [Bar]'])
        return output

   
    def get_closest_rows(self):
        '''
        2.-
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

    def slope(self,rows,Prop,level):

        '''
        3.1.1.-
        get slope to intrerpolate by defined property, level=0 temperature; level=1 pressure
        '''
        Prop_interp = (Prop - rows.index.get_level_values(level).unique()[0]) /  \
            (rows.index.get_level_values(level).unique()[1] - \
                rows.index.get_level_values(level).unique()[0])
        return Prop_interp

    def min_value(self,rows,level):
        '''
        3.1.2.-
        '''
        min_value = rows[rows.index.get_level_values(level=level)==rows.index.get_level_values(level=level).min()]
        min_value = min_value.reset_index()
        return min_value

    def max_value(self,rows,level):     
        '''
        3.1.3.-
        '''  
        max_value = rows[rows.index.get_level_values(level=level)==rows.index.get_level_values(level=level).max()]
        max_value = max_value.reset_index()
        return max_value

    def interpolation(self,value_min,value_max,slope):
        '''
        3.1.4.-
        '''  
        output = value_min +(value_max-value_min)*slope
        return output

    #def __str__(self):
    #    return ''' {} = {}'''.format(self.param, self.select_property())

# trying some values

# h1 = State(H2O_complete,H2O_sat,297,1.51,0,'H saturated liquid [kJ/kg]')
# h1.select_property()

# print(h1,'\n')

#s = State(H2O_complete,H2O_sat,297,1.51,0,'H saturated liquid [kJ/kg]')
#s.saturation_check_state()
#s.main_get_properties()


t = State(H2O_complete,H2O_sat,297,1.51,0,'H saturated liquid [kJ/kg]')
t.saturation_check_state()
get_closest_rows = t.get_closest_rows()
get_property_data = t.get_property_data(get_closest_rows,level=0)
get_data_P = t.get_property_data(get_property_data, level=1)
print(get_data_P.T)


#print('state: ',)
#print(sat.saturation_data())

# h2 = State(H2O_complete,H2O_sat,297,1.51,0,'H saturated liquid [kJ/kg]')
#print('***',h2.saturation_closest_data(),'\n')

# s1 = State(H2O_complete,H2O_sat,297,1.51,0,'S saturated liquid [kJ/(kg K)]')
# s1.select_property()
# print(s1,'\n')


#print(H2O_sat)

# ---------------------------
#           tests
# ---------------------------
'''
class ThermoTest(unittest.TestCase):
    # enthalpy sub-cooled  water
    def test_Item_1(self):
        #self.s = State(df,T,P,x,param)
        x = 104.8
        self.s = State(H2O_complete,H2O_sat,273.15+25,1,0,'H saturated liquid [kJ/kg]')
        self.s.get_property_data()
        self.s.get_data_P()
        self.assertAlmostEqual(self.s.select_property(), x, delta=x*0.01)

    # entropy sasturated water
    def test_Item_2(self):
        #self.s = State(df,T,P,x,param)
        x = 0.3673
        self.s = State(H2O_complete,H2O_sat,273.15+25,1,0,'S saturated liquid [kJ/(kg K)]')
        self.s.get_property_data()
        self.s.get_data_P()
        self.assertAlmostEqual(self.s.select_property(), x, delta=x*0.01)
        #print('error = ', ((104.8-self.s.get_data_T_P()[0])) / \
        #    self.s.get_data_T_P()[0] )

    # enthalpy superheated  water
    def test_Item_3(self):
        #self.s = State(df,T,P,x,param)
        x = 3583.167
        self.s = State(H2O_complete,H2O_sat,823,14,0,'H gas [kJ/kg]')
        self.s.get_property_data()
        self.s.get_data_P()
        self.assertAlmostEqual(self.s.select_property(), x, delta=x*0.01)

if __name__ == "__main__":
    unittest.main()


'''