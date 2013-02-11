# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 21:02:02 2013

@author: Nokukhanya Khwela
         Modified by Rowly Mudzhiba
"""

import numpy as np
from scipy import linalg
from scipy import signal
from plotgraphs import * 
from MODminifunc import*
from Tuners import*
 
# Process Transfer function 
Gp_n = [.125]       
Gp_d = [1,3,3,1]

TD =0                 # Dead time (s)                            
TD_n = [-(TD/2),1]               # Approximating the time delay term in the denominator
TD_d = [(TD/2),1]                # by a first-order Pade´ approximation

OL_Gp_n = np.polymul(Gp_n,TD_n)     # Dead time is added to the Process transfer function.
OL_Gp_d = np.polymul(Gp_d,TD_d)     
                                 
SP =1                       # Set Point            

tfinal = 50# simulation period
dt = 0.2
t = np.arange(0, tfinal, dt)
entries = len(t)
num =100               # number of tuning constant sets
x = np.zeros((entries,num))

por = np.zeros(num)             # What are these two variables?
tr = np.zeros(num)
[k_c,t_i,t_d]  = RPG(num,2)     # Random Parameter Generator
                                # Options: 1= P, 2 = PI, 3 = PID

# Different Ysp inputs
u = Ramp(t,dt,5,SP)             # Choose either of them by commenting the other
u = Step(t,SP)

  
# coefficients of the transfer function Gp = kp/(s^3 + As^2 + Bs +C)
A =3
B = 3
C = 1                 # Old process coefficients used in the initial project
kp =0.125 
SP = SP

kcst = np.arange(0,60,dt)

# Relatiopnship btwn kc and Ti obtained through the direct substitution method
tist =kp*kcst*A**2/(((A*B) - C - (kp*kcst))*(C + (kp*kcst)))


kczn ,tizn,tdzn = ZN(Gp_n,Gp_d,t,SP,'PI',dt,TD) # Ziegler-Nichols settings via function ZN
kcch ,tich,tdch = Cohen_Coon(OL_Gp_n,OL_Gp_d,t,SP,'PI',dt,TD)  

## System responce
for k in range(0,num):
    if k==num-1:
        kc = kczn           # Inserting Ziegler-Nicholas parameters
        ti = tizn
        td = tdzn
        
    elif k == num-2:        # Inserting Cohen-Coon parameters
        kc = kcch
        ti = tich
        td = tdch
    else:    
        kc =k_c[k]
        ti = t_i[k]
        td = t_d[k]
        

    if ti == 0:
        Gc_d = 1
        Gc_n = [kc*ti*td,(kc*ti),kc] 
        
    else:    
        Gc_n = [kc*ti*td,(kc*ti),kc]            #New code
        Gc_d = [ti,0] 
        
                                          # The controller and process TFs are entered here                                           # because the process selection interface hasnt been 
                                            # designed.
    TF_n = np.polymul(OL_Gp_n,Gc_n)
    TF_d = np.polyadd(np.polymul(Gc_d,OL_Gp_d),TF_n)
    (A,B,C,D) =signal.tf2ss(TF_n,TF_d)      # Transfer Function is converted to State Space
    
    mat = A                                 # new code
#    Amat = linalg.inv(mat)
    rootsA = np.array(linalg.eigvals(A))
    sys = signal.lti(A,B,C,D)
    
    
    step_response = signal.lsim((A,B,C,D),u,t,X0=None,interp=1)[1]
#    step_response = sys.step(T=t)[1]
   
    if (rootsA.real < 0).all():
        for i in range(0,entries):          # Stabilty of the Closed Loop is checked 
            X = step_response
            x[i,k] = X[i]
    else:
        x[:,k] = np.NaN
        
    
    k_c[k] = kc
    t_i[k] = ti
    
kc = k_c
ti = t_i
x = x.T

fig = plotgraphs(kc,ti,x,num,entries,t,tfinal,dt,SP,kcst,tist)