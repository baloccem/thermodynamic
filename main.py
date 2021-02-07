#!/usr/bin/env python

'''Thermodynamic module to calculate the enthalpy and entropy
of a fluid at given temperature and pressure.

TBD:    
        - calculation of exergy
        - add test for saturated conditions
        - add more working fluids
 

Author: Emilio Balocchi
'''

import pandas as pd
import unittest


#ch_exergy = pd.read_excel('ch_exergy.xls',index_col=0, header = 0, skiprows = 0 )
H2O_complete = pd.read_csv('H2O_complete.dat',' ', header = 0, skiprows = 0 )
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


class Properties():
    def __init__(self,df,df_sat,T,P,x):
        self.T = T
        self.P = P
        self.x = x
        self.df = df
        self.df_sat = df_sat
   
    def saturation_check_state(self):
        '''
        check state against saturated line
        '''
        if self.T <= 647.29:
            self.P_sat = self.saturation_data().reset_index()['p [Bar]'][0]

            if round(self.P,2) > round(self.P_sat,2):
                #print("At current P of:", self.P, " bar the state condition is subcooled liquid")
                self.state = 0
            elif round(self.P,2) < round(self.P_sat,2):
                #print("At current P of:", self.P, " bar the state condition is superheated")
                self.state = 1
            else:
                #print("At current P of:", self.P, " bar the state condition is saturated")
                self.state = 2
        else:
            self.state = 1
        return self.state


    def saturation_data(self):
        '''
        input: df, thermodynamic table; 
        output: df, properties at defined T and P
        '''

        rows = self.get_closest_rows('sat')

        # interpolate by temperature
        slope = self.slope(rows,self.T,level=0)
        min_value_T = self.min_value(rows,level=0)
        max_value_T = self.max_value(rows,level=0)
        output = self.interpolation(min_value_T,max_value_T,slope)
        output = output.set_index(['T K','p [Bar]'])
        return output

           
    def get_property_data(self,rows,level):

        '''
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

   
    def get_closest_rows(self, temp_flag=''):
        '''
        input: df, thermodynamic table; 
        output: df, 4 closest rows from target T and P
       
        '''
        
        if temp_flag == 'sat':
            df_in = self.df_sat
        else:
            df_in = self.df

        df1 =df_in.loc[df_in.index.get_level_values(level=0) < self.T]
        df1 = df1[df1.index.get_level_values(level=0).max()==df1.index.get_level_values(level=0)]
        
        df2 =df_in.loc[df_in.index.get_level_values(level=0) > self.T]
        df2 = df2[df2.index.get_level_values(level=0).min()==df2.index.get_level_values(level=0)]    

        self.df_out = df1.append(df2)
        
        if temp_flag != 'sat':
 
            df3 =self.df_out.loc[self.df_out.index.get_level_values(level=1) < self.P]
            df3 = df3[df3.index.get_level_values(level=1).max()==df3.index.get_level_values(level=1)]
            
            df4 =self.df_out.loc[self.df_out.index.get_level_values(level=1) > self.P]
            df4 = df4[df4.index.get_level_values(level=1).min()==df4.index.get_level_values(level=1)] 

            self.df_out = df3.append(df4)

        return self.df_out

    def slope(self,rows,Prop,level):

        '''
        get slope to intrerpolate by defined property, level=0 temperature; level=1 pressure
        '''
        Prop_interp = (Prop - rows.index.get_level_values(level).unique()[0]) /  \
            (rows.index.get_level_values(level).unique()[1] - \
                rows.index.get_level_values(level).unique()[0])
        return Prop_interp

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

    def main_get_properties(self):
        self.saturation_check_state()
        get_closest_rows = self.get_closest_rows()
        get_property_data = self.get_property_data(get_closest_rows,level=0)
        get_property_data = self.get_property_data(get_property_data, level=1)   
        return get_property_data


    def get_property(self,liquid,gas):
        state = self.saturation_check_state()
        if state == 0:
            name = liquid
            X_total = self.main_get_properties()[name][0]   
        elif state == 1:
            name = gas
            X_total = self.main_get_properties()[name][0]   
        else:
            X_liq = self.main_get_properties()[liquid][0]
            X_gas = self.main_get_properties()[gas][0]
            X_total = X_liq + self.x*(X_gas - X_liq)
        return X_total

    def get_enthalpy(self):
        liquid = "H saturated liquid [kJ/kg]"
        gas = "H gas [kJ/kg]"
        return self.get_property(liquid,gas)

    def get_entropy(self):
        liquid = "S saturated liquid [kJ/(kg K)]"
        gas = "S gas [kJ/(kg K)]"
        return self.get_property(liquid,gas)

    def __str__(self):
        state = self.saturation_check_state()
        A = "At current T and P the state condition is"
        if state == 0:
             A += " subcooled liquid"
        elif state == 1:
            A += " superheated"
        else:
            A +=" saturated"
        
        output = str(A) + '\n' + str(repr(self.main_get_properties().T))

        return output


# some calculations

p1 = Properties(H2O_complete,H2O_sat,315.69,2.18,0)
p1.main_get_properties()
print(p1)

p2 = Properties(H2O_complete,H2O_sat,823,14,0)
p2.main_get_properties()
print(p2)

# saturated condition
p3 = Properties(H2O_complete,H2O_sat,351.15,0.4368,0.6)
p3.main_get_properties()
print(p3)



# ---------------------------
#           tests
# ---------------------------

class ThermoTest(unittest.TestCase):
    # enthalpy liquid water
    def test_Item_1(self):
        x = 104.8
        self.p = Properties(H2O_complete,H2O_sat,273.15+25,1,0)
        self.p.main_get_properties()
        self.assertAlmostEqual(self.p.get_enthalpy(), x, delta=x*0.01)

    # entropy liquid water
    def test_Item_2(self):
        x = 0.3673
        self.p = Properties(H2O_complete,H2O_sat,273.15+25,1,0)
        self.p.main_get_properties()
        self.assertAlmostEqual(self.p.get_entropy(), x, delta=x*0.01)


    # enthalpy superheated  water
    def test_Item_3(self):
        x = 3583.167
        self.p = Properties(H2O_complete,H2O_sat,823,14,0)
        self.p.main_get_properties()
        self.assertAlmostEqual(self.p.get_enthalpy(), x, delta=x*0.01)


    # enthalpy saturated  water
    #def test_Item_4(self):
    #    x = 3583.167
    #    self.p = Properties(H2O_complete,H2O_sat,823,14,0)
    #    self.p.main_get_properties()
    #    self.assertAlmostEqual(self.p.get_enthalpy(), x, delta=x*0.01)

if __name__ == "__main__":
    unittest.main()


